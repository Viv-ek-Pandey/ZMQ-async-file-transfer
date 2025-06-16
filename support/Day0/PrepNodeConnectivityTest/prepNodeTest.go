package main

import (
	"fmt"
	"log"
	"os"

	"github.com/masterzen/winrm"
)

/* Program can be used to check the winRM remote command invocation */

func main() {
	host := os.Args[1] // Windows VM IP or hostname

	// Hardcoded parameters
	port := 5985                // WinRM HTTP port (5986 for HTTPS)
	username := "Administrator" // Windows username
	password := "M0v3@nywh3r3"  // Windows password
	useHTTPS := false           // Set to true if using HTTPS
	insecure := false           // Accept self-signed certs for HTTPS

	// Create endpoint
	endpoint := winrm.NewEndpoint(host, port, useHTTPS, insecure, nil, nil, nil, 0)

	// Create WinRM client
	client, err := winrm.NewClient(endpoint, username, password)
	if err != nil {
		log.Fatalf("Failed to create WinRM client: %v", err)
	}

	// Run 'dir' command
	cmd := "dir"
	stdout, _, _, err := client.RunWithString(cmd, "")
	if err != nil {
		log.Fatalf("Failed to run command: %v", err)
	}

	fmt.Println("\nCommand exited with output: \n", stdout)
}
