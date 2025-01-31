# Define a log file
$LogFile = "C:\scripts_test\sysprep_log.txt"

# Define unattended file
$UnattendFile = "C:\scripts_test\answerFileWin2k19.xml"

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
    
    try {
        Start-Process -FilePath "C:\Windows\System32\Sysprep\sysprep.exe" -ArgumentList "/generalize /oobe /reboot /unattend:$UnattendFile" -Wait -ErrorAction Stop
        Write-Log "Sysprep process completed successfully."
    } catch {
        $ErrorMessage = "Sysprep process failed: $_"
        Write-Log $ErrorMessage
        Write-Error $ErrorMessage
    }
} else {
    $ErrorMessage = "Unattend file $UnattendFile not found."
    Write-Log $ErrorMessage
    Write-Error $ErrorMessage
}

# Log the end of the script
Write-Log "Sysprep script finished."