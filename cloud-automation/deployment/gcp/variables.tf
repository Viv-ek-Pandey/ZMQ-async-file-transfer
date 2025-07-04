variable "region" {
  description = "Region"
  default     = null
}
variable "account_id" {
  description = "GCP Account ID"
  default     = null
}
variable "display_name" {
  description = "Service Account Name"
  default     = null
}
variable "role_id" {
  description = "Role Name"
  default     = null
}
variable "project" {
  description = "Gcp project ID"
  default     = null
}
variable "title" {
  description = "Custom Role Title"
  default     = null
}
variable "network" {
  description = "VPC Name"
  default     = null
}
variable "mgmt_firewall_tag_name" {
  description = "Management Firewall tag Name"
  default     = null
  type        = list(any)
}
variable "mgmt_firewall_ingress_name" {
  description = "Management ingress rule Name"
  default     = null
}
variable "mgmt_firewall_egress_name" {
  description = "Management egress rule Name"
  default     = null
}
variable "prep_firewall_tag_name" {
  description = "Prep Node Firewall tag  Name"
  default     = null
  type        = list(any)
}
variable "prep_firewall_ingress_name" {
  description = "Prep node ingress rule Name"
  default     = null
}
variable "prep_firewall_egress_name" {
  description = "Prep node egress rule Name"
  default     = null
}
variable "mgmt_server_name" {
  description = "VM-1 Name"
  default     = null
}
variable "repl_node_name" {
  description = "VM-2 Name"
  default     = null
}

variable "prep_node_name" {
  description = "VM-4 Name"
  default     = null
}
variable "mgmt_server_type" {
  description = "VM-1 Instance Type"
  default     = null
}
variable "repl_node_type" {
  description = "VM-2 Instance Type"
  default     = null
}

variable "prep_node_type" {
  description = "VM-4 Instance Type"
  default     = null
}
variable "mgmt_server_zone" {
  description = "VM-1 Availability Zone"
  default     = null
}
variable "repl_node_zone" {
  description = "VM-2 Availability Zone"
  default     = null
}

variable "prep_node_zone" {
  description = "VM-4 Availability Zone"
  default     = null
}
variable "subnet" {
  description = "Subnet ID"
  default     = null
}
variable "mgmt_server_image" {
  description = "VM-1 Image ID"
  default     = null
}
variable "repl_node_image" {
  description = "VM-2 Image ID"
  default     = null
}

variable "prep_node_image" {
  description = "VM-4 Image ID"
  default     = null
}
variable "ssh_keys" {
  description = "SSH Keys"
  default     = null
}
variable "repl_node_count" {
  description = "Repl node count"
  default     = null
}
variable "prep_node_count" {
  description = "Prep node count"
  default     = null
}
variable "create_pre_req" {
  description = "Determines whether to create the Pre requisite"
  type        = bool
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
variable "mgmt_firewall_source_range" {
  description = "mgmt_firewall_source_cidr value"
  default     = null
  type        = list(any)
}
variable "repl_firewall_source_range" {
  description = "repl_firewall_source_cidr value"
  default     = null
  type        = list(any)
}

variable "prep_firewall_source_range" {
  description = "prep_firewall_source_cidr value"
  default     = null
  type        = list(any)
}
variable "mgmt_firewall_destination_range" {
  description = "mgmt_firewall_source_cidr value"
  default     = null
  type        = list(any)
}
variable "repl_firewall_destination_range" {
  description = "repl_firewall_source_cidr value"
  default     = null
  type        = list(any)
}
variable "prep_firewall_destination_range" {
  description = "prep_firewall_source_cidr value"
  default     = null
  type        = list(any)
}
variable "associate_public_ip" {
  description = "Determines whether to attach dynamic public IP to the VM"
  type        = bool
}