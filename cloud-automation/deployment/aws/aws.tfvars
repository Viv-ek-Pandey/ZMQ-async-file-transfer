# AWS Region where the Datamotive nodes will be deployed.
region                      = "us-east-2"
availability_zone           = "us-east-2a"

# Credentials of AWS IAM User which will be used for creating the infrastructure
access_key                  = "AKIARWF3J3WPEC4W7QRL"
secret_key                  = "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"

# IAM User & Policy names which will be used by Datamotive solution
iam_user                    = "DM-User"
iam_policy                  = "DM-Policy"

# Flag to indicate if IAM User and Policy needs to be created
iam_create                  = "true"

# ID of VPC & Subnet where the Datamotive nodes will be deployed.
vpc_id                      = "vpc-1be26170"
subnet_id                   = "subnet-9027c6ed"

# Flag to indicate if Security group needs to be created 
security_group_create = "true"

# Flag to indicate if deployed nodes should have public ip or not.
associate_public_ip_address = "true"

# Datamotive management node properties. Specify the ami id as shared by Datamotive. Modify other fields with caution.
mgmt_create_instance        = "true"
mgmt_server_ami             = "ami-01c26149a28db34b5"
mgmt_server_name            = "terraform-dm-mgmt-server-6April"
mgmt_instance_type          = "t2.micro"
mgmt_security_group_name    = "DM-Mgmt-SG"
mgmt_security_group_cidr    = ["0.0.0.0/0"]

# Datamotive replication node properties. Specify the ami id as shared by Datamotive & count for the number of nodes you want to deploy. Modify other fields with caution.
repl_create_instance        = "true"
repl_node_ami               = "ami-023cfbd4687387ed5"
repl_node_count             = "1"
repl_node_name              = "6April-dm-repl-node-tf"
repl_instance_type          = "t2.micro"
repl_security_group_cidr    = ["0.0.0.0/0"]

# Datamotive windows prep node properties. Specify the ami id as shared by Datamotive & count for the number of nodes you want to deploy. Modify other fields with caution.
prep_create_instance        = "true"
prep_node_ami               = "ami-0a5a6b6686fcf44fa"
prep_node_count             = "1"
prep_node_name              = "terraform-dm-prep-node-tf"
prep_instance_type          = "t2.micro"
prep_security_group_name    = "DM-Prep-SG"
prep_security_group_cidr    = ["0.0.0.0/0"]

# Datamotive Management and Replication Node SSH Key Name
ssh_key_name               = ""
