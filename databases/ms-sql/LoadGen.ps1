# prerequisite
# Create a database in MS-SQL, use BikeStore database
# Script is not diretly executable for execution follow below steps
#  1. Open SSMS
#  2. Connect DB
#  3. Right click on database and start powershell, provide the below powershell path
$fnames = @("John", "James", "Jane", "Joe", "Jim", "Bill")
$1names = @("McGraw", "Lincoln", "Washington", "Gates", "Clinton", "Ford")
$zips = 10 .. 99
$filePath = "G:\dbInsertLogs.txt"

while($true) {
$date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$count = $count + 1
$fname = Get-Random -InputObject $fnames
$lname = Get-Random -InputObject $1names
$zip = Get-Random -InputObject $zips
Invoke-SqlCmd -Query "INSERT INTO sales.customers (first_name, last_name, email, zip_code) VALUES ('$fname', '$lname', 'pat@dm.io', '$zip')"
if ($count -eq 2000) {
$count = 0

If ($count -eq 0) {
  $textToAppend = "Record Inserted at $date"
  # Check if the file exists
  If (Test-Path $filePath) {
      # File exists, append the text
      Add-Content -Path $filePath -Value $textToAppend
  } Else {
      # File does not exist, create it and append the text
      New-Item -Path $filePath -ItemType File -Force
      Add-Content -Path $filePath -Value $textToAppend
  }
}

Invoke-SqlCmd -Query "delete from sales.customers where email='pat@dm. io'"
}
}