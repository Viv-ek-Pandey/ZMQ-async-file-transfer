#!/bin/bash
LOG_DIR="/opt/dmservice"
LOG_FILE="$LOG_DIR/script_output.log"
 
# Function to log messages to both stdout and the log file
log() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a "$LOG_FILE"
}
 
# Apache machine's ssh details
Username="ubuntu"
PemKeyFile="/opt/dmservice/postscript/DM_mumbai_stg.pem"
# Source database virtual machine name
DatabaseMachineName="ubuntu-mysql"
# Source Apache virtual machine name
ApacheMachineName="ubuntu-apache"
# File location where ipv4 needs to be updated in Apache machine
SearchFilePath="/usr/java/apache-tomcat-8.5.78/webapps/todo-mvc/WEB-INF/classes/application.properties"
# source database machine ipv4, which needs be replaced with recoverd database machine private ipv4 address
SearchString="1.2.3.4"

# this variable used to store Parsed json received from DM workflow having recovery entity details
INPUT_JSON=""

# Execute command on Linux instance using SSH
# $1 : instance id
# $2 : instance ipv4 address
# $3 : command
ExecuteCommandOnLinux() {
    # Variable to store command outputs
    command_output=""
    log "Executing command on instance: $1 [$2]"
    ssh_command="ssh -o StrictHostKeyChecking=no -i $PemKeyFile $Username@$2"
    log "Target instance ssh string: $ssh_command"
    input_command=$3
    log "Input command to execute in target instance: $input_command"
    log "Executing command: $ssh_command \"$input_command\""
    sudo chmod 400 $PemKeyFile
    ssh -o StrictHostKeyChecking=no -i $PemKeyFile $Username@$2 "$input_command"
}
 
# $1 : json data received from recovery script
ParseJson() {
    all_args="$*"
    all_args_concatenated="${all_args// /}"
    log "Parsing input: $all_args_concatenated"
    INPUT_JSON=$(echo "$all_args_concatenated" | jq 'del(.status, .code, .message, .data)')
}
 
main() {
    # Parse json
    ParseJson $1
    NewIpAddress=""       # Database machine new IP address
    TargetInstanceID=""   # New target instance ID
    TargetInstanceIpv4="" # New Target instance public Ipv4 address
    for k in $(jq '.vms | keys | .[]' <<< "$INPUT_JSON"); do
        value=$(jq -r ".vms[$k]" <<< "$INPUT_JSON")
        name=$(jq -r '.name' <<< "$value")
        PrivateIP=$(jq -r '.ips[0].privateIP' <<< "$value")
        PublicIP=$(jq -r '.ips[0].publicIP' <<< "$value")
        TargetID=$(jq -r '.targetID' <<< "$value")
        if [ "$name" = "$DatabaseMachineName" ]; then
            NewIpAddress=$PrivateIP
            log "Virtual machine: $name --- Private IP address: $NewIpAddress"
        fi
        if [ "$name" = "$ApacheMachineName" ]; then
            TargetInstanceID=$TargetID
            TargetInstanceIpv4=$PublicIP
            log "Virtual machine: $name --- Instance ID: $TargetInstanceID"
        fi
    done
    # Execute command on the target instance
    ExecuteCommandOnLinux "$TargetInstanceID" "$TargetInstanceIpv4" "sudo sed -i 's/${SearchString}/${NewIpAddress}/g' ${SearchFilePath}"
}
 
# Entry point
main "$@"