#!/bin/bash
####################################################################################################
# README: Post-VM Recovery Script
#
# Overview:
# This Bash script automates several steps to configure and prepare a virtual machine (VM) after recovery:
# 1. Starts sysprep monitoring scheduler 
# 2. Invokes sysprep
# 3. Sets up SAN Policy
# 4. Rename hostname for VM
# 5. Update IP address
# 6. Rejoin the VM to AD
# 7. Invoke services configurator script which makes application specific modifications
#
# Input JSON Format:
# The script expects a JSON input with the following structure:
# {
#   "name": "<VM_NAME>",
#   "sourceID": "<SOURCE_ID>",
#   "ips": [
#     {
#       "publicIP": "<PUBLIC_IP>",
#       "privateIP": "<PRIVATE_IP>"
#     }
#   ],
#   "credentials": {
#     "username": "<USERNAME>",
#     "password": "<PASSWORD>"
#   }
# }
#
# Example Input:
# {
#   "name": "VM-WIN-test-recovery",
#   "sourceID": "example-source-id",
#   "ips": [
#     {
#       "publicIP": "192.168.1.100",
#       "privateIP": "10.0.0.10"
#     }
#   ],
#   "credentials": {
#     "username": "admin",
#     "password": "securepassword123"
#   }
# }
#
# Key Functions:
# 1. log: Logs messages to both stdout and a log file.
# 2. ParseJson: Parses JSON input and stores it in the INPUT_JSON variable.
#
# Execution:
# Run the script as follows:
# ./PostVMRecovery.sh '<input_json>'
#
# Example Command:
# ./PostVMRecovery.sh '{"name":"VM-WIN-test-recovery","sourceID":"example-source-id","ips":[{"publicIP":"192.168.1.100","privateIP":"10.0.0.10"}],"credentials":{"username":"admin","password":"securepassword123"}}'
#
# Prerequisites:
# - jq: Install using `sudo apt install jq -y`.
# - VMware PowerCLI
#
# Logs:
# All logs are written to `/opt/dmservice/logs/VMRecovery.log`.
####################################################################################################
#log file path
LOG_FILE="/opt/dmservice/logs/VMRecovery.log"
# Variable to store the parsed JSON received from the DM workflow containing recovery entity details
INPUT_JSON=""
# Variables for target vCenter
VCENTER_SERVER="10.1.34.63"
VCENTER_USER="administrator@vsphere.local"
VCENTER_PASSWORD='VMware@321'
# Function to log messages to both stdout and the log file
log() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a "$LOG_FILE"
}
# Function to parse the JSON data received from the script
# $1 : JSON data
ParseJson() {
    local all_args="$*"
    local all_args_concatenated="${all_args// /}"
    INPUT_JSON=$(echo "$all_args_concatenated" | jq '.')
}
# Function to run provided powershell on VM with arguments
run_script_on_vm() {
    local VM_NAME=$1
    local username=$2
    local password=$3
    local SCRIPT_PATH=$4
    # Validate inputs
    if [[ -z "$VM_NAME" || -z "$username" || -z "$password" || -z "$SCRIPT_PATH" ]]; then
        log "ERROR: Missing required parameters: VM_NAME, username, password, or SCRIPT_PATH."
        return 1
    fi
    # Log the operation
    log "Running PowerShell script on VM: $VM_NAME"
    log "Script Path: $SCRIPT_PATH"
    # PowerShell script to execute
    pwsh_command=$(cat <<EOF
    Import-Module VMware.PowerCLI
    Connect-VIServer -Server $VCENTER_SERVER -User $VCENTER_USER -Password '$VCENTER_PASSWORD' -Protocol https -Port 443 -Force
    \$vm = Get-VM -Name "$VM_NAME*" | Where-Object { \$_.PowerState -eq 'PoweredOn' } | Select-Object -First 1
    \$startTime = Get-Date
    while (\$vm.PowerState -ne 'PoweredOn' -or \$vm.ExtensionData.Guest.ToolsRunningStatus -ne 'guestToolsRunning') {
        \$elapsedTime = (New-TimeSpan -Start \$startTime -End (Get-Date)).TotalSeconds
        if (\$elapsedTime -ge 90) {
            Write-Output "Timeout reached. Exiting loop."
            Write-Output "The guest operations agent could not be contacted"
            Disconnect-VIServer -Server $VCENTER_SERVER -Force -Confirm:\$false
            Exit 1
        }
        Write-Output "Guest Tools not found in running state for VM $VM_NAME"
        Start-Sleep -Seconds 5
        \$vm = Get-VM -Name "$VM_NAME*" | Where-Object { \$_.PowerState -eq 'PoweredOn' } | Select-Object -First 1
    }
    \$filePath = "$SCRIPT_PATH"
	\$result = Invoke-VMScript -VM \$vm -ScriptText \$filePath -GuestUser $username -GuestPassword '$password' -ScriptType PowerShell
	Write-Output \$result
	\$output = \$result.ScriptOutput  # Fetch the actual output of the script
	Write-Output "Script Output: \$output"
	if (\$result.ExitCode -ne 0) {
		Write-Output "Script failed with exit code"
	} else {
		Write-Output "Script executed successfully!"
	}
	# Disconnect from vCenter
	Disconnect-VIServer -Server $VCENTER_SERVER -Force -Confirm:\$false
EOF
)
    local max_retries=30
    local retry_interval=10
    local attempt=1
	
	while [[ $attempt -le $max_retries ]]; do
        log "Attempt $attempt of $max_retries"
        # Execute the PowerShell command and capture output
		pwsh_output=$(pwsh -Command "$pwsh_command" 2>&1)
		echo "$pwsh_output"
		# Log the PowerShell output
		echo "$pwsh_output" >> "$LOG_FILE"
		# Check for specific error messages
		if [[ $pwsh_output == *"The guest operations agent could not be contacted"* ]]; then
			log "PS command attempt $attempt failed. Retrying the command in $retry_interval seconds..."
            sleep $retry_interval
            attempt=$((attempt + 1))
		elif [[ $pwsh_output == *"Failed to authenticate with the guest operating system"* ]]; then
			log "ERROR: Failed to authenticate with the guest operating system."
			return 2
		elif [[ $pwsh_output == *"A general system error occurred: vix"* ]]; then
			log "Session disconnected"
			return 3
		elif [[ $pwsh_output == *"Script failed with exit code"* ]]; then
			log "ERROR: Script execution failed with an error."
			return 1
		elif [[ $pwsh_output == *"Script executed successfully"* ]]; then
			log "Script executed successfully on the VM."
			return 0
		fi
    done
    log "ERROR: Script execution failed after $max_retries attempts."
    return 1
}
# Main function
main() {
    # Delaying the start of post script by 1 min. so if DM static IP is being set it should get completed
    sleep 10
    
    # Log the start of the script with the current date and time
    log "Post-VM Recovery Script started at: $(date '+%Y-%m-%d %H:%M:%S')"
    # Parse the input JSON
    ParseJson "$1"
    # Extract recovered VM ID, name, and public IP
    local VM_NAME=$(echo "$INPUT_JSON" | jq -r '.name' | tr -d '`' | sed 's/null//g' | tr -d '\n')
    local target_ip=$(echo "$INPUT_JSON" | jq -r '.ips[0].publicIP' | tr -d '`' | sed 's/null//g' | tr -d '\n')
    local username=$(echo "$INPUT_JSON" | jq -r '.credentials.username')
    local password=$(echo "$INPUT_JSON" | jq -r '.credentials.password')
    # Print the extracted values
    log "Recovered VM Name: $VM_NAME"
    log "IP: $target_ip"
    log "Username: $username"
    #log "Password: $password"
	run_script_on_vm "$VM_NAME" $username $password "C:\\scripts_test\\StartSysprepScheduler.ps1" 
    if [ $? -ne 0 ]; then
      log "Error occurred while starting the sysprep status scheduler on VM"
      exit 1
    fi
    run_script_on_vm "$VM_NAME" $username $password "C:\\scripts_test\\start-sysprep.ps1" 
    if [ $? -ne 0 ]; then
      log "Error occurred while performing sysprep on VM"
    fi
    sysprep_complete=0
	retry_interval=30
	local attempt=1
	local max_attempts=60
	# Check if sysprep is completed
	while [[ $sysprep_complete -ne 1 ]]; do
		log "Checking for Sysprep completion marker file (Attempt $attempt of $max_attempts)"
		# Run the script to check for the Sysprep completion marker
		run_script_on_vm "$VM_NAME" $username $password "if (Test-Path 'C:\\scripts_test\\SysprepComplete.txt') { exit 0 } else { exit 1 }"
		exit_code=$?
		if [[ $exit_code -eq 0 ]]; then
			log "Sysprep process completed."
			sysprep_complete=1
			# Delete the marker file
			log "Removing the Sysprep marker file..."
			run_script_on_vm "$VM_NAME" $username $password "Remove-Item -Path 'C:\\scripts_test\\SysprepComplete.txt' -Force"
			if [[ $? -ne 0 ]]; then
				log "WARNING: Failed to remove the Sysprep marker file. Manual cleanup may be required."
			fi
		elif [[ $exit_code -eq 2 ]]; then
			log "ERROR: Authentication failure detected. Retrying with new credentials."
			username="NewAdmin"
			password="Datamotive@1234"
			log "Using generalized creds for user: $username"
		elif [[ $exit_code -eq 3 ]]; then
			log "Session disconnected. Retrying after $retry_interval seconds..."
			sleep $retry_interval
		else
			log "INFO: Sysprep marker not found yet. Waiting $retry_interval seconds before retrying..."
			sleep $retry_interval
		fi
		
		attempt=$((attempt + 1))
		if [[ $attempt -gt $max_attempts ]]; then
			log "ERROR: Maximum retry attempts reached. Sysprep verification failed."
			exit 1
		fi
	done
	run_script_on_vm "$VM_NAME" $username $password "C:\\scripts_test\\set_sanpolicy.ps1"
	if [ $? -ne 0 ]; then
		log "Exiting, error occurred while setting san policy as online all"
	exit 1
	fi
	log "SAN Policy set successfully"	
	
	run_script_on_vm "$VM_NAME" $username $password "C:\\scripts_test\\disjoinAD.ps1" 
    if [ $? -ne 0 ]; then
      log "Exiting, error occurred while removing VM from AD"
      exit 1
    fi
    log "Removed VM from AD"
	# waiting for 10 seconds for system to go into reboot
    sleep 10
    run_script_on_vm "$VM_NAME" $username $password "C:\\scripts_test\\renameHostname_dr.ps1" 
    if [ $? -ne 0 ]; then
      log "Exiting, error occurred while renaming VM "
      exit 1
    fi
    log "Renamed VM hostname"
	# waiting for 10 seconds for system to go into reboot
	sleep 10
    run_script_on_vm "$VM_NAME" $username $password "C:\\scripts_test\\update_ip_dr.ps1" 
    if [ $? -ne 0 ]; then
      log "Exiting, error occurred while updating IP"
      exit 1
    fi
    # before joining VM to AD, waiting for 10 seconds
    sleep 10
    run_script_on_vm "$VM_NAME" $username $password "C:\\scripts_test\\jointoAD.ps1" 
    if [ $? -ne 0 ]; then
      log "Exiting, error occurred while joining to AD"
      exit 1
    fi
	log "Rejoined VM to AD"
	# waiting for 180 seconds for system to go into reboot and the AD policies to be applied
    sleep 180
    run_script_on_vm "$VM_NAME" $username $password "C:\\scripts_test\\IISConfigurator_DR.ps1"
    if [ $? -ne 0 ]; then
      log "Exiting, error occurred while executing script"
      exit 1
    fi
    log "Script execution completed"
    exit 0
}
# Execute the main function with all passed arguments
main "$@"
