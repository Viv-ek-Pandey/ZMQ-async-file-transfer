variable "vsphere_server" {
  description = "vSphere vCenter Server Hostname/IP Address"
  default     = null
}
variable "vsphere_username" {
  description = "User name for vCenter Server user. User must have privileges to deploy and configure OVA in required location within the vSphere infrastructure."
  default     = null
}
variable "vsphere_password" {
  description = "Password of the vCenter Server user."
  default     = null
}
variable "datacenter_name" {
  description = "Name of vSphere Datacenter to deploy the Datamotive Management Console VM."
  default     = null
}
variable "datastore_name" {
  description = "Name of vSphere Datastore to deploy the Datamotive Management Console VM."
  default     = null
}
variable "compute_cluster_name" {
  description = "Name of vSphere Compute Cluster to deploy the Datamotive Management Console VM."
  default     = null
}
variable "esxi_host_name" {
  description = "Name of vSphere ESXi Host to deploy the Datamotive Management Console VM."
  default     = null
}
variable "network_name" {
  description = "Name of vSphere Network to deploy the Datamotive Management Console VM."
  default     = null
}
variable "mgmt_create_from_repository" {
  description = "Determines whether to create the virtual machine from OVA in remote repository"
  type        = bool
  default     = true
}
variable "mgmt_server_name" {
  description = "datamotive-management-console"
  default     = null
}
variable "mgmt_server_ova" {
  description = "VM-1 ami ID"
  default     = null
}
variable "repl_create_instance" {
  description = "Determines whether to create the virtual machine"
  type        = bool
  default	  = false
}
variable "repl_node_count" {
  description = "Repl node count"
  default     = null
}
variable "repl_node_name" {
  description = "VM-2 Name"
  default     = null
}
variable "repl_node_ova" {
  description = "VM-2 ami ID"
  default     = null
}

variable "prep_create_instance" {
  description = "Determines whether to create the virtual machine"
  type        = bool
  default	  = false
}
variable "prep_node_count" {
  description = "Prep node count"
  default     = null
}
variable "prep_node_name" {
  description = "VM-4 Name"
  default     = null
}
variable "prep_node_ova" {
  description = "VM-4 ami ID"
  default     = null
}