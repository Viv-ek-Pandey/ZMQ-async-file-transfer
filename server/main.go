package main

import (
	"fmt"
	"log"
	"server/config"
	"server/utils"
	"sync"
)

var wg sync.WaitGroup

func main() {
	pipe := make(chan string)
	go InitBroker(pipe)
	wg.Add(1)
	for i := 0; i < config.AppConfig.Server.NumberOfWorkers; i++ {
		workerID := utils.GetRandID()
		filename := fmt.Sprintf("%s%d.txt", config.AppConfig.Server.GeneratedFileNamePrefix, i+1)
		wg.Add(1)
		go ServerWorker(pipe, workerID, filename)
	}
	wg.Wait()
	<-pipe
	<-pipe
	log.Println("main completed")

}
