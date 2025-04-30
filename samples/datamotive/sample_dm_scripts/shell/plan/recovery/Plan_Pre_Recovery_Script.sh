#!/bin/bash

# Datamotive Pre-Recovery Script
# Execution Level: Protection Plan
# =================================
# This script is invoked before starting the recovery process for any workload.
#
# @Parameter: JSON Array of VMs selected for recovery
# {
#   "vms": [
#     {
#       "name": "<PROTECTED_VM_NAME>",
#       "sourceID": "<VM_ID>",
#       "targetID": "",
#       "ips": [
#         {
#           "publicIP": "",
#           "privateIP": ""
#         },
#         {
#           "publicIP": "",
#           "privateIP": ""
#         }
#       ],
#       "credentials": {
#         "username": "",
#         "password": ""
#       }
#     }
#   ]
# }
# @Parameter: Input parameters (if set during plan creation)
# @Return: Exit codes indicating success or failure:
#     0 - Success
#     1 - Failure

# Define the log file path
LOG_FILE="/opt/dmservice/logs/PlanRecovery.log"

# Variable to store the parsed JSON received from the DM workflow containing recovery entity details
INPUT_JSON=""

# Function to log messages to both stdout and the log file
log() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a "$LOG_FILE"
}

# Function to parse the JSON data received from the recovery script
# $1 : JSON data
ParseJson() {
    local all_args="$*"
    local all_args_concatenated="${all_args// /}"
    INPUT_JSON=$(echo "$all_args_concatenated" | jq 'del(.status, .code, .message, .data)')
}

# Main function
main() {
    # Log the start of the script with the current date and time
    log "Pre-Plan Recovery Script started at: $(date '+%Y-%m-%d %H:%M:%S')"

    # Log the input JSON
    log "Input JSON: $1"

    # Parse the input JSON
    ParseJson "$1"
    
    # Example: Extract source instance ID and name
    local source_id=$(echo "$INPUT_JSON" | jq -r '.vms[0].sourceID' | tr -d '`' | sed 's/null//g' | tr -d '\n')
    local source_name=$(echo "$INPUT_JSON" | jq -r '.vms[0].name' | tr -d '`' | sed 's/null//g' | tr -d '\n')

    # Log the extracted details
    log "Name: $source_name Source ID: $source_id"

    # Exit successfully
    exit 0
}

# Execute the main function with all passed arguments
main "$@"
