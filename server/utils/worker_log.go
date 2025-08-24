// utils/logging.go or wherever appropriate
package utils

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sync"
	"time"
)

func InitChunkTimingCSV(workerID string) (*csv.Writer, *os.File, error) {

	fileName := fmt.Sprintf("%s/%s.csv", RunLogDir, workerID)
	logFile, err := os.Create(fileName)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to create CSV log: %v", err)
	}

	writer := csv.NewWriter(logFile)
	// Detailed timing per chunk
	// ChunkNo,ClientID,WorkerID,ClientSentMicros,BrokerRecvMicros,WorkerRecvMicros,ClientToBrokerMicros,BrokerToWorkerMicros,ClientToWorkerMicros
	if err := writer.Write([]string{
		"ChunkNo",
		"ClientSent",
		"BrokerRecvAt",
		"Client(sent)-Broker(recv)",
		"BrokerSent",
		"WokerRecv",
		"Broker(sent)-Worker(recv)",
		"WokerMSGDelay(time between msg)",
	}); err != nil {
		return nil, nil, fmt.Errorf("failed to write CSV header: %v", err)
	}

	return writer, logFile, nil
}

func LogChunkTiming(wg *sync.WaitGroup, workerWriter *csv.Writer, workerLogChan <-chan []string) {

	defer wg.Done()
	defer func() {
		if workerWriter != nil {
			workerWriter.Flush()
		}
	}()
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case row, ok := <-workerLogChan:
			if !ok {
				if workerWriter != nil {
					workerWriter.Flush()
				}
				return
			}
			if workerWriter != nil {
				if err := workerWriter.Write(row); err != nil {
					log.Printf("worker csv write err: %v", err)
				}
			}

		case <-ticker.C:
			if workerWriter != nil {
				workerWriter.Flush()
			}

		}
	}

}
