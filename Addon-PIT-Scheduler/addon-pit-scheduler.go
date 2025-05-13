package main

import (
	"bytes"
	"context"
	"dataengine/drmservice/mos"
	"dataengine/drmservice/services/drmrestclient"
	"dataengine/shared/constant"
	"dataengine/shared/logger"
	"dataengine/shared/sharedmos"
	"dataengine/shared/util"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/mysql"
	"go.uber.org/zap"
)

const (
	BinaryFilename  string = "dm-pit-scheduler"
	ServiceLocation string = "/opt/dmservice/bin"
	LogFilepath     string = "/opt/dmservice/logs/DM-PIT-Scheduler-%s.log"

	EventPITCheckpointPreserved             string = "point-in-time.checkpoint.preserved"
	EventPITCheckpointPreserveFailed        string = "point-in-time.checkpoint.preserve.failed"
	EventPITCheckpointPreservedDeleted      string = "point-in-time.checkpoint.preserve.deleted"
	EventPITCheckpointPreservedDeleteFailed string = "point-in-time.checkpoint.preserve.delete.failed"
)

var (
	// DM Service Credentials
	Host     string = "127.0.0.1"
	Port     int    = 5000
	User     string = "Administrator"
	Password string = ""

	// Scheduler Arguments
	SchedulerName     string
	RetentionDuration int
	CronInterval      string
	ProtectionPlans   string

	logPrefix            string
	RecoveryPlatformType string
)

// Global current time
var currentTime time.Time = time.Now().UTC()

func main() {

	// Parse arguments
	if err := ParseArgs(); err != nil {
		log.Fatalln("Error while parsing the arguments: ", err)
	}

	// Initiate the logger
	if err := logger.InitLogger(fmt.Sprintf(LogFilepath, SchedulerName)); err != nil {
		log.Fatalln("Error Initiating the logger: ", err.Error())
	}

	// Initiate the scheduler
	InitiateScheduler()
}

func ParseArgs() error {

	var showHelp bool
	var createScheduler bool
	var removeScheduler bool

	flag.BoolVar(&showHelp, "help", false, "Show help")
	flag.BoolVar(&createScheduler, "create-scheduler", true, "Flag used to create the PIT Scheduler")
	flag.BoolVar(&removeScheduler, "remove-scheduler", false, "Flag used to remove the PIT Scheduler")

	flag.StringVar(&SchedulerName, "scheduler-name", "", "Name of the scheduler (Required)")
	flag.StringVar(&CronInterval, "cron-interval", "", "Cron Interval string to scheduler the job (Required)")
	flag.StringVar(&ProtectionPlans, "protection-plans", "", "Comma-separated list of protection plan names (Required)")
	flag.IntVar(&RetentionDuration, "retention-duration", 0, "Retention duration in minutes (Required)")
	flag.Parse()

	if showHelp {
		fmt.Fprintf(flag.CommandLine.Output(), "Usage of %s:\n", os.Args[0])
		flag.PrintDefaults()
		os.Exit(0)
	}

	// Uninstall the scheduler by Scheduler Name
	if removeScheduler {
		if SchedulerName == "" {
			return fmt.Errorf("invalid or missing --scheduler-name, please provide the scheduler name")
		}
		if err := removeCronJob(); err != nil {
			log.Fatalln("Error while removing scheduler: ", err)
		}
		os.Exit(0)
	}

	// Validation
	if SchedulerName == "" {
		return fmt.Errorf("invalid or missing --scheduler-name, please provide the scheduler name")
	}
	if RetentionDuration <= 0 {
		return fmt.Errorf("invalid or missing --retention-duration (in minutes), please provide the retention duration")
	}
	if ProtectionPlans == "" {
		return fmt.Errorf("invalid or missing --protection-plans, please provide the protection plan names")
	}

	// Install the scheduler by Scheduler Name
	if createScheduler {
		if CronInterval == "" {
			return fmt.Errorf("invalid or missing --cron-interval, please provide the cron interval")
		}
		if err := createCronJob(); err != nil {
			log.Fatalln("Error while setting up the scheduler: ", err)
		}
		log.Printf("Scheduler: %s | Retention: %d min | Plans: %v", SchedulerName, RetentionDuration, ProtectionPlans)
		os.Exit(0)
	}

	return nil
}

func createCronJob() error {
	log.Println("Setting up the PIT scheduler :", SchedulerName)

	executablePath := fmt.Sprintf("%s/%s", ServiceLocation, BinaryFilename)

	// Copy the executable to /opt/dmservice/bin
	currentPath, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("failed to get current working directory: %w", err)
	}

	sourceFile := filepath.Join(currentPath, BinaryFilename)
	destFile := filepath.Join(ServiceLocation, BinaryFilename)
	if cmdOutput, cmdErr := util.ExecuteCommand("cp", "-rf", sourceFile, destFile); cmdErr != nil {
		return fmt.Errorf("failed to copy executable: %w, output: %s", cmdErr, string(cmdOutput))
	}

	// Prepare cron job line
	cronCommand := fmt.Sprintf(
		`%s %s --scheduler-name="%s" --retention-duration=%d --protection-plans="%s" --create-scheduler=false`,
		CronInterval,
		executablePath,
		SchedulerName,
		RetentionDuration,
		ProtectionPlans,
	)

	// Fetch current crontab
	currentCrontabBytes, err := exec.Command("crontab", "-l").Output()
	if err != nil {
		// Handle "no crontab for user" gracefully
		if exitErr, ok := err.(*exec.ExitError); ok && exitErr.ExitCode() == 1 {
			currentCrontabBytes = []byte{}
		} else {
			return fmt.Errorf("failed to read existing scheduled jobs: %w", err)
		}
	}
	currentCrontab := string(currentCrontabBytes)

	// Prevent duplicate cron job entries
	if strings.Contains(currentCrontab, cronCommand) {
		return fmt.Errorf("checkpoint schedule already exists")
	}
	if strings.Contains(currentCrontab, fmt.Sprintf("--SchedulerName=\"%s\"", SchedulerName)) {
		return fmt.Errorf("checkpoint schedule already exists with name %s", SchedulerName)
	}

	// Add new cron job
	newCrontab := currentCrontab + "\n" + cronCommand + "\n"
	newCrontab = strings.ReplaceAll(newCrontab, `"`, `\"`)
	newCrontab = strings.ReplaceAll(newCrontab, "`", "\\`")
	newCrontab = strings.ReplaceAll(newCrontab, "$", `\$`)
	cmd := exec.Command("bash", "-c", fmt.Sprintf(`echo "%s" | crontab -`, newCrontab))
	if output, err := cmd.CombinedOutput(); err != nil {
		return fmt.Errorf("failed to create checkpoint schedule: %v, output: %s", err, string(output))
	}

	log.Println("PIT checkpoint scheduler successfully created: ", SchedulerName)
	return nil
}

func removeCronJob() error {
	log.Println("Uninstalling the PIT scheduler: ", SchedulerName)

	// Fetch current crontab
	currentCrontabBytes, err := exec.Command("crontab", "-l").Output()
	if err != nil {
		// Handle "no crontab for user" gracefully
		if exitErr, ok := err.(*exec.ExitError); ok && exitErr.ExitCode() == 1 {
			currentCrontabBytes = []byte{}
		} else {
			return fmt.Errorf("failed to read existing scheduled jobs: %w", err)
		}
	}
	currentCrontab := string(currentCrontabBytes)

	// Check and Update Scheduler
	var updatedCrontab []string
	var foundScheduler bool
	for _, cornTab := range strings.Split(currentCrontab, "\n") {
		if strings.Contains(cornTab, fmt.Sprintf("--scheduler-name=\"%s\"", SchedulerName)) {
			foundScheduler = true
			continue
		}
		updatedCrontab = append(updatedCrontab, cornTab)
	}
	if !foundScheduler {
		return fmt.Errorf("scheduler not found with name %s", SchedulerName)
	}

	// Update the cron tab
	newCrontab := strings.Join(updatedCrontab, "\n")
	newCrontab = strings.ReplaceAll(newCrontab, `"`, `\"`)
	newCrontab = strings.ReplaceAll(newCrontab, "`", "\\`")
	newCrontab = strings.ReplaceAll(newCrontab, "$", `\$`)
	cmd := exec.Command("bash", "-c", fmt.Sprintf(`echo "%s" | crontab -`, newCrontab))
	if output, err := cmd.CombinedOutput(); err != nil {
		return fmt.Errorf("failed to uninstall PIT scheduler: %v, output: %s", err, string(output))
	}

	log.Println("PIT checkpoint scheduler successfully uninstalled: ", SchedulerName)
	return nil
}

