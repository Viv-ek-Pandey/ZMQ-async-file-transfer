# Path to the input file
$inputFile = "C:\Scripts\DriveMapping.txt"

# Path to the log file
$logFile = "C:\Scripts\ReassignDriveLetters.log"

# Function to log messages to the log file
function Write-Log {
    param (
        [string]$Message
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp - $Message"
    $logEntry | Out-File -FilePath $logFile -Append
    Write-Output $logEntry
}

# Start logging
Write-Log "Script started."

# Verify if the input file exists
if (-Not (Test-Path $inputFile)) {
    Write-Log "Error: Input file ${inputFile} not found. Please generate it first."
    exit 1
}

# Read drive mappings from the input file
$driveMappings = Get-Content $inputFile | ForEach-Object {
    $line = $_ -split ","
    [PSCustomObject]@{
        VolumeId   = $line[0]
        DriveLetter = $line[1]
    }
}

# Log the drive mappings
Write-Log "Drive mappings loaded from ${inputFile}:"
$driveMappings | ForEach-Object { Write-Log "VolumeId: $($_.VolumeId), DriveLetter: $($_.DriveLetter)" }

# List of temporary letters to use in case of conflicts
$tempLetters = @("Z", "Y", "X", "W", "V", "U", "T", "S", "R", "Q")

# Function to find an available temporary letter
function Get-AvailableTempLetter {
    param (
        [array]$volumes,
        [array]$tempLetters
    )
    foreach ($letter in $tempLetters) {
        if (-Not ($volumes | Where-Object { $_.DriveLetter -eq $letter })) {
            return $letter
        }
    }
    return $null
}

# Reassign drive letters
foreach ($mapping in $driveMappings) {
    # Refresh the list of volumes at the start of each iteration
    $volumes = Get-Volume

    $volumeId = $mapping.VolumeId
    $desiredLetter = $mapping.DriveLetter

    # Find the target volume
    $volume = $volumes | Where-Object { $_.UniqueId -eq $volumeId }

    if ($volume) {
        # Check if the desired letter is already in use
        $conflictingVolume = $volumes | Where-Object { $_.DriveLetter -eq $desiredLetter }
        if ($conflictingVolume) {
            # Find an available temporary letter
            $tempLetter = Get-AvailableTempLetter -volumes $volumes -tempLetters $tempLetters

            if ($tempLetter) {
                Write-Log "Conflicting drive letter $desiredLetter in use by Volume ID $($conflictingVolume.UniqueId). Moving it to $tempLetter."
                Set-Partition -DriveLetter $conflictingVolume.DriveLetter -NewDriveLetter $tempLetter -Confirm:$false
                Write-Log "Conflicting volume moved to $tempLetter."
            } else {
                Write-Log "Error: No available temporary letters for conflicting volume with letter $desiredLetter. Skipping."
                continue
            }
        }

        # Assign the desired letter to the target volume
        Write-Log "Assigning $desiredLetter to Volume ID $volumeId."
        Set-Partition -DriveLetter $volume.DriveLetter -NewDriveLetter $desiredLetter -Confirm:$false
        Write-Log "Volume ID $volumeId successfully reassigned to $desiredLetter."
    } else {
        Write-Log "Warning: Volume with ID $volumeId not found. Skipping."
    }
}

# End logging
Write-Log "Script completed."
