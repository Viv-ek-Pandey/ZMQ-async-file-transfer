package utils

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"sync/atomic"
)

var idCounter int64

func GetRandID() string {
	next := atomic.AddInt64(&idCounter, 1)
	return fmt.Sprintf("W%d", next)
}

func ComputeSHA256(filePath string) (string, error) {
	file, err := os.ReadFile(filePath)
	if err != nil {
		return "", err
	}
	hash := sha256.Sum256(file)
	return hex.EncodeToString(hash[:]), nil
}
