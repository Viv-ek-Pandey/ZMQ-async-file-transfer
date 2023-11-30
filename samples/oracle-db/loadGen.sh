#!/bin/bash

# Set Oracle environment variables
export ORACLE_HOME=
export ORACLE_SID=

# Credentials
USER=""
PASS=""

LOG_FILE="insert.log"
# Loop to insert data every 1 seconds
while true; do
    # SQL Command
    SQL_COMMAND=""

    echo $SQL_COMMAND | $ORACLE_HOME/bin/sqlplus -s $USER/$PASS
    # Check if the insert was successful
    if [ $? -eq 0 ]; then
        # Log timestamp to file
        echo "Record added at $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG_FILE
    else
        # Log failure (optional)
        echo "Failed to add record at $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG_FILE
    fi
    # Wait for 5 seconds
    sleep 1
done