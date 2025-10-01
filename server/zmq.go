package main

import (
	"fmt"
	"log"
	"server/config"
	"time"

	zmq "github.com/pebbe/zmq4"
)

func newZmqDealerSocket(id string, tcpAddr string) (*zmq.Socket, error) {

	socket, err := zmq.NewSocket(zmq.DEALER)
	if err != nil {
		return nil, err
	}
	err = socket.SetRcvtimeo(time.Minute * 3)
	if err != nil {
		return nil, err
	}

	socket.SetIdentity(id)

	err = socket.Connect(tcpAddr)
	if err != nil {
		log.Panicln("[Worker]: failed to connect tcpAddr :", tcpAddr)
		return nil, err
	}
	// log.Printf("[Worker %s]: Starting. Connected to broker backend.", workerID)

	return socket, err

}

func getBrokerRouters() (*zmq.Socket, *zmq.Socket, error) {
	// Frontend ROUTER (for clients)
	frontend, err := zmq.NewSocket(zmq.ROUTER)
	if err != nil {
		return nil, nil, fmt.Errorf("[Broker]: Error creating frontend ROUTER: %w", err)
	}

	frontend.SetRcvtimeo(180 * time.Second)
	frontend.SetTcpKeepalive(1)
	frontend.SetTcpKeepaliveIdle(300)
	frontend.SetTcpKeepaliveIntvl(300)

	frontend.SetHeartbeatIvl(2 * time.Second)
	frontend.SetHeartbeatTimeout(1 * time.Second)

	if err := frontend.Bind(config.AppConfig.Server.FrontendTCPAddress); err != nil {
		return nil, nil, fmt.Errorf("[Broker]: Failed to bind frontend ROUTER: %w", err)
	}
	log.Println("[Broker]: Frontend ROUTER bound to", config.AppConfig.Server.FrontendTCPAddress)

	// Backend Router (for workers)
	backend, err := zmq.NewSocket(zmq.ROUTER)
	if err != nil {
		return nil, nil, fmt.Errorf("[Broker]: Error creating backend DEALER: %w", err)
	}

	if err := backend.Bind(config.AppConfig.Server.BackendInprocAddress); err != nil {
		return nil, nil, fmt.Errorf("[Broker]: Failed to bind backend DEALER: %w", err)
	}
	log.Println("[Broker]: Backend DEALER bound to", config.AppConfig.Server.BackendInprocAddress)

	return frontend, backend, nil
}
