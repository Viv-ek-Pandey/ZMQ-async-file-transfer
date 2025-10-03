package main

import (
	"log"
	"time"

	zmq "github.com/pebbe/zmq4"
)

func newZmqDealerSocket(id string, tcpAddr string) (*zmq.Socket, error) {

	socket, err := zmq.NewSocket(zmq.DEALER)
	if err != nil {
		return nil, err
	}
	socket.SetIdentity(id)

	socket.SetRcvtimeo(180 * time.Second)

	socket.SetTcpKeepalive(1)

	// TCP keepalive idle (secs before starting probes)
	socket.SetTcpKeepaliveIdle(300)

	// TCP keepalive interval (secs between probes)
	socket.SetTcpKeepaliveIntvl(300)

	// Heartbeat interval (send heartbeat every 2s)
	socket.SetHeartbeatIvl(2 * time.Second)

	// Heartbeat timeout (peer considered dead if no reply in 1s)
	socket.SetHeartbeatTimeout(1 * time.Second)

	// Connection timeout (abort connect if not established in 2s)
	socket.SetConnectTimeout(2 * time.Second)

	err = socket.Connect(tcpAddr)
	if err != nil {
		log.Panicln("[Client]: failed to connect tcpAddr :", tcpAddr)
		return nil, err
	}

	return socket, err

}
