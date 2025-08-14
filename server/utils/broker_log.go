package utils

import (
	"encoding/csv"
	"os"
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

// func WriteBrokerTimingRow(w *csv.Writer, clientID, workerID, msgType string, chunkNo string, durationMicros int64) error {
// 	if w == nil {
// 		return nil
// 	}
// 	rec := []string{clientID, workerID, msgType, chunkNo, fmt.Sprintf("%d", durationMicros)}
// 	if err := w.Write(rec); err != nil {
// 		return err
// 	}
// 	w.Flush()
// 	return nil
// }
