#!/bin/bash
####################################################################################################
# README: Post Plan Enable NSG Rule and Join AD
#
# Overview:
# This Bash script automates the process of:
# 1. Removing a specific rule from an Azure Network Security Group (NSG).
# 2. Validating the Azure VM Agent's readiness on a specific Virtual Machine (VM).
# 3. Initiating an Active Directory (AD) join process for the VM.
#
# Input JSON Format:
# The script expects a JSON input with the following structure:
# {
#   "vms": [
#     {
#       "name": "<VM_NAME>",
#       "sourceID": "<SOURCE_ID>",
#       "targetID": "<RESOURCE_GROUP>:<VM_NAME>",
#       "ips": [
#         {
#           "publicIP": "<PUBLIC_IP>",
#           "privateIP": "<PRIVATE_IP>"
#         }
#       ],
#       "credentials": {
#         "username": "<USERNAME>",
#         "password": "<PASSWORD>"
#       }
#     }
#   ]
# }
#
# Example Input:
# {
#   "vms": [
#     {
#       "name": "VM-WIN-dm-test-drill-1234567890",
#       "sourceID": "example-source-id:vm-12345",
#       "targetID": "example-resource-group:VM-WIN-dm-test-drill-1234567890",
#       "ips": [
#         {
#           "publicIP": "74.225.159.186",
#           "privateIP": "10.0.0.8"
#         }
#       ],
#       "credentials": {
#         "username": "admin",
#         "password": "password123"
#       }
#     }
#   ]
# }
#
# Key Functions:
# 1. log: Logs messages to both stdout and a log file.
# 2. ParseJson: Parses JSON input and stores the result in the INPUT_JSON variable.
# 3. remove_rule: Removes a specific rule by name from an Azure NSG.
# 4. check_vm_agent_status: Checks the readiness of the Azure VM Agent on a specific VM.
# 5. joinAD: Executes a PowerShell script on the target VM to join it to Active Directory.
#
# Execution:
# Run the script as follows:
# ./VMRecovery.sh '<input_json>'
#
# Example Command:
# ./VMRecovery.sh '{"vms":[{"name":"VM-WIN-dm-test-drill-1234567890","sourceID":"example-source-id:vm-12345","targetID":"example-resource-group:VM-WIN-dm-test-drill-1234567890","ips":[{"publicIP":"74.225.159.186","privateIP":"10.0.0.8"}],"credentials":{"username":"admin","password":"password123"}}]}'
#
# Prerequisites:
# - Azure CLI: Install and authenticate using `az login`.
# - jq: Install using `sudo apt install jq -y`.
# - PowerShell Script: Ensure `C:\joinAD.ps1` exists on the target VM.
#
# Logs:
# All logs are written to `/opt/dmservice/logs/VMRecovery.log`.
####################################################################################################

# Log file path
LOG_FILE="/opt/dmservice/logs/VMRecovery.log"
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

# Function to remove a rule by name from the NSG
# $1: Resource Group, $2: NSG Name, $3: Rule Name
remove_rule() {
    local resource_group="$1"
    local nsg_name="$2"
    local rule_name="$3"

    log "Removing rule '$rule_name' from NSG $nsg_name..."

    az network nsg rule delete \
        --resource-group "$resource_group" \
        --nsg-name "$nsg_name" \
        --name "$rule_name" 2>>"$LOG_FILE"

    if [[ $? -eq 0 ]]; then
        log "Rule '$rule_name' removed successfully."
    else
        log "Failed to remove rule '$rule_name'."
    fi
}

# Function to check VM Agent status
check_vm_agent_status() {
    local VM_NAME=$1
    local RESOURCE_GROUP=$2
    local TIMEOUT=600 # 10 minutes in seconds
    local INTERVAL=30 # Check every 30 seconds
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

    echo "VM Agent did not come up within the timeout period ($TIMEOUT seconds)."
    return 1
}

# Function to join AD using Azure VM Agent
joinAD() {
    local resource_group="$1"
    local vm_name="$2"

    log "Starting Active Directory join process for VM: $vm_name in Resource Group: $resource_group..."

    # PowerShell script to be executed on the VM
    local script_path="C:\\joinAD.ps1"

    # Run the PowerShell script using Azure VM Agent
    az vm run-command invoke \
        --command-id RunPowerShellScript \
        --resource-group "$resource_group" \
        --name "$vm_name" \
        --scripts "$script_path" \
        --output json 2>>"$LOG_FILE" | jq '.' >>"$LOG_FILE"

    if [[ $? -eq 0 ]]; then
        log "Successfully initiated the AD join process on VM: $vm_name."
    else
        log "Failed to execute the AD join process on VM: $vm_name."
    fi
}

# Check VM Agent status for all VMs
check_all_vm_agents() {
    local resource_group="$1"
    local vms_count=$(echo "$INPUT_JSON" | jq -r '.vms | length')
    log "Checking VM Agent status for all $vms_count VMs..."

    for ((i = 0; i < vms_count; i++)); do
        # Extract the target ID for the current VM
        local TARGET_ID=$(echo "$INPUT_JSON" | jq -r ".vms[$i].targetID")
        # Extract the VM name from the target ID (split by colon and get the second part)
        local VM_NAME=$(echo "$TARGET_ID" | awk -F':' '{print $2}')
        log "Checking VM Agent status for VM $((i + 1))/$vms_count: $VM_NAME"

        # Check the VM Agent status
        check_vm_agent_status "$VM_NAME" "$resource_group"

        # Exit the function if any VM Agent is not running
        if [ $? -ne 0 ]; then
            log "VM Agent is not running for VM: $VM_NAME. Cannot proceed to AD join."
            return 1
        fi

        log "VM Agent is running for VM: $VM_NAME."
    done

    log "All VM Agents are online. Proceeding to AD join."
    return 0
}

# Join AD for all VMs
join_all_vms_to_ad() {
    local resource_group="$1"
    local vms_count=$(echo "$INPUT_JSON" | jq -r '.vms | length')
    log "Starting AD join process for all $vms_count VMs..."

    for ((i = 0; i < vms_count; i++)); do
        # Extract the target ID for the current VM
        local TARGET_ID=$(echo "$INPUT_JSON" | jq -r ".vms[$i].targetID")
        # Extract the VM name from the target ID (split by colon and get the second part)
        local VM_NAME=$(echo "$TARGET_ID" | awk -F':' '{print $2}')
        log "Joining VM $((i + 1))/$vms_count to AD: $VM_NAME"

        # Call the joinAD function
        joinAD "$resource_group" "$VM_NAME"

        # Check the result of the AD join operation
        if [ $? -eq 0 ]; then
            log "Successfully joined VM: $VM_NAME to the domain."
        else
            log "Failed to join VM: $VM_NAME to the domain."
        fi
    done

    log "Completed AD join process for all VMs."
}

# Main function to execute the script
main() {
    log "Script to remove rule execution started."

    # Define your parameters
    local resource_group="release-1.2.1"
    local nsg_name="vt-nsg-icici"
    local rule_name="DenySpecificIP"

    # Log the input JSON
    log "Input JSON: $1"
    # parse json
    ParseJson "$1"

    # Step 1: Check if all VM Agents are online
    check_all_vm_agents "$resource_group"
    if [ $? -ne 0 ]; then
        log "Exiting because not all VM Agents are online."
        exit 1
    fi
    remove_rule "$resource_group" "$nsg_name" "$rule_name"
    # added sleep to wait rule to take effect
    sleep 60
    # initiate Join AD
    join_all_vms_to_ad "$resource_group"

    log "Plan Recovery script process completed successfully."
}

# Execute the main function
main "$@"
