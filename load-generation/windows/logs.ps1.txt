# Set log file path
$logFilePath = "C:\Logs\mylog.log"
$maxLogFileSizeMB = 10

# Function to generate log entries
function Generate-LogEntry {
    Param (
        [string]$logFilePath
    )
    # Create log entry with timestamp
    $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss.ffff') - This is a sample log entry."
    
    # Append log entry to the log file
    Add-Content -Path $logFilePath -Value $logEntry
}

# Function to check log file size and delete older logs if size exceeds 10 MB
function Manage-LogFiles {
    Param (
        [string]$logFilePath,
        [int]$maxFileSizeMB
    )
    # Check if log file exists
    if (Test-Path $logFilePath) {
        $fileSizeMB = (Get-Item $logFilePath).Length / 1MB
        # If log file size exceeds the limit, delete older logs
        if ($fileSizeMB -ge $maxFileSizeMB) {
            # Get files sorted by creation time
            $files = Get-ChildItem -Path (Split-Path $logFilePath) | Sort-Object CreationTime
            $totalSizeDeleted = 0
            foreach ($file in $files) {
                $totalSizeDeleted += $file.Length / 1MB
                Remove-Item -Path $file.FullName -Force
                # If total size deleted exceeds the limit, break the loop
                if ($totalSizeDeleted -ge $maxFileSizeMB) {
                    break
                }
            }
        }
    }
}

# Main loop to generate logs
while ($true) {
    # Generate log entry
    Generate-LogEntry -logFilePath $logFilePath
    # Check log file size and manage logs
    Manage-LogFiles -logFilePath $logFilePath -maxFileSizeMB $maxLogFileSizeMB
    # Wait for 1 millisecond before generating next log
    Start-Sleep -Milliseconds 1
}
