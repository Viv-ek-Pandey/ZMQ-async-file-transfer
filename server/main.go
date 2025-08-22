package main

import (
	"fmt"
	"log"
	"runtime"
	"server/config"
	"server/utils"
	"sync"
)

var wg sync.WaitGroup

func main() {
	numWorkers := config.AppConfig.Server.NumberOfWorkers
	runtime.GOMAXPROCS(1)
	pipe := make(chan struct{}, numWorkers)
	wg.Add(1)
	go InitBroker(pipe)
	for i := 0; i < numWorkers; i++ {
		workerID := utils.GetRandID()
		filename := fmt.Sprintf("%s%d.txt", config.AppConfig.Server.GeneratedFileNamePrefix, i+1)
		wg.Add(1)
		go ServerWorker(pipe, workerID, filename)
	}

	wg.Wait()

	log.Println("**DONE**")
}
