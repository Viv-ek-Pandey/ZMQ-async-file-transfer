#!/bin/bash

####################################################################################################
# README: Post-VM Recovery Script
#
# Overview:
# This Bash script automates several steps to configure and prepare a virtual machine (VM) after recovery:
# 1. Verifies the readiness of the Azure VM Agent on the target VM.
# 2. Copies required files (e.g., answer files and scripts) from Azure Storage to the VM.
# 3. Executes a Sysprep operation on the VM to prepare it for reuse.
# 4. Enables RDP post-Sysprep.
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
# 3. check_vm_agent_status: Checks the readiness of the Azure VM Agent on a specific VM.
# 4. run_copy_file: Copies a file from Azure Storage to the VM.
# 5. run_sysprep: Executes a Sysprep operation on the target VM using an answer file.
#
# Execution:
# Run the script as follows:
# ./PostVMRecovery.sh '<input_json>'
#
# Example Command:
# ./PostVMRecovery.sh '{"name":"VM-WIN-test-recovery","sourceID":"example-source-id","ips":[{"publicIP":"192.168.1.100","privateIP":"10.0.0.10"}],"credentials":{"username":"admin","password":"securepassword123"}}'
#
# Prerequisites:
# - Azure CLI: Install and authenticate using `az login`.
# - jq: Install using `sudo apt install jq -y`.
# - Azure Storage Configuration: Ensure the required files are stored in the Azure Storage container.
#
# Logs:
# All logs are written to `/opt/dmservice/logs/VMRecovery.log`.
####################################################################################################


#log file path
LOG_FILE="/opt/dmservice/logs/VMRecovery.log"

# azure resource group name
RESOURCE_GROUP="release-1.2.1"
# azure storage account name
ACCOUNT_NAME="automationcitemp"
# azure container name where files are stored
CONTAINER_NAME="tempcontainer"

# Unattend xml file (answer file for sysprep)
UNATTEND_FILE="answerFileWin2k19.xml"
# powershell script to initiate sysprep as process
SYSPREP_FILE="start-sysprep.ps1"
# script to enable rdp after sysprep
SYSPREP_ENABLE_RDP="SysprepSpecialize.cmd"

# Variable to store the parsed JSON received from the DM workflow containing recovery entity details
INPUT_JSON=""

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



