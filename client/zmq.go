package main

import (
	"client/config"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
	"sync"
	"time"

	zmq "github.com/pebbe/zmq4"
)

func newZmqSocket(id string, tcpAddr string) (*zmq.Socket, error) {

	socket, err := zmq.NewSocket(zmq.DEALER)
	if err != nil {
		return nil, err
	}
	err = socket.SetRcvtimeo(time.Minute * 10)
	if err != nil {
		return nil, err
	}

	if config.AppConfig.Common.RecvBufSize != 0 && config.AppConfig.Common.SendBufSize != 0 {
		log.Println("[Client]: Overwriting kernel default TCP buffer size")
		socket.SetRcvbuf(config.AppConfig.Common.RecvBufSize)
		socket.SetSndbuf(config.AppConfig.Common.SendBufSize)
	}

	if config.AppConfig.Client.HighWaterMark > 0 {
		socket.SetSndhwm(config.AppConfig.Client.HighWaterMark)
		log.Printf("\n[Client]: Setting High Water Mark %v\n", config.AppConfig.Client.HighWaterMark)
	}
	socket.SetIdentity(id)

	err = socket.Connect(tcpAddr)
	if err != nil {
		log.Panicln("[Client]: failed to connect tcpAddr :", tcpAddr)
		return nil, err
	}

	MapClientToTCPPort(5559, id)

	return socket, err

}

var clientPortMap sync.Map
var usedLocalPorts sync.Map // localPort(int) -> bool

func MapClientToTCPPort(targetPort int, cID string) error {
	pid := os.Getpid()

	// Use shell to execute ss -tupn | grep :targetPort
	cmd := exec.Command("bash", "-c", fmt.Sprintf("ss -tupn | grep :%d", targetPort))
	output, err := cmd.Output()
	if err != nil {
		return fmt.Errorf("failed to run ss command: %v", err)
	}

	lines := strings.Split(string(output), "\n")

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}

		// Only process lines that belong to our process
		if strings.Contains(line, fmt.Sprintf("pid=%d", pid)) {
			conn := parseProcessConnectionLineNew(line)
			// Check if this client ID already has a mapping
			if _, exists := clientPortMap.Load(cID); exists {
				fmt.Printf("Client %s already mapped\n", cID)
				break
			}

			// Check if this local port is already used
			if _, portUsed := usedLocalPorts.Load(conn.LocalPort); portUsed {
				continue // skip this connection, try next line
			}

			// Assign the connection to this client
			clientPortMap.Store(cID, conn)
			usedLocalPorts.Store(conn.LocalPort, true)
			// fmt.Printf("Mapped client %s to local port %d\n", cID, conn.LocalPort)
			break // mapping done
		}
	}

	return nil
}
