$DMLogDir = "C:\dm"

# Define the path to the text file
$filePath = "C:\dm\dm_output.txt"


if (!(Test-Path $DMLogDir)) {New-Item $DMLogDir -Type Directory}

if (!(Test-Path $filePath)) {New-Item $filePath -Type File}


# Define the new line to add
$newLine = "Setting VM san policy to OnlineAll."

# Add the new line to the file
Add-Content -Path $filePath -Value $newLine


function Set-SANPolicy-OnlineAll {
    try {
        $diskpartCommands = @"
san policy=OnlineAll
exit
"@

        $diskpartOutput = $diskpartCommands | diskpart
        Add-Content -Path $filePath "SAN policy set to OnlineAll. Diskpart output: $diskpartOutput"

        # Verify the change
        $verifyCommands = @"
san
exit
"@

        $verifyOutput = $verifyCommands | diskpart
        $verifyOutput = $verifyOutput -join "`n"  # Join the array into a single string

        if ($verifyOutput -match "SAN Policy\s*:\s*OnlineAll") {
            Add-Content -Path $filePath "SAN policy successfully verified as OnlineAll."
        } else {
            Add-Content -Path $filePath "Failed to verify SAN policy as OnlineAll."
        }
        # Get all disks that are currently offline and set them to online
        Get-Disk | Where-Object IsOffline -Eq $True | Set-Disk -IsOffline $False
	Get-Disk | Where-Object IsReadOnly -Eq $True | Set-Disk -IsReadOnly $False
    } catch {
        $errorMessage = "Error while setting SAN policy: $($_.Exception.Message)"
        $errorDetails = $_.InvocationInfo.PositionMessage
        $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $errorMessage`n$errorDetails`n"
        
        # Log the error to a file
        Add-Content -Path $logFile -Value $logEntry

        Write-Output $errorMessage
        Write-Output $errorDetails
        exit 1
    }
}

# Call the function to set the SAN policy
Set-SANPolicy-OnlineAll