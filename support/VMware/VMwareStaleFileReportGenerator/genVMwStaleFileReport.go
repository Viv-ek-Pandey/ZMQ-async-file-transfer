package main

import (
	"bufio"
	"context"
	"dataengine/drservice/drsconstant"
	"encoding/csv"
	"errors"
	"flag"
	"fmt"
	"net/url"
	"os"
	"sort"
	"strconv"
	"strings"

	"github.com/vmware/govmomi"
	"github.com/vmware/govmomi/find"
	"github.com/vmware/govmomi/object"
	"github.com/vmware/govmomi/property"
	"github.com/vmware/govmomi/vim25/mo"
	"github.com/vmware/govmomi/vim25/soap"
	"github.com/vmware/govmomi/vim25/types"
)

func main() {
	var port int64 = 443
	// Parse command line flags
	vcenter := flag.String("vcenter", "", "vCenter URL")
	username := flag.String("user", "", "vCenter username")
	password := flag.String("pass", "", "vCenter password")
	vmFile := flag.String("vm-file", "", "Path to file containing VM names (one per line)")
	output := flag.String("out", "vm_report.csv", "Output CSV file")
	flag.Parse()

	if *vcenter == "" || *username == "" || *password == "" || *vmFile == "" {
		fmt.Println("All flags are required: -vcenter -user -pass -vm-file")
		flag.Usage()
		os.Exit(1)
	}

	fmt.Println("Reading VM names from file: ", *vmFile)
	vmNames, err := readVMNamesFromFile(*vmFile)
	if err != nil {
		fmt.Printf("Could not read VM names from file: %v\n", err)
		os.Exit(1)
	}

	if len(vmNames) == 0 {
		fmt.Printf("No VM names found in the provided file\n")
		os.Exit(1)
	}

	// vcenter := "54.38.146.200"
	// username := "administrator@vsphere.local"
	// password := "Ht1&WzfykP8$FuiM"
	// vmList := "win-ICICI-sysprep-ps,win16-uefi-"

	ctx, c, err := ConnectVCenter(port, *vcenter, *username, *password)
	if err != nil {
		fmt.Printf("Error connecting with vCenter [%s]. Aborting operation...\n", *vcenter)
		return
	}
	defer DisConnectVCenter(ctx, c)

	finder := find.NewFinder(c.Client, true)
	dc, err := finder.DefaultDatacenter(ctx)
	if err != nil {
		fmt.Println("Default Datacenter not found: ", err)
		panic(err)
	}
	finder.SetDatacenter(dc)

	file, err := os.Create(*output)
	if err != nil {
		fmt.Println("Failed to create output CSV file: ", err)
		panic(err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	writer.Write([]string{"S.no", "VM Name", "Needs Consolidation", "Snapshot Count", "Has Stale VMDK", "Datastore VMDKs", "Active IO Disks", "Snapshot Disks"})

	for i, name := range vmNames {
		vmObj, err := finder.VirtualMachine(ctx, name)
		if err != nil {
			fmt.Printf("VM not found: %s \n", name)
			continue
		}

		vm := object.NewVirtualMachine(c.Client, vmObj.Reference())
		snaps, snapCount, err := GetVMSnapshots(ctx, vm)
		if err != nil {
			fmt.Printf("Snapshot fetch failed for %s \n", name)
			continue
		}

		activeBacking, _ := FetchActiveIODisks(ctx, c, vm)
		dsFiles, _ := FetchVMFilesFromDatastore(ctx, c, vm)
		snapshotBacking, _ := FetchSnapshotBackingFiles(ctx, c, snaps)
		needsConsolidation := "false"

		for ds, paths := range snapshotBacking {
			activeBacking[ds] = append(activeBacking[ds], paths...)
		}

		stale := computeStaleVmwareVMFiles(activeBacking, dsFiles)
		if stale {
			fmt.Printf("Stale Files found for VM [%s]\n", name)
		}

		var moVM mo.VirtualMachine
		_ = vm.Properties(ctx, vm.Reference(), []string{"runtime"}, &moVM)
		if moVM.Runtime.ConsolidationNeeded != nil && *moVM.Runtime.ConsolidationNeeded {
			needsConsolidation = "true"
		}

		writer.Write([]string{
			fmt.Sprintf("%d", i+1),
			name,
			needsConsolidation,
			fmt.Sprintf("%d", snapCount),
			fmt.Sprintf("%v", stale),
			fmt.Sprintf("%v", dsFiles),
			fmt.Sprintf("%v", activeBacking),
			fmt.Sprintf("%v", snapshotBacking),
		})
	}
}

// GetVMSnapshots returns all snapshots and their total count
func GetVMSnapshots(vmctx context.Context, vmobj *object.VirtualMachine) ([]types.VirtualMachineSnapshotTree, int, error) {
	var vm mo.VirtualMachine
	err := vmobj.Properties(vmctx, vmobj.Reference(), []string{"snapshot"}, &vm)
	if err != nil {
		return nil, 0, err
	}

	var collect func([]types.VirtualMachineSnapshotTree) int
	collect = func(snaps []types.VirtualMachineSnapshotTree) int {
		count := 0
		for _, snap := range snaps {
			count++
			count += collect(snap.ChildSnapshotList)
		}
		return count
	}

	if vm.Snapshot != nil {
		return vm.Snapshot.RootSnapshotList, collect(vm.Snapshot.RootSnapshotList), nil
	}
	return nil, 0, nil
} // Keep the remaining helper functions as-is

// computeStaleVmwareVMFiles - compares the VM's disks backing files with those in datastore vmdk files,
// returns true if they do not match
func computeStaleVmwareVMFiles(vmBackingMap map[string][]string, dsFilesMap map[string][]string) bool {
	mismatch := false
	if len(vmBackingMap) != len(dsFilesMap) {
		mismatch = true
		goto EXIT
	}
	for ds, paths := range vmBackingMap {
		dsPaths, ok := dsFilesMap[ds]
		if !ok || len(dsPaths) != len(paths) {
			mismatch = true
			goto EXIT
		}

		dsPathsCopy := append([]string(nil), dsPaths...)
		pathsCopy := append([]string(nil), paths...)

		sort.Strings(dsPathsCopy)
		sort.Strings(pathsCopy)

		for i := range dsPathsCopy {
			if pathsCopy[i] != dsPathsCopy[i] {
				mismatch = true
				goto EXIT
			}
		}
	}
EXIT:
	// if mismatch {
	// 	fmt.Println("Backing files map: ", vmBackingMap)
	// 	fmt.Println("Datastore files map: ", dsFilesMap)
	// }
	return mismatch
}

// FetchActiveIODisks - Fetches the disk paths for the VM used for active IO
func FetchActiveIODisks(vmctx context.Context, client *govmomi.Client, vmObj *object.VirtualMachine) (map[string][]string, error) {
	var vm mo.VirtualMachine
	var refs []types.ManagedObjectReference
	ref := types.ManagedObjectReference{
		Type:  vmObj.Reference().Type,
		Value: vmObj.Reference().Value,
	}
	refs = append(refs, ref)
	activeBackingMap := make(map[string][]string)
	pc := property.DefaultCollector(client.Client)
	err := pc.Retrieve(vmctx, refs, []string{"config.hardware.device"}, &vm)
	if err != nil {
		fmt.Printf("Fetching VM disks failed for VM [%s]: %s\n", vmObj.Name(), err)
		return nil, err
	}
	disks := object.VirtualDeviceList(vm.Config.Hardware.Device).SelectByType((*types.VirtualDisk)(nil))

	// for each VM disk fetch the backing disk path
	for _, disk := range disks {
		disk := disk.(*types.VirtualDisk)
		backing, ok := disk.Backing.(*types.VirtualDiskFlatVer2BackingInfo)
		if !ok {
			errorMsg := fmt.Sprintf("Invalid disk backing type for VM [%s]", vmObj.Name())
			fmt.Println(errorMsg)
			return nil, errors.New(errorMsg)
		}
		filePath := backing.FileName

		parts := strings.SplitN(strings.Trim(filePath, "[]"), "]", 2)
		if len(parts) != 2 {
			errorMsg := fmt.Sprintf("Unexpected datastore path format while fetching disk information for VM [%s], file path: %s", vmObj.Name(), filePath)
			fmt.Println(errorMsg)
			return nil, errors.New(errorMsg)
		}

		datastoreName := strings.TrimSpace(parts[0])
		vmFolder := strings.TrimSpace(parts[1])
		vmDisk := vmFolder[strings.LastIndex(vmFolder, "/")+1:] // Disk file name
		// populate the map
		// map[datastore2:[win_vm-000001.vmdk win_vm.vmdk] datastore1: [win_vm_1.vmdk]]
		activeBackingMap[datastoreName] = append(activeBackingMap[datastoreName], vmDisk)
	}
	return activeBackingMap, nil
}

// FetchVMFilesFromDatastore - Fetch list of VM disk files from all it's associated datastores
func FetchVMFilesFromDatastore(vmctx context.Context, client *govmomi.Client, vmObj *object.VirtualMachine) (map[string][]string, error) {
	// Get VM's datastore and layout
	var moVM mo.VirtualMachine
	pc := property.DefaultCollector(client.Client)
	err := pc.RetrieveOne(vmctx, vmObj.Reference(), []string{"datastore", "layout"}, &moVM)
	if err != nil {
		fmt.Printf("Failed to fetch files layout associated with VM [%s]: %s\n", vmObj.Name(), err)
		return nil, err
	}

	if len(moVM.Datastore) == 0 {
		errorMsg := fmt.Sprintf("No datastore associated with the VM [%s]", vmObj.Name())
		fmt.Println(errorMsg)
		return nil, errors.New(errorMsg)
	}

	dsFilesMap := make(map[string][]string)
	for _, dsRef := range moVM.Datastore {
		var ds mo.Datastore
		err = pc.RetrieveOne(vmctx, dsRef, []string{"summary", "browser"}, &ds)
		if err != nil {
			fmt.Printf("Failed to fetch summary and file browser for Datastore [%s] associated with VM %s, error: %v\n", dsRef, vmObj.Name(), err)
			return nil, err
		}

		for _, vmDiskLayout := range moVM.Layout.Disk {
			// Extract folder path inside datastore based on VM layout
			// A VM might have files spread across multiple datastores
			if len(vmDiskLayout.DiskFile) <= 0 {
				errorMsg := fmt.Sprintf("No disk files found in VM layout for VM [%s]", vmObj.Name())
				fmt.Println(errorMsg)
				return nil, errors.New(errorMsg)
			}
			parts := strings.SplitN(strings.Trim(vmDiskLayout.DiskFile[0], "[]"), "]", 2)
			if len(parts) != 2 {
				errorMsg := fmt.Sprintf("Unexpected VM disk file path format while fetching disk information for VM [%s], file path: %s", vmObj.Name(), vmDiskLayout.DiskFile[0])
				fmt.Println(errorMsg)
				return nil, errors.New(errorMsg)
			}

			datastoreName := strings.TrimSpace(parts[0])
			if datastoreName == ds.Summary.Name {
				vmFolder := strings.TrimSpace(parts[1])
				vmDir := vmFolder[:strings.LastIndex(vmFolder, "/")]

				// Browse the VM folder
				fmt.Printf("Fetching VM files from datastore path [%s] %s\n", datastoreName, vmDir)
				browser := object.NewHostDatastoreBrowser(client.Client, ds.Browser)
				searchSpec := types.HostDatastoreBrowserSearchSpec{
					MatchPattern: []string{"*.vmdk"},
				}
				task, err := browser.SearchDatastore(vmctx, "["+datastoreName+"] "+vmDir, &searchSpec)
				if err != nil {
					fmt.Printf("Failed to search VM files in datastore [%s] associated with VM %s, error: %v\n", ds.Name, vmObj.Name(), err)
					return nil, err
				}

				info, err := task.WaitForResult(vmctx, nil)
				if err != nil {
					fmt.Printf("Failed to search VM files in datastore [%s] associated with VM %s, error: %v\n", ds.Name, vmObj.Name(), err)
					return nil, err
				}
				result := info.Result.(types.HostDatastoreBrowserSearchResults)

				var dsFiles []string
				for _, file := range result.File {
					// skip supporting VMDK files like delta and ctk files
					if strings.Contains(file.GetFileInfo().Path, drsconstant.VMwareSparseFile) ||
						strings.Contains(file.GetFileInfo().Path, drsconstant.VMwareFlatFile) ||
						strings.Contains(file.GetFileInfo().Path, drsconstant.VMwareDeltaFile) ||
						strings.Contains(file.GetFileInfo().Path, drsconstant.VMwareCTKFile) {
						continue
					}
					dsFiles = append(dsFiles, file.GetFileInfo().Path)
				}
				dsFilesMap[datastoreName] = dsFiles
				break
			}
		}
	}
	return dsFilesMap, nil
}

// FetchSnapshotBackingFiles - Fetches the snapshot disk files
func FetchSnapshotBackingFiles(vmctx context.Context, client *govmomi.Client, snapshots []types.VirtualMachineSnapshotTree) (map[string][]string, error) {

	// Map snapshot name to backing files
	snapshotBackingMap := make(map[string][]string)

	var walk func([]types.VirtualMachineSnapshotTree) error
	walk = func(snapshots []types.VirtualMachineSnapshotTree) error {
		pc := property.DefaultCollector(client.Client)
		for _, snap := range snapshots {
			// Get the snapshot VM object
			snapshotRef := snap.Snapshot

			var snapVM mo.VirtualMachineSnapshot
			err := pc.RetrieveOne(vmctx, snapshotRef, []string{"config.hardware.device"}, &snapVM)
			if err != nil {
				fmt.Printf("Failed to fetch snpshot disks of snapshot [%s] associated with VM %s, error: %v\n", snap.Name, snap.Vm.Reference().Value, err)
				return err
			}

			for _, dev := range snapVM.Config.Hardware.Device {
				if disk, ok := dev.(*types.VirtualDisk); ok {
					if backing, ok := disk.Backing.(*types.VirtualDiskFlatVer2BackingInfo); ok {
						parts := strings.SplitN(strings.Trim(backing.FileName, "[]"), "]", 2)
						if len(parts) != 2 {
							errorMsg := fmt.Sprintf("Unexpected snapshot disk file path format for snapshot [%s] associated with VM [%s], file path: %s",
								snap.Name, snap.Vm.Reference().Value, backing.FileName)
							fmt.Println(errorMsg)
							return errors.New(errorMsg)
						}

						datastoreName := strings.TrimSpace(parts[0])
						vmFolder := strings.TrimSpace(parts[1])
						vmDisk := vmFolder[strings.LastIndex(vmFolder, "/")+1:]
						snapshotBackingMap[datastoreName] = append(snapshotBackingMap[datastoreName], vmDisk)
					}
				}
			}

			// Recurse into child snapshots
			err = walk(snap.ChildSnapshotList)
			if err != nil {
				return err
			}
		}
		return nil
	}

	if err := walk(snapshots); err != nil {
		return nil, err
	}
	return snapshotBackingMap, nil
}

func ConnectVCenter(vCenterPort int64, vCenterHostname, vCenterUsername, vCenterPassword string) (context.Context, *govmomi.Client, error) {
	vCenterURL := "https://" + vCenterHostname + ":" + strconv.FormatInt(vCenterPort, 10)
	fmt.Println("vCenter server URL: " + vCenterURL)
	parsedURL, err := soap.ParseURL(vCenterURL)
	if err != nil {
		fmt.Printf("Error parsing url %s\n", vCenterURL)
		return nil, nil, err
	}
	parsedURL.User = url.UserPassword(vCenterUsername, vCenterPassword)
	ctx := context.Background()

	//insecure is true for self signed certificates
	client, err := govmomi.NewClient(ctx, parsedURL, true)
	if err != nil {
		fmt.Println("vCenter server logging in error: ", err)
		return nil, nil, err
	}
	fmt.Println("Successfully connected to vCenter:", vCenterHostname)
	return ctx, client, nil
}

func DisConnectVCenter(ctx context.Context, client *govmomi.Client) {
	if client == nil {
		return
	}
	fmt.Println("Logging out of vCenter server...")
	err := client.Logout(ctx)
	if err != nil {
		fmt.Println("Error while logging out vCenter server:", err)
	}
	fmt.Println("Logged out of vCenter server successfully.")
}

func readVMNamesFromFile(filePath string) ([]string, error) {
	var vmNames []string

	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open VM names file: %w", err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		vmName := strings.TrimSpace(scanner.Text())
		if vmName != "" {
			vmNames = append(vmNames, vmName)
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("failed to read VM names from file: %w", err)
	}
	return vmNames, nil
}
