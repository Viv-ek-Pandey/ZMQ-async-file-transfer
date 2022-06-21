package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"golang.org/x/oauth2/google"
	"google.golang.org/api/compute/v1"
	"google.golang.org/api/googleapi"
)

// VMScriptInputDetails - script input details
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

// GCP Site Details
type GCPDetails struct {
	ProjectID string
	Zone      string
	Region    string
}

type InstanceDetails struct {
	ID                 uint64
	InstanceName       string
	InstanceID         string
	InstanceType       string
	VolumeType         string
	VolumeIOPS         int64
	AvailZone          string
	Tags               []Tags
	FolderPath         string
	Networks           []RecoveryNetwork
	SecurityGroups     string
	BootPriority       int
	PreScript          string
	PostScript         string
	IsResetRequired    bool
	DeleteInstance     bool
	SourceMoref        string
	RecoveryEntitiesID uint64
	//RecoveryEntities   RecoveryEntities
}

// Tags - key value pairs
type Tags struct {
	Key             string             `gorm:"primary_key;" json:"key"`
	Value           string             `gorm:"primary_key;" json:"value"`
	InstanceDetails []*InstanceDetails `gorm:"many2many:instance_tags;"`
}

// RecoveryNetwork - Model object describing recovery network details
type RecoveryNetwork struct {
	ID                uint64          `gorm:"primary_key;autoIncrement;" json:"id"`
	IsPublicIP        bool            `json:"isPublicIP"`
	PublicIP          string          `json:"publicIP"`
	PrivateIP         string          `json:"privateIP"`
	Subnet            string          `json:"Subnet"`
	SecurityGroups    string          `gorm:"type:text;" json:"securityGroups"`
	VpcID             string          `json:"vpcId"`
	NetworkTier       string          `json:"networkTier"`
	NetworkMoref      string          `json:"networkMoref"`
	Network           string          `gorm:"type:text;" json:"network"`
	IsFromSource      bool            `json:"isFromSource"`
	InstanceDetailsID uint64          `gorm:"column:instance_details_id" json:"-"`
	InstanceDetails   InstanceDetails `json:"-"`
}

const (
	GCPDISKSIZE           int64  = 40
	WINDOWS               string = "windows"
	DEBSOURCEIMAGE        string = "projects/debian-cloud/global/images/family/debian-9"
	WINSOURCEIMAGE        string = "projects/windows-cloud/global/images/windows-server-2016-dc-core-v20200211"
	NETWORKPATH           string = "/global/networks/default"
	MACHINETYPE           string = "zones/%s/machineTypes/%s"
	SOURCESNAPSHOT        string = "projects/%s/global/snapshots/%s"
	DISKTYPE              string = "projects/%s/zones/%s/diskTypes/%s"
	ALLOWHTTP             string = "http-server"
	GCPOperationTimeout   int64  = 20
	AttachRetries                = 2
	AWSSnapshotRetryCount        = 5
	SnapshotWaitExceeded         = "Snapshot wait time exceeded"
)

// Compute Service API Client
var computeService *compute.Service

func initialize(ctx context.Context) error {
	//ConnectGCP - Make connection to gcp and return client obj
	client, err := google.DefaultClient(ctx, compute.CloudPlatformScope)
	if err != nil {
		log.Println("Error while creating client: ", err)
		return err
	}

	computeService, err = compute.New(client)
	if err != nil {
		log.Println("Error while creating a compute client: ", err)
		return err
	}

	//In case of running outsde GCP VM, comment above code and uncomment below defined code
	// var err error
	// computeService, err = compute.NewService(ctx, option.WithCredentialsFile("D:\\work\\dm\\keys\\gcp\\datamotivedev-eafbd9ad524a.json")) // Json file having service control
	// if err != nil {
	// 	log.Println("Error while connecting to GCP compute service:", err)
	// 	return err
	// }

	return nil
}

func readJSON(input string) (*PplanScriptInputDetails, error) {
	pplanInput := &PplanScriptInputDetails{}

	// un-comment this once
	err := json.Unmarshal([]byte(input), pplanInput)
	if err != nil {
		log.Println("error loading json: ", err)
		return nil, err
	}

	return pplanInput, nil
}

