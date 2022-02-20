package main

import (
	"log"
	"strings"

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
	machineList := []machine{}

	// un-comment this once
	// err := json.Unmarshal([]byte(input), machineList)
	// if err != nil {
	// 	log.Println("error loading json: ", err)
	// 	return nil, err
	// }

	// comment this and un-comment the above code
	m := &machine{
		Name:     "svann-org-mattermost-ubuntu18-04",
		IP:       "35.209.155.83",
		Username: "ubuntu",
		Password: "Datamotive@123",
	}
	machineList = append(machineList, *m)

	return &machineList, nil
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

	commandList := []string{
		`sudo sed -i 's/192.168.1.124/192.168.2.151/g' /opt/mattermost/config/config.json`,
		`service mattermost restart`,
	}

	for _, cmd := range commandList {
		out, err := session.CombinedOutput(cmd)
		if err != nil {
			log.Println("output: ", string(out), err)
			return err
		}
		log.Println("output: ", string(out))
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
	machineList, err := readJSON("")
	if err != nil {
		return
	}
	for _, machine := range *machineList {
		if strings.Contains(machine.Name, "svann-org-mattermost-ubuntu18-04") {
			dbIP := "192.168.2.135" // getVMIP(*machineList, "ad")
			err = runRemoteLinuxCommand(machine.IP, machine.Username, machine.Password, dbIP)
			if err != nil {
				return
			}
		}
	}
}
