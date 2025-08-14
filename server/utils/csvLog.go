// utils/logging.go or wherever appropriate
package utils

import (
	"encoding/csv"
	"fmt"
	"os"
	"strconv"
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
		"ClientSentMicros",
		"BrokerRecvAt(socket(case:)start-time)",
		"BrokerSentMicros",
		"WokerRecvMicros",
		"WokerMSGDelay(msgWait(loop) -> message recv)",
	}); err != nil {
		return nil, nil, fmt.Errorf("failed to write CSV header: %v", err)
	}

	return writer, logFile, nil
}

func LogChunkTiming(writer *csv.Writer, chunkNumber int, start time.Time, end time.Time) {
	duration := end.Sub(start)

	startStr := start.Format("15:04:05.000000")
	endStr := end.Format("15:04:05.000000")

	microseconds := duration.Microseconds()

	writer.Write([]string{strconv.Itoa(chunkNumber), startStr, endStr, strconv.FormatInt(microseconds, 10)})
}