func getGCEInstance(instanceId string, projectId string, zone string) (*compute.Instance, error) {
	if instanceId != "" {
		ctx := context.Background()
		resp, err := computeService.Instances.Get(projectId, zone, instanceId).Context(ctx).Do()
		if err != nil {
			log.Println("Error while getting details for instance: ", instanceId, " ", err)
			return nil, err
		}
		return resp, nil
	}
	return nil, errors.New("No GCE Instance fetched for invalid instance id: " + instanceId)
}

//CreateInstance - create an instance.
func createInstance(ctx context.Context, gcpdetails *GCPDetails, instName string, instanceDetails InstanceDetails, guestOS string) (string, error) {
	log.Println("Creating Instance...")
	sourceImage := ""
	if strings.Contains(strings.ToLower(guestOS), WINDOWS) {
		sourceImage = WINSOURCEIMAGE
		log.Println("Creating Windows Instance")
	} else {
		sourceImage = DEBSOURCEIMAGE
		log.Println("Creating Linux Instance", guestOS)
	}

	disks := &compute.AttachedDisk{
		AutoDelete: true,
		Boot:       true,
		Mode:       "READ_WRITE",
		Interface:  "SCSI",
		DeviceName: instName,
		InitializeParams: &compute.AttachedDiskInitializeParams{
			DiskName:    instName,
			DiskSizeGb:  GCPDISKSIZE,
			SourceImage: sourceImage,
		},
	}

	var diskList []*compute.AttachedDisk
	diskList = append(diskList, disks)

	var networkInterfaceList = createNetworkConfig(instanceDetails.Networks, gcpdetails)
	log.Println("Created network configuration")

	instanceStruct := &compute.Instance{
		MachineType:       fmt.Sprintf(MACHINETYPE, gcpdetails.Zone, instanceDetails.InstanceType),
		Name:              instName,
		Disks:             diskList,
		NetworkInterfaces: networkInterfaceList,
		DisplayDevice: &compute.DisplayDevice{
			EnableDisplay: true,
		},
	}
	if instanceDetails.SecurityGroups != "" && instanceDetails.SecurityGroups != "-" {
		secGrps := strings.Split(instanceDetails.SecurityGroups, ",")
		instanceStruct.Tags = &compute.Tags{
			Items: secGrps,
		}
	}
	log.Println("Created security groups configuration")

	itemList := []*compute.MetadataItems{}
	for _, metadata := range instanceDetails.Tags {
		val := metadata.Value
		item := &compute.MetadataItems{
			Key:   metadata.Key,
			Value: &val,
		}
		itemList = append(itemList, item)
	}
	metadata := &compute.Metadata{
		Items: itemList,
	}
	instanceStruct.Metadata = metadata
	log.Println("Created metadata tags configuration")

	resp, err := computeService.Instances.Insert(gcpdetails.ProjectID, gcpdetails.Zone, instanceStruct).Context(ctx).Do()
	if err != nil {
		log.Println("Error while creating instance is: ", err)
		if gerr, ok := err.(*googleapi.Error); ok {
			return "", errors.New(gerr.Message)
		}
		return "", err
	}
	log.Println("Create Instance initiated...")
	err = waitForOperation(ctx, computeService, gcpdetails.ProjectID, gcpdetails.Zone, resp, GCPOperationTimeout)
	if err != nil {
		log.Println("Error while waiting for create instance: ", err)
		return "", err
	}
	log.Println("Instance created successfully with name: ", instName)
	return instName, nil
}

// CreateNetworkConfig - create network config for instance
func createNetworkConfig(networks []RecoveryNetwork, gcpdetails *GCPDetails) []*compute.NetworkInterface {
	log.Println("Configuring network interfaces for GCP with config")
	var networkInterfaceList []*compute.NetworkInterface
	for _, network := range networks {
		networkInterface := &compute.NetworkInterface{}
		// set interface network
		networkInterface.Network = network.Network
		networkInterface.Subnetwork = "projects/" + gcpdetails.ProjectID + "/regions/" + gcpdetails.Region + "/subnetworks/" + network.Subnet
		// set private ip
		if network.PrivateIP != "" {
			networkInterface.NetworkIP = network.PrivateIP
		}
		// set public ip
		if network.PublicIP != "None" {
			accessConfig := &compute.AccessConfig{}
			accessConfig.Name = "External NAT"
			accessConfig.NetworkTier = network.NetworkTier
			if network.PublicIP != "None" && network.PublicIP != "Ephemeral" {
				accessConfig.NatIP = network.PublicIP
			}
			networkInterface.AccessConfigs = []*compute.AccessConfig{accessConfig}
		}
		networkInterfaceList = append(networkInterfaceList, networkInterface)
	}
	return networkInterfaceList
}

