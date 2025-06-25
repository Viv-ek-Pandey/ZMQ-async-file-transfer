package vmInfo

import (
	"context"
	"encoding/csv"
	"fmt"
	"net/url"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/vmware/govmomi"
	"github.com/vmware/govmomi/find"
	"github.com/vmware/govmomi/object"
)

// dcIterator -  a goroutine that will iterate over all datacenters.
// While iterating over a datacenter it will get all its vms and try to check it with vm name in targetVMs map
// If vm name matches with the name in file then it will add it to inputchan in  pointer to vm form
func dcIterator(ctx context.Context, finder *find.Finder, dcs []*object.Datacenter, targetVMs map[string]bool, inputChan chan<- *object.VirtualMachine, vmFound map[string]bool, foundMu *sync.Mutex) {
	for _, dc := range dcs {
		finder.SetDatacenter(dc)
		vmList, err := finder.VirtualMachineList(ctx, "*")
		if err != nil {
			continue
		}

		for _, vm := range vmList {
			name, err := vm.ObjectName(ctx)
			if err != nil {
				continue
			}

			if targetVMs[name] {
				inputChan <- vm
				foundMu.Lock()
				vmFound[name] = true
				foundMu.Unlock()
			}
		}
	}
	close(inputChan)
}

// / GetConcurrentReportByVMName will generate VMReport in concurrent way for provided vms in vmfilepath
func GetConcurrentReportByVMName(URL string, username string, password string, outPath string, targetVMs []string, goroutineCount int) error {

	// connection creation part
	start := time.Now()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	user, err := url.Parse(URL)
	if err != nil {
		return fmt.Errorf("URL parse error: %w", err)
	}
	user.User = url.UserPassword(username, password)

	client, err := govmomi.NewClient(ctx, user, true)
	if err != nil {
		return fmt.Errorf("vCenter connection failed: %w", err)
	}
	defer client.Logout(ctx)

	// Getting all datacenter list
	finder := find.NewFinder(client.Client, true)
	dcs, err := finder.DatacenterList(ctx, "*")
	if err != nil {
		return fmt.Errorf("datacenter list error: %w", err)
	}

	// If output folder not provided set it to cwd
	timestamp := time.Now().Format("2006-01-02_15-04-05")
	folderPath := outPath
	if folderPath == "" {
		cwd, _ := os.Getwd()
		folderPath = cwd
	}

	// verify provided output folder exist
	if _, err := os.Stat(folderPath); os.IsNotExist(err) {
		err := os.MkdirAll(folderPath, os.ModePerm)
		if err != nil {
			return fmt.Errorf("failed to create output folder: %w", err)
		}
	}

	// VMReport folder creation inside the output folder path
	// If VMReport is present from first then append the new files to same folder
	vmInfoPath := filepath.Join(folderPath, "VMReport")
	if _, err := os.Stat(vmInfoPath); os.IsNotExist(err) {
		err := os.MkdirAll(vmInfoPath, os.ModePerm)
		if err != nil {
			return fmt.Errorf("failed to create VMInfo folder: %w", err)
		}
	}

	// file creation with timestamp
	fileName := fmt.Sprintf("report_%s.csv", timestamp)
	filePath := filepath.Join(vmInfoPath, fileName)

	file, err := os.Create(filePath)
	if err != nil {
		return fmt.Errorf("file creation error %w", err)
	}
	defer file.Close()
	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Title writing in csv
	writer.Write([]string{"VMName", "HasSnapshots", "HasCBTEnabled", "HasVmwareTools", "BootType", "GuestOS", "HardwareVersion", "ESXiHost", "CPU", "MemoryMB"})

	// Channels and synchronization
	inputChan := make(chan *object.VirtualMachine, 8) // Workers will read from this channel
	outputChan := make(chan Data, 8)                  // Workers will write data on this channel
	var wg sync.WaitGroup                             // Track gracefull completion of workers
	var writerWg sync.WaitGroup                       // Track gracefull completion of anonymous writer goroutine
	vmFound := make(map[string]bool)                  // Track vmnames in file
	foundMu := sync.Mutex{}                           // Mutex for proper value modification in vmFound map

	// Prepare map for lookup
	targetVMMap := make(map[string]bool) // store the provided vm in map in order to get quick access
	for _, vm := range targetVMs {
		targetVMMap[vm] = true
		vmFound[vm] = false
	}

	// starting worker goroutines
	for i := 0; i < goroutineCount; i++ {
		wg.Add(1)
		go workers(ctx, client, inputChan, outputChan, &wg)
	}

	// anonymous writer goroutine will write processed data in csv
	// anonymous  writer goroutine will stop when outputchan is closed
	writerWg.Add(1)
	go func() {
		defer writerWg.Done()
		for val := range outputChan {
			err := writer.Write([]string{
				val.vmName,
				fmt.Sprintf("%v", val.hasSnapshot),
				fmt.Sprintf("%v", val.snapshotEnabled),
				fmt.Sprintf("%v", val.toolsInstalled),
				val.bootType,
				val.guestOS,
				val.hardwareVersion,
				val.esxiHost,
				fmt.Sprintf("%d", val.cpu),
				fmt.Sprintf("%d", val.memoryMB),
			})
			if err != nil {
				fmt.Println("Error writing to CSV:", err)
			}
		}
	}()

	// starting  dcIterator- will add pointer to required vm on inputchan
	go dcIterator(ctx, finder, dcs, targetVMMap, inputChan, vmFound, &foundMu)

	// as all worker complete the task outputchan will be closed
	go func() {
		wg.Wait()
		close(outputChan)
	}()

	// waiting to entire csv data should be written in file
	writerWg.Wait()

	// vm's which are present in file but are not found
	for vm, found := range vmFound {
		if !found {
			writer.Write([]string{vm, "N/A", "False"})
		}
	}

	fmt.Printf("Total time taken: %s\n", time.Since(start))
	return nil
}
