package main

import (
	"client/config"
	"client/utils"
	"fmt"
	"runtime"
	"sync"
)

type sendFrom struct {
	clientID    string
	chunkNumber int
}

var wg sync.WaitGroup

func main() {
	runtime.GOMAXPROCS(1)

	limit := make(chan sendFrom, 1)

	numWorkers := config.AppConfig.Client.NumberOfWorkers
	nxt := make(chan struct{})
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		randID := utils.GetRandID()
		go ClientWorker(randID, &wg, nxt, limit)
		<-nxt
	}

	// -------------------------
	wg.Wait()
	fmt.Println("** DONE **")
}
