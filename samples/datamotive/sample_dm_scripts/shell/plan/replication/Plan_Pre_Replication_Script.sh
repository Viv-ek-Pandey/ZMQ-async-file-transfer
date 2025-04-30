#!/bin/bash

# Datamotive Pre-Replication Script
# Execution Level: Protection Plan
# =================================
# This script is invoked before starting the replication process for any workload in the protection plan.
#
# @Parameters: JSON Array of Protected VMs
# {
#   "vms": [
#     {
#       "name": "<PROTECTED_VM_NAME>",
#       "sourceID": "<VM_ID>",
#       "ips": [
#         {
#           "publicIP": "<VM_IP>",
#           "privateIP": ""
#         }
#       ]
#     }
#   ]
# }
# @Return: Exit codes indicating success or failure:
#     0 - Success
#     1 - Failure

# Define the log file path
LOG_FILE="/opt/dmservice/logs/PlanReplication.log"

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
    INPUT_JSON=$(echo "$all_args_concatenated" | jq 'del(.status, .code, .message, .data)')
}

# Main function
main() {
    # Log the start of the script with the current date and time
    log "Pre-Plan Replication Script started at: $(date '+%Y-%m-%d %H:%M:%S')"

    # Log the input JSON
    log "Input JSON: $1"

    # Parse the input JSON
    ParseJson "$1"
    
    # Extract the source ID and public IP of the first VM in the list
    local source_id=$(echo "$INPUT_JSON" | jq -r '.vms[0].sourceID' | tr -d '`' | sed 's/null//g' | tr -d '\n')
    local source_ip=$(echo "$INPUT_JSON" | jq -r '.vms[0].ips[0].publicIP' | tr -d '`' | sed 's/null//g' | tr -d '\n')

    # Log the extracted details
    log "Source ID: $source_id, IP: $source_ip"

    # Exit successfully
    exit 0
}

# Execute the main function with all passed arguments
main "$@"
