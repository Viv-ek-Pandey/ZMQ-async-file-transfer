# Hardcoded values
$dnsServer = "192.99.222.65"
$domainName = "dmlabs.local"
$domainUser = "dmlabs.local\Administrator"
$domainPassword = "Datamotive@123"

# Step 1: Configure DNS nameserver for the first NIC
Write-Host "Configuring DNS nameserver to $dnsServer..." -ForegroundColor Yellow
$firstNIC = Get-NetAdapter | Sort-Object ifIndex | Select-Object -First 1

if ($firstNIC) {
    Set-DnsClientServerAddress -InterfaceAlias $firstNIC.InterfaceAlias -ServerAddresses $dnsServer
    Write-Host "DNS nameserver set to $dnsServer for NIC: $($firstNIC.InterfaceAlias)" -ForegroundColor Green
} else {
    Write-Host "No network adapters found. Unable to configure DNS." -ForegroundColor Red
    exit 1
}

# Step 2: Join the domain
Write-Host "Joining the domain $domainName..." -ForegroundColor Yellow

# Create a credential object
$securePassword = ConvertTo-SecureString $domainPassword -AsPlainText -Force
$domainCredential = New-Object System.Management.Automation.PSCredential($domainUser, $securePassword)

try {
    Add-Computer -DomainName $domainName -Credential $domainCredential -Restart
    Write-Host "Successfully joined the domain $domainName. The system will now restart." -ForegroundColor Green
} catch {
    Write-Host "Failed to join the domain. Error: $_" -ForegroundColor Red
}