func InitiateScheduler() {
	zap.S().Info("Started executing PIT scheduler: ", SchedulerName)

	// Get user credentials
	if err := getUserCredentials(); err != nil {
		zap.S().Errorf("%s : Error getting user credentials: %v", err)
		os.Exit(1)
	}

	var protectionPlans []mos.ProtectionPlan
	if err := getProtectionPlans(&protectionPlans); err != nil {
		zap.S().Errorf("%s : Error while getting protection plans: %v", logPrefix, err)
		return
	}

	var eligibleProtectionPlans []mos.ProtectionPlan

	// Check plans available in DM
	for _, planName := range strings.Split(ProtectionPlans, ",") {
		var planFound bool
		for _, plan := range protectionPlans {
			if plan.Name == planName {
				planFound = true
				if !plan.RecoverySite.Node.IsLocalNode {
					zap.S().Warnf("%s : Skipping local protection plan: %s", logPrefix, plan.Name)
					continue
				}
				if plan.Status == mos.Stopped {
					zap.S().Warnf("%s : Skipping stopped protection plan: %s", logPrefix, plan.Name)
					continue
				}
				if !plan.RecoveryPointConfiguration.IsRecoveryCheckpointEnabled {
					zap.S().Warnf("%s : Skipping plan without PIT enabled: %s", logPrefix, plan.Name)
					continue
				}
				eligibleProtectionPlans = append(eligibleProtectionPlans, plan)
				continue
			}
		}
		if !planFound {
			zap.S().Errorf("%s : Protection plan not found in DM: %s", logPrefix, planName)
		}
	}

	// Process protection plans in parallel
	for _, plan := range eligibleProtectionPlans {
		// Process protection plan in a separate goroutine
		processPortectionPlan(plan)
	}

}

func getUserCredentials() error {
	zap.S().Infof("%s : Getting users credentials for user: %s", logPrefix, User)

	dbConnStr := fmt.Sprintf(
		"%s:%s@tcp(%s:%s)/%s?charset=utf8mb4&parseTime=True&loc=Local",
		"root", "321@evitomataD", Host, "3308", "datamotive",
	)

	mysqlDB, err := gorm.Open("mysql", dbConnStr)
	if err != nil {
		return fmt.Errorf("database connection failed: %w", err)
	}
	defer mysqlDB.Close()

	var user mos.User
	if err := mysqlDB.Where("lower(username) = ? ", User).Take(&user).Error; err != nil {
		zap.S().Errorf("%s : Error getting user from database: %v", logPrefix, err.Error())
		return err
	}
	Password = user.Password // set the password

	zap.S().Infof("%s : Successfully fetched the user details", logPrefix)
	return nil
}

