package vmInfo

import (
	"context"
	"encoding/csv"
	"fmt"
	"net/url"
	"os"
	"sync"
	"time"

	"path/filepath"

	"github.com/vmware/govmomi"
	"github.com/vmware/govmomi/find"
	"github.com/vmware/govmomi/object"
	"github.com/vmware/govmomi/vim25/mo"
	"github.com/vmware/govmomi/vim25/types"
)

// Data for Output channel
type Data struct {
	vmName          string
	hasSnapshot     bool
	snapshotEnabled bool
	toolsInstalled  bool
	bootType        string
	guestOS         string
	hardwareVersion string
	esxiHost        string
	cpu             int
	memoryMB        int64
}

// workers will run concurrently
// -- read  pointer to vm from inputchan
// -- fetch the required data per vm
// -- Add the data on output chan
func workers(ctx context.Context, client *govmomi.Client, inputChan <-chan *object.VirtualMachine, outputChan chan<- Data, wg *sync.WaitGroup) {
	defer wg.Done()

	// VM Data extraction
	for vm := range inputChan {
		var mvm mo.VirtualMachine
		err := vm.Properties(ctx, vm.Reference(), []string{"name", "snapshot", "config", "guest", "runtime"}, &mvm)
		if err != nil {
			fmt.Println("Error fetching VM properties:", err)
			continue
		}

		vmName := mvm.Name // Information of  VM name

		hasSnapshot := false // Information for snapshot of VM
		if mvm.Snapshot != nil {
			hasSnapshot = true
		}

		snapshotEnabled := false // Information of CBT Enabled
		if mvm.Config != nil && mvm.Config.ChangeTrackingEnabled != nil {
			snapshotEnabled = *mvm.Config.ChangeTrackingEnabled
		}

		toolsInstalled := false // VMware tools installed
		if mvm.Guest != nil {
			toolsInstalled = mvm.Guest.ToolsStatus == types.VirtualMachineToolsStatusToolsOk
		}

		bootType := "Unknown" // Information of  bootType on VM
		if mvm.Config != nil && mvm.Config.BootOptions != nil && mvm.Config.BootOptions.EfiSecureBootEnabled != nil {
			if *mvm.Config.BootOptions.EfiSecureBootEnabled {
				bootType = "EFI"
			} else {
				bootType = "BIOS"
			}
		}

		guestOS := "" // Information of  Guest OS on VM
		if mvm.Config != nil {
			guestOS = mvm.Config.GuestFullName
		}

		hardwareVersion := "" // Information of  hardware version  on VM
		if mvm.Config != nil {
			hardwareVersion = mvm.Config.Version
		}

		esxiHost := "" // Information of  Esxi Host on VM
		if mvm.Runtime.Host != nil {
			hostSystem := object.NewHostSystem(client.Client, *mvm.Runtime.Host)

			var moHost mo.HostSystem
			err := hostSystem.Properties(ctx, hostSystem.Reference(), []string{"name"}, &moHost)
			if err == nil {
				esxiHost = moHost.Name
			}
		}

		cpu := 0 // Information of  CPU on VM
		memoryMB := int64(0)
		if mvm.Config != nil {
			cpu = int(mvm.Config.Hardware.NumCPU)
			memoryMB = int64(mvm.Config.Hardware.MemoryMB)
		}

		// write data on output channel
		outputChan <- Data{
			vmName:          vmName,
			hasSnapshot:     hasSnapshot,
			snapshotEnabled: snapshotEnabled,
			toolsInstalled:  toolsInstalled,
			bootType:        bootType,
			guestOS:         guestOS,
			hardwareVersion: hardwareVersion,
			esxiHost:        esxiHost,
			cpu:             cpu,
			memoryMB:        memoryMB,
		}

	}

}

// will generate VMReport in concurrent  way for provided dcname
func GetConcurrentReport(URL string, username string, password string, DCName string, outPath string, goroutineCount int) error {

	// Vcenter Connection creation Part
	start := time.Now()
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	user, err := url.Parse(URL)
	if err != nil {
		fmt.Println("URL parse error: ", err)
		os.Exit(1)
	}

	user.User = url.UserPassword(username, password)
	client, err := govmomi.NewClient(ctx, user, true)
	if err != nil {
		fmt.Println("Failed to connect: ", err)
		return err
	}
	defer client.Logout(ctx)
	fmt.Println("Connected Successfully")

	// connecting to datacenter and getting VM List
	finder := find.NewFinder(client.Client, true)

	dc, err := finder.Datacenter(ctx, DCName)
	if err != nil {
		return fmt.Errorf(" Datacenter level failure: %w", err)
	}
	finder.SetDatacenter(dc)
	fmt.Println("data center found, ", dc)

	vms, err := finder.VirtualMachineList(ctx, "*")
	if err != nil {
		return fmt.Errorf("Error fetching VMs: %w", err)
	}

	// If output path is not provided it will be default to CWD
	timestamp := time.Now().Format("2006-01-02_15-04-05")
	folderPath := outPath
	if folderPath == "" {
		cwd, _ := os.Getwd()
		folderPath = cwd
	}

	// If output path is  provided it but not physically exist then create it
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

	var wg sync.WaitGroup                             // Track gracefull completion of workers
	inputChan := make(chan *object.VirtualMachine, 8) // Workers will read from this channel
	outputChan := make(chan Data, 8)                  // Workers will write data on this channel

	// Starting worker functions
	for i := 0; i < goroutineCount; i++ {
		wg.Add(1)
		go workers(ctx, client, inputChan, outputChan, &wg)
	}

	// anonymous writer goroutine will write processed data in csv
	// anonymous  writer goroutine will stop when outputchan is closed
	var writeWg sync.WaitGroup
	writeWg.Add(1)
	go func() {
		defer writeWg.Done()
		for val := range outputChan {

			// write in csv operation
			if err := writer.Write([]string{
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
			}); err != nil {
				fmt.Println("Error writing to CSV: ", err)
			}
		}
	}()

	//  passing vm input to workers with inputChan channel and then closing the channel
	for _, vm := range vms {
		inputChan <- vm
	}
	close(inputChan)

	// Function to close output channel after all workers have done their task
	// no waitgroup tracking  as workers complete it will close output channel
	go func() {
		wg.Wait()
		close(outputChan)
	}()

	// waiting for anonymous writer function
	writeWg.Wait()

	fmt.Printf("Total time taken: %s\n", time.Since(start))

	return nil

}
