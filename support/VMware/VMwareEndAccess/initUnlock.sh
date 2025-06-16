#!/bin/bash

# Check for required arguments
if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <vcenter> <username> <password> <vm_moref>"
  exit 1
fi

VCENTER="$1"
USERNAME="$2"
PASSWORD="$3"
VM_MOREF="$4"

# Path to VDDK libraries
VDDK_LIB_PATH="/usr/local/lib:/opt/dmservice/vmware_lib/lib64/"

# Set LD_LIBRARY_PATH
export LD_LIBRARY_PATH="${VDDK_LIB_PATH}:${LD_LIBRARY_PATH}"

# Create log file with timestamp and vm_moref in name
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/${VM_MOREF}_${TIMESTAMP}.log"

# Path to the compiled C binary
BINARY="${SCRIPT_DIR}/unlocker"

# Run the program and redirect stdout and stderr to log file
"${BINARY}" "${VCENTER}" "${USERNAME}" "${PASSWORD}" "${VM_MOREF}" > "${LOG_FILE}" 2>&1

# Show log file path
echo "Execution complete."


