#!/bin/bash

# Datamotive Pre-Recovery Script
# Execution Level: VM
# =================================
# This script is invoked before VM recovery.
#
# @Parameters: Recovered VM JSON
# {
#   "name": "<PROTECTED_VM_NAME>",
#   "sourceID": "<SOURCE_VM_ID>",
#   "targetID": "<RECOVERED_VM_ID>",
#   "ips": [
#     {
#       "publicIP": "",
#       "privateIP": ""
#     }
#   ],
#   "credentials": {
#     "username": "",
#     "password": ""
#   }
# }
# @Return: Exit codes indicating success or failure:
#     0 - Success
#     1 - Failure

# Define the log file path
LOG_FILE="/opt/dmservice/logs/VMRecovery.log"

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
    INPUT_JSON=$(echo "$all_args_concatenated" | jq '.')
}

# Main function
main() {
    # Log the start of the script with the current date and time
    log "Pre-VM Recovery Script started at: $(date '+%Y-%m-%d %H:%M:%S')"

    # Log the input JSON
    log "Input JSON: $1"

    # Parse the input JSON
    ParseJson "$1"
    
    # Extract the source VM ID and name
    local source_id=$(echo "$INPUT_JSON" | jq -r '.sourceID' | tr -d '`' | sed 's/null//g' | tr -d '\n')
    local source_name=$(echo "$INPUT_JSON" | jq -r '.name' | tr -d '`' | sed 's/null//g' | tr -d '\n')

    # Log the extracted details
    log "Source ID: $source_id Name: $source_name"

    # Exit successfully
    exit 0
}

# Execute the main function with all passed arguments
main "$@"