// WaitForOperation - Waits for specified operation to get completed infinitely
func waitForOperation(ctx context.Context, computeService *compute.Service, project string, zone string, op *compute.Operation, timeoutMin int64) error {
	ctx, cancel := context.WithTimeout(ctx, time.Minute*time.Duration(timeoutMin))
	defer cancel()
	ctx.Deadline()

	counter := 0
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			log.Println("Timeout while waiting for operation to get completed")
			return errors.New("Timeout while waiting for operation to get completed")
		case <-ticker.C:
			counter++
			result, err := computeService.ZoneOperations.Get(project, zone, op.Name).Do()
			if err != nil {
				log.Println("Error occured while fetching operation status: ", err)
				return errors.New("Error occured while calling ZoneOperations.Get: " + err.Error())
			}
			if result.Status == "DONE" {
				if result.Error != nil {
					var errors []string
					for _, e := range result.Error.Errors {
						errors = append(errors, e.Message)
					}
					return fmt.Errorf("operation %q failed with error(s): %s", op.Name, strings.Join(errors, ", "))
				}
				log.Println("Operation Completed successfully in ", counter, " attempts")
				return nil
			}
		}
	}
}

func createInstanceDetailsFromSource(instance *compute.Instance, gcpDetails GCPDetails, srcProject string) (InstanceDetails, error) {
	details := InstanceDetails{}
	details.InstanceName = instance.Name
	mcTypeStr := instance.MachineType
	details.InstanceType = mcTypeStr[strings.LastIndex(mcTypeStr, "/")+1:]

	// Set network details
	var networkInterfaceList []RecoveryNetwork
	for _, network := range instance.NetworkInterfaces {
		networkInterface := RecoveryNetwork{}
		// set interface network
		nw := network.Network
		// Replace source project name with target
		nw = strings.ReplaceAll(nw, srcProject, gcpDetails.ProjectID)
		networkInterface.Network = nw
		subnetStr := network.Subnetwork
		subnetName := subnetStr[strings.LastIndex(subnetStr, "/")+1:]
		networkInterface.Subnet = subnetName
		// set private ip
		if network.NetworkIP != "" {
			networkInterface.PrivateIP = network.NetworkIP
		} else {
			networkInterface.PrivateIP = ""
		}
		//TODO: Figure out how to handle case where user is assigning specific IP
		networkInterface.PrivateIP = ""
		// set public ip
		for _, accessConfig := range network.AccessConfigs {
			networkInterface.NetworkTier = accessConfig.NetworkTier
			if accessConfig.Name == "External NAT" {
				//networkInterface.PublicIP = accessConfig.NatIP
				networkInterface.PublicIP = ""
				break
			}
		}
		networkInterfaceList = append(networkInterfaceList, networkInterface)
	}
	details.Networks = networkInterfaceList

	// Set Security Groups
	secGroups := ""
	for _, item := range instance.Tags.Items {
		secGroups += item + ","
	}
	secGroups = strings.TrimSuffix(secGroups, ",")
	details.SecurityGroups = secGroups

	// Set Metadata tags
	var tags []Tags
	for _, meta := range instance.Metadata.Items {
		tag := Tags{}
		tag.Key = meta.Key
		tag.Value = *meta.Value
		tags = append(tags, tag)
	}
	details.Tags = tags

	return details, nil
}

