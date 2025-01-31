
$DMLogDir = "C:\dm"

# Define the path to the text file
$filePath = "C:\dm\dm_output.txt"

if (!(Test-Path $DMLogDir)) {New-Item $DMLogDir -Type Directory}

if (!(Test-Path $filePath)) {New-Item $filePath -Type File}

# Define the new line to add
$newLine = "Renaming hostname for VM."

# Add the new line to the file
Add-Content -Path $filePath -Value $newLine

Rename-Computer "New-Hostname" -Restart
