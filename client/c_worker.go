package main

import (
	"client/config"
	"crypto/sha256"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"
	"sync"
	"time"

	zmq "github.com/pebbe/zmq4"
)

func ClientWorker(clientID string, wg *sync.WaitGroup, nxt chan struct{}) {
	socket, err := newZmqSocket(clientID, config.AppConfig.Client.BrokerTCPAddress)
	if err != nil {
		log.Printf("\nerror in creating new socket [%v]\n", err)
		log.Panic(err)
	}
	nxt <- struct{}{}

	defer func() {
		socket.Close()
		// log.Printf("[Client %s]: Socket closed .", clientID)
		wg.Done()
	}()
	filePath := config.AppConfig.Client.FilePath
	chunkSize := config.AppConfig.Client.ChunkSize

	// ------ Initial "CONNECT" message ----------
	_, err = socket.SendMessage([]string{"CONNECT"})
	if err != nil {
		log.Panicln("error in sending --CONNECT-- msg", err)
	}
	// log.Printf("[Client %s]: Sent CONNECT request.", clientID)

	// --- 2. Receive "CONNECTED" reply ---

	replyFrames, err := socket.RecvMessage(0)
	if err != nil {
		log.Println("[Client]: error in recv CONNECT reply: ", err)
		log.Panic(err)
	}
	// fmt.Println("[Client] - got CONNECT reply", replyFrames)

	if replyFrames[0] == "CONNECTED" {
		log.Println("connected cID :", clientID)
		totalChunks, err := getTotalChunks(chunkSize, filePath)
		if err != nil {
			log.Panic(err)
		}

		msg := []string{"METADATA", fmt.Sprintf("%d", totalChunks)}
		// log.Printf("[Client %s]: Sending metadata message: %v", clientID, msg)

		_, err = socket.SendMessage(msg) // Use ... to send each string as a separate frame
		if err != nil {
			fmt.Printf("\nerror in sending {msg-MetaData} for client %s, err :[%v]\n", clientID, err)
			log.Panic(err)
		}
		// log.Printf("[Client %s]: Metadata message sent!", clientID)

		//===================SEND DATA===================//

		replyFrames, err = socket.RecvMessage(0)
		if err != nil {
			fmt.Printf("\nerror in recv reply after METADATA for client %s: [%v]\n", clientID, err)
			log.Panic(err)
		}
		// log.Printf("[Client %s]: Got reply AFTER METADATA: %v, len: %d", clientID, replyFrames, len(replyFrames))
		var workerId string
		if len(replyFrames) >= 1 && replyFrames[0] == "SENDDATA" {
			// log.Printf("[Client %s]: Received SENDDATA signal, starting file transfer.", clientID)
			file, err := os.Open(filePath)
			if err != nil {
				log.Println("[Client]: Error opening file:", err)
				log.Panic(err)
			}
			defer file.Close()
			workerId = replyFrames[1]

			csvLogger, err := InitializeCSVLogger(clientID, workerId)
			if err != nil {
				log.Printf("[Client %s]: Failed to initialize CSV logger: %v", clientID, err)
				log.Panic(err)
			}
			defer csvLogger.Close()

			chunkBuf := make([]byte, chunkSize)
			chunkNumber := 1
			log.Printf("[Client#%s] Sending Data", clientID)
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
				dataToSend := chunkBuf[:bytesRead]
				hash := sha256.Sum256(dataToSend)
				dataMsg := []string{"CHUNK", strconv.Itoa(chunkNumber), string(dataToSend), string(hash[:]), strconv.FormatInt(sentAt, 10)}
				_, err = socket.SendMessage(dataMsg)
				if err != nil {
					log.Printf("\nerror in sending {DATA(chunks)} client : %s   |  err [%v]", clientID, err)
				}
				// log.Printf("\n[Client]: %s - Sent chunk :%d", clientID, chunkNumber)

				if (!config.AppConfig.Common.NoAck) && (config.AppConfig.Common.AckAfter > 0) && (chunkNumber%config.AppConfig.Common.AckAfter == 0 || chunkNumber == int(totalChunks)) {
					//log tcp connection info
					err = logTCPStats(socket, clientID, workerId, csvLogger)
					if err != nil {
						log.Printf("[Client %s]: Failed to log TCP stats: %v", clientID, err)
					}

					ackFrames, err := socket.RecvMessage(0)
					if err != nil {
						log.Printf("\nerror recving  ACK for chunk %d: %v", chunkNumber, err)
						break
					}
					if len(ackFrames) < 2 || ackFrames[0] != "ACK" {
						log.Printf("\ninvalid ACK message: %v", ackFrames)
						break
					}

				}
				chunkNumber++
			}
			// log.Println("**********Client waiting for DONE FROM SERVER :", clientID)
			// wait for done from server after sending all chunk
			replyFrames, err = socket.RecvMessage(0)
			if err != nil {
				fmt.Printf("\nerror in recv reply after chunks for client %s: [%v]\n", clientID, err)
				log.Panic(err)
			}

			// log.Printf("[Client %s]: Got reply after CHUNKS: %v", clientID, replyFrames)
			if len(replyFrames) >= 1 && replyFrames[0] == "DONE" {
				_, err = socket.SendMessage("Done")
				if err != nil {
					log.Printf("\nerror in sending {DONE} client : %s   |  err [%v]\n", clientID, err)
				}
			}

			// checksum, err := utils.ComputeSHA256(filePath)
			// if err != nil {
			// 	log.Println("Checksum error:", err)
			// 	log.Panic(err)
			// }
			// log.Println(" checksum is:", checksum)
		}

	} else {
		log.Printf("[Client %s]: Initial connection failed. Expected 'CONNECTED', got: %v", clientID, replyFrames)
	}
	log.Printf("[Client#%s] Done", clientID)
}

func getTotalChunks(chunkSize int64, filePath string) (int64, error) {

	fileInfo, err := os.Stat(filePath)

	if err != nil {
		log.Panic(err)
	}
	totalChunks := (fileInfo.Size() + chunkSize - 1) / chunkSize
	return totalChunks, nil
}
func logTCPStats(socket *zmq.Socket, clientID, workerId string, csvLogger *CSVLogger) error {

	// Extract port from broker address
	// targetPort, err := extractPortFromAddress(config.AppConfig.Client.BrokerTCPAddress)
	// if err != nil {
	// 	log.Printf("Failed to extract port from broker address, using default 5559: %v", err)
	// 	targetPort = 5559
	// }

	// Use the configurable TCP matching and logging function
	return MatchZMQToTCPByProcess(csvLogger, clientID)
}
