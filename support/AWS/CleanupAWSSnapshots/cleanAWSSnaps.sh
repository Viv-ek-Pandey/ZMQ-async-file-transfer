#!/bin/bash

# Cleans up AWS snapshots for the provided instance names from the cloud using AWS CLI

# Update the VM names as required
INSTANCE_NAMES=("KNA-SQL001" "KNA-SQL04" "KIM-EDI01")

# Loop through each instance ID
for INSTANCE_NAME in "${INSTANCE_NAMES[@]}"; do
    echo "Processing for instance: $INSTANCE_NAME"

    # Fetch all snapshots with matching prefix
    ALL_SNAPSHOTS=$(aws ec2 describe-snapshots \
        --filters "Name=tag:Name,Values=$INSTANCE_NAME*" \
        --query "Snapshots[].SnapshotId" \
        --output text)

    # Check if any completed snapshots were found
    if [[ -n "$ALL_SNAPSHOTS" ]]; then
        for SNAPSHOT_ID in $ALL_SNAPSHOTS; do
            aws ec2 delete-snapshot --snapshot-id "$SNAPSHOT_ID"
        done
    fi
	
	echo "Processing completed for instance: $INSTANCE_NAME"
done

