package main

import (
	"client/config"
	"client/utils"
	"sync"

	zmq "github.com/pebbe/zmq4"
)

var wg sync.WaitGroup

func main() {
	numWorkers := config.AppConfig.Client.NumberOfWorkers

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		randID := utils.GetRandID()
		go ClientWorker(randID, &wg)
	}

	// -------------------------
	wg.Wait()
}

func CheckConn(socket *zmq.Socket, cId string, wId string, wg *sync.WaitGroup) {
	targetPort := 5559

	// Parse TCP connections
	// fmt.Printf("\nParsing TCP connections to port %d...\n", targetPort)
	// _, err := ParseSSOutput(targetPort)
	// if err != nil {
	// 	log.Fatalf("Failed to parse ss output: %v", err)
	// }

	// fmt.Printf("Found %d TCP connections\n\n", len(tcpConnections))

	// Match ZMQ sockets to TCP connections using process-based approach
	zmqSocketWithMeta := ZmqConnMetaData{
		Conn:     socket,
		ClientId: cId,
		WorkerId: wId,
	}
	MatchZMQToTCPByProcess([]ZmqConnMetaData{zmqSocketWithMeta}, targetPort)
	wg.Done()

}
