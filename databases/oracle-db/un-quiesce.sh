#!/bin/bash

# README
# Description: This script is used to remotely un-quiesce an Oracle database.
# It sets the necessary Oracle environment variables, reverses the database from a quiesced state,
# and disables restricted sessions. This operation is essential for maintenance tasks that require the database
# to be in an unquiesced state for normal operations to resume.

# Instructions:
# 1. Update the REMOTE_HOST and REMOTE_USER.
# 2. Ensure that ORACLE_HOME and ORACLE_SID are set correctly for the Oracle environment on the remote server.
# 3. Ensure that the SQL*Plus commands within the script are appropriate for your maintenance tasks.
# 4. Ensure SSH keys are set up for passwordless or key-based authentication to the remote server.
# 5. Confirm the Oracle binaries are correctly referenced in the PATH variable.
# 6. Execute this script from a bash shell with the necessary permissions to perform database operations.

# Remote server credentials
REMOTE_HOST=""
REMOTE_USER=""

# The script content
SCRIPT="
# Set Oracle environment variables
export ORACLE_HOME=/u01/app/oracle/product/19.0.0/db_1
export ORACLE_SID=orcl
export PATH=\$ORACLE_HOME/bin:\$PATH

# Quiesce the database
echo 'Quiescing the database...'
/u01/app/oracle/product/19.0.0/db_1/bin/sqlplus / as sysdba << EOF
WHENEVER SQLERROR EXIT SQL.SQLCODE;
SET TIMING ON;
ALTER SYSTEM UNQUIESCE;
ALTER SYSTEM DISABLE RESTRICTED SESSION;
EXIT;
EOF

# Check for errors
if [ \$? -ne 0 ]; then
    echo 'Failed to un-quiesce the database.'
    exit 1
fi

echo 'Database is now in unquiesced state.'
"

# Send the script to the remote server, execute it, and then delete it
ssh ${REMOTE_USER}@${REMOTE_HOST} "bash -s" <<< "$SCRIPT"