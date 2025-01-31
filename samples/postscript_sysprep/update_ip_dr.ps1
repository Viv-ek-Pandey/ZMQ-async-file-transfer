$InterfaceAlias = "Ethernet0"  # Replace with the name of your network adapter
$NewIPAddress = "10.1.34.4"  # Replace with the desired IP address
$NewSubnetMask = "255.255.255.0"  # Replace with the desired subnet mask
$NewGateway = "10.1.34.1"  # Replace with the desired gateway
$NewDNSServers = "10.1.34.26,10.16.36.108"  # Replace with the desired DNS servers

# Calculate the prefix length from the subnet mask
$prefixLength = ($NewSubnetMask -split '\.').ForEach({ [Convert]::ToString([int]$_, 2).PadLeft(8, '0') }) -join '' -replace '0+$' | Measure-Object -Character | Select-Object -ExpandProperty Characters


$DMLogDir = "C:\dm"

# Define the path to the text file
$filePath = "C:\dm\dm_output.txt"

$password = "Datamotive@123" | ConvertTo-SecureString -asPlainText -Force
$username = "dmtest\Administrator"

if (!(Test-Path $DMLogDir)) {New-Item $DMLogDir -Type Directory} # Creating log directory
 
if (!(Test-Path $filePath)) {New-Item $filePath -Type File} # Creating log file

# Define the new line to add
$newLine = "Updating IP config for DR VM."

# Add the new line to the file
Add-Content -Path $filePath -Value $newLine

# Remove existing IP addresses
Get-NetIPAddress -InterfaceAlias $InterfaceAlias | Remove-NetIPAddress -Confirm:$false

# Remove existing DNS servers
Set-DnsClientServerAddress -InterfaceAlias $InterfaceAlias -ResetServerAddresses

# it ensures that the default gateway has a valid next hop address before attempting to remove it
# Without this check, you might attempt to remove a non-existent gateway, which could lead to errors
$gateway = (Get-NetIPConfiguration -InterfaceAlias $InterfaceAlias).IPv4DefaultGateway

if ($gateway -and $gateway.NextHop) {
    Remove-NetRoute -InterfaceAlias $InterfaceAlias -NextHop $gateway.NextHop -ErrorAction Stop -Confirm:$false
    Add-Content -Path $filePath -Value "Gateway $($gateway.NextHop) removed successfully."
} else {
    Add-Content -Path $filePath -Value "No gateway set for the adapter."
}

# Change the IP address
New-NetIPAddress -InterfaceAlias $InterfaceAlias -IPAddress $NewIPAddress -PrefixLength $prefixLength -DefaultGateway $NewGateway

# Set the DNS servers
Set-DnsClientServerAddress -InterfaceAlias $InterfaceAlias -ServerAddresses ($NewDNSServers -split ",")