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
)

func ClientWorker(clientID string, wg *sync.WaitGroup) {
	socket, err := NewZmqSocket(clientID, config.AppConfig.Client.BrokerTCPAddress)
	if err != nil {
		log.Printf("\nerror in creating new socket [%v]\n", err)
		return
	}

	defer func() {
		socket.Close()
		log.Printf("[Client %s]: Socket closed .", clientID)
		wg.Done()
	}()
	filePath := config.AppConfig.Client.FilePath
	chunkSize := config.AppConfig.Client.ChunkSize

	// ------ Initial "CONNECT" message ----------
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
		// log.Printf("[Client %s]: Sending metadata message: %v", clientID, msg)

		_, err = socket.SendMessage(msg) // Use ... to send each string as a separate frame
		if err != nil {
			fmt.Printf("\nerror in sending {msg-MetaData} for client %s, err :[%v]\n", clientID, err)
			return
		}
		// log.Printf("[Client %s]: Metadata message sent!", clientID)

		// //===========TEST CONNECTION=================//
		// // --- 4. Receive "START-CONN-TEST" signal ---
		// // log.Printf("\n\n ** WAITING FOR START CONN TEST SIGNAL ** \n\n")
		// replyFrames, err = socket.RecvMessage(0) // RecvMessage here must match the broker's send
		// if err != nil {
		// 	fmt.Printf("\nerror in recv reply after METADATA for client %s: [%v]\n", clientID, err)
		// 	return
		// }
		// log.Printf("[Client %s]: Got reply after METADATA: %v", clientID, replyFrames)

		// var workerId string

		// if len(replyFrames) >= 2 && replyFrames[1] == "START-CONN-TEST" {
		// 	log.Printf("[Client %s]: Received START-CONN-TEST signal, starting conn test.", clientID)
		// 	file, err := os.Open("100MB.txt")
		// 	if err != nil {
		// 		log.Println("[Client]: Error opening file:", err)
		// 		return
		// 	}
		// 	defer file.Close()
		// 	testMsgNumber := 1
		// 	chunkBuf := make([]byte, 1048576)
		// 	workerId = replyFrames[2]

		// 	for {
		// 		bytesRead, err := file.Read(chunkBuf)
		// 		if err != nil && err != io.EOF {
		// 			log.Println("Error reading chunk:", err)
		// 			break
		// 		}
		// 		if bytesRead == 0 {
		// 			break // done
		// 		}
		// 		if testMsgNumber == 10 {
		// 			// wg.Add(1)
		// 			// go CheckConn(socket, clientID, workerId, wg)
		// 		}
		// 		dataToSend := chunkBuf[:bytesRead]
		// 		dataMsg := []string{"", "TestConn", string(dataToSend)}
		// 		_, err = socket.SendMessage(dataMsg)
		// 		if err != nil {
		// 			log.Printf("\nerror in sending {DATA(chunks)} client : %s   |  err [%v]", clientID, err)
		// 		}
		// 		testMsgNumber++
		// 	}
		// } else {
		// 	fmt.Println("**FAILED TO RECV START CONN TEST MSG**")
		// 	return
		// }
		// log.Printf("[Client %s]: Waiting for  reply after TEST CONN: %v", clientID, replyFrames)
		// replyFrames, err = socket.RecvMessage(0) // RecvMessage here must match the broker's send
		// if err != nil {
		// 	fmt.Printf("\nerror in recv reply after Test CONN for client %s: [%v]\n", clientID, err)
		// 	return
		// }
		// log.Printf("[Client %s]: Got reply after TEST CONN: %v", clientID, replyFrames)
		// if len(replyFrames) >= 1 && replyFrames[1] == "CONN TEST DONE" {

		// } else {
		// 	log.Println("*****CONN TEST FAILED!!***")
		// 	return
		// }
		// //===========TEST CONNECTION=================//
		//TO-DO*****
		// IF BAD CONNECTION SEND RECONNECT MESSAGE TO WORKER

		//============Good connection! procceed!==============//

		//===================SEND DATA===================//
		replyFrames, err = socket.RecvMessage(0)
		if err != nil {
			fmt.Printf("\nerror in recv reply after TestConn for client %s: [%v]\n", clientID, err)
			return
		}
		// log.Printf("[Client %s]: Got reply after CONNECTION TEST: %v", clientID, replyFrames)
		var workerId string
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
				dataMsg := []string{"", "CHUNK", strconv.Itoa(chunkNumber), string(dataToSend), string(hash[:]), strconv.FormatInt(sentAt, 10)}
				_, err = socket.SendMessage(dataMsg)
				if err != nil {
					log.Printf("\nerror in sending {DATA(chunks)} client : %s   |  err [%v]", clientID, err)
				}
				// log.Printf("\n[Client]: %s - Sent chunk :%d", clientID, chunkNumber)

				if (!config.AppConfig.Common.NoAck) && (config.AppConfig.Common.AckAfter > 0) && (chunkNumber%config.AppConfig.Common.AckAfter == 0 || chunkNumber == int(totalChunks)) {
					// wait for ACK before sending the next chunk
					wg.Add(1)
					go CheckConn(socket, clientID, workerId, wg)
					ackFrames, err := socket.RecvMessage(0)
					if err != nil {
						log.Printf("\nerror recving  ACK for chunk %d: %v", chunkNumber, err)
						break
					}
					// Expected shape: [workerID, clientID, "ACK", chunkNum]
					if len(ackFrames) < 2 || ackFrames[1] != "ACK" {
						log.Printf("\ninvalid ACK message: %v", ackFrames)
						break
					}

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

			// checksum, err := utils.ComputeSHA256(filePath)
			// if err != nil {
			// 	log.Println("Checksum error:", err)
			// 	return
			// }
			// log.Println(" checksum is:", checksum)
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
