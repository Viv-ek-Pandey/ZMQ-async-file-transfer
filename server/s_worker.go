package main

import (
	"log"
	"os"
	"server/config"
	"server/utils"
	"strconv"
)

// ServerWorker represents a worker handling file chunks.
func ServerWorker(pipe chan<- struct{}, workerID string, outputFilename string) {
	defer func() {
		wg.Done()
	}()

	if !config.AppConfig.Server.NoWrite {
		// Create/truncate the output file.
		truncateFile(outputFilename, workerID)
	}

	// 1. Initialize ZMQ DEALER Socket
	responder, err := newZmqDealerSocket(workerID, config.AppConfig.Server.BackendInprocAddress)
	if err != nil {
		log.Printf("[Worker %s]: Error creating DEALER socket: %v", workerID, err)
		log.Panic(err)
	}
	defer responder.Close()

	// 2. Register the worker with the broker
	_, err = responder.SendMessage("REGISTER")
	if err != nil {
		log.Printf("[Worker %s]: Error sending REGISTER message: %v", workerID, err)
		log.Panic(err)
	}
	// log.Printf("[Worker %s]: Sent REGISTER message to broker.", workerID)

	for {
		var totalExpectedChunks int // Total chunks as parsed from METADATA

		// --- 3. Receive METADATA message from Broker ---

		// log.Printf("[Worker %s]: Waiting for METADATA message from broker...", workerID)
		frames, err := responder.RecvMessage(0)
		if err != nil {
			log.Printf("[Worker %s]: Error receiving METADATA message: %v", workerID, err)
			continue
		}
		// log.Printf("[Worker %s]: Received message from broker: %v, len frames : %d", workerID, frames, len(frames))

		// Parse the METADATA message
		// Expected frames: ["METADATA", totalChunksStr]
		if len(frames) >= 2 && frames[0] == "METADATA" {
			chunkCountStr := frames[1] // Total chunks
			totalExpectedChunks, err = strconv.Atoi(chunkCountStr)
			if err != nil {
				log.Printf("[Worker %s]: Failed to parse total chunk count '%s': %v", workerID, chunkCountStr, err)
				log.Panic(err)
			}
			// log.Printf("[Worker %s]: Received METADATA . Total Chunks: %d", workerID, clientZMQID, totalExpectedChunks)
		} else {
			log.Printf("[Worker %s]: Received invalid METADATA message format: %v", workerID, frames)
			log.Panic(err)
		}

		// --- 4. Send "SENDDATA" signal to Broker (which forwards to Client) ---
		// log.Printf("[Worker %s]: Sending SENDDATA signal for Client %s.", workerID, clientZMQID)
		_, err = responder.SendMessage("SENDDATA")
		if err != nil {
			log.Printf("[Worker %s]: Error sending SENDDATA message: %v", workerID, err)
			log.Panic(err)
		}
		// log.Printf("[Worker %s]: SENDDATA signal sent for Client %s.", workerID, clientZMQID)
		var file *os.File
		var receivedChunks int

		// Open file for writing (append mode to continue from where we left off)
		file, err = os.OpenFile(outputFilename, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
		if err != nil {
			log.Printf("[Worker %s]: Error opening file '%s' for writing: %v", workerID, outputFilename, err)
			log.Panic(err)
		}
		defer file.Close()

		// Main loop for receiving and writing chunks
		log.Printf("[Worker#%s] Recving Chunk", workerID)
		for receivedChunks < totalExpectedChunks {
			log.Printf("[Worker %s]: Waiting for chunk %d...", workerID, receivedChunks+1)

			// --- 5. Receive Chunk Message from Broker ---
			msg, err := responder.RecvMessage(0)

			if err != nil {
				log.Printf("[Worker %s]: Error receiving chunk message: %v", workerID, err)
				log.Panic(err)
			}

			// log.Printf("[Worker %s]: Received chunk message: %v", workerID, msg)

			// Check if this is a METADATA message (client reconnecting)
			// if len(msg) >= 2 && msg[0] == "METADATA" {
			// 	log.Printf("[Worker %s]: RECONNECTED!", workerID)
			// 	// Check if file exists to determine if we're resuming
			// 	if fileInfo, err := os.Stat(outputFilename); err == nil {
			// 		log.Printf("[Worker %s]: File exists with size %d bytes, will append new data", workerID, fileInfo.Size())
			// 	} else {
			// 		log.Printf("[Worker %s]: Creating new file", workerID)
			// 	}
			// 	// Send SENDDATA signal to the reconnecting client
			// 	_, err = responder.SendMessage("SENDDATA")
			// 	if err != nil {
			// 		log.Printf("[Worker %s]: Error sending SENDDATA message to reconnecting client: %v", workerID, err)
			// 		log.Panic(err)
			// 	}
			// 	continue // Continue processing chunks
			// }

			// Expected frames: ["CHUNK", chunkNumberStr, chunkData, hash]
			if len(msg) >= 4 && msg[0] == "CHUNK" {
				chunkNumberStr := msg[1]
				cNum, _ := strconv.Atoi(chunkNumberStr)
				if cNum != receivedChunks+1 {
					log.Panicf("\n expected : %d  - got %d", receivedChunks+1, cNum)
					log.Panic("wrong chunk number!")
				}

				if !config.AppConfig.Server.NoWrite {
					// hashFromClient := msg[4]
					// hash := sha256.Sum256([]byte(msg[3]))
					// if hashFromClient != string(hash[:]) {
					// 	log.Printf("[Worker %s] : Chunk HASH MISSMATCH ", workerID)
					// }
					_, err := file.Write([]byte(msg[2])) // Write to file
					if err != nil {
						log.Printf("[Worker %s]: Error writing chunk %s to file '%s': %v", workerID, chunkNumberStr, outputFilename, err)
						log.Panic(err)
					}
				}

				receivedChunks++
				// log.Printf("[Worker %s]: Wrote chunk %s . Received: %d/%d", workerID, chunkNumberStr, receivedChunks, totalExpectedChunks)

				if !config.AppConfig.Common.NoAck && config.AppConfig.Common.AckAfter > 0 && (chunkNumberStr == strconv.FormatInt(int64(totalExpectedChunks), 10) || receivedChunks%config.AppConfig.Common.AckAfter == 0) {
					log.Println("sending ACk ")
					// time.Sleep(time.Second * 5)
					if _, err := responder.SendMessage("ACK", chunkNumberStr, workerID); err != nil {
						// log.Printf("[Worker %s]: Error sending ACK for chunk %s to client %s: %v", workerID, ackChunkNum, clientZMQID, err)
					}
					// log.Printf("[Worker %s]: Sent ACK for chunk %s.", workerID, chunkNumberStr)

				}

			} else {
				log.Printf("[Worker %s]: Received invalid chunk message format (too few frames or incorrect routing): %v", workerID, msg)
				break
			}
		}
		log.Printf("[Worker#%s] Recv Complete", workerID)

		// log.Printf("[Worker %s]: All expected chunks (%d) received(%d) and written to file successfully.", workerID, totalExpectedChunks, receivedChunks)

		checksum, err := utils.ComputeSHA256(outputFilename)
		if err != nil {
			log.Printf("[Worker %s]: Error computing SHA256 checksum for file '%s': %v", workerID, outputFilename, err)
		}
		log.Printf("[Worker %s]: SHA256 Checksum of received file '%s': %s", workerID, outputFilename, checksum)

		//send done after all expected chunk recvd
		_, err = responder.SendMessage("DONE", checksum)
		if err != nil {
			log.Printf("[Worker %s]: Error sending DONE message: %v", workerID, err)
			log.Panic(err)
		}
		break // break so worker is free for next client!
	}

}

func truncateFile(fileName string, wId string) {
	file, err := os.Create(fileName)
	if err != nil {
		log.Printf("[Worker %s]: Error creating/truncating file '%s': %v", wId, fileName, err)
		log.Panic(err)
	}
	file.Close()
}
