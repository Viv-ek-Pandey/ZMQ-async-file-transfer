#!/bin/bash
####################################################################################################
# README: NSG Rule Management Script
#
# Overview:
# This Bash script automates the process of adding a deny rule to an Azure Network Security Group (NSG).
# The rule denies traffic from a specified IP address and port.
#
# Key Functions:
# 1. log: Logs messages to both stdout and a log file.
# 2. add_deny_rule: Adds a deny rule to an Azure NSG for a specific IP and port.
#
# Execution:
# Run the script as follows:
# ./NSGRuleManager.sh
#
# Variables:
# - Resource Group: Replace <RESOURCE_GROUP> with the name of your Azure resource group.
# - NSG Name: Replace <NSG_NAME> with the name of your Network Security Group.
# - Rule Name: Replace <RULE_NAME> with the name of the rule to be created.
# - IP Address: Replace <IP_ADDRESS> with the IP address to block.
# - Port: Replace <PORT> with the port number to block or "*" for all ports.
#
# Example Command:
# ./NSGRuleManager.sh
#
# Example Variables:
# - Resource Group: "rg-prod"
# - NSG Name: "vt-nsg-icici"
# - Rule Name: "DenySpecificIP"
# - IP Address: "192.99.222.65"
# - Port: "*"
#
# Logs:
# All logs are written to /opt/dmservice/logs/VMRecovery.log.
#
####################################################################################################

# Log file path
LOG_FILE="/opt/dmservice/logs/VMRecovery.log"

# Function to log messages to both stdout and the log file
log() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a "$LOG_FILE"
}

# Function to add rule for a specific port and IP in the NSG
# $1: Resource Group, $2: NSG Name, $3: Rule Name, $4: Port, $5: IP Address
add_deny_rule() {
    local resource_group="$1"
    local nsg_name="$2"
    local rule_name="$3"
    local port="$4"
    local ip_address="$5"

    log "Adding deny rule '$rule_name' for IP $ip_address on port $port in NSG $nsg_name..."
    # check set the highest priority before setting please check the security group
    az network nsg rule create \
        --resource-group "$resource_group" \
        --nsg-name "$nsg_name" \
        --name "$rule_name" \
        --priority 100 \
        --access Deny \
        --protocol Tcp \
        --direction Outbound \
        --source-address-prefixes "$ip_address" \
        --destination-port-ranges "$port" \
        --output json 2>>"$LOG_FILE" | jq '.' >>"$LOG_FILE"

    if [[ $? -eq 0 ]]; then
        log "Deny rule '$rule_name' added successfully."
    else
        log "Failed to add deny rule '$rule_name'."
    fi
}

# Main function to execute the script
main() {
    log "Script to add rule execution started."

    # Define your parameters
    local resource_group=""
    local nsg_name=""
    local rule_name="DenySpecificIP"
    local ip=""
    local port="*"

    add_deny_rule "$resource_group" "$nsg_name" "$rule_name" "$port" "$ip"

    log "Script to add rule execution completed."
}

# Execute the main function
main
