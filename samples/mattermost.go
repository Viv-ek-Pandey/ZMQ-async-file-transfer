package main

import (
	"encoding/json"
	"log"
	"os"
	"strings"
	"time"

	"golang.org/x/crypto/ssh"
)

type machine struct {
	Name     string `json:"name"`
	IP       string `json:"ip"`
	Username string `json:"username"`
	Password string `json:"password"`
	OS       string `json:"os"`
}

func readJSON(input string) (*[]machine, error) {
	machineList := &[]machine{}

	// un-comment this once
	err := json.Unmarshal([]byte(input), machineList)
	if err != nil {
		log.Println("error loading json: ", err)
		return nil, err
	}

	// comment this and un-comment the above code
	// m := &machine{
	// 	Name:     "svann-org-mattermost-ubuntu18-04",
	// 	IP:       "35.209.155.83",
	// 	Username: "ubuntu",
	// 	Password: "Datamotive@123",
	// }
	// machineList = append(machineList, *m)

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

func runRemoteLinuxCommand(ip string, username string, pasword string, dbIP string) error {

	client, session, err := connecToLinuxMachine(ip, username, pasword)
	if err != nil {
		return err
	}

	cmd := "sudo sed -i 's/192.168.1.6/13.59.84.0/g' /opt/mattermost/config/config.json && sudo systemctl enable mattermost.service && sudo service mattermost restart"
	out, err := session.CombinedOutput(cmd)
	if err != nil {
		log.Println("output for command: ", cmd, string(out), err)
		return err
	}
	client.Close()
	return nil
}

func connecToLinuxMachine(ip string, username string, pasword string) (*ssh.Client, *ssh.Session, error) {
	sshConfig := &ssh.ClientConfig{
		User: username,
		Auth: []ssh.AuthMethod{ssh.Password(pasword)},
	}
	sshConfig.HostKeyCallback = ssh.InsecureIgnoreHostKey()

	client, err := ssh.Dial("tcp", ip+":22", sshConfig)
	if err != nil {
		log.Println("Connection failed: ", err)
		return nil, nil, err
	}

	session, err := client.NewSession()
	if err != nil {
		log.Println("Connection failed: ", err)
		return nil, nil, err
	}
	return client, session, err
}

func main() {
	time.Sleep(time.Second * 60)
	machineList, err := readJSON(os.Args[1])
	if err != nil {
		return
	}
	for _, machine := range *machineList {
		if strings.Contains(machine.Name, "svann-org-messaging-app") {
			dbIP := "192.168.2.135" // getVMIP(*machineList, "ad")
			err = runRemoteLinuxCommand(machine.IP, machine.Username, machine.Password, dbIP)
			if err != nil {
				return
			}
		}
	}
}
