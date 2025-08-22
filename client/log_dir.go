package main

import (
	"fmt"
	"os"
	"time"
)

// RunLogDir is the per-run directory under client/log where CSVs are written.
var RunLogDir string

func init() {
	// Create log directory if it doesn't exist
	timestamp := time.Now().Format("15-04-05")
	RunLogDir = fmt.Sprintf("log/%v", timestamp)
	if err := os.MkdirAll(RunLogDir, 0o777); err != nil {
		fmt.Printf("failed to create log directory: %v", err)
	}
}
