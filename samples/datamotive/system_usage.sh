#!/bin/bash
DATA_FILE="data.json"

initialize_file() {
    if [ ! -f "$DATA_FILE" ]; then
        # If file doesn't exist, create it and start a JSON array
        echo "[" > "$DATA_FILE"
    else
        # If file exists, remove the last character (closing bracket or comma)
        sed -i '$ s/,$//' "$DATA_FILE"
    fi
}

# Function to collect system usage data and append to JSON file
collect_data() {
    # Get average CPU usage across all cores
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')

    # Get memory usage as a percentage
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')

    # Get swap memory usage as a percentage
    SWAP_USAGE=$(free | grep Swap | awk '{if ($2 == 0) {print "0.00"} else {printf "%.2f", $3/$2 * 100.0}}')

    # Get the current timestamp
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    # Create JSON object with the collected data
    JSON_DATA=$(cat <<EOF
    {
        "timestamp": "$TIMESTAMP",
        "cpu_usage": $CPU_USAGE,
        "mem_usage": $MEM_USAGE,
        "swap_usage": $SWAP_USAGE
    }
EOF
    )
    echo "$JSON_DATA," >> "$DATA_FILE"
}

# Run the setup to prepare the file for appending
initialize_file

# Run the collection every 10 seconds
while true; do
    collect_data
    sleep 10
done
