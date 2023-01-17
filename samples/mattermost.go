package main

import (
	"encoding/json"
	"log"
	"os"
	"strings"
	"time"

	"golang.org/x/crypto/ssh"
)

var appVMPort = "22"

type VMScriptInputDetails struct {
	Name        string                `gorm:"type:text;" json:"name"`
	SourceID    string                `json:"sourceID"`
	TargetID    string                `json:"targetID"`
	NetworkInfo []VMScriptNetworkInfo `json:"ips"`
	Credentials VMScriptCredentials   `json:"credentials"`
}

// VMScriptNetworkInfo - Network information of the instance to be used in the script
type VMScriptNetworkInfo struct {
	PublicIP  string `json:"publicIP"`
	PrivateIP string `json:"privateIP"`
}

// VMScriptCredentials - Credentials of the instance to be used in the script
type VMScriptCredentials struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

// PplanScriptInputDetails - Protection plan script input details
type PplanScriptInputDetails struct {
	VMs []VMScriptInputDetails `json:"vms"`
}

func readJSON(input string) (PplanScriptInputDetails, error) {
	sinput := PplanScriptInputDetails{}

	err := json.Unmarshal([]byte(input), &sinput)
	if err != nil {
		log.Println("error loading json: ", err)
		return sinput, err
	}

	return sinput, nil
}

func runRemoteLinuxCommand(ip string, username string, pasword string, dbIP string) error {

	client, session, err := connecToLinuxMachine(ip, username, pasword)
	if err != nil {
		return err
	}

	cmd := "sudo sed -i 's/[0-9]\\{1,3\\}\\.[0-9]\\{1,3\\}\\.[0-9]\\{1,3\\}\\.[0-9]\\{1,3\\}/'" + dbIP + "'/g' /opt/mattermost/config/config.json && sudo systemctl enable mattermost.service && sudo service mattermost restart"
	log.Println("command: ", cmd)
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

	client, err := ssh.Dial("tcp", ip+":"+appVMPort, sshConfig)
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
	log.Println("Input json: ", os.Args[1])
	scriptInput, err := readJSON(os.Args[1])
	if err != nil {
		return
	}
	var dbIP, appIP, username, password string
	for _, machine := range scriptInput.VMs {
		if strings.Contains(machine.Name, "db") {
			dbIP = machine.NetworkInfo[0].PrivateIP
		}
		if strings.Contains(machine.Name, "app") {
			appIP = machine.NetworkInfo[0].PublicIP
			username = machine.Credentials.Username
			password = machine.Credentials.Password
		}
	}
	err = runRemoteLinuxCommand(appIP, username, password, dbIP)
	if err != nil {
		return
	}
}

