package main

import (
	"client/config"
	"client/utils"
	"fmt"
	"runtime"
	"sync"
)

var wg sync.WaitGroup

func main() {
	runtime.GOMAXPROCS(1)

	//make done
	numWorkers := config.AppConfig.Client.NumberOfWorkers
	nxt := make(chan struct{})
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		randID := utils.GetRandID()
		go ClientWorker(randID, &wg, nxt)
		<-nxt
	}

	// -------------------------
	wg.Wait()
	fmt.Println("** DONE **")
}
