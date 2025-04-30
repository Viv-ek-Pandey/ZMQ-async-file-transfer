#!/bin/bash

# Datamotive Post-Replication Script
# Execution Level: VM
# =================================
# This script is invoked after creating a snapshot of a protected workload.
#
# @Parameters: Protected VM JSON
# {
#   "name": "<PROTECTED_VM_NAME>",
#   "sourceID": "<VM_ID>",
#   "ips": [
#     {
#       "publicIP": "<VM_IP>",
#       "privateIP": ""
#     }
#   ]
# }
# @Return: Exit codes indicating success or failure:
#     0 - Success
#     1 - Failure

# Define the log file path
LOG_FILE="/opt/dmservice/logs/VMReplication.log"

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

# Main function
main() {
    # Log the start of the script with the current date and time
    log "Post-VM Replication Script started at: $(date '+%Y-%m-%d %H:%M:%S')"

    # Log the input JSON
    log "Input JSON: $1"

    # Parse the input JSON
    ParseJson "$1"

    # Extract the source VM ID, name, and public IP
    local source_id=$(echo "$INPUT_JSON" | jq -r '.sourceID' | tr -d '`' | sed 's/null//g' | tr -d '\n')
    local source_name=$(echo "$INPUT_JSON" | jq -r '.name' | tr -d '`' | sed 's/null//g' | tr -d '\n')
    local source_ip=$(echo "$INPUT_JSON" | jq -r '.ips[0].publicIP' | tr -d '`' | sed 's/null//g' | tr -d '\n')

    # Log the extracted details
    log "Source ID: $source_id, Name: $source_name, IP: $source_ip"

    # Exit successfully
    exit 0
}

# Execute the main function with all passed arguments
main "$@"
