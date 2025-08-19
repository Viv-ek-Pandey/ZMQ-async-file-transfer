package utils

import (
	"fmt"
	"os"
	"server/config"
	"time"
)

// RunLogDir is the per-run directory under server/log where CSVs are written.
var RunLogDir string

func init() {
	RunLogDir = fmt.Sprintf("log/run-%s-", time.Now().Format("0102-1504"))
	if config.AppConfig.Server.NoWrite {
		RunLogDir += "no-write"
	}
	_ = os.MkdirAll(RunLogDir, 0o777)
}