func processPortectionPlan(plan mos.ProtectionPlan) error {
	zap.S().Infof("Processing protection plan: %s", plan.Name)

	RecoveryPlatformType = string(plan.RecoverySite.Node.PlatformType)

	for _, vm := range plan.ProtectedEntities.VirtualMachines {
		logPrefix = fmt.Sprintf("%s-%s", plan.Name, vm.Name)

		var pitCheckpoints []mos.PointInTimeCheckpoint

		// Get PIT checkpoints by workload ID
		if err := getPointInTimeCheckpointsByWorkloadID(vm.Moref, &pitCheckpoints); err != nil {
			zap.S().Errorf("%s : Error getting PIT checkpoints for workload %s: %v", logPrefix, vm.Name, err)
			continue
		}

		// Preserve checkpoint by workload
		if err := preserveCheckpoint(pitCheckpoints); err != nil {
			zap.S().Errorf("%s : Error while preserving checkpoint for workload %s: %v", logPrefix, vm.Name, err)

			// Generate Failure Events
			GenerateSchedulerEventForPIT(mos.PointInTimeCheckpoint{
				WorkloadName:       vm.Name,
				WorkloadID:         vm.Moref,
				ProtectionPlanName: plan.Name,
				ProtectionPlanID:   plan.ID,
			}, EventPITCheckpointPreserveFailed, err.Error())
			continue
		}

		// Delete expired checkpoints
		if err := deleteExpiredCheckpoint(pitCheckpoints); err != nil {
			zap.S().Errorf("%s : Error deleting expired checkpoints : %v", logPrefix, err)

			// Generate Failure Events
			GenerateSchedulerEventForPIT(mos.PointInTimeCheckpoint{
				WorkloadName:       vm.Name,
				WorkloadID:         vm.Moref,
				ProtectionPlanName: plan.Name,
				ProtectionPlanID:   plan.ID,
			}, EventPITCheckpointPreservedDeleteFailed, err.Error())
			continue
		}
	}

	return nil
}

func preserveCheckpoint(pitCheckpoints []mos.PointInTimeCheckpoint) error {
	zap.S().Infof("%s : Started preserving PIT checkpoints for workload", logPrefix)

	expireTime := currentTime.Add(time.Duration(RetentionDuration) * time.Minute)
	expireTimeStr := expireTime.Format(time.RFC3339)

	// check for last preserved checkpoint by scheduler in top to bottom order
	var startIndex int = -1
	for idx, pit := range pitCheckpoints {
		if strings.Contains(pit.PreserveDescription, SchedulerName) {
			startIndex = idx
			break
		}
	}
	if startIndex == -1 {
		zap.S().Warnf("%s : No preserved checkpoint found by scheduler", logPrefix)
		startIndex = len(pitCheckpoints)
	}

	// Iterate through PIT checkpoints in bottom to top order
	for i := startIndex - 1; i >= 0; i-- {

		// Fetch the Latest PIT checkpoint
		pit, err := getPointInTimeCheckpoint(pitCheckpoints[i].ID)
		if err != nil {
			zap.S().Errorf("%s : Error fetching PIT checkpoint [%s]: %v", logPrefix, pit.ID, err)
			continue
		}

		if pit.CheckpointStatus != mos.AVAILABLE {
			continue // Skip : if checkpoint not available
		}

		// Update description
		if pit.PreserveDescription != "" {
			pit.PreserveDescription += fmt.Sprintf(",[%s:%s]", SchedulerName, expireTimeStr)
		} else {
			pit.PreserveDescription = fmt.Sprintf("[%s:%s]", SchedulerName, expireTimeStr)
		}

		pit.IsPreserved = true // Mark as preserved

		// Update expiration time
		if pit.ExpirationTime < expireTime.Unix() {
			pit.ExpirationTime = expireTime.Unix()
		}

		// Update the checkpoint status in DM Infra and Raise event
		if err := updatePointInTimeCheckpoint(pit); err != nil {
			zap.S().Errorf("%s : Error preserving PIT checkpoint: %v", logPrefix, err)
			return fmt.Errorf("failed to preserve PIT checkpoint with time [%s UTC]: %v", util.ConvertUnixTimeToDateTime(pit.CreationTime), err)
		}
		GenerateSchedulerEventForPIT(pit, EventPITCheckpointPreserved, "")
		zap.S().Infof("%s : PIT checkpoint preserved [%s] : %s", logPrefix, pit.ID, pit.PreserveDescription)
		return nil
	}

	return fmt.Errorf("no new checkpoint found to preserve for workload")
}

