# Import the WebAdministration module for IIS management
Import-Module WebAdministration

# Define a log file
$LogFile = "C:\scripts_test\IISWebBindings_log.txt"

# Log a function to write to the log file
function Write-Log {
    param (
        [string]$Message
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "$Timestamp - $Message"
}

# Variables
$SiteName = "Default Web Site"
$OldHostHeader = "old.example.com"
$NewHostHeader = "new.example.com"
$OldIPAddress = "192.99.222.73"
$NewIPAddress = "192.99.222.72"
$Port = 443
$Protocol = "https"

try {
    $binding = Get-WebBinding -Name $SiteName | Where-Object {
        $_.protocol -eq $Protocol
    }

    if ($binding) {
        # Retrieve the SSL certificate thumbprint
        $sslBindingPath = "$OldIPAddress!$Port"
        $newSSLBindingPath = "$NewIPAddress!$Port"

        $thumbprint = (Get-Item -Path "IIS:\SslBindings\$sslBindingPath").Thumbprint
        if ($thumbprint) {
            Write-Log "SSL Certificate Thumbprint: $thumbprint"

            # Remove the old binding
            Remove-WebBinding -Name $SiteName -IPAddress $OldIPAddress -Port $Port -Protocol $Protocol -HostHeader $OldHostHeader
            Write-Log "Old binding removed: '$OldIPAddress':'$Port':'$OldHostHeader'"

            # Add the new binding
            New-WebBinding -Name $SiteName -IPAddress $NewIPAddress -Port $Port -Protocol $Protocol -HostHeader $NewHostHeader
            Write-Log "New binding created: '$NewIPAddress':'$Port':'$NewHostHeader'"

            # Ensure the certificate exists in the Personal Store
            $certificate = Get-ChildItem -Path Cert:\LocalMachine\My | Where-Object { $_.Thumbprint -eq $thumbprint }

            if ($certificate) {
                # Apply the certificate to the SSL binding
                Push-Location IIS:\SslBindings
                New-Item -Path $newSSLBindingPath -Thumbprint $thumbprint
                Pop-Location
                Write-Log "SSL Certificate successfully applied to $newSSLBindingPath."
            } else {
            Write-Log "Certificate with thumbprint $thumbprint not found in the Personal store."
            }
        } else {
            Write-Log "No SSL certificate found for the binding."
        }
    } else {
        Write-Log "Binding not found: '$OldIPAddress':'$Port':'$OldHostHeader'"
    }
} catch {
    Write-Log "Error setting SSL Bindings: $_" 
}
