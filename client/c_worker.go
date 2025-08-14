package main

import (
	"client/config"
	"client/utils"
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"
	"sync"
	"time"
)

func ClientWorker(clientID string, wg *sync.WaitGroup) {
	socket, err := NewZmqSocket(clientID, config.AppConfig.Client.BrokerTCPAddress)
	if err != nil {
		log.Printf("\nerror in creating new socket [%v]\n", err)
		return
	}
	socket.SetLinger(-1)

	defer func() {
		log.Printf("[Client %s]: Closing socket and marking WaitGroup Done. Waiting for all messages to be sent...", clientID)
		socket.Close()                                                            // This will now block until all messages are delivered (or an error occurs)
		log.Printf("[Client %s]: Socket closed and all messages sent.", clientID) // This log will appear only after messages are flushed
		wg.Done()
	}()
	filePath := config.AppConfig.Client.FilePath
	chunkSize := config.AppConfig.Client.ChunkSize

	// ------ Initial "CONNECT" message ----------
	// Client (DEALER) sends only the application command.
	// The DEALER socket automatically prepends its ZMQ identity and an empty delimiter.
	_, err = socket.SendMessage([]string{"", "CONNECT"})
	if err != nil {
		log.Panicln("error in sending --CONNECT-- msg", err)
	}
	log.Printf("[Client %s]: Sent CONNECT request.", clientID)

	// --- 2. Receive "CONNECTED" reply ---
	// Client (DEALER) receives only the application frames back,
	// as the ROUTER broker strips its routing frames.
	replyFrames, err := socket.RecvMessage(0)
	if err != nil {
		log.Println("[Client]: error in recv CONNECT reply: ", err)
		return
	}
	fmt.Println("[Client] - got CONNECT reply", replyFrames)

	if replyFrames[1] == "CONNECTED" {
		log.Println("connected cID :", clientID)
		totalChunks, err := getTotalChunks(chunkSize, filePath)
		if err != nil {
			return
		}
		msg := []string{"", "METADATA", fmt.Sprintf("%d", totalChunks)}
		log.Printf("[Client %s]: Sending metadata message: %v", clientID, msg)
		_, err = socket.SendMessage(msg) // Use ... to send each string as a separate frame
		if err != nil {
			fmt.Printf("\nerror in sending {msg-MetaData} for client %s, err :[%v]\n", clientID, err)
			return
		}
		log.Printf("[Client %s]: Metadata message sent!", clientID)
		// --- 4. Receive "SENDDATA" signal ---
		// Client (DEALER) receives only application frames.
		replyFrames, err = socket.RecvMessage(0) // RecvMessage here must match the broker's send
		if err != nil {
			fmt.Printf("\nerror in recv reply after METADATA for client %s: [%v]\n", clientID, err)
			return
		}
		log.Printf("[Client %s]: Got reply after METADATA: %v", clientID, replyFrames)

		if len(replyFrames) >= 1 && replyFrames[1] == "SENDDATA" {
			log.Printf("[Client %s]: Received SENDDATA signal, starting file transfer.", clientID)
			file, err := os.Open(filePath)
			if err != nil {
				log.Println("[Client]: Error opening file:", err)
				return
			}
			defer file.Close()

			chunkBuf := make([]byte, chunkSize)
			chunkNumber := 1
			// Use per-worker file for client logs; workerID will be known after first ACK
			var csvWriter *csv.Writer
			var logFile *os.File
			ackAfter := 0
			for {
				bytesRead, err := file.Read(chunkBuf)
				if err != nil && err != io.EOF {
					log.Println("Error reading chunk:", err)
					break
				}
				if bytesRead == 0 {
					break // done
				}
				sentAt := time.Now().UnixMilli()
				// Include client-sent timestamp as a frame after data
				dataMsg := []string{"", "CHUNK", strconv.Itoa(chunkNumber), string(chunkBuf[:bytesRead]), strconv.FormatInt(sentAt, 10)}
				_, err = socket.SendMessage(dataMsg)
				if err != nil {
					log.Printf("\nerror in sending {DATA(chunks)} client : %s   |  err [%v]", clientID, err)
				}
				log.Printf("\n[Client]: %s - Sent chunk :%d", clientID, chunkNumber)
				ackAfter++

				if !config.AppConfig.Common.NoAck && ackAfter >= 10 {
					// wait for ACK before sending the next chunk
					ackFrames, err := socket.RecvMessage(0)
					ackAt := time.Now().UnixMilli()
					if err != nil {
						log.Printf("\nerror waiting for ACK for chunk %d: %v", chunkNumber, err)
						break
					}
					// Expected shape: [workerID, clientID, "ACK", chunkNum]
					if len(ackFrames) < 2 || ackFrames[1] != "ACK" {
						log.Printf("\ninvalid ACK message: %v", ackFrames)
						break
					}
					//verify ACK chunk number matches (if provided)
					if len(ackFrames) >= 2 {
						if ackChunkNum, err := strconv.Atoi(ackFrames[2]); err == nil {
							if ackChunkNum != chunkNumber {
								log.Printf("\nACK chunk mismatch: expected %d got %d", chunkNumber, ackChunkNum)
							}
						}
					}
					// On first ACK, we know workerID; init file per worker (broker sends [clientID, workerID, ...])
					workerIDForLog := ""
					if len(ackFrames) >= 4 {
						workerIDForLog = ackFrames[3] // ackFrames[2] should be workerID
					}
					if csvWriter == nil {
						csvWriter, logFile, err = utils.InitClientTimingCSV(clientID, workerIDForLog)
						if err != nil {
							log.Println("Error initializing client timing CSV:", err)
						}
						if logFile != nil {
							defer logFile.Close()
						}
					}
					if csvWriter != nil {
						rtt := sentAt - ackAt
						csvWriter.Write([]string{
							strconv.Itoa(chunkNumber),
							strconv.FormatInt(rtt, 10),
						})
						csvWriter.Flush()
					}
					ackAfter = 0
				}

				chunkNumber++
			}
			log.Println("**********Client waiting for DONE FROM SERVER :", clientID)
			// wait for done from server after sending all chunk
			replyFrames, err = socket.RecvMessage(0)
			if err != nil {
				fmt.Printf("\nerror in recv reply after chunks for client %s: [%v]\n", clientID, err)
				return
			}
			log.Printf("[Client %s]: Got reply after CHUNKS: %v", clientID, replyFrames)
			if len(replyFrames) >= 1 && replyFrames[1] == "DONE" {
				_, err = socket.SendMessage("", "Done")
				if err != nil {
					log.Printf("\nerror in sending {DONE} client : %s   |  err [%v]\n", clientID, err)
				}
			}

			checksum, err := utils.ComputeSHA256(filePath)
			if err != nil {
				log.Println("Checksum error:", err)
				return
			}
			log.Println(" checksum is:", checksum)
		}

	} else {
		log.Printf("[Client %s]: Initial connection failed. Expected 'CONNECTED', got: %v", clientID, replyFrames)
	}
}

func getTotalChunks(chunkSize int64, filePath string) (int64, error) {

	fileInfo, err := os.Stat(filePath)

	if err != nil {
		log.Println("error getting file info: ", err)
		return 0, err
	}
	totalChunks := (fileInfo.Size() + chunkSize - 1) / chunkSize
	return totalChunks, nil
}
