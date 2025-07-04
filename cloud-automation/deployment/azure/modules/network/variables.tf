variable "client_id" {
  description = "Azure account client_id"
  type        = string
  default     = null
}
variable "client_secret" {
  description = "Azure account client_secret"
  type        = string
  default     = null
}
variable "subscription_id" {
  description = "Azure account subscription_id"
  type        = string
  default     = null
}
variable "tenant_id" {
  description = "Azure account tenant_id"
  type        = string
  default     = null
}
variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
  default     = null
}
variable "storage_account_name" {
  description = "Azure storage account name"
  type        = string
  default     = null
}
variable "location" {
  description = "Azure accont region"
  type        = string
  default     = null
}
variable "mgmt_security_group" {
  description = "Mgmt Security Group Name"
  type        = string
  default     = null
}
variable "prep_security_group" {
  description = "Repl Security Group Name"
  type        = string
  default     = null
}
variable "mgmt_vm_name" {
  description = "Mgmt Server Name"
  type        = string
  default     = null
}
variable "repl_vm_name" {
  description = "Repl Server Name"
  type        = string
  default     = null
}

variable "prep_vm_name" {
  description = "Prep Server Name"
  type        = string
  default     = null
}
variable "vnet_name" {
  description = "Vnet Name"
  type        = string
  default     = null
}
variable "vnet_address_space" {
  description = "CIDR Value for Vnet"
  type        = list(any)
  default     = null
}
variable "subnet_name" {
  description = "Subnet Name"
  type        = string
  default     = null
}
variable "subnet_address_space" {
  description = "CIDR Value for Subnet"
  type        = list(any)
  default     = null
}
variable "mgmt_vm_size" {
  description = "Mgmt Server VM Size"
  type        = string
  default     = null
}
variable "mgmt_user_name" {
  description = "Mgmt Server Admin User Name"
  type        = string
  default     = null
}
variable "mgmt_user_password" {
  description = "Mgmt Server Admin User Password"
  type        = string
  default     = null
}
variable "mgmt_image" {
  description = "Mgmt Server Image ID"
  type        = string
  default     = null
}
variable "repl_vm_size" {
  description = "Repl Node VM Size"
  type        = string
  default     = null
}
variable "repl_user_name" {
  description = "Repl Node Admin User Name"
  type        = string
  default     = null
}
variable "repl_user_password" {
  description = "Repl Node Admin User Password"
  type        = string
  default     = null
}
variable "repl_image" {
  description = "Repl Node Image ID"
  type        = string
  default     = null
}
variable "prep_vm_size" {
  description = "Prep Node VM Size"
  type        = string
  default     = null
}
variable "prep_user_name" {
  description = "Prep Node Admin User Name"
  type        = string
  default     = null
}
variable "prep_user_password" {
  description = "Prep Node Admin User Password"
  type        = string
  default     = null
}
variable "prep_image" {
  description = "Prep Node Image ID"
  type        = string
  default     = null
}
variable "mgmt_create_vm" {
  description = "Determines whether to create the VM"
  type        = bool
}
variable "repl_create_vm" {
  description = "Determines whether to create the VM"
  type        = bool
}
variable "prep_create_vm" {
  description = "Determines whether to create the VM"
  type        = bool
}
variable "repl_node_count" {
  description = "Repl node count"
  default     = null
}
variable "prep_node_count" {
  description = "Prep node count"
  default     = null
}
variable "mgmt_source_address_prefix" {
  description = "mgmt_nsg_source_cidr value"
  default     = null
}
variable "mgmt_destination_address_prefix" {
  description = "mgmt_nsg_destination_cidr value"
  default     = null
}
variable "prep_source_address_prefix" {
  description = "prep_nsg_source_cidr value"
  default     = null
}
variable "prep_destination_address_prefix" {
  description = "prep_nsg_destination_cidr value"
  default     = null
}
variable "mgmt_inbound_allowed_ports" {
  description = "List of allowed ports"
  type        = list(number)
  default     = null
}
variable "mgmt_outbound_allowed_ports" {
  description = "List of allowed ports"
  type        = list(number)
  default     = null
}
variable "prep_inbound_allowed_ports" {
  description = "List of allowed ports"
  type        = list(number)
  default     = null
}
variable "prep_outbound_allowed_ports" {
  description = "List of allowed ports"
  type        = list(number)
  default     = null
}
variable "mgmt_disable_password_authentication" {
  description = "Disable Password Authentication for Mgmt Server"
  default     = null
}
variable "repl_disable_password_authentication" {
  description = "Disable Password Authentication for Repl Node"
  default     = null
}
variable "prep_disable_password_authentication" {
  description = "Disable Password Authentication for Prep Node"
  default     = null
}
variable "mgmt_inbound_name" {
  description = "Mgmt Security Group Inbound Rule Name"
  default     = null
}
variable "mgmt_outbound_name" {
  description = "Mgmt Security Group Outbound Rule Name"
  default     = null
}
variable "prep_inbound_name" {
  description = "Prep Security Group Inbound Rule Name"
  default     = null
}
variable "prep_outbound_name" {
  description = "Prep Security Group Outbound Rule Name"
  default     = null
}
variable "storage_account_tier" {
  description = "Storage Account Tier"
  default     = null 
  type        = string
}

variable "storage_account_replication_type" {
  description = "Storage Account Replication Type"
  default     = null 
  type        = string
}

variable "image_gallery_name" {
  description = "Datamotive Image Gallery Name"
  default     = null 
  type        = string
}

variable "node_disk_type" {
  description = "Datamotive Node Disk Type"
  default     = null 
  type        = string
}

variable "storage_account_create" {
  description = "Determines whether to create the Storage Account"
  type        = bool
}

variable "security_group_create" {
  description = "Determines whether to create the Security Groups"
  type        = bool
}

variable "associate_public_ip" {
  description = "Determines whether to create and associate Public IP to nodes"
  type        = bool
}
