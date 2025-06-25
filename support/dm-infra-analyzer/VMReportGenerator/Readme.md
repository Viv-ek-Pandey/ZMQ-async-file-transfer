A utility to generate VM reports for specified vCenter infrastructure. Supports both datacenter-wide and file specified VM's reporting. The output is a CSV file containing details about VMs.

VMReport.exe
All required flags: -vcenter -username -password AND either -dcname or -vmfilepath

Usage of VMReport.exe:
-vcenter string
  vCenter IP or hostname
-username string
  vCenter username
-password string
  vCenter password
-dcname string
  Datacenter name (Required if -vmfilepath not used)
-vmfilepath string
  Path to file containing VM names (one per line, Required if -dcname not used)
-process string
  Execution mode: 'sequential' or 'concurrent' (default "concurrent")
-goroutinecount string
  Number of goroutines for concurrent execution (default "10")
-out string
  Output folder path (default is current working directory)

## Utility Sample Run Command:

For Datacenter name as input
VMReport.exe -vcenter "198.2*#.1*9.75" -username "dv@vsphere.localname" -password "Datamotive@567" -dcname "dec-dv-dc"

optional fields -

- process "sequential" [Either "sequential" or "concurrent" , default "concurrent"]
- goroutinecount "12" [default "10"]
- out "D:\Datamotive\Internship\Week4\Output"

---

---

For VM File Path as input
VMReport.exe -vcenter "198.2*#.1*9.75" -username "dv@vsphere.localname" -password "Datamotive@567" -vmfilepath "vmList.txt"

optional fields -

- process "sequential" [Either "sequential" or "concurrent" , default "concurrent"]
- goroutinecount "12" [default "10"]
- out "D:\Datamotive\Internship\Week4\Output"

---

---

- Commands for local setup
  go mod init github.com/digvijay22/reportTask
  go get github.com/vmware/govmomi

- build commands
  go build -o VMReport.exe main.go
