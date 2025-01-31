
$DMLogDir = "C:\dm"

# Define the path to the text file
$filePath = "C:\dm\dm_output.txt"

$password = "Password@123" | ConvertTo-SecureString -asPlainText -Force
$username = "domainname\username"

if (!(Test-Path $DMLogDir)) {New-Item $DMLogDir -Type Directory} # Creating log directory
 
if (!(Test-Path $filePath)) {New-Item $filePath -Type File} # Creating log file

# Define the new line to add
$newLine = "Removing VM from AD."

# Add the new line to the file
Add-Content -Path $filePath -Value $newLine

Set-ExecutionPolicy Remotesigned

# $Password = ConvertTo-SecureString "Datamotive@123" -AsPlainText -Force
# $Credential = New-Object System.Management.Automation.PSCredential("dmtest\Administrator", $Password)


$credential = New-Object System.Management.Automation.PSCredential($username,$password)
Remove-Computer -UnjoinDomaincredential $credential -WorkgroupName "Local" -PassThru -Verbose -Restart -Force

