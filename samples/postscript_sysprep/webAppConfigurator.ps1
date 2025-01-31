Import-Module WebAdministration
 
# Function to set a descriptive name for the IIS server
# function Set-IISDescription {
#     param (
 
#             [string]$description
 
#     )
 
#     Path to the file where we store the IIS description
#     $configFilePath = "C:\inetpub\wwwroot\iis_description.txt"
#     Write the description to the file
#     Set-Content -Path $configFilePath -Value $description
 
# }
 
# Set the IIS server description
# $description = "INF-DR-w2k20"
# Set-IISDescription -description $description
 
 
# Set the application pool identity
# $appPoolName = "DefaultAppPool"    # The name of the application pool you want to change
# $username = "Pruadm"      # Replace with your actual domain and username
# $password = "Password12"             # Replace with your actual password
# Set-ItemProperty "IIS:\AppPools\$appPoolName" -Name processModel -Value @{userName=$username; password=$password; identitytype=3}
 
 
# Bind a certificate to the IIS site
# $siteName = "Default Web Site"         # The name of the site you're binding the certificate to
# $ipAddress = "0.0.0.0"                       # The IP address (use * for all IP addresses)
# $port = 443                            # The port number (443 is standard for HTTPS)
# $thumbprint = "d85e92f442af08c518ff6f54d794eca472748041"  # Replace with your certificate thumbprint
 
# Command to bind the certificate
# New-Item "IIS:\SslBindings\$ipAddress!$port" -Value $thumbprint -SslFlags 0
 
# Remove old SSL certificate binding
# Write-Host "Removing old SSL certificate binding..."
# netsh http delete sslcert ipport=$($ipAddress):$port
 
# Add new SSL certificate binding
# Write-Host "Adding new SSL certificate binding..."
# netsh http add sslcert ipport=$($ipAddress):$port certhash=$thumbprint appid=$appid
 
# Restart IIS
iisreset
 
 
# Restart another service
$serviceName = "W3SVC"  # Replace with the name of the service you want to restart
Restart-Service -Name $serviceName


#Application trigger commandr
cmd.exe /c 'C:\Windows\Scripts\FileRename_DR.cmd'
