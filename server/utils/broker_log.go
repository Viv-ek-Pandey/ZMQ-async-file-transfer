package utils

import (
	"encoding/csv"
	"log"
	"os"
	"sync"
	"time"
)

// InitBrokerTimingCSV creates/overwrites a CSV file to log broker timings.
// Header: Event,ClientID,WorkerID,MsgType,ChunkNo,DurationMicros
func InitBrokerTimingCSV() (*csv.Writer, *os.File, error) {
	if err := os.MkdirAll(RunLogDir, 0o755); err != nil {
		return nil, nil, err
	}
	fileName := RunLogDir + "/broker.csv"
	f, err := os.Create(fileName)
	if err != nil {
		return nil, nil, err
	}
	w := csv.NewWriter(f)
	if err := w.Write([]string{"ClientID", "WorkerID", "MsgType", "Message Recv Delay(socket pool - > broker recv)"}); err != nil {
		f.Close()
		return nil, nil, err
	}
	return w, f, nil
}

func LogBrokerTimmings(wg *sync.WaitGroup, brokerLogChan chan []string, brokerWriter *csv.Writer) {

	defer wg.Done()
	defer func() {
		if brokerWriter != nil {
			brokerWriter.Flush()
		}
	}()
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case row, ok := <-brokerLogChan:
			if !ok {
				if brokerWriter != nil {
					brokerWriter.Flush()
				}
				return
			}
			if brokerWriter != nil {
				if err := brokerWriter.Write(row); err != nil {
					log.Printf("broker csv write err: %v", err)
				}
			}

		case <-ticker.C:
			if brokerWriter != nil {
				brokerWriter.Flush()
			}

		}
	}

}
