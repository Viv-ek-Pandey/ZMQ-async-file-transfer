package vmInfo

import (
	"context"
	"encoding/csv"
	"fmt"
	"net/url"
	"os"
	"path/filepath"
	"time"

	"github.com/vmware/govmomi"
	"github.com/vmware/govmomi/find"
	"github.com/vmware/govmomi/object"
	"github.com/vmware/govmomi/vim25/mo"
	"github.com/vmware/govmomi/vim25/types"
)

// GetReportByVMName will generate VMReport in sequential way for provided vms in vmfilepath
func GetReportByVMName(URL string, username string, password string, outPath string, targetVMs []string) error {

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

	// Getting all datacenters
	finder := find.NewFinder(client.Client, true)

	dcs, err := finder.DatacenterList(ctx, "*")
	if err != nil {
		return fmt.Errorf("Unable to list datacenters: %w", err)
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
	fileName := fmt.Sprintf("report_%s_by_vname.csv", timestamp)
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

	//  foundVMs - map for tracking the vmname from list
	foundVMs := make(map[string]bool)
	//Iterate on each dc
	for _, dc := range dcs {
		finder.SetDatacenter(dc)
		//vmObjects - all vms in dc
		vmObjects, err := finder.VirtualMachineList(ctx, "*")
		if err != nil {
			continue
		}

		// vmMap - store all vm present in the vmObjects along with their pointer
		vmMap := make(map[string]*object.VirtualMachine)
		for _, vm := range vmObjects {
			name, _ := vm.ObjectName(ctx)
			vmMap[name] = vm
		}

		// VM Data extraction
		for _, targetVM := range targetVMs {

			vmObj, found := vmMap[targetVM]

			if !found {
				continue
			}

			// Extract properties
			var mvm mo.VirtualMachine
			err := vmObj.Properties(ctx, vmObj.Reference(), []string{"name", "snapshot", "config", "guest", "runtime"}, &mvm)
			if err != nil {
				fmt.Printf("Error fetching properties for VM %s: %v\n", targetVM, err)
				continue
			}

			hasSnapshot := (mvm.Snapshot != nil)

			snapshotEnabled := false
			if mvm.Config != nil && mvm.Config.ChangeTrackingEnabled != nil {
				snapshotEnabled = *mvm.Config.ChangeTrackingEnabled
			}

			toolsInstalled := false
			if mvm.Guest != nil {
				toolsInstalled = mvm.Guest.ToolsStatus == types.VirtualMachineToolsStatusToolsOk
			}

			bootType := "Unknown"
			if mvm.Config != nil && mvm.Config.BootOptions != nil && mvm.Config.BootOptions.EfiSecureBootEnabled != nil {
				if *mvm.Config.BootOptions.EfiSecureBootEnabled {
					bootType = "EFI"
				} else {
					bootType = "BIOS"
				}
			}

			guestOS := ""
			if mvm.Config != nil {
				guestOS = mvm.Config.GuestFullName
			}

			hardwareVersion := ""
			if mvm.Config != nil {
				hardwareVersion = mvm.Config.Version
			}

			esxiHost := ""
			if mvm.Runtime.Host != nil {
				hostSystem := object.NewHostSystem(client.Client, *mvm.Runtime.Host)
				var moHost mo.HostSystem
				err := hostSystem.Properties(ctx, hostSystem.Reference(), []string{"name"}, &moHost)
				if err == nil {
					esxiHost = moHost.Name
				}
			}

			cpu := 0
			memoryMB := int64(0)
			if mvm.Config != nil {
				cpu = int(mvm.Config.Hardware.NumCPU)
				memoryMB = int64(mvm.Config.Hardware.MemoryMB)
			}

			// Final CSV write
			writer.Write([]string{
				targetVM,

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
			foundVMs[targetVM] = true
		}
	}

	// vm's which are present in file but are not found
	for _, vm := range targetVMs {
		if !foundVMs[vm] {
			writer.Write([]string{vm, "N/A", "False"})
		}
	}

	fmt.Printf("Total time taken: %s\n", time.Since(start))

	return nil

}
