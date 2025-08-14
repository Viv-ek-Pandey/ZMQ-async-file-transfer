package utils

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"log"
	"os"
	"sync/atomic"
)

func CreateEmptyFile(name string) {
	f, err := os.Create(name)
	if err != nil {
		log.Println("Failed to create file:", name)
	}
	f.Close()
}

var idCounter int64

func GetRandID() string {
	next := atomic.AddInt64(&idCounter, 1)
	return fmt.Sprintf("W%d", next)
}

type ConfigOptions struct {
	DisableFileWrite bool
	HighWaterMark    bool
	UseTcp           bool
}

func ComputeSHA256(filePath string) (string, error) {
	file, err := os.ReadFile(filePath)
	if err != nil {
		return "", err
	}
	hash := sha256.Sum256(file)
	return hex.EncodeToString(hash[:]), nil
}
