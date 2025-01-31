# log file path
$LogFile = "C:\scripts_test\MonitorSysprep_log.txt"

# Function to write to the log file
function Write-Log {
    param (
        [string]$Message
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "$Timestamp - $Message"
}

# Function to check if sysprep is pending
function Is-SysprepPending {
    $registryPath = "HKLM:\SYSTEM\Setup"

    try {
        $setupState = Get-ItemProperty -Path $registryPath -Name "SystemSetupInProgress" -ErrorAction SilentlyContinue
        $setupPhase = Get-ItemProperty -Path $registryPath -Name "SetupPhase" -ErrorAction SilentlyContinue

        if ($setupState.SystemSetupInProgress -eq 1 -or ($setupPhase -and $setupPhase.SetupPhase -ne 0)) {
        Write-Log "Sysprep registry keys set"
            return $true
        }
    } catch {
        Write-Log "Unable to access the registry to check sysprep state. Ensure you have appropriate permissions."
    }

    $sysprepProcess = Get-Process -Name "sysprep" -ErrorAction SilentlyContinue
    if ($sysprepProcess) {
    Write-Log "Sysprep process running"
        return $true
    }
    Write-Log "Sysprep process is not running"
    return $false
}

# Path to mark completion
$completionMarker = "C:\scripts_test\SysprepComplete.txt"

# Check if sysprep is complete
if (-not (Test-Path $completionMarker)) {
    Write-Log "Checking for sysprep pending state..."

    while (Is-SysprepPending) {
        Write-Log "Sysprep is in progress. Waiting for 30 seconds..."
        Start-Sleep -Seconds 30
    }

    # Create completion marker
    New-Item -ItemType File -Path $completionMarker -Force | Out-Null
    Write-Log "Sysprep process is complete."
} else {
   Write-Log "Sysprep already completed. Exiting."
}

# Cleanup scheduled task if it exists
$taskName = "MonitorSysprep"
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}
Remove-Item -Path "C:\SysprepComplete.txt"