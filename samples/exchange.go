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

// Waiting for 10 minutes till the time VM boots up in GCP

var RetryCount int = 60

func runWindowsCommand(ip string, username string, password string, ubuntuIP string) error {
	endpoint := winrm.NewEndpoint(ip, 5985, false, false, nil, nil, nil, 720*time.Second)
	//zap.S().Debug("Connecting to windows host: ", host)
	client, err := winrm.NewClient(endpoint, username, password)
	if err != nil {
		log.Println("Error while connecting to windows winrm: ", err)
		return err
	}
	log.Println("Connection successful: ", client)

	// commandList := []string{
	// 	`Disable-NetAdapterBinding -Name 'Ethernet' -ComponentID 'ms_tcpip6'`,
	// 	`Set-DNSClientServerAddress "Ethernet" –ServerAddresses ("192.168.2.135")`,
	// 	`Start-Service –Name MSExchange*`,
	// }

	// for _, cmd := range commandList {
	// 	err = runCommand(client, cmd)
	// 	if err != nil {
	// 		log.Println("Error while running command: ", cmd, err)
	// 		return err
	// 	}
	// }
	cmd := `Disable-NetAdapterBinding -Name 'Ethernet 2' -ComponentID 'ms_tcpip6';Set-DNSClientServerAddress "Ethernet 2" –ServerAddresses ("192.168.2.135")`
	err = runCommand(client, cmd)
	if err != nil {
		log.Println("Error while running command: ", cmd, err)
		return err
	}
	return nil
}

func readJSON(input string) (*[]machine, error) {
	// machineList := &[]machine{}
	machineList := &[]machine{}

	err := json.Unmarshal([]byte(input), machineList)
	if err != nil {
		log.Println("error loading json: ", err)
		return nil, err
	}
	// m := &machine{
	// 	Name:     "svann-org-mattermost-ubuntu18-04",
	// 	IP:       "35.209.155.83",
	// 	Username: "ubuntu",
	// 	Password: "Datamotive@123",
	// }
	// machineList = append(machineList, *m)
	log.Println("Vm struct set: ", machineList)
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
	// time.Sleep(time.Minute * 10)
	machineList, err := readJSON(os.Args[1])
	// machineList, err := readJSON("")
	if err != nil {
		return
	}

	for _, machine := range *machineList {
		if strings.Contains(machine.Name, "exchange") {
			log.Println("VM found: ", machine)
			// TODO Add loop to wait till connection comes
			adIP := "192.168.2.135" // getVMIP(*machineList, "ad")
			for i := 0; i < RetryCount; i++ {
				err := runWindowsCommand(machine.IP, machine.Username, machine.Password, adIP)
				if err != nil {
					log.Println("Error while executing command, sleeping for sometime: ", err)
					time.Sleep(time.Second * 60)
					// Wait till VM boots up and connection is available
				}
				// log.Println("Command executed successfully")
			}
			// err = runWindowsCommand(machine.IP, machine.Username, machine.Password, adIP)
			// if err != nil {
			// 	return
			// }
		}
	}
}
