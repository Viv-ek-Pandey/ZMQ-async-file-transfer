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

func InitBroker() {
	defer func() {
		wg.Done()
	}()

	log.Printf("\n [Broker] - Starting ROUTER sockets with config %+v \n", config.AppConfig.Server)
	frontend, backend, err := getBrokerRouters()
	if err != nil {
		log.Fatalf("[Broker] - Failed to init sockets: %v", err)
	}
	defer frontend.Close()
	defer backend.Close()

	//===================== CSV Logging ============================
	brokerWriter, brokerFile, _ := utils.InitBrokerTimingCSV()
	defer func() {
		if brokerFile != nil {
			brokerFile.Close()
		}
	}()
	brokerLogChan := make(chan []string, 10000)

	wg.Add(1)
	go utils.LogBrokerTimmings(&wg, brokerLogChan, brokerWriter)
	//===================== CSV Logging ============================

	poller := zmq.NewPoller()
	poller.Add(frontend, zmq.POLLIN)
	poller.Add(backend, zmq.POLLIN)
	log.Println("[Broker]: Poller initialized.")

	for {
		sockets, _ := poller.Poll(-1)
		for _, socket := range sockets {

			switch s := socket.Socket; s {
			case backend: // Messages FROM workers TO broker (via backend)

				// log.Println("[Broker]: Backend socket ready for message.")
				//Worker sends:
				//  [worker_identity,  "REGISTER"]
				//               OR
				// [worker_identity, "SENDDATA"]
				//               OR
				// [worker_identity, "ACK", chunkNum, worker_ZMQ_identity]
				//               OR
				// [worker_identity, "DONE"]

				msgWaitStart := time.Now().UnixMilli()
				frames, err := s.RecvMessage(0)
				msgRecv := time.Now().UnixMilli()
				if err != nil {
					log.Printf("[Broker]: Error receiving from backend: %v", err)
					log.Panic(err)
				}
				log.Printf("[Broker]: Received from worker (backend): %v", frames)

				// Basic validation:
				if len(frames) < 2 {
					log.Printf("[Broker]: Malformed message from worker (too few frames): %v", frames)
					log.Panic(err)
				}
				workerZMQID, msgType := frames[0], frames[1]
				clientZMQID := FindClient(frames[0])

				//replace index 0 with client ID
				frames[0] = clientZMQID

				//======================== CSV LOGGING=============================
				rtt := strconv.FormatInt(msgRecv-msgWaitStart, 10)
				brokerLogChan <- []string{clientZMQID, workerZMQID, msgType, rtt}
				//======================== CSV LOGGING=============================

				switch msgType {
				case "REGISTER":
					wmap.Store(workerZMQID, "") // Store worker as available
					log.Printf("[Broker]: Registered new worker: %s", workerZMQID)

				case "SENDDATA":
					frames = append(frames, workerZMQID)
					_, err = frontend.SendMessage(frames)
					if err != nil {
						log.Printf("[Broker]: WARN: Failed to forward message from worker to client %s: %v", clientZMQID, err)
					}
				case "ACK":
					_, err = frontend.SendMessage(frames)
					if err != nil {
						log.Printf("[Broker]: WARN: Failed to forward message from worker to client %s: %v", clientZMQID, err)
					}
				case "DONE":
					_, err = frontend.SendMessage(frames)
					if err != nil {
						log.Printf("[Broker]: WARN: Failed to forward message from worker to client %s: %v", clientZMQID, err)
					}
				default:
					log.Println(frames)
					log.Panic("Backend DEFAULT CASE")
				}

				// log.Printf("[Broker]: Forwarding worker reply to client %s: %v", clientZMQID, frames)

			case frontend: // Messages FROM clients TO broker (via frontend)

				// Client sends: ["CONNECT"]
				// OR
				// Client sends: ["METADATA", totalChunks]
				// OR
				// Client sends: ["CHUNK", ChunkNum, ChunkData, clientSentAt]
				// OR
				// Client sends: ["Done"]

				msgWaitStart := time.Now().UnixMilli()
				frames, err := s.RecvMessage(0)
				msgRecv := time.Now().UnixMilli()
				if err != nil {
					log.Printf("[Broker]: Error receiving from frontend: %v", err)
					continue
				}
				// log.Printf("[Broker]: Received from client (frontend): %s", frames[:6])

				// Basic validation:
				if len(frames) < 2 {
					log.Printf("[Broker]: Malformed message from client (too few frames): %v", frames)
					continue
				}

				clientZMQID, msgType := frames[0], frames[1]

				workerID := FindWorker(clientZMQID) // Find or assign a worker for this client

				if workerID == "" {
					_, err = frontend.SendMessage(clientZMQID, "", "NO_AVAILABLE_WORKERS")
					if err != nil {
						log.Printf("[Broker]: Error sending NO_AVAILABLE_WORKERS to client %s: %v", clientZMQID, err)
					}
					continue // Skip to next ready socket
				}
				//======================== CSV LOGGING=============================
				rtt := strconv.FormatInt(msgRecv-msgWaitStart, 10)
				brokerLogChan <- []string{clientZMQID, workerID, frames[1], rtt}
				//======================== CSV LOGGING=============================

				frames[0] = workerID

				switch msgType {

				case "CONNECT":
					// log.Printf("[Broker]: Client %s CONNECT request. Assigned worker %s. Sending CONNECTED.", clientZMQID, workerID)
					_, err := frontend.SendMessage(clientZMQID, "CONNECTED") // Include assigned workerID
					if err != nil {
						log.Printf("[Broker]: [ERROR] sending CONNECTED message to client %s: %v", clientZMQID, err)
					}

				case "METADATA":
					// log.Printf("[Broker]: Forwarding METADATA from client %s to worker %s: %v", clientZMQID, workerID, messageForWorker)
					_, err := backend.SendMessage(frames)
					if err != nil {
						log.Printf("[Broker]: WARN: Failed to forward METADATA to worker %s for client %s: %v", workerID, clientZMQID, err)
					}

				case "Done":
					log.Printf("[Worker %s]: Done - Setting free", workerID)
					wmap.Store(workerID, "")

				case "CHUNK":
					// log.Printf("[Broker]: Forwarding chunk %s from client %s to worker %s", frames[3], clientZMQID, workerID)
					brkRecvAt := strconv.FormatInt(msgRecv, 10)
					brkSendAt := strconv.FormatInt(time.Now().UnixMilli(), 10)
					frames = append(frames, brkRecvAt, brkSendAt) // Append broker's timestamp
					_, err := backend.SendMessage(frames)
					if err != nil {
						log.Printf("[Broker]: WARN: Failed to forward chunk to worker %s for client %s: %v", workerID, clientZMQID, err)
					}
				default:
					log.Println(frames)
					log.Panic("Frontend DEFAULT!!")
				}
			} // End switch s := socket.Socket
		} // End for _, socket := range sockets
	} // End for {} (main poller loop)
}

// FindWorker assigns a worker to a client or returns an already assigned one.
func FindWorker(cID string) string {
	var assignedWorkerID, newWorkerID string

	wmap.Range(func(key, value any) bool {
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
		// log.Printf("[Broker:FindWorker]: Assigned client %s to new worker %s.", cID, newWorkerID)
	}

	return newWorkerID // Could still be "" if none available
}

// FindClient retrieves the clientID assigned to a specific worker.
func FindClient(wID string) string {
	// log.Println("[Broker] - Finding client for wId :", wID)
	val, ok := wmap.Load(wID)
	if ok {
		if clientID, isString := val.(string); isString {
			return clientID
		}
	}
	return ""
}
