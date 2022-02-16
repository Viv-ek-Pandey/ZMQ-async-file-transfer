package main

import (
	"encoding/json"
	"errors"
	"log"
	"os"
	"strings"

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
	endpoint := winrm.NewEndpoint(ip, 5985, false, false, nil, nil, nil, 0)
	//zap.S().Debug("Connecting to windows host: ", host)
	client, err := winrm.NewClient(endpoint, username, password)
	if err != nil {
		log.Println("Error while connecting to windows winrm: ", err)
		return err
	}
	command := `get-content C:\\xampp\\htdocs\\osticket\\include\\ost-config-db.php | %{$_ -replace "51.89.240.70", "` + ubuntuIP + `"}
	sc stop Apache2.4
	sc start Apache2.4`
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

func main() {
	machineList, err := readJSON(os.Args[1])
	if err != nil {
		return
	}
	for _, machine := range *machineList {
		if strings.Contains(machine.Name, "win") {
			ubunutIP := getVMIP(*machineList, "prod-ubuntu-14-04")
			err = runWindowsCommand(machine.IP, machine.Username, machine.Password, ubunutIP)
			if err != nil {
				return
			}
		}
	}
}