// CreateSnapshot - Creates snapshot for specified Volume name
func createSnapshot(ctx context.Context, gcpDetails *GCPDetails, diskName string, snapName string) (string, error) {
	rb := &compute.Snapshot{
		// TODO: Add desired fields of the request body.
		Name: snapName,
	}

	// In case create snapshot returns error code "RESOURCE_OPERATION_RATE_EXCEEDED"
	// Retry create snapshot
	snapResp := &compute.Operation{}
	var err error
	log.Println("Initiated create snapshot for disk in GCP...")
	for i := 1; i <= AWSSnapshotRetryCount; i++ {
		snapResp, err = computeService.Disks.CreateSnapshot(gcpDetails.ProjectID, gcpDetails.Zone, diskName, rb).Context(ctx).Do()
		if err != nil {
			if strings.Contains(strings.ToLower(err.Error()), "rate has been exceeded") {
				log.Println("Resource operation rate exceeded, retrying after 30 seconds")
				time.Sleep(30 * time.Second)
				if i == AWSSnapshotRetryCount {
					return "", errors.New("Resource limit exceeded, unable to create snapshot for current iteration")
				}
				continue
			} else {
				log.Println("Error occured while creating snapshot: ", err)
				return "", err
			}
		}
		err = waitForOperation(ctx, computeService, gcpDetails.ProjectID, gcpDetails.Zone, snapResp, GCPOperationTimeout)
		if err != nil {
			if strings.Contains(strings.ToLower(err.Error()), "already exist") {
				// If already a snapshot of same name is found. delete it
				log.Println("Snapshot already exists, deleting previous snapshot first")
				err := deleteSnapshot(ctx, computeService, gcpDetails, snapName)
				if err != nil {
					log.Println("Error while Deleting snapshot at GCP site: ", err)
					return "", err
				}
				time.Sleep(30 * time.Second)
			} else if strings.Contains(strings.ToLower(err.Error()), "Timeout") {
				return snapName, errors.New(SnapshotWaitExceeded)
			} else {
				log.Println("Error while waiting for create snapshot: ", err)
				return "", err
			}
		} else {
			break
		}
	}

	log.Println("Snapshot created successully with name: ", snapName)
	return snapName, nil
}

// DeleteSnapshot - Deletes snapshot for specifed Volume name
func deleteSnapshot(ctx context.Context, computeService *compute.Service, gcpdetails *GCPDetails, snapName string) error {
	log.Println("Initiated delete snapshot for disk in GCP...")
	for i := 0; i < AWSSnapshotRetryCount; i++ {
		resp, err := computeService.Snapshots.Delete(gcpdetails.ProjectID, snapName).Context(ctx).Do()
		if err != nil {
			log.Println("Error occured while deleting snapshot, retrying: ", err)
			time.Sleep(10 * time.Second)
		} else if i == AWSSnapshotRetryCount-1 {
			log.Println("Max retry attempt exceeded for delete snapshot")
			return errors.New("Max retry attempt exceeded for delete snapshot")

		} else {
			// TODO: Change code below to process the `resp` object:
			log.Println("Snapshot deleted successfully: ", resp)
			break
		}
	}
	return nil
}

