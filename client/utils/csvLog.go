package utils

import (
	"encoding/csv"
	"fmt"
	"os"
)

// InitClientTimingCSV creates/overwrites a CSV file to log client timings per chunk.
// Filename pattern: log/<clientID>-<workerID>.client.csv
func InitClientTimingCSV(clientID, workerID string) (*csv.Writer, *os.File, error) {
	if err := os.MkdirAll(RunLogDir, 0o755); err != nil {
		return nil, nil, err
	}
	fileName := fmt.Sprintf("%s/%s-%s.client.csv", RunLogDir, clientID, workerID)
	f, err := os.Create(fileName)
	if err != nil {
		return nil, nil, err
	}
	w := csv.NewWriter(f)
	if err := w.Write([]string{"ChunkNo", "ChunkSend-AckDelta"}); err != nil {
		f.Close()
		return nil, nil, err
	}
	return w, f, nil
}
