package main

import (
	"client/config"
	"client/utils"
	"fmt"
	"sync"
)

var wg sync.WaitGroup

func main() {

	fmt.Printf("Chunk Size: %d bytes\n", config.AppConfig.Client.ChunkSize)

	for i := 0; i < config.AppConfig.Client.NumberOfWorkers; i++ {
		wg.Add(1)
		randID := utils.GetRandID()
		go ClientWorker(randID, &wg)
	}
	wg.Wait()
}