func main() {
	ctx := context.Background()
	err := initialize(ctx)
	if err != nil {
		log.Println("Error initializing Google API Client: ", err)
		return
	}

	//Default arguments for recovered vm list
	pplanInput, err := readJSON(os.Args[1])
	if err != nil {
		log.Println("Error getting recovered VMs list ", err)
		return
	}

	// TODO: Remove test code
	//pplanInput := generateTestData()

	// User argument for source project
	userInput := os.Args[2]
	inputArr := strings.Split(userInput, ",")
	srcProject := strings.TrimSpace(inputArr[0])
	trgProject := strings.TrimSpace(inputArr[1])
	trgZone := strings.TrimSpace(inputArr[2])
	log.Println("Moving ", pplanInput.VMs, " from ", srcProject, " to Target Project: ", trgProject, " in zone: ", trgZone)

	// Recovered GCP project details
	srcGcpDetails := GCPDetails{}
	srcGcpDetails.ProjectID = srcProject
	srcGcpDetails.Zone = trgZone
	srcGcpDetails.Region = trgZone[:len(trgZone)-2]
	log.Println("GCP Source Details: ", srcGcpDetails)

	// Target GCP project details
	gcpDetails := GCPDetails{}
	gcpDetails.ProjectID = trgProject
	gcpDetails.Zone = trgZone
	gcpDetails.Region = trgZone[:len(trgZone)-2]
	log.Println("GCP Target Details: ", gcpDetails)

	// Script execution status
	var scriptStatus bool = true

	// GCP Recovered Instance List
	for _, recoveredVM := range pplanInput.VMs {
		log.Println("Moving recovered virtual machine: ", recoveredVM.TargetID)
		// 1. Get Machine details from Compute API (Instance type, metadata tags, volume type, network, subnet, public ip, private ip & firewall tags)
		instance, err := getGCEInstance(recoveredVM.TargetID, srcProject, trgZone)
		if err != nil {
			log.Println("Error fetching GCE instance: ", recoveredVM.TargetID)
			scriptStatus = false
			continue
		}

		instanceDetails, err1 := createInstanceDetailsFromSource(instance, gcpDetails, srcProject)
		if err1 != nil {
			log.Println("Error creating instance details for instance: ", instance.Name)
			scriptStatus = false
			continue
		}

		// 2. Stop the recovered instance
		err1 = stopInstance(ctx, &srcGcpDetails, recoveredVM.Name)
		if err1 != nil {
			log.Println("Error stopping recovered instance in source project ", err1)
			scriptStatus = false
			continue
		}

		// TODO: Figure out source vm operating system
		guestOs := "linux"
		// 2.1 Create similar instance in target project
		trgInstName, err1 := createInstance(ctx, &gcpDetails, instance.Name, instanceDetails, guestOs)
		if err1 != nil {
			log.Println("Error creating instance in target project ", err1)
			scriptStatus = false
			continue
		}
		log.Println("Created instance ", trgInstName)

		// 2.2 Stop instance and detach it's default boot disk
		err1 = stopInstance(ctx, &gcpDetails, trgInstName)
		if err1 != nil {
			log.Println("Error stopping newly created instance in target project ", err1)
			scriptStatus = false
			continue
		}

		// 2.3 Detach it's boot disk
		// Describe volume attached to gcp instance and detach them
		err1 = detachVolume(ctx, &gcpDetails, trgInstName, trgInstName)
		if err1 != nil {
			log.Println("Error while detaching volume in GCP: ", err)
			scriptStatus = false
			continue
		}
		log.Println("TODO: Remove this Detached disk ", trgInstName)

		//delete that detached boot volume from GCP instance
		err = deleteDisk(ctx, &gcpDetails, trgInstName)
		if err != nil {
			log.Println("Error Deleting volume in GCP: ", err)
			scriptStatus = false
			continue
		}
		log.Println("TODO: Remove this Deleted disk ", trgInstName)

		// 2.4 Snapshot all the disks
		snapNamePrefix := "-dm-snap"
		log.Println("Total disk: ", len(instance.Disks))
		for _, disk := range instance.Disks {
			// Create disk snapshot in target project & region
			snapName := disk.DeviceName + snapNamePrefix
			snapName, err1 = createSnapshot(ctx, &srcGcpDetails, disk.DeviceName, snapName)
			if err1 != nil {
				log.Println("Failed to move disk ", disk.DeviceName, " of instance ", instance.Name)
				log.Println("Moving to next instance")
				break
			}
			log.Println("Snapshot ", snapName, " created for disk ", disk.DeviceName)
			// 2.5 Create disk in target project in same region & zone
			//TODO: Find ways to identify correct Volume type based on source disk
			diskType := "pd-standard"
			diskName, err1 := createDisk(ctx, &srcGcpDetails, &gcpDetails, snapName, 0, snapName, diskType)
			if err1 != nil {
				log.Println("Failed to create disk ", diskName, " of instance ", instance.Name)
				log.Println("Moving to next instance")
				break
			}
			log.Println("Created disk ", snapName)
			// 2.6 Attach newly created disk to the instance
			// TODO: Pass isWin flag based on instance's guest operating system
			attachGCPVolume(ctx, &gcpDetails, instance.Name, diskName, disk.Boot, false, false)
			log.Println("Attached disk ", snapName)
		}
		if err1 != nil {
			// Disk snapshot or creation operation has failed for this instance. Abort this instance and move to next one
			scriptStatus = false
			continue
		}

		// 2.5 Start the instance log new IP
		err1 = startInstance(ctx, &gcpDetails, trgInstName)
		if err1 != nil {
			log.Println("Error starting target instance")
			scriptStatus = false
			continue
		}
	}
	log.Println("Script execution status: ", scriptStatus)
}

