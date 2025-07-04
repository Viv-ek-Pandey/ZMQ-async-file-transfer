variable "region" {
  description = "AWS region"
  default     = null
}
variable "availability_zone" {
  description = "Availability Zone"
  default     = null
}
variable "access_key" {
  description = "AWS Access Key"
  default     = null
}
variable "secret_key" {
  description = "AWS Secret Key"
  default     = null
}
variable "iam_user" {
  description = "IAM User Name"
  default     = null
}
variable "iam_policy" {
  description = "IAM Policy Name"
  default     = null
}
variable "vpc_id" {
  description = "VPC ID"
  default     = null
}
variable "mgmt_security_group_name" {
  description = "Security Group 1 Name "
  default     = null
}
variable "repl_security_group_name" {
  description = "Security Group 2 Name "
  default     = null
}

variable "prep_security_group_name" {
  description = "Security Group 4 Name "
  default     = null
}
variable "mgmt_server_ami" {
  description = "VM-1 ami ID"
  default     = null
}
variable "repl_node_ami" {
  description = "VM-2 ami ID"
  default     = null
}

variable "prep_node_ami" {
  description = "VM-4 ami ID"
  default     = null
}
variable "mgmt_instance_type" {
  description = "VM-1 Instance Type"
  default     = null
}
variable "repl_instance_type" {
  description = "VM-2 Instance Type"
  default     = null
}

variable "prep_instance_type" {
  description = "VM-4 Instance Type"
  default     = null
}
variable "subnet_id" {
  description = "Subnet ID"
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
variable "mgmt_security_group_cidr" {
  description = "security_group_1_cidr value"
  default     = null
  type        = list(any)
}
variable "repl_security_group_cidr" {
  description = "security_group_2_cidr value"
  default     = null
  type        = list(any)
}

variable "prep_security_group_cidr" {
  description = "security_group_4_cidr value"
  default     = null
  type        = list(any)
}
variable "associate_public_ip_address" {
  description = "associate_public_ip_address"
  default     = null
}
variable "mgmt_create_instance" {
  description = "Determines whether to create the EC2 instance"
  type        = bool
}
variable "repl_create_instance" {
  description = "Determines whether to create the EC2 instance"
  type        = bool
}
variable "prep_create_instance" {
  description = "Determines whether to create the EC2 instance"
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
variable "iam_create" {
  description = "Determines whether to create the IAM User and Policy"
  default     = null
}
variable "security_group_create" {
  description = "Determines whether to create the Security Groups"
  default     = null
}

variable "ssh_key_name" {
  description = "Node SSH Key Pair Name"
  default     = null
}