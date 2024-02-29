#!/bin/bash

# Description: This script is used to quiesce an Oracle database remotely.
# It sets the necessary Oracle environment variables, calculates the time taken
# to put the database into a quiesced state, and runs any maintenance tasks that
# are commented out within the script.

# Instructions:
# 1. Update the REMOTE_HOST and REMOTE_USER variables with the remote server's host address and username.
# 2. Ensure that ORACLE_HOME and ORACLE_SID are set correctly for the Oracle environment.
# 3. Add any database maintenance tasks where commented within the SQL block.
# 4. Ensure SSH keys are set up for passwordless authentication or key based authentication.
# 5. Make sure the Oracle binaries are correctly referenced in the PATH variable.
# 6. Run this script from a bash shell with appropriate permissions.


# Remote server credentials
REMOTE_HOST=""
REMOTE_USER="grid"

# The script content
SCRIPT="
# Set Oracle environment variables
export ORACLE_HOME=/u01/app/oracle/product/19.0.0/db_1
export ORACLE_SID=orcl
export PATH=\$ORACLE_HOME/bin:\$PATH

# Start timing
start_time=\$(date +%s)

# Quiesce the database
echo 'Quiescing the database...'
/u01/app/oracle/product/19.0.0/db_1/bin/sqlplus / as sysdba << EOF
WHENEVER SQLERROR EXIT SQL.SQLCODE;
SET TIMING ON;
ALTER SYSTEM ENABLE RESTRICTED SESSION;
ALTER SYSTEM QUIESCE RESTRICTED;
-- Your maintenance tasks
EXIT;
EOF

# End timing
end_time=\$(date +%s)

# Calculate duration
duration=\$((end_time - start_time))

# Output results
echo \$duration
echo 'Database is now in quiesced state.'
"
# Now run the SCRIPT variable with ssh command
ssh ${REMOTE_USER}@${REMOTE_HOST} "bash -s" <<< "$SCRIPT"