# Function to check VM Agent status
check_vm_agent_status() {
    local VM_NAME=$1
    local RESOURCE_GROUP=$2
    local TIMEOUT=600   # 10 minutes in seconds
    local INTERVAL=30   # Check every 30 seconds
    local ELAPSED=0

    log "Checking Azure VM agent status for VM: $VM_NAME in Resource Group: $RESOURCE_GROUP"

    while [ $ELAPSED -lt $TIMEOUT ]; do
        # Get the VM instance view and extract the vmAgent status
        vm_agent_status=$(az vm get-instance-view \
            --name "$VM_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --query "instanceView.vmAgent.statuses[0].displayStatus" \
            --output tsv)

        if [[ "$vm_agent_status" == "Ready" ]]; then
            log "VM Agent is up and running: $vm_agent_status"
            return 0
        else
            log "VM '$VM_NAME' Agent status is '$vm_agent_status'. Checking again in $INTERVAL seconds..."
            sleep $INTERVAL
            ELAPSED=$((ELAPSED + INTERVAL))
        fi
    done

    log "VM '$VM_NAME' Agent did not come up within the timeout period ($TIMEOUT seconds)."
    return 1
}

# Function to copy file from azure container to recovered vm
run_copy_file() {
    local VM_NAME=$1
    local RESOURCE_GROUP=$2
    local FILE_NAME=$3
    local EXPIRY=$(date -d "$(date +'%Y')-12-31T23:59:59Z" -u +"%Y-%m-%dT%H:%M:%SZ")

    # Log the inputs
    log "Inputs: VM_NAME=$VM_NAME, RESOURCE_GROUP=$RESOURCE_GROUP, FILE_NAME=$FILE_NAME"

    # Ensure FILE_NAME is provided
    if [[ -z "$FILE_NAME" ]]; then
        log "Error: FILE_NAME parameter is missing."
        return 1
    fi

    # Get the blob URL
    log " '$VM_NAME' Generating full URL for blob storage..."
    blob_url=$(az storage blob url \
        --account-name "$ACCOUNT_NAME" \
        --container-name "$CONTAINER_NAME" \
        --name "$FILE_NAME" \
        --output tsv 2>/dev/null)

    if [[ -z "$blob_url" ]]; then
        log "Error: Failed to generate blob URL for $FILE_NAME."
        return 1
    fi

    # Generate SAS token
    log " '$VM_NAME' Generating SAS token..."
    sas_token=$(az storage blob generate-sas \
        --account-name "$ACCOUNT_NAME" \
        --container-name "$CONTAINER_NAME" \
        --name "$FILE_NAME" \
        --permissions r \
        --expiry "$EXPIRY" \
        --output tsv 2>/dev/null)

    if [[ -z "$sas_token" ]]; then
        log "Error: Failed to generate SAS token for $FILE_NAME."
        return 1
    fi

    # Construct the full URL
    local full_url="${blob_url}?${sas_token}"
    log "Full URL generated: $full_url"

    # Run the Azure VM command
    log "Running command on VM: $VM_NAME in Resource Group: $RESOURCE_GROUP"
    az vm run-command invoke \
        --command-id RunPowerShellScript \
        --name "$VM_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --scripts "Invoke-WebRequest -Uri '${full_url}' -OutFile 'C:\\$FILE_NAME'; PowerShell -ExecutionPolicy Bypass -File 'C:\\$FILE_NAME'" \
        --output json > output.json 2>&1

    # Check for success or failure
    if [[ $? -eq 0 ]]; then
        log "File successfully copied and executed on VM."
    else
        log "Error: Failed to execute the script on the VM. Check the output.json file for details."
        return 1
    fi
}


run_sysprep() {
    local VM_NAME=$1
    local RESOURCE_GROUP=$2
    log "Running Sysprep on VM: $VM_NAME in Resource Group: $RESOURCE_GROUP"
    az vm run-command invoke \
    --command-id RunPowerShellScript \
    --name "$VM_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --scripts "powershell.exe -File C:\start-sysprep.ps1 -UnattendFile \"C:\\$UNATTEND_FILE\""


    if [[ $? -ne 0 ]]; then
        log "ERROR: Sysprep execution failed on the VM."
        return 1
    fi
    log "Sysprep executed successfully on the VM '$VM_NAME'"
    return 0
}


# Main function
main() {
    # Log the start of the script with the current date and time
    log "Post-VM Recovery Script started at: $(date '+%Y-%m-%d %H:%M:%S')"

    # Log the input JSON
    log "Input JSON: $1"

    # Parse the input JSON
    ParseJson "$1"

    # Extract recovered VM ID, name, and public IP
    local VM_NAME=$(echo "$INPUT_JSON" | jq -r '.name' | tr -d '`' | sed 's/null//g' | tr -d '\n')
    local target_ip=$(echo "$INPUT_JSON" | jq -r '.ips[0].publicIP' | tr -d '`' | sed 's/null//g' | tr -d '\n')

    check_vm_agent_status "$VM_NAME" "$RESOURCE_GROUP"

    # Exit only if the VM agent is not running
    if [ $? -ne 0 ]; then
      log "Exiting because the VM Agent is not running."
      exit 1
    fi
    # copy required files to VM
    run_copy_file "$VM_NAME" "$RESOURCE_GROUP" "$UNATTEND_FILE"
    run_copy_file "$VM_NAME" "$RESOURCE_GROUP" "$SYSPREP_FILE"
    run_copy_file "$VM_NAME" "$RESOURCE_GROUP" "$SYSPREP_ENABLE_RDP"

    # initiate the sysprep
    run_sysprep "$VM_NAME" "$RESOURCE_GROUP"
    # Sleep Added so that sysprep process started and plan post scripts can wait for agent to come up again
    sleep 240
    # Exit successfully
    exit 0
}

# Execute the main function with all passed arguments
main "$@"
