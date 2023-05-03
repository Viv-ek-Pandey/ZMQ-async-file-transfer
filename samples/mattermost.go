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
var retryCount = 4 // default script timeout is 300 seconds

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

func runRemoteLinuxCommand(ip string, username string, password string, dbIP string) error {
	if dbIP == "" || ip == "" || username == "" || password == "" {
		log.Println("Failed fetching all the required values from script input")
		os.Exit(1)
	}
	client, session, err := connectToLinuxMachine(ip, username, password)
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

func connectToLinuxMachine(ip string, username string, password string) (*ssh.Client, *ssh.Session, error) {
	sshConfig := &ssh.ClientConfig{
		User: username,
		Auth: []ssh.AuthMethod{ssh.Password(password)},
	}
	sshConfig.HostKeyCallback = ssh.InsecureIgnoreHostKey()
	var client *ssh.Client
	var err error
	for i := 0; i <= retryCount; i++ {
		time.Sleep(time.Second * 60)
		client, err = ssh.Dial("tcp", ip+":"+appVMPort, sshConfig)
		if err != nil {
			if i == retryCount {
				log.Println("SSH connection failed: ", err)
				return nil, nil, err
			}
			log.Println("Connection failed, retrying: ", err)
			continue
		}
	}

	session, err := client.NewSession()
	if err != nil {
		log.Println("Creating session failed: ", err)
		return nil, nil, err
	}
	return client, session, err
}

func main() {
	/*
		We identify the VMs by its name
		Script works only if the DB vm name has 'db' in it and app VM name has 'app' in it
	*/
	log.Println("Input json: ", os.Args[1])
	scriptInput, err := readJSON(os.Args[1])
	if err != nil {
		os.Exit(1)
	}
	var dbIP, appIP, username, password string
	for _, machine := range scriptInput.VMs {
		if strings.Contains(machine.Name, "db") {
			if machine.NetworkInfo[0].PrivateIP == "" &&
				machine.NetworkInfo[0].PublicIP != "" {
				// In case of VMware only public IP field is populated
				dbIP = machine.NetworkInfo[0].PublicIP
			} else {
				dbIP = machine.NetworkInfo[0].PrivateIP
			}
		}
		if strings.Contains(machine.Name, "app") {
			appIP = machine.NetworkInfo[0].PublicIP
			username = machine.Credentials.Username
			password = machine.Credentials.Password
		}
	}
	err = runRemoteLinuxCommand(appIP, username, password, dbIP)
	if err != nil {
		os.Exit(1)
	}
}
