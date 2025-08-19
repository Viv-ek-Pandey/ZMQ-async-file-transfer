package main

import (
	"client/config"
	"client/utils"
	"fmt"
	"sync"
)

var wg sync.WaitGroup

func main() {
	numWorkers := config.AppConfig.Client.NumberOfWorkers

	// -------------------------
	// NEW: Channels for batch sync
	// batchDoneChan: workers notify main after completing a batch
	batchDoneChan := make(chan string, numWorkers)
	// batchStartChan: main signals workers to start next batch
	batchStartChan := make(chan struct{})

	fullClear := false
	if !config.AppConfig.Common.NoAck && (config.AppConfig.Common.AckAfter > 0) && config.AppConfig.Common.TcpFullClear {
		fullClear = true
	}

	for i := 0; i < config.AppConfig.Client.NumberOfWorkers; i++ {
		wg.Add(1)
		randID := utils.GetRandID()
		go ClientWorker(randID, &wg, batchDoneChan, batchStartChan, fullClear)
	}

	if fullClear {
		// -------------------------
		// NEW: Main routine batch coordinator
		totalBatches := 1000 // set according to file size / ackAfter chunks
		for batch := 0; batch < totalBatches; batch++ {
			// Wait for all workers to finish current batch
			for i := 0; i < numWorkers; i++ {
				<-batchDoneChan
			}
			// Signal all workers to start next batch
			for i := 0; i < numWorkers; i++ {
				batchStartChan <- struct{}{}
				fmt.Printf("\n\n\n *** Starting new batch **** \n\n\n")
			}
		}
	}

	// -------------------------
	wg.Wait()
}
