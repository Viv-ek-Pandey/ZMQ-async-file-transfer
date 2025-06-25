package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/digvijay22/reportTask/vmInfo"
)

// Input parsing variables
var (
	vcenterIP      = flag.String("vcenter", "", "vCenter IP or hostname")
	username       = flag.String("username", "", "vCenter username")
	password       = flag.String("password", "", "vCenter password")
	dcname         = flag.String("dcname", "", "Datacenter name")
	process        = flag.String("process", "", "Concurrent OR Sequential")
	goroutinecount = flag.String("goroutinecount", "10", "Count of goroutines")
	outPath        = flag.String("out", "", "Output folder path")
	vmFilePath     = flag.String("vmfilepath", "", "Path to file containing VM names (one per line)")
)

// Reads VM name from file
func readVMsFromFile(path string) ([]string, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var vms []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line != "" {
			vms = append(vms, line)
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return vms, nil
}

func main() {

	flag.Parse()

	// Handling the parsed input
	if *vcenterIP == "" || *username == "" || *password == "" {
		fmt.Println("Error: -vcenter, -user and -pass flags are mandatory.")
		// flag.Usage()
		os.Exit(1)
	}

	if (*dcname == "" && *vmFilePath == "") || (*dcname != "" && *vmFilePath != "") {
		fmt.Println("Error: Either -dcname or -vmfilepath must be specified, but not both.")
		// flag.Usage()
		os.Exit(1)
	}

	URL := fmt.Sprintf("https://%s/sdk", *vcenterIP)

	// Process selection for provided dcname
	if *dcname != "" {
		if *process == "sequential" {
			err := vmInfo.GetReport(URL, *username, *password, *dcname, *outPath)
			if err != nil {
				fmt.Println("Error in sequential Report generation through dc name:", err)
				return
			}
		} else {
			count, err := strconv.Atoi(*goroutinecount)
			if err != nil {
				fmt.Println("Invalid goroutine count: ", *goroutinecount)
			}

			err = vmInfo.GetConcurrentReport(URL, *username, *password, *dcname, *outPath, count)
			if err != nil {
				fmt.Println("Error in concurrent concurrent report generation through dc name:", err)
				return
			}
		}
	}

	// Process selection for provided vmfilepath
	if *vmFilePath != "" {
		vmList, err := readVMsFromFile(*vmFilePath)
		if err != nil {
			fmt.Println("Failed to read VM names from file:", err)
			os.Exit(1)
		}

		if *process == "sequential" {
			err := vmInfo.GetReportByVMName(URL, *username, *password, *outPath, vmList)
			if err != nil {
				fmt.Println("Error in sequential Report generation through VM list from file :", err)
				return
			}
		} else {
			count, err := strconv.Atoi(*goroutinecount)
			if err != nil {
				fmt.Println("Invalid goroutine count: ", *goroutinecount)
			}

			err = vmInfo.GetConcurrentReportByVMName(URL, *username, *password, *outPath, vmList, count)
			if err != nil {
				fmt.Println("Error in concurrent concurrent report generation through VM list from file:", err)
				return
			}
		}

	}

}
