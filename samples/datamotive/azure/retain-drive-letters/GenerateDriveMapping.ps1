# Path to the output file
$outputFile = "C:\Scripts\DriveMapping.txt"

# Ensure the output directory exists
$directory = Split-Path -Path $outputFile
if (-Not (Test-Path $directory)) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}

# Get all volumes, filter those with drive letters, skip C, and sort by ascending drive letters
$volumes = Get-Volume | Where-Object { $_.DriveLetter -ne $null -and $_.DriveLetter -ne "C" } | Sort-Object DriveLetter

Write-Output "Generating Drive Mapping..."
$output = @()

foreach ($volume in $volumes) {
    # Extract the raw Volume ID and Drive Letter
    $output += "$($volume.UniqueId),$($volume.DriveLetter)"
}

# Save to the file
$output | Set-Content -Path $outputFile
Write-Output "Drive Mapping saved to $outputFile"