func deleteExpiredCheckpoint(pitCheckpoints []mos.PointInTimeCheckpoint) error {
	zap.S().Infof("%s : Started deleting expired PIT checkpoints for workload", logPrefix)

	// Regex to match entries like [Label:Timestamp]
	re := regexp.MustCompile(`\[(.*?):(.*?)\]`)

	// Delete expired checkpoints that were preserved by this scheduler
	for i := len(pitCheckpoints) - 1; i >= 0; i-- {

		// Fetch the Latest PIT checkpoint
		pit, err := getPointInTimeCheckpoint(pitCheckpoints[i].ID)
		if err != nil {
			zap.S().Errorf("%s : Error fetching PIT checkpoint [%s]: %v", logPrefix, pit.ID, err)
			continue
		}

		switch {
		case !pit.IsPreserved:
			continue // Skip : if checkpoint not preserved
		case !strings.Contains(pit.PreserveDescription, SchedulerName):
			continue // Skip : if preserve description does not contain scheduler name
		}

		var preserveDescription []string
		for _, presDesc := range strings.Split(pit.PreserveDescription, constant.CommaDelimiter) {
			if re.MatchString(presDesc) {
				match := re.FindStringSubmatch(presDesc)
				schedulerExpireTime, err := time.Parse(time.RFC3339, match[2])
				if err != nil {
					preserveDescription = append(preserveDescription, presDesc)
					continue
				}
				if schedulerExpireTime.Unix() > time.Now().UTC().Unix() {
					preserveDescription = append(preserveDescription, presDesc)
					continue
				}
			} else {
				preserveDescription = append(preserveDescription, presDesc)
			}
		}

		switch {
		case len(preserveDescription) > 0 && pit.PreserveDescription != strings.Join(preserveDescription, constant.CommaDelimiter):
			// Update the PIT checkpoint description as checkpoint might be preserved by other scheduler or by the user
			pit.PreserveDescription = strings.Join(preserveDescription, constant.CommaDelimiter)
			if err := updatePointInTimeCheckpoint(pit); err != nil {
				zap.S().Errorf("%s : Error updating PIT checkpoint description [%s] : %s", logPrefix, pit.ID, err.Error())
			}
			zap.S().Infof("%s : PIT checkpoint description updated [%s] : %s", logPrefix, pit.ID, pit.PreserveDescription)
		case len(preserveDescription) == 0 && pit.ExpirationTime <= time.Now().UTC().Unix():
			// Delete the PIT checkpoint and raise event
			if err := deletePointInTimeCheckpoint(pit); err != nil {
				zap.S().Errorf("%s : Error deleting the PIT checkpoint: %v", logPrefix, err)
				return err
			}
			GenerateSchedulerEventForPIT(pit, EventPITCheckpointPreservedDeleted, "")
			zap.S().Infof("%s : Preserved PIT checkpoint deleted [%s] successfully", logPrefix, pit.ID)
		}

		break
	}

	return nil
}

func GenerateSchedulerEventForPIT(pit mos.PointInTimeCheckpoint, eventType string, failureReason string) error {

	var eventDescription string
	var eventSeverity string
	var snapshotIDs []string
	for _, checkpoint := range pit.Checkpoints {
		snapshotIDs = append(snapshotIDs, checkpoint.CheckpointID)
		if RecoveryPlatformType == string(mos.VMware) {
			break
		}
	}

	// Build Impacted Object URNs
	impactedObjectURNs := []string{
		fmt.Sprintf("%s:%s:%d", constant.EventObjectTypeProtectionPlan, pit.ProtectionPlanName, pit.ProtectionPlanID),
		fmt.Sprintf("%s:%s:%s", constant.EventObjectTypeVirtualMachine, pit.WorkloadName, pit.WorkloadID),
	}

	switch eventType {
	case EventPITCheckpointPreservedDeleted:
		eventDescription = fmt.Sprintf(
			"Point-in-time checkpoint deleted by scheduler %s of time %s (UTC) of workload %s of protection plan %s. Deleted checkpoint IDs: [%s]",
			SchedulerName, util.ConvertUnixTimeToDateTime(pit.CreationTime), pit.WorkloadName, pit.ProtectionPlanName, strings.Join(snapshotIDs, ","),
		)
		eventSeverity = string(constant.SeverityLevelInfo)
		impactedObjectURNs = append(impactedObjectURNs, fmt.Sprintf("%s:%s", constant.EventObjectTypePointInTimeCheckpoint, pit.ID))
	case EventPITCheckpointPreserved:
		eventDescription = fmt.Sprintf(
			"Point-in-time checkpoint preserved by scheduler %s of time %s (UTC) of workload %s of protection plan %s. Preserved checkpoint IDs: [%s]",
			SchedulerName, util.ConvertUnixTimeToDateTime(pit.CreationTime), pit.WorkloadName, pit.ProtectionPlanName, strings.Join(snapshotIDs, ","),
		)
		eventSeverity = string(constant.SeverityLevelInfo)
		impactedObjectURNs = append(impactedObjectURNs, fmt.Sprintf("%s:%s", constant.EventObjectTypePointInTimeCheckpoint, pit.ID))
	case EventPITCheckpointPreserveFailed:
		eventDescription = fmt.Sprintf(
			"Point-in-time checkpoint preservation failed by scheduler %s of workload %s of protection plan %s. Failure Reason: %s",
			SchedulerName, pit.WorkloadName, pit.ProtectionPlanName, failureReason,
		)
		eventSeverity = string(constant.SeverityLevelError)
	case EventPITCheckpointPreservedDeleteFailed:
		eventDescription = fmt.Sprintf(
			"Point-in-time checkpoint deletion failed by scheduler %s of workload %s of protection plan %s. Failure Reason: %s",
			SchedulerName, pit.WorkloadName, pit.ProtectionPlanName, failureReason,
		)
		eventSeverity = string(constant.SeverityLevelError)
	default:
		return fmt.Errorf("un-supported event type: %s", eventType)
	}

	event := sharedmos.Event{
		Topic:              constant.EventTopicPointInTimeCheckpoint,
		Description:        eventDescription,
		Severity:           constant.SeverityLevel(eventSeverity),
		Timestamp:          time.Now().Unix(),
		Generator:          User,
		AffectedObject:     constant.EventObjectTypePointInTimeCheckpoint,
		ImpactedObjectURNs: strings.Join(impactedObjectURNs, ","),
		EventType:          constant.EventType(eventType),
	}

	if err := generateEvent(event); err != nil {
		zap.S().Errorf("%s : Error generating event [%s]: %s", logPrefix, eventType, err.Error())
		return err
	}
	return nil
}

// getProtectionPlans fetches all configured protection plans
func getProtectionPlans(protectionPlans *[]mos.ProtectionPlan) error {
	zap.S().Infof("%s : Fetching all configured protection plans", logPrefix)

	ctx, cancel := context.WithTimeout(context.Background(), 180*time.Second)
	defer cancel()

	client := drmrestclient.NewClient(Host, Port, 180)
	if err := client.Login(ctx, User, Password); err != nil {
		zap.S().Errorf("%s : Error logging in to DM Infra: %v", logPrefix, err)
		return err
	}
	defer client.Logout(ctx)

	restURL := fmt.Sprintf("%s/protection/plans", client.BaseURL)

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, restURL, nil)
	if err != nil {
		zap.S().Errorf("%s : Error creating protection plan request: %v", logPrefix, err)
		return err
	}

	if err := client.SendRequest(req, protectionPlans); err != nil {
		zap.S().Errorf("%s : Error sending protection plan request: %v", logPrefix, err)
		return err
	}

	zap.S().Infof("%s : Successfully fetched protection plans", logPrefix)
	return nil
}

