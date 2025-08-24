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
	err = socket.SetRcvtimeo(time.Minute * 10)
	if err != nil {
		return nil, err
	}

	if config.AppConfig.Common.RecvBufSize != 0 && config.AppConfig.Common.SendBufSize != 0 {
		log.Println("[Worker]: Overwriting kernel default TCP buffer size")
		socket.SetRcvbuf(config.AppConfig.Common.RecvBufSize)
		socket.SetSndbuf(config.AppConfig.Common.SendBufSize)
	}

	if config.AppConfig.Server.HighWaterMark > 0 {
		socket.SetSndhwm(config.AppConfig.Server.HighWaterMark)
		log.Printf("\n[Worker]: Setting High Water Mark %v\n", config.AppConfig.Server.HighWaterMark)
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

	if config.AppConfig.Common.RecvBufSize != 0 && config.AppConfig.Common.SendBufSize != 0 {
		log.Println("[Broker]: Overwriting kernel default TCP buffer size")
		frontend.SetRcvbuf(config.AppConfig.Common.RecvBufSize)
		frontend.SetSndbuf(config.AppConfig.Common.SendBufSize)
	}

	if config.AppConfig.Server.HighWaterMark > 0 {
		if err := frontend.SetRcvhwm(config.AppConfig.Server.HighWaterMark); err != nil {
			return nil, nil, fmt.Errorf("[Broker]: Error setting High Water Mark: %w", err)
		}
		log.Printf("[Broker-Frontend]: Setting HighWaterMark %v\n", config.AppConfig.Server.HighWaterMark)
	}

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
