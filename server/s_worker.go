package main

import (
	"fmt"
	"log"
	"os"
	"server/config"
	"server/utils"
	"strconv"
	"time"
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

	// ======================CSV Logging=========================
	workerWriter, workerFile, _ := utils.InitChunkTimingCSV(workerID)
	defer func() {
		if workerFile != nil {
			workerFile.Close()
		}
	}()
	workerLogChan := make(chan []string, 10000)

	wg.Add(1)
	go utils.LogChunkTiming(&wg, workerWriter, workerLogChan)
	// ======================CSV Logging=========================

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
		if !config.AppConfig.Server.NoWrite {
			// Reopen file for actual writing (using O_TRUNC to clear content if previous write was incomplete)

			file, err = os.OpenFile(outputFilename, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0644)
			if err != nil {
				log.Printf("[Worker %s]: Error opening file '%s' for writing: %v", workerID, outputFilename, err)
				log.Panic(err)
			}
			defer file.Close()
		}

		receivedChunks := 0

		//for total time to get all data
		transferStartTime := time.Now().UnixMilli()
		lastAck := transferStartTime

		// Main loop for receiving and writing chunks
		log.Printf("[Worker#%s] Recving Chunk", workerID)
		for receivedChunks < totalExpectedChunks {
			// log.Printf("[Worker %s]: Waiting for chunk %d...", workerID, receivedChunks+1)

			// --- 5. Receive Chunk Message from Broker ---
			chunkWaitStart := time.Now().UnixMilli()
			msg, err := responder.RecvMessage(0)
			chunkMessageRecv := time.Now().UnixMilli()

			if err != nil {
				log.Printf("[Worker %s]: Error receiving chunk message: %v", workerID, err)
				log.Panic(err)
			}

			// log.Printf("[Worker %s]: Received chunk message: %v", workerID, msg) // Too noisy for data chunks

			// Expected frames: ["CHUNK", chunkNumberStr, chunkData, hash,clientSentAtStr, brkRecv,brokerSentAtStr]
			if len(msg) >= 6 && msg[0] == "CHUNK" {
				chunkNumberStr := msg[1]
				clientSent, _ := (strconv.Atoi(msg[4]))
				brokerRecv, _ := (strconv.Atoi(msg[5]))
				clientToBrokerRtt := brokerRecv - clientSent
				brokerSent, _ := strconv.Atoi(msg[6])
				brokerToWorkerRtt := int(chunkMessageRecv) - brokerSent
				rtt := strconv.FormatInt(chunkMessageRecv-chunkWaitStart, 10)

				// ======================CSV Logging=========================

				// chunknumber , clientsent , brkRecv,client(send)-broker(recv), brokersent  ,worker rec,broker(send)-worker(recv),  worker loop-recv rtt
				workerLogChan <- []string{chunkNumberStr, getTimeStringFromUnixMilliString(msg[4]),
					getTimeStringFromUnixMilliString(msg[5]), strconv.Itoa(clientToBrokerRtt), getTimeStringFromUnixMilliString(msg[6]), getTimeStringFromUnixMilliString(strconv.Itoa(int(chunkMessageRecv))), strconv.Itoa(brokerToWorkerRtt), rtt}
				// ======================CSV Logging=========================

				if !config.AppConfig.Server.NoWrite {
					// hashFromClient := msg[4]
					// hash := sha256.Sum256([]byte(msg[3]))
					// if hashFromClient != string(hash[:]) {
					// 	log.Printf("[Worker %s] : Chunk HASH MISSMATCH ", workerID)
					// }
					_, err := file.Write([]byte(msg[3])) // Write to file
					if err != nil {
						log.Printf("[Worker %s]: Error writing chunk %s to file '%s': %v", workerID, chunkNumberStr, outputFilename, err)
						log.Panic(err)
					}
				}

				receivedChunks++
				// log.Printf("[Worker %s]: Wrote chunk %s for Client %s. Received: %d/%d", workerID, chunkNumberStr, clientZMQID, receivedChunks, totalExpectedChunks)

				if !config.AppConfig.Common.NoAck && config.AppConfig.Common.AckAfter > 0 && (chunkNumberStr == strconv.FormatInt(int64(totalExpectedChunks), 10) || receivedChunks%config.AppConfig.Common.AckAfter == 0) {
					if _, err := responder.SendMessage("ACK", chunkNumberStr, workerID); err != nil {
						// log.Printf("[Worker %s]: Error sending ACK for chunk %s to client %s: %v", workerID, ackChunkNum, clientZMQID, err)
					}
					ackTime := time.Now().UnixMilli()
					ackDelta := ackTime - lastAck
					lastAck = ackTime
					workerLogChan <- []string{fmt.Sprintf("Delta From Start/Prev Ack  Time Millisecond :  %d", ackDelta)}
					// log.Printf("[Worker %s]: Sent ACK for chunk %s to client %s.", workerID, ackChunkNum, clientZMQID)

				}

			} else {
				log.Printf("[Worker %s]: Received invalid chunk message format (too few frames or incorrect routing): %v", workerID, msg)
				break
			}
		}
		log.Printf("[Worker#%s] Recv Complete", workerID)
		transferEndTime := time.Now().UnixMilli()

		totalTransferTime := transferEndTime - transferStartTime
		workerLogChan <- []string{fmt.Sprintf("TOTAL Time in MilliSec : %d", totalTransferTime)}

		// log.Printf("[Worker %s]: All expected chunks (%d) received(%d) and written to file successfully.", workerID, totalExpectedChunks, receivedChunks)

		//send done after all expected chunk recvd
		_, err = responder.SendMessage("DONE")
		if err != nil {
			log.Printf("[Worker %s]: Error sending DONE message: %v", workerID, err)
			log.Panic(err)
		}
	}
	close(workerLogChan)
	// if !config.AppConfig.Server.NoWrite {
	// 	// Compute checksum of the received file
	// 	finalFile, err := os.Open(outputFilename)
	// 	if err != nil {
	// 		log.Printf("[Worker %s]: Error opening file '%s' for checksum: %v", workerID, outputFilename, err)
	// 		log.Panic(err)
	// 	}
	// 	defer finalFile.Close()

	// 	hash := sha256.New()
	// 	_, err = io.Copy(hash, finalFile)
	// 	if err != nil {
	// 		log.Printf("[Worker %s]: Error computing checksum for '%s': %v", workerID, outputFilename, err)
	// 		log.Panic(err)
	// 	}

	// 	checksum := hex.EncodeToString(hash.Sum(nil))
	// 	log.Printf("[Worker %s]: SHA256 Checksum of received file '%s': %s", workerID, outputFilename, checksum)

	// }
	// pipe <- struct{}{}
	// log.Printf("[Worker %s]: Done. Signaled completion.", workerID)
}

func truncateFile(fileName string, wId string) {
	file, err := os.Create(fileName)
	if err != nil {
		log.Printf("[Worker %s]: Error creating/truncating file '%s': %v", wId, fileName, err)
		log.Panic(err)
	}
	file.Close()
}

func getTimeStringFromUnixMilliString(str string) string {
	ms, _ := strconv.ParseInt(str, 10, 64)
	t := time.UnixMilli(ms)

	return t.Format("15:04:05.000")
}
