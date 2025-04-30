param(
    [string]$UnattendFile
)

# Define a log file
$LogFile = "C:\sysprep_log.txt"

# Log a function to write to the log file
function Write-Log {
    param (
        [string]$Message
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "$Timestamp - $Message"
}

# Log the start of the script
Write-Log "Sysprep script started."

# Check if the unattend file exists
if (Test-Path $UnattendFile) {
    Write-Log "Unattend file found: $UnattendFile"
    Write-Log "Starting Sysprep process..."
    
    Start-Process -FilePath "C:\Windows\System32\Sysprep\Sysprep.exe" `
              -ArgumentList "/generalize /oobe /reboot /unattend:$UnattendFile"

    Write-Log "Sysprep process initiated successfully."
} else {
    $ErrorMessage = "Unattend file $UnattendFile not found."
    Write-Log $ErrorMessage
    Write-Error $ErrorMessage
}

# Log the end of the script
Write-Log "Sysprep script finished."
