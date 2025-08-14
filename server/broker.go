package main

import (
	"log"
	"server/config"
	"server/utils"
	"strconv"
	"sync"
	"time"

	zmq "github.com/pebbe/zmq4"
)

// wmap stores the mapping between workerID and assigned clientID.
var wmap sync.Map

func InitBroker(pipe chan<- string) {
	log.Printf("\n [Broker] - Starting new socket with config %+v \n", config.AppConfig.Server)
	frontend, err := zmq.NewSocket(zmq.ROUTER)
	if err != nil {
		log.Fatalf("[Broker]: Error creating frontend ROUTER socket: %v", err)
	}
	if config.AppConfig.Common.RecvBufSize != 0 && config.AppConfig.Common.SendBufSize != 0 {
		log.Println("[Broker]: Overwriting kernel default TCP buffer size")
		frontend.SetRcvbuf(config.AppConfig.Common.RecvBufSize)
		frontend.SetSndbuf(config.AppConfig.Common.SendBufSize)
	}
	defer frontend.Close()
	// if err = frontend.SetRcvhwm(config.AppConfig.Server.HighWaterMark); err != nil {
	// 	log.Printf("\n[Broker-ERROR]: Setting HighWaterMark %v\n", config.AppConfig.Server.HighWaterMark)
	// 	return
	// }
	// log.Printf("\n[Broker]: Setting HighWaterMark %v\n", config.AppConfig.Server.HighWaterMark)
	frontend.Bind(config.AppConfig.Server.FrontendTCPAddress)
	log.Println("[Broker]: Frontend ROUTER bound to", config.AppConfig.Server.FrontendTCPAddress)

	backend, err := zmq.NewSocket(zmq.ROUTER)
	if err != nil {
		log.Fatalf("[Broker]: Error creating backend DEALER socket: %v", err)
	}
	defer backend.Close()
	backend.Bind(config.AppConfig.Server.BackendInprocAddress) // In-process communication for local workers
	log.Println("[Broker]: Backend ROUTER bound to ", config.AppConfig.Server.BackendInprocAddress)

	// --- CSV Logging
	brokerWriter, brokerFile, _ := utils.InitBrokerTimingCSV()
	defer func() {
		if brokerFile != nil {
			brokerFile.Close()
		}
	}()
	brokerLogChan := make(chan []string, 10000)

	wg.Add(1)
	go func() {
		defer wg.Done()
		defer func() {
			if brokerWriter != nil {
				brokerWriter.Flush()
			}
		}()
		ticker := time.NewTicker(2 * time.Second)
		defer ticker.Stop()

		for {
			select {
			case row, ok := <-brokerLogChan:
				if !ok {
					if brokerWriter != nil {
						brokerWriter.Flush()
					}
					return
				}
				if brokerWriter != nil {
					if err := brokerWriter.Write(row); err != nil {
						log.Printf("broker csv write err: %v", err)
					}
				}

			case <-ticker.C:
				if brokerWriter != nil {
					brokerWriter.Flush()
				}

			}
		}
	}()

	poller := zmq.NewPoller()
	poller.Add(frontend, zmq.POLLIN)
	poller.Add(backend, zmq.POLLIN)
	log.Println("[Broker]: Poller initialized.")

	for { // Main broker event loop
		sockets, err := poller.Poll(-1)
		log.Println("[Broker]: Polling ****************")
		if err != nil {
			log.Printf("[Broker]: Error polling sockets: %v", err)
			time.Sleep(100 * time.Millisecond) // Small pause
			continue
		}

		// Iterate through all sockets that have events
		for _, socket := range sockets {
			// log.Println("Socket poll triggered for:", socket.Socket) // Debugging

			switch s := socket.Socket; s {
			case backend: // Messages FROM workers TO broker (via backend)

				log.Println("[Broker]: Backend socket ready for message.")

				// Worker's DEALER sends: [worker_ZMQ_identity, "", "REGISTER"]
				// OR
				// Worker's DEALER sends: [client_ZMQ_identity, "", "ACK", chunkNum, worker_ZMQ_identity]
				// OR
				// Worker's DEALER sends: [client_ZMQ_identity, "", "SENDDATA"]
				msgWaitStart := time.Now().UnixMilli()
				frames, err := s.RecvMessage(0)
				msgRecv := time.Now().UnixMilli()
				if err != nil {
					log.Printf("[Broker]: Error receiving from backend: %v", err)
					continue // Skip to next ready socket
				}
				log.Printf("[Broker]: Received from worker (backend): %v", frames)

				// Basic validation:
				if len(frames) < 2 {
					log.Printf("[Broker]: Malformed message from worker (too few frames): %v", frames)
					continue
				}

				// Check if it's a REGISTER message (sent by worker to self-identify)
				// Expected: [ "REGISTER", workerID]
				if len(frames) == 2 && frames[1] == "REGISTER" {
					workerZMQID := frames[0]    // The worker's ID is frames[1]
					wmap.Store(workerZMQID, "") // Store worker as available
					log.Printf("[Broker]: Registered new worker: %s", workerZMQID)
					continue // Process next socket event
				}

				// If not REGISTER, it's an application reply from a worker to a client
				// Expected format: [worker_id, "", application_payload_from_worker...]
				clientZMQID := FindClient(frames[0]) // This is now the client's ZMQ ID for routing
				// frames[1] should be the empty delimiter

				//======================== CSV LOGGING=============================
				rtt := strconv.FormatInt(msgRecv-msgWaitStart, 10)
				brokerLogChan <- []string{clientZMQID, frames[0], frames[2], rtt}
				//======================== CSV LOGGING=============================

				// Forward the worker's reply directly to the client via the frontend
				// The frontend ROUTER uses frames[0] (clientZMQID) to route it.
				log.Printf("[Broker]: Forwarding worker reply to client %s: %v", clientZMQID, frames)
				msgToClient := []string{clientZMQID}
				msgToClient = append(msgToClient, frames[1:]...)
				_, err = frontend.SendMessage(msgToClient)
				if err != nil {
					log.Printf("[Broker]: WARN: Failed to forward message from worker to client %s: %v", clientZMQID, err)
				}
				log.Println("[Broker]: Message forwarded to client.")
				// No `break` here, allow `for _, socket` loop to continue to next ready socket.

			case frontend: // Messages FROM clients TO broker (via frontend)
				log.Println("[Broker]: Frontend socket ready for message.")

				// Client's DEALER sends: ["", "CONNECT"]
				// OR
				// Client's DEALER sends: ["", "METADATA", totalChunks]
				// OR
				// Client's DEALER sends: ["", ChunkNum, ChunkData, clientSentAt]
				// OR
				// Client's DEALER sends: ["", "Done"]

				msgWaitStart := time.Now().UnixMilli()
				frames, err := s.RecvMessage(0) // Read ONE message
				msgRecv := time.Now().UnixMilli()
				if err != nil {
					log.Printf("[Broker]: Error receiving from frontend: %v", err)
					continue // Skip to next ready socket
				}
				// log.Printf("[Broker]: Received from client (frontend): %s", frames)

				// Basic validation:
				if len(frames) < 2 {
					log.Printf("[Broker]: Malformed message from client (too few frames): %v", frames)
					continue
				}

				clientZMQID := frames[0] // Client's ZMQ identity

				// frames[1] is the empty delimiter
				msgType := ""
				if len(frames) > 2 {
					msgType = frames[2]
				}

				workerID := FindWorker(clientZMQID) // Find or assign a worker for this client

				if workerID == "" {
					log.Printf("[Broker]: No available workers for client %s. Sending NO_AVAILABLE_WORKERS.", clientZMQID)
					_, err = frontend.SendMessage(clientZMQID, "", "NO_AVAILABLE_WORKERS")
					if err != nil {
						log.Printf("[Broker]: Error sending NO_AVAILABLE_WORKERS to client %s: %v", clientZMQID, err)
					}
					continue // Skip to next ready socket
				}
				//======================== CSV LOGGING=============================
				rtt := strconv.FormatInt(msgRecv-msgWaitStart, 10)
				brokerLogChan <- []string{clientZMQID, workerID, frames[2], rtt}
				//======================== CSV LOGGING=============================

				switch msgType {
				case "CONNECT":
					// Client sends: [clientZMQID, "", "CONNECT", clientSentMicros]
					// Broker replies to client: [clientZMQID, "", "CONNECTED", workerID, brokerSentMicros]
					log.Printf("[Broker]: Client %s CONNECT request. Assigned worker %s. Sending CONNECTED.", clientZMQID, workerID)
					_, err := frontend.SendMessage(clientZMQID, "", "CONNECTED") // Include assigned workerID
					if err != nil {
						log.Printf("[Broker]: [ERROR] sending CONNECTED message to client %s: %v", clientZMQID, err)
					}
					// No need to forward CONNECT to worker unless worker needs specific init via this message.
					// If worker needs it, uncomment and adapt:
					// messageForWorker := []string{workerID}
					// messageForWorker = append(messageForWorker, frames...)
					// _, err = backend.SendMessage(messageForWorker...)
					// if err != nil { log.Printf("[Broker]: WARN: Failed to forward CONNECT to worker %s: %v", workerID, err) }

				case "METADATA":
					// Client sends: [clientZMQID, "", "METADATA", totalChunksStr]
					// Broker forwards to worker: [workerID,"", "METADATA", totalChunksStr,]
					messageForWorker := []string{workerID}                     // Start with worker ID for backend routing
					messageForWorker = append(messageForWorker, frames[1:]...) // Add client's original frames

					log.Printf("[Broker]: Forwarding METADATA from client %s to worker %s: %v", clientZMQID, workerID, messageForWorker)
					_, err := backend.SendMessage(messageForWorker)
					if err != nil {
						log.Printf("[Broker]: WARN: Failed to forward METADATA to worker %s for client %s: %v", workerID, clientZMQID, err)
					}

				case "Done":
					// Client sends: [clientZMQID, "", "Done"]
					// Broker forwards to worker: [workerID, clientZMQID, "", "Done", brokerSentMicros]
					// messageForWorker := []string{workerID}
					// messageForWorker = append(messageForWorker, frames...) // Add client's original frames
					// brkSendAt := strconv.FormatInt(time.Now().UnixMicro(), 10)
					// messageForWorker = append(messageForWorker, brkSendAt)

					// log.Printf("[Broker]: Forwarding DONE from client %s to worker %s: %v", clientZMQID, workerID, messageForWorker)
					// _, err := backend.SendMessage(messageForWorker)
					// if err != nil {
					// 	log.Printf("[Broker]: WARN: Failed to forward DONE to worker %s for client %s: %v", workerID, clientZMQID, err)
					// }
					// Important: Release the worker when the client is done
					wmap.Store(workerID, "") // Set worker's mapping back to "" (available)
					log.Printf("[Broker]: Worker %s is now available after client %s finished.", workerID, clientZMQID)

				default: // This case handles actual chunk data, as msgType will be the chunk number (e.g., "1", "2")
					// Client sends: [clientZMQID, "", ChunkNum, ChunkData, clientSentMicros]
					// Broker forwards to worker: [workerID, clientZMQID, "", ChunkNum, ChunkData, clientSentMicros, brokerSentMicros]
					messageForWorker := []string{workerID}
					messageForWorker = append(messageForWorker, frames[1:]...) // Add client's original frames
					brkRecvAt := strconv.FormatInt(msgWaitStart, 10)
					brkSendAt := strconv.FormatInt(time.Now().UnixMilli(), 10)
					messageForWorker = append(messageForWorker, brkRecvAt, brkSendAt) // Append broker's timestamp

					log.Printf("[Broker]: Forwarding chunk %s from client %s to worker %s", messageForWorker[3], clientZMQID, workerID)
					_, err := backend.SendMessage(messageForWorker)
					if err != nil {
						log.Printf("[Broker]: WARN: Failed to forward chunk to worker %s for client %s: %v", workerID, clientZMQID, err)
					}
				}
			} // End switch s := socket.Socket
		} // End for _, socket := range sockets
	} // End for {} (main poller loop)

	// log.Println("Broker completed")
	// pipe <- "Done"
}

// FindWorker assigns a worker to a client or returns an already assigned one.
// It stores the mapping in wmap: workerID -> clientID.
func FindWorker(cID string) string {
	var assignedWorkerID, newWorkerID string

	wmap.Range(func(key, value interface{}) bool {
		if val, ok := value.(string); ok {
			if val == cID {
				// Client is already assigned
				assignedWorkerID = key.(string)
				return false // No need to search further
			}
			if val == "" && newWorkerID == "" {
				// Remember first available worker
				newWorkerID = key.(string)
			}
		}
		return true
	})

	// Return existing assignment if found
	if assignedWorkerID != "" {
		return assignedWorkerID
	}

	// Assign new worker if available
	if newWorkerID != "" {
		wmap.Store(newWorkerID, cID)
		log.Printf("[Broker:FindWorker]: Assigned client %s to new worker %s.", cID, newWorkerID)
	}

	return newWorkerID // Could still be "" if none available
}

// FindClient retrieves the clientID assigned to a specific worker.
func FindClient(wID string) string {
	log.Println("[Broker] - Finding client for wId :", wID)
	val, ok := wmap.Load(wID)
	if ok {
		if clientID, isString := val.(string); isString {
			return clientID
		}
	}
	return ""
}
