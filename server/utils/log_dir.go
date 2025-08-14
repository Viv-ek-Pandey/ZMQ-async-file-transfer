package utils

import (
	"fmt"
	"os"
	"time"
)

// RunLogDir is the per-run directory under server/log where CSVs are written.
var RunLogDir string

func init() {
	RunLogDir = fmt.Sprintf("log/run-%s-", time.Now().Format("20060102-1504"))
	// if config.AppConfig.Client.FilePath != "" {
	// 	RunLogDir += config.AppConfig.Client.FilePath
	// }
	_ = os.MkdirAll(RunLogDir, 0o755)
}
