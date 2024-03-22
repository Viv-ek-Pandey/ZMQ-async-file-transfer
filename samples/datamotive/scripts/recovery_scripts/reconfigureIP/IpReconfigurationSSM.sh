#!/bin/bash
LOG_DIR="/opt/dmservice"
LOG_FILE="$LOG_DIR/script_output.log"
 
# Function to log messages to both stdout and the log file
log()
{
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a "$LOG_FILE"
}
 
 
# this variable used to store Parsed json received from DM workflow having recovery entity details
INPUT_JSON=""
# IAM role name provided by user with which need to attach policy
IAM_ROLE_NAME="aws-ssm-2"
# Region where your instance is located
REGION="ap-south-2"
 
# Virtual machine name whose Ipv4 needs to be updated on Target virtual machine
SourceVM="ubuntu-mysql"
# Virtual machine name where the IPv4 address needs to be updated
TargetVM="ubuntu-apache"
# Search string in the file
SearchString="x.x.x.x"
#
FilePath=/usr/java/apache-tomcat-8.5.78/webapps/todo-mvc/WEB-INF/classes/application.properties
 
 
# Variable to store command outputs
COMMAND_OUTPUT=""
 
 
# Execute command on linux instance using ssm
# $1 : instace_id
# $2 : commands
# $3 : region
ExecuteCommandOnLinux()
{
    log "$1 $2 $3"
    command_id=$(aws ssm send-command --targets "Key=instanceids,Values=$1" --document-name "AWS-RunShellScript" \
    --parameters "commands=[\"$2\"]" --region "$3" \
    --query "Command.CommandId" --output text)
 
    # Wait for command to complete, using command_id to monitor the command execution
    aws ssm wait command-executed --instance-id "$1" --command-id "$command_id" --region "$3"
 
    # Get the command execution results
    output=$(aws ssm get-command-invocation --instance-id "$1" --command-id "$command_id" \
    --region "$3" --query "StandardOutputContent" --output text)
 
    log "Command output: $output"
    COMMAND_OUTPUT="$output"
}
 
 
# $1 : json data received from recovery script
ParseJson()
{
   all_args="$*"
   all_args_concatenated="${all_args// /}"
   log "parsing input $all_args_concatenated"
   INPUT_JSON=$(echo "$all_args_concatenated" | jq 'del(.status, .code, .message, .data)')
}
 
# Attch IAM role to EC2 instance
# $1 : TargetInstanceID
# $2 : IAM_ROLE_NAME
AttachProfile()
{
    TargetInstanceID="$1"
    aws ec2 associate-iam-instance-profile --instance-id "$TargetInstanceID" --iam-instance-profile Name="$2"
        if [ $? -eq 0 ]; then
            log "IAM Role $IAM_ROLE_NAME attached to EC2 instance $TargetInstanceID."
            log "AWS Profile is attached run command on the recovered instance"
        else
            log "Error: Unable to attach IAM Role to EC2 instance."
        fi
}
 
main()
{
    # USAGE:
    # Call this script with following params
    # ./ssm_ops <entity-input-Json> <IAM-ROLE-NAME> <REGION>
    # Parse json
    ParseJson $1
    NewIpAddress=""       # source VM recoved machine IP
    TargetInstanceID=""   # target instance id where IP needs to be updated
    for k in $(jq '.vms | keys | .[]' <<< "$INPUT_JSON"); do
        value=$(jq -r ".vms[$k]" <<< "$INPUT_JSON");
        name=$(jq -r '.name' <<< "$value");
        PrivateIP=$(jq -r '.ips[0].privateIP' <<< "$value");
        TargetID=$(jq -r '.targetID' <<< "$value");
        if [ "$name" = "$SourceVM" ]
        then {
            NewIpAddress=$PrivateIP
            log "virtual machine: $name --- private ip address: $NewIpAddress"
        }
        fi
        if [ "$name" = "$TargetVM" ]
        then {
            TargetInstanceID=$TargetID
            log "virtual machine: $name --- instance ID: $TargetInstanceID"
        }
        fi
    done
 
    command='sudo sed -i 's/${SearchString}/${NewIpAddress}/g' '
    command+=$FilePath
    # Attach Profile
    AttachProfile $TargetInstanceID $IAM_ROLE_NAME $REGION
    aws ec2 reboot-instances --instance-ids $TargetInstanceID
    log "waiting instance to get reboot..."
    sleep 180
    log "instance rebooted successfully..."
    log "executing command - [$command]"
    ExecuteCommandOnLinux "$TargetInstanceID" "$command" "$REGION"
}
main $@