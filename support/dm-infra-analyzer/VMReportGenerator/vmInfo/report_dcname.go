package vmInfo

import (
	"context"
	"encoding/csv"
	"fmt"
	"net/url"
	"os"
	"time"

	"path/filepath"

	"github.com/vmware/govmomi"
	"github.com/vmware/govmomi/find"
	"github.com/vmware/govmomi/object"
	"github.com/vmware/govmomi/vim25/mo"
	"github.com/vmware/govmomi/vim25/types"
)

// GetReport - will generate VMReport in sequential way for provided dcname
func GetReport(URL string, username string, password string, DCName string, outPath string) error {

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

	// Title writing in csv
	writer := csv.NewWriter(file)
	defer writer.Flush()
	writer.Write([]string{"VMName", "HasSnapshots", "HasCBTEnabled", "HasVmwareTools", "BootType", "GuestOS", "HardwareVersion", "ESXiHost", "CPU", "MemoryMB"})

	// VM Data extraction
	for _, vm := range vms {
		var mvm mo.VirtualMachine
		err = vm.Properties(ctx, vm.Reference(), []string{"name", "snapshot", "config", "guest", "runtime"}, &mvm)
		if err != nil {
			return fmt.Errorf("Error fetching vm properties %w ", err)
		}

		vmName := mvm.Name // Information of  VM name

		hasSnapshot := false // Information of snapshot on VM
		if mvm.Snapshot != nil {
			hasSnapshot = true
		}

		snapshotEnabled := false // Information of CBT enabled
		if mvm.Config != nil && mvm.Config.ChangeTrackingEnabled != nil {
			snapshotEnabled = *mvm.Config.ChangeTrackingEnabled
		}

		toolsInstalled := false // Information of  vmware tools on VM
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

		// write in csv operation
		writer.Write([]string{
			vmName,
			fmt.Sprintf("%v", hasSnapshot),
			fmt.Sprintf("%v", snapshotEnabled),
			fmt.Sprintf("%v", toolsInstalled),
			bootType,
			guestOS,
			hardwareVersion,
			esxiHost,
			fmt.Sprintf("%d", cpu),
			fmt.Sprintf("%d", memoryMB),
		})
	}

	fmt.Printf("Total time taken: %s\n", time.Since(start))

	return nil

}
