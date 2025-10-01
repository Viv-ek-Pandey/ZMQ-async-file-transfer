package main

import (
	"client/config"
	"client/utils"
	"crypto/sha256"
	"fmt"
	"io"
	"log"
	"os"
	"strconv"
	"sync"
	"time"
)

func ClientWorker(clientID string, wg *sync.WaitGroup, failoverChan chan<- FailoverInfo) {
	ClientWorkerWithResume(clientID, wg, failoverChan, 1)
}

func ClientWorkerWithResume(clientID string, wg *sync.WaitGroup, failoverChan chan<- FailoverInfo, startChunk int) {
	fmt.Printf("🚀 Starting new client  with identity %s, resuming from chunk %d\n", clientID, startChunk)

	socket, err := newZmqDealerSocket(clientID, config.AppConfig.Client.BrokerTCPAddress)
	if err != nil {
		log.Printf("\nerror in creating new socket [%v]\n", err)
		log.Panic(err)
	}

	defer func() {
		socket.Close()
		log.Printf("[Client %s]: Socket closed .", clientID)
		wg.Done()
	}()
	filePath := fmt.Sprintf("file%s.txt", clientID)
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
		// log.Println("connected cID :", clientID)
		totalChunks, err := getTotalChunks(chunkSize, filePath)
		if err != nil {
			log.Panic(err)
		}

		msg := []string{"METADATA", fmt.Sprintf("%d", totalChunks)}
		// log.Printf("[Client %s]: Sending metadata message: %v", clientID, msg)

		_, err = socket.SendMessage(msg)
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

		if len(replyFrames) >= 1 && replyFrames[0] == "SENDDATA" {
			file, err := os.Open(filePath)
			if err != nil {
				log.Println("[Client]: Error opening file:", err)
				log.Panic(err)
			}
			defer file.Close()

			chunkBuf := make([]byte, chunkSize)
			chunkNumber := startChunk

			// Validate start chunk number
			if startChunk < 1 {
				log.Printf("[Client %s]: Invalid start chunk number %d, using 1", clientID, startChunk)
				startChunk = 1
			}
			if startChunk > int(totalChunks) {
				log.Printf("[Client %s]: Start chunk %d exceeds total chunks %d, using %d", clientID, startChunk, totalChunks, totalChunks)
				startChunk = int(totalChunks)
			}

			// Seek to the starting position if resuming
			if startChunk > 1 {
				seekPos := int64(startChunk-1) * chunkSize
				_, err = file.Seek(seekPos, 0)
				if err != nil {
					log.Printf("[Client %s]: Error seeking to position %d: %v", clientID, seekPos, err)
					log.Panic(err)
				}
				log.Printf("[Client#%s] Resuming from chunk %d (seeking to position %d, chunk size %d)", clientID, startChunk, seekPos, chunkSize)
			} else {
				log.Printf("[Client#%s] Sending Data from beginning (chunk 1)", clientID)
			}
			sleepAfter := 0
			for {
				bytesRead, err := file.Read(chunkBuf)
				if err != nil && err != io.EOF {
					log.Println("Error reading chunk:", err)
					break
				}
				if bytesRead == 0 {
					break // done
				}

				dataToSend := chunkBuf[:bytesRead]
				hash := sha256.Sum256(dataToSend)
				dataMsg := []string{"CHUNK", strconv.Itoa(chunkNumber), string(dataToSend), string(hash[:])}

				_, err = socket.SendMessage(dataMsg)
				if err != nil {
					log.Printf("\nerror in sending {DATA(chunks)} client : %s   |  err [%v]", clientID, err)
				}
				// log.Printf("\n[Client]: %s - Sent chunk :%d", clientID, chunkNumber)
				if sleepAfter == 100 {
					log.Println("stimulating delay")
					time.Sleep(time.Second * 2)
					sleepAfter = 0
				}

				if (!config.AppConfig.Common.NoAck) && (config.AppConfig.Common.AckAfter > 0) && (chunkNumber%config.AppConfig.Common.AckAfter == 0 || chunkNumber == int(totalChunks)) {
					log.Printf("[CLIENT# %s]waiting ACK!\n", clientID)
					ackMsg, err := socket.RecvMessage(0)
					if err != nil {
						log.Panic(err)
					}
					log.Println("GOT ack from server!", ackMsg)

					// if chunkNumber < int(totalChunks) {

					// 	wg.Add(1)
					// 	failoverInfo := FailoverInfo{
					// 		ClientID:    clientID,
					// 		ChunkNumber: chunkNumber + 1, // Next chunk to send (chunkNumber is the last sent chunk)
					// 		FilePath:    filePath,
					// 		ChunkSize:   chunkSize,
					// 	}
					// 	// log.Printf("[Client %s]: Sending failover info - last sent chunk %d, next chunk to send %d", clientID, chunkNumber, failoverInfo.ChunkNumber)
					// 	failoverChan <- failoverInfo
					// 	//kill the client mid-transfer to simulate failover
					// 	return
					// }
				}
				chunkNumber++
				sleepAfter++
			}

			log.Println("**********Client waiting for DONE FROM SERVER :", clientID)
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
			checksumFromServer := replyFrames[1]

			checksum, err := utils.ComputeSHA256(filePath)
			if err != nil {
				log.Println("Checksum error:", err)
				log.Panic(err)
			}
			log.Println("checkSUM client :", checksum)
			log.Println("checkSUM server :", checksumFromServer)

			log.Println(" checksum match :", checksum == checksumFromServer)
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
