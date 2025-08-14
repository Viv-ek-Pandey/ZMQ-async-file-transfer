package main

import (
	"client/config"
	"log"
	"time"

	zmq "github.com/pebbe/zmq4"
)

func NewZmqSocket(id string, tcpAddr string) (*zmq.Socket, error) {

	log.Printf("\n[Client] -  Making New Socket with config %+v", config.AppConfig.Client)
	socket, err := zmq.NewSocket(zmq.DEALER)
	if err != nil {
		return nil, err
	}
	err = socket.SetRcvtimeo(time.Minute * 20)
	if err != nil {
		return nil, err
	}
	if config.AppConfig.Common.RecvBufSize != 0 && config.AppConfig.Common.SendBufSize != 0 {
		log.Println("[Client]: Overwriting kernel default TCP buffer size")
		socket.SetRcvbuf(config.AppConfig.Common.RecvBufSize)
		socket.SetSndbuf(config.AppConfig.Common.SendBufSize)
	}

	// socket.SetSndhwm(config.AppConfig.Client.HighWaterMark)
	// log.Printf("\n[Client]: Setting High Water Mark %v\n", config.AppConfig.Client.HighWaterMark)
	socket.SetIdentity(id)

	// socket.SetIdentity(id)
	log.Println("Starting Client:", id)

	err = socket.Connect(tcpAddr)
	if err != nil {
		log.Panicln("[Client]: failed to connect tcpAddr :", tcpAddr)
		return nil, err
	}
	log.Println("[Client]: connect to tcpAddr:", tcpAddr)

	return socket, err

}
