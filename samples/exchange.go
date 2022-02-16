package main

import (
	"encoding/json"
	"errors"
	"log"
	"os"
	"strings"
	"time"

	"github.com/masterzen/winrm"
)

type machine struct {
	Name     string `json:"name"`
	IP       string `json:"ip"`
	Username string `json:"username"`
	Password string `json:"password"`
	OS       string `json:"os"`
}

func runWindowsCommand(ip string, username string, password string, ubuntuIP string) error {
	endpoint := winrm.NewEndpoint(ip, 5985, false, false, nil, nil, nil, 120*time.Second)
	//zap.S().Debug("Connecting to windows host: ", host)
	client, err := winrm.NewClient(endpoint, username, password)
	if err != nil {
		log.Println("Error while connecting to windows winrm: ", err)
		return err
	}
	commandList := []string{
		`Disable-NetAdapterBinding -Name 'Ethernet' -ComponentID 'ms_tcpip6'`,
		`Set-DNSClientServerAddress "Ethernet" –ServerAddresses ("192.168.2.135")`,
		`Start-Service –Name MSExchange*`,
	}

	for _, cmd := range commandList {
		err = runCommand(client, cmd)
		if err != nil {
			return err
		}
	}
	return nil
}

func readJSON(input string) (*[]machine, error) {
	machineList := &[]machine{}

	err := json.Unmarshal([]byte(input), machineList)
	if err != nil {
		log.Println("error loading json: ", err)
		return nil, err
	}

	return machineList, nil
}

func getVMIP(machineList []machine, name string) string {

	for _, machine := range machineList {
		if machine.Name == name {
			return machine.IP
		}
	}

	return ""
}

func runCommand(client *winrm.Client, command string) error {
	stdout, stderr, stdcode, err := client.RunPSWithString(command, "")
	if err != nil {
		log.Println("Error while running command :", err)
		return err
	}
	if stdcode != 0 {
		log.Println("Command has error")
		return errors.New(stderr)
	}
	log.Println("stdout: ", stdout)
	return nil
}

func main() {
	machineList, err := readJSON(os.Args[1])
	if err != nil {
		return
	}
	for _, machine := range *machineList {
		if strings.Contains(machine.Name, "exchange") {
			adIP := "192.168.2.135" // getVMIP(*machineList, "ad")
			err = runWindowsCommand(machine.IP, machine.Username, machine.Password, adIP)
			if err != nil {
				return
			}
		}
	}
}
