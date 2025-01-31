
$DMLogDir = "C:\dm"

# Define the path to the text file
$filePath = "C:\dm\dm_output.txt"

$password = "Password@123" | ConvertTo-SecureString -asPlainText -Force
$username = "domainname\username"
$domain = "domainname.com"


if (!(Test-Path $DMLogDir)) {New-Item $DMLogDir -Type Directory}

if (!(Test-Path $filePath)) {New-Item $filePath -Type File}


# Define the new line to add
$newLine = "Rejoining VM to AD again."

# Add the new line to the file
Add-Content -Path $filePath -Value $newLine

# Set-ExecutionPolicy Remotesigned

$credential = New-Object System.Management.Automation.PSCredential($username,$password)

#Command to join the domain without entering the password manually
Add-Computer -DomainName $domain -Credential $credential -Restart

# Commenting this so on failback we are able to execute ps scripts
# Set-ExecutionPolicy -Scope LocalMachine -ExecutionPolicy Restricted -Force

