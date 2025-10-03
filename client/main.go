package main

import (
	"client/config"
	"client/utils"
	"fmt"
	"runtime"
	"sync"
)

type FailoverInfo struct {
	ClientID    string
	ChunkNumber int
	FilePath    string
	ChunkSize   int64
}

var wg sync.WaitGroup

func main() {
	runtime.GOMAXPROCS(1)

	failoverChan := make(chan FailoverInfo, 10) // Channel for failover events

	numWorkers := config.AppConfig.Client.NumberOfWorkers

	// Start failover handler
	//For testing set-identity kill the client worker and start a new worker with same identity
	go handleFailover(failoverChan, &wg, failoverChan)

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		randID := utils.GetRandID()
		go ClientWorker(randID, &wg, failoverChan)
	}

	// -------------------------
	wg.Wait()
	fmt.Println("** DONE **")
}

func handleFailover(failoverChan <-chan FailoverInfo, wg *sync.WaitGroup, sendFailoverChan chan<- FailoverInfo) {
	for failoverInfo := range failoverChan {
		go ClientWorkerWithResume(failoverInfo.ClientID, wg, sendFailoverChan, failoverInfo.ChunkNumber)
	}
}