//StopInstance - stops the instance.
func stopInstance(ctx context.Context, gcpdetails *GCPDetails, instance string) error {
	resp, err := computeService.Instances.Stop(gcpdetails.ProjectID, gcpdetails.Zone, instance).Context(ctx).Do()
	if err != nil {
		log.Println("Error while stopping instance is: ", err)
		return err
	}
	log.Println("Initiated stop instance...")
	err = waitForOperation(ctx, computeService, gcpdetails.ProjectID, gcpdetails.Zone, resp, GCPOperationTimeout)
	if err != nil {
		log.Println("Error while waiting for stop instance: ", err)
		return err
	}
	log.Println("Instance stopped successfully", resp)
	return nil
}

//StartInstance - starts the instance.
func startInstance(ctx context.Context, gcpdetails *GCPDetails, instance string) error {
	resp, err := computeService.Instances.Start(gcpdetails.ProjectID, gcpdetails.Zone, instance).Context(ctx).Do()
	if err != nil {
		log.Println("Error while starting instance is: ", err)
		return err
	}
	log.Println("Initiated start instance...")
	err = waitForOperation(ctx, computeService, gcpdetails.ProjectID, gcpdetails.Zone, resp, GCPOperationTimeout)
	if err != nil {
		log.Println("Error while waiting for start instance: ", err)
		return err
	}
	log.Println("Instance started successfully", resp)
	return nil
}

// CreateDisk - Creates a disk of specified name and size
func createDisk(ctx context.Context, srcGcpdetails *GCPDetails, gcpdetails *GCPDetails, diskname string, size int64, snapshotName string, volType string) (string, error) {
	diskType := fmt.Sprintf(DISKTYPE, gcpdetails.ProjectID, gcpdetails.Zone, volType)
	log.Println("Creating disk of type: ", diskType)
	diskParam := &compute.Disk{
		// TODO: Add disk parameters
		Name: diskname,
		Type: diskType,
	}

	if size != 0 {
		diskParam.SizeGb = size
	} else {
		diskParam.SourceSnapshot = fmt.Sprintf(SOURCESNAPSHOT, srcGcpdetails.ProjectID, snapshotName)
	}

	resp, err := computeService.Disks.Insert(gcpdetails.ProjectID, gcpdetails.Zone, diskParam).Context(ctx).Do()
	if err != nil {
		log.Println("Error while creating disk: ", err)
		if gerr, ok := err.(*googleapi.Error); ok {
			return "", errors.New(gerr.Message)
		}
		return "", err
	}
	log.Println("Initiated create disk...")
	err = waitForOperation(ctx, computeService, gcpdetails.ProjectID, gcpdetails.Zone, resp, GCPOperationTimeout)
	if err != nil {
		log.Println("Error while waiting for create disk: ", err)
		return "", err
	}
	// TODO: Change code below to process the `resp` object:
	log.Println("Disk created successfully with name :", diskname)
	return diskname, nil
}

// AttachGCPVolume - Attach
func attachGCPVolume(ctx context.Context, gcpdetails *GCPDetails, instName string, volumeName string, boot bool, isWin bool, isDevicePath bool) (string, error) {
	var volumeAttached bool
	var devicePath string
	//var err error
	// attach to instance using instance id and device name
	// for loop to attach a ebs volume umtil retryAttempt exceeds
	// 1. attach volume if error encountered
	// 2. try to reattcah
	for i := 0; i <= AttachRetries; i++ {
		gerr := attachVolume(ctx, gcpdetails, instName, volumeName, boot)
		if gerr != nil {
			log.Println("Error in attaching volume: ", gerr)
			if strings.Contains(gerr.Error(), "already in use") {
				continue
			}
			break
		} else {
			log.Println("Volume attached to instance with id: ", volumeName)
			volumeAttached = true
			break
		}
	}
	if !volumeAttached {
		log.Println("Error while attaching Volume: Attach volume exceeds maximum retry attempts")
		return devicePath, errors.New("Error while attaching Volume: Attach volume exceeds maximum retry attempts")
	}

	// if isDevicePath {
	// 	devicePath, err = GetDeviceName(ctx, computeService, gcpdetails, instName, volumeName, isWin)
	// 	if err != nil {
	// 		zap.S().Error("Device Path not found")
	// 		return "", err
	// 	}
	// }
	return devicePath, nil
}

// AttachVolume - Attaches a specified voluem to specified instance id
func attachVolume(ctx context.Context, gcpDetails *GCPDetails, instName string, volumeName string, boot bool) error {
	// get disk source info
	diskInfo, err := getDiskInfo(ctx, gcpDetails, volumeName)
	if err != nil {
		log.Println("Error while fetching disk info: ", err)
		return err
	}
	rb := &compute.AttachedDisk{
		DeviceName: volumeName,
		Boot:       boot,
		Source:     diskInfo.SelfLink,
	}

	resp, err := computeService.Instances.AttachDisk(gcpDetails.ProjectID, gcpDetails.Zone, instName, rb).Context(ctx).Do()
	if err != nil {
		log.Println("Error occured while attaching disk: ", err)
		if gerr, ok := err.(*googleapi.Error); ok {
			return errors.New(gerr.Message)
		}
		return err
	}
	log.Println("Initiated attach disk...")
	err = waitForOperation(ctx, computeService, gcpDetails.ProjectID, gcpDetails.Zone, resp, GCPOperationTimeout)
	if err != nil {
		log.Println("Error while waiting for attach disk: ", err)
		return err
	}
	// TODO: Change code below to process the `resp` object:
	log.Println("Volume attached to specified instance successfully")
	return nil
}

// GetDiskInfo - Returns complete info for specified disk
func getDiskInfo(ctx context.Context, gcpdetails *GCPDetails, diskName string) (*compute.Disk, error) {
	resp, err := computeService.Disks.Get(gcpdetails.ProjectID, gcpdetails.Zone, diskName).Context(ctx).Do()
	if err != nil {
		log.Println("Error occured while getting disk info: ", err)
		return nil, err
	}
	return resp, nil
}

// DetachVolume - Detaches a specified volume id
func detachVolume(ctx context.Context, gcpdetails *GCPDetails, deviceName string, instName string) error {
	resp, err := computeService.Instances.DetachDisk(gcpdetails.ProjectID, gcpdetails.Zone, instName, deviceName).Context(ctx).Do()
	if err != nil {
		if strings.Contains(err.Error(), "No attached disk found with device name") {
			// Ignore the detaching step
			return nil
		}
		log.Println("Error occured while detaching disk: ", err.Error())
		if gerr, ok := err.(*googleapi.Error); ok {
			return errors.New(gerr.Message)
		}
		return err
	}
	log.Println("Initiated detach disk...")
	err = waitForOperation(ctx, computeService, gcpdetails.ProjectID, gcpdetails.Zone, resp, GCPOperationTimeout)
	if err != nil {
		if strings.Contains(err.Error(), "No attached disk found with device name") {
			// Ignore the detaching step
			return nil
		}
		log.Println("Error while waiting for detach disk: ", err)
		return err
	}
	// TODO: Change code below to process the `resp` object:
	log.Println("Volume detached successfully")
	return nil
}

// DeleteDisk -  Deletes a specified disk with id
func deleteDisk(ctx context.Context, gcpdetails *GCPDetails, diskname string) error {
	resp, err := computeService.Disks.Delete(gcpdetails.ProjectID, gcpdetails.Zone, diskname).Context(ctx).Do()
	if err != nil {
		log.Println("Error occured while deleting disk: ", err)
		if gerr, ok := err.(*googleapi.Error); ok {
			return errors.New(gerr.Message)
		}
		return err
	}
	log.Println("Initiated delete disk...")
	err = waitForOperation(ctx, computeService, gcpdetails.ProjectID, gcpdetails.Zone, resp, GCPOperationTimeout)
	if err != nil {
		log.Println("Error while waiting for delete disk: ", err)
		return err
	}
	log.Println("Disk deleted successfully")
	return nil
}

func printInstanceDetails(instance *compute.Instance) {
	log.Println("Moving Instance ID: ", instance.Id)
}

func generateTestData() *PplanScriptInputDetails {
	pplanInput := &PplanScriptInputDetails{}
	vmList := []VMScriptInputDetails{}
	vm := VMScriptInputDetails{}
	vm.Name = "searce-centos7"
	vm.TargetID = "searce-centos7"
	vmList = append(vmList, vm)
	pplanInput.VMs = vmList
	return pplanInput
}
