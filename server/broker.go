package main

import (
	"encoding/binary"
	"log"
	"server/config"

	zmq "github.com/pebbe/zmq4"
)

// wmap stores workerID -> clientID assignment.
var wmap = make(map[string]string)

// cmap stores clientID -> assigned workerID mapping
var cmap = make(map[string]string)

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

	//MONITOR

	// Create monitor endpoint
	err = frontend.Monitor("inproc://router-monitor", zmq.EVENT_ALL)
	if err != nil {
		log.Printf("[Broker]: Error setting up monitor: %v", err)
	} else {
		monitor, err := zmq.NewSocket(zmq.PAIR)
		if err != nil {
			log.Printf("[Broker]: Error creating monitor socket: %v", err)
		} else {
			err = monitor.Connect("inproc://router-monitor")
			if err != nil {
				log.Printf("[Broker]: Error connecting monitor: %v", err)
				monitor.Close()
			} else {
				// Start monitoring goroutine
				go func() {
					defer monitor.Close()
					log.Println("[Monitor]: Frontend monitoring started")

					for {
						// Receive the event as a multipart message
						parts, err := monitor.RecvMessageBytes(0)
						if err != nil {
							log.Printf("[Monitor]: Error receiving event: %v", err)
							break
						}

						if len(parts) < 2 {
							continue
						}

						// Parse event data
						if len(parts[0]) < 6 {
							continue
						}

						event := zmq.Event(binary.LittleEndian.Uint16(parts[0][0:2]))
						// value := binary.LittleEndian.Uint32(parts[0][2:6])
						addr := string(parts[1])

						switch event {
						case zmq.EVENT_CONNECT_DELAYED:
							log.Printf("[Monitor]: Client connect DELAYED from %s", addr)
						case zmq.EVENT_CONNECT_RETRIED:
							log.Printf("[Monitor]: Client connect RETRIED from %s", addr)
						case zmq.EVENT_CONNECTED:
							log.Printf("[Monitor]: Client connected from %s", addr)
						case zmq.EVENT_DISCONNECTED:
							log.Printf("[Monitor]: Client disconnected from %s", addr)
						case zmq.EVENT_ACCEPTED:
							log.Printf("[Monitor]: Connection accepted from %s", addr)
						case zmq.EVENT_BIND_FAILED:
							log.Printf("[Monitor]: Bind failed on %s", addr)
						case zmq.EVENT_LISTENING:
							log.Printf("[Monitor]: Socket listening on %s", addr)
						case zmq.EVENT_CLOSE_FAILED:
							log.Printf("[Monitor]: Close failed on %s", addr)
						default:
							// log.Printf("[Monitor]: Event %d on %s (value: %d)", event, addr, value)
						}
					}

					log.Println("[Monitor]: Frontend monitoring stopped")
				}()
			}
		}
	}

	//monitor ======

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
				// [worker_identity, "ACK", chunkNum]
				//               OR
				// [worker_identity, "DONE"]

				frames, err := s.RecvMessage(0)
				if err != nil {
					log.Printf("[Broker]: Error receiving from backend: %v", err)
					log.Panic(err)
				}
				// log.Printf("[Broker]: Received from worker (backend): %v", frames)

				// Basic validation:
				if len(frames) < 2 {
					log.Printf("[Broker]: Malformed message from worker (too few frames): %v", frames)
					log.Panic(err)
				}
				workerZMQID, msgType := frames[0], frames[1]
				clientZMQID := FindClient(frames[0])

				//replace index 0 with client ID
				frames[0] = clientZMQID

				switch msgType {
				case "REGISTER":
					wmap[workerZMQID] = "" // Store worker as available
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
				// Client sends: ["CHUNK", ChunkNum, ChunkData]
				// OR
				// Client sends: ["Done"]

				frames, err := s.RecvMessage(0)
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
					log.Printf("[Worker %s]: Done ", workerID)

				case "CHUNK":
					// log.Printf("[Broker]: Forwarding chunk %s from client %s to worker %s", frames[2], clientZMQID, workerID)

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

	// Find either existing assignment or first available worker
	for workerID, client := range wmap {
		if client == cID {
			assignedWorkerID = workerID
			break
		}
		if client == "" && newWorkerID == "" {
			newWorkerID = workerID
		}
	}

	// Return existing assignment if found
	if assignedWorkerID != "" {
		cmap[cID] = assignedWorkerID
		return assignedWorkerID
	}

	// Assign new worker if available
	if newWorkerID != "" {
		wmap[newWorkerID] = cID
		cmap[cID] = newWorkerID
		log.Printf("[Broker:FindWorker]: Assigned client %s to new worker %s.", cID, newWorkerID)
	}

	return newWorkerID
}

// FindClient retrieves the clientID assigned to a specific worker.
func FindClient(wID string) string {
	if clientID, exists := wmap[wID]; exists {
		return clientID
	}
	return ""
}