func getPointInTimeCheckpointsByWorkloadID(workloadID string, pitCheckpoints *[]mos.PointInTimeCheckpoint) error {
	zap.S().Infof("%s : Fetching PIT checkpoints for workload: %s", logPrefix, workloadID)

	ctx := context.Background()
	client := drmrestclient.NewClient(Host, Port, 180)
	if err := client.Login(ctx, User, Password); err != nil {
		zap.S().Errorf("%s : Error logging in to DM Infra: %v", logPrefix, err)
		return err
	}
	defer client.Logout(ctx)
	defer ctx.Done()

	const pageQueryLimit = 100
	pageQueryOffset := 0

	for {
		restURL := fmt.Sprintf("%s/checkpoints?workloadID=%s&limit=%d&offset=%d", client.BaseURL, workloadID, pageQueryLimit, pageQueryOffset)

		req, err := http.NewRequest(http.MethodGet, restURL, nil)
		if err != nil {
			zap.S().Errorf("%s : Error creating request: %v", logPrefix, err)
			return err
		}

		var resp sharedmos.PageResponse
		if err = client.SendRequest(req, &resp); err != nil {
			zap.S().Errorf("%s : Error sending request: %v", logPrefix, err)
			return err
		}

		// Convert response.Records to strongly typed slice
		jsonBytes, err := json.Marshal(resp.Records)
		if err != nil {
			zap.S().Errorf("%s : Error marshalling records: %v", logPrefix, err)
			return err
		}

		var batch []mos.PointInTimeCheckpoint
		if err = json.Unmarshal(jsonBytes, &batch); err != nil {
			zap.S().Errorf("%s : Error unmarshalling PIT checkpoint records: %v", logPrefix, err)
			return err
		}

		*pitCheckpoints = append(*pitCheckpoints, batch...)

		if !resp.HasNext {
			break
		}
		pageQueryOffset = int(resp.NextOffset)
	}

	zap.S().Infof("%s : Fetched %d PIT checkpoints for workload [%s]", logPrefix, len(*pitCheckpoints), workloadID)
	return nil
}

func updatePointInTimeCheckpoint(pitCheckpoint mos.PointInTimeCheckpoint) error {
	zap.S().Infof("%s : Updating PIT checkpoint [%s]", logPrefix, pitCheckpoint.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 180*time.Second)
	defer cancel()

	client := drmrestclient.NewClient(Host, Port, 180)
	if err := client.Login(ctx, User, Password); err != nil {
		zap.S().Errorf("%s : Error logging in to DM Infra: %v", logPrefix, err)
		return err
	}
	defer client.Logout(ctx)

	restURL := fmt.Sprintf("%s/checkpoints", client.BaseURL)

	reqBody, err := json.Marshal([]mos.PointInTimeCheckpoint{pitCheckpoint})
	if err != nil {
		zap.S().Errorf("%s : Error marshalling request body: %v", logPrefix, err)
		return err
	}

	req, err := http.NewRequest(http.MethodPut, restURL, bytes.NewBuffer(reqBody))
	if err != nil {
		zap.S().Errorf("%s : Error creating PUT request: %v", logPrefix, err)
		return err
	}

	var response []mos.UpdateCheckpointApiResp
	if err = client.SendRequest(req, &response); err != nil {
		zap.S().Errorf("%s : Error sending PUT request: %v", logPrefix, err)
		return err
	}

	for _, resp := range response {
		if resp.PointInTimeCheckpoint.ID == pitCheckpoint.ID && resp.ErrorMessage != "" {
			zap.S().Errorf("%s : Checkpoint update failed for [%s]: %s", logPrefix, pitCheckpoint.ID, resp.ErrorMessage)
			return errors.New(resp.ErrorMessage)
		}
	}

	zap.S().Infof("%s : Successfully updated checkpoint [%s]", logPrefix, pitCheckpoint.ID)
	return nil
}

func deletePointInTimeCheckpoint(pitCheckpoint mos.PointInTimeCheckpoint) error {
	zap.S().Infof("%s : Deleting PIT checkpoint [%s]", logPrefix, pitCheckpoint.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 180*time.Second)
	defer cancel()

	client := drmrestclient.NewClient(Host, Port, 180)
	if err := client.Login(ctx, User, Password); err != nil {
		zap.S().Errorf("%s : Error logging in to DM Infra: %v", logPrefix, err)
		return err
	}
	defer client.Logout(ctx)

	restURL := fmt.Sprintf("%s/checkpoints?id=%s", client.BaseURL, pitCheckpoint.ID)

	req, err := http.NewRequest(http.MethodDelete, restURL, nil)
	if err != nil {
		zap.S().Errorf("%s : Error creating DELETE request: %v", logPrefix, err)
		return err
	}

	var response []mos.DeleteCheckpointApiResp
	if err := client.SendRequest(req, &response); err != nil {
		zap.S().Errorf("%s : Error sending DELETE request: %v", logPrefix, err)
		return err
	}

	for _, resp := range response {
		if resp.CheckpointID == pitCheckpoint.ID && resp.ErrorMessage != "" {
			zap.S().Errorf("%s : Error deleting checkpoint [%s]: %s", logPrefix, pitCheckpoint.ID, resp.ErrorMessage)
			return errors.New(resp.ErrorMessage)
		}
	}

	zap.S().Infof("%s : Successfully deleted PIT checkpoint [%s]", logPrefix, pitCheckpoint.ID)
	return nil
}

func getPointInTimeCheckpoint(pitID string) (mos.PointInTimeCheckpoint, error) {
	zap.S().Infof("%s : Fetching PIT checkpoint by ID [%s]", logPrefix, pitID)

	ctx, cancel := context.WithTimeout(context.Background(), 180*time.Second)
	defer cancel()

	client := drmrestclient.NewClient(Host, Port, 180)
	if err := client.Login(ctx, User, Password); err != nil {
		zap.S().Errorf("%s : Error logging in to DM Infra: %v", logPrefix, err)
		return mos.PointInTimeCheckpoint{}, err
	}
	defer client.Logout(ctx)

	restURL := fmt.Sprintf("%s/checkpoints/%s", client.BaseURL, pitID)

	req, err := http.NewRequest(http.MethodGet, restURL, nil)
	if err != nil {
		zap.S().Errorf("%s : Error creating GET request: %v", logPrefix, err)
		return mos.PointInTimeCheckpoint{}, err
	}

	var response mos.PointInTimeCheckpoint
	if err := client.SendRequest(req, &response); err != nil {
		zap.S().Errorf("%s : Error sending GET request: %v", logPrefix, err)
		return mos.PointInTimeCheckpoint{}, err
	}

	zap.S().Infof("%s : Successfully fetched PIT checkpoint [%s]", logPrefix, pitID)
	return response, nil
}

func generateEvent(event sharedmos.Event) error {
	zap.S().Debugf("%s : Generating event for PIT checkpoint: %v", logPrefix, event.EventType)

	ctx, cancel := context.WithTimeout(context.Background(), 180*time.Second)
	defer cancel()

	client := drmrestclient.NewClient(Host, Port, 180)
	if err := client.Login(ctx, User, Password); err != nil {
		zap.S().Errorf("%s : Error logging in to DM Infra: %v", logPrefix, err)
		return err
	}
	defer client.Logout(ctx)

	restURL := fmt.Sprintf("%s/events", client.BaseURL)
	reqBody, err := json.Marshal(event)
	if err != nil {
		zap.S().Errorf("%s : Error marshalling request body: %v", logPrefix, err)
		return err
	}

	req, err := http.NewRequest(http.MethodPost, restURL, bytes.NewBuffer(reqBody))
	if err != nil {
		zap.S().Errorf("%s : Error creating POST request: %v", logPrefix, err)
		return err
	}

	var response sharedmos.Event
	if err := client.SendRequest(req, &response); err != nil {
		zap.S().Errorf("%s : Error sending POST request: %v", logPrefix, err)
		return err
	}

	zap.S().Debugf("%s : Successfully generated event: ", logPrefix, response.EventType)
	return nil
}
