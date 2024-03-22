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
IAM_ROLE_NAME=$2
# Region where your instance is located
REGION=$3
# Variable to store command outputs
COMMAND_OUTPUT=""

# Execute command on linux instance using ssm
# $1 : instace_id
# $2 : commands
# $3 : region
ExecuteCommandOnLinux()
{
    echo $1 $2 $3
    command_id=$(aws ssm send-command --instance-ids "$1" --document-name "AWS-RunShellScript" \
    --comment "Run custom command" --parameters commands=["$2"] --region "$3" \
    --query "Command.CommandId" --output text)
  
    # Wait for command to complete, used command_id to monitor the command execution
    aws ssm wait command-executed --instance-id "$1" --command-id "$command_id" --region "$3"
  
    # Get the command execution results
    output=$(aws ssm get-command-invocation --instance-id "$1" --command-id "$command_id" \
    --region "$REGION" --query "StandardOutputContent" --output text)
  
    echo "Command output:" $output
    COMMAND_OUTPUT=$output
}

# Execute command on windows instance using ssm
# $1 : instace_id
# $2 : commands
# $3 : region
ExecuteCommandOnWindows()
{
    # Start SSM session with the instance
    log "Starting SSM session with EC2 instance $1..."

    echo "Write-Output 'SSM Session Started'"
    output=$(aws ssm send-command \
        --instance-ids "$1" \
        --document-name "AWS-RunPowerShellScript" \
        --comment "Execute custom command" \
        --parameters "{\"commands\":[\"$2\"]}" \
        --region "$3" \
        --query "Command.CommandId" \
        --output text)

    # Wait for the command to complete
    aws ssm wait command-executed --instance-id "$1" --command-id "$output" --region "$3"

    # Get the command execution results
    output=$(aws ssm get-command-invocation \
        --instance-id "$1" \
        --command-id "$output" \
        --region "$3" \
        --query "StandardOutputContent" \
        --output text)

    log "Command output:" $output
    echo "$output" | tee -a "$LOG_FILE"

    # End the SSM session
    log "Ending SSM session with EC2 instance $INSTANCE_ID..."
    echo "Write-Output 'SSM Session Ended'"
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
# $1 : target_id
# $2 : IAM_ROLE_NAME
AttachProfile()
{
    target_id="$1"
    aws ec2 associate-iam-instance-profile --instance-id "$target_id" --iam-instance-profile Name="$2"
        if [ $? -eq 0 ]; then
            log "IAM Role $IAM_ROLE_NAME attached to EC2 instance $target_id."
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
    # Get target instance id [Plan Level]
    target_id=$(echo "$INPUT_JSON" | jq -r '.vms[0].targetID' | tr -d '`' | sed 's/null//g' | tr -d '\n')
    
    # Get target instance id [VM Level]
    #target_id=$(echo "$INPUT_JSON" | jq -r '.targetID' | tr -d '`' | sed 's/null//g' | tr -d '\n')
    log "targetID $target_id"

    # Attach Profile
    AttachProfile $target_id $IAM_ROLE_NAME $REGION
    aws ec2 reboot-instances --instance-ids $target_id
    # Note if post role attachment it may take some time to ssm agents to accept the connection
    # For Linux;
    #     ExecuteCommandOnLinux  "$target_id" "cat /etc/os-release" "$REGION" 
    # For Windows;
    #     ExecuteCommandOnWindows  "$target_id" "Get-Process" "$REGION"
    sleep 120
    ExecuteCommandOnLinux "$target_id" "cat /etc/os-release" "$REGION" 
    #ExecuteCommandOnWindows "$target_id" "Get-Process" "$REGION"
}
main $@