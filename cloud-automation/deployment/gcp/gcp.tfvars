# GCP Region, Project and Network where the Datamotive nodes will be deployed.
region                           = "us-central-1"
project                          = "datamotivedev"
network                          = "default"
subnet                           = "default"

# Flag to indicate whether to deploy the GCP Pre-requisite like service account, Role and Security groups
create_pre_req                   = "true"

# Datamotive service account which will be attached to the nodes for GCP communication
account_id                       = "dm-service"
display_name                     = "dm-service"

# Datamotive GCP Role details which will be used by the service account
role_id                          = "dmrole"
title                            = "datamotive"

# Datamotive Management and Replication Nodes Security groups details
mgmt_firewall_tag_name           = ["dm-mgmt-sg"]
mgmt_firewall_ingress_name       = "dm-mgmt-ingress"
mgmt_firewall_egress_name        = "dm-mgmt-egress"
mgmt_firewall_source_range       = ["0.0.0.0/0"]
mgmt_firewall_destination_range  = ["0.0.0.0/0"]

# Datamotive Prep Node Security groups details
prep_firewall_tag_name           = ["dm-prep-sg"]
prep_firewall_ingress_name       = "dm-prep-ingress"
prep_firewall_egress_name        = "dm-prep-egress"
prep_firewall_source_range       = ["0.0.0.0/0"]
prep_firewall_destination_range  = ["0.0.0.0/0"]

# Flag to indicate if deployed nodes should have public ip or not.
associate_public_ip              = "true"

# Datamotive management node properties. Specify the Image id as shared by Datamotive. Modify other fields with caution.
mgmt_create_vm                   = "true"
mgmt_server_name                 = "dm-mgmt-server"
mgmt_server_type                 = "n2-standard-2"
mgmt_server_zone                 = "us-central1-a"
mgmt_server_image                = "projects/datamotivedev/global/images/dm-mgmt-gcp-1-4-0-2695"

# Datamotive replication node properties. Specify the Image id as shared by Datamotive & count for the number of nodes you want to deploy. Modify other fields with caution.
repl_create_vm                   = "true"
repl_node_count                  = 2
repl_node_name                   = "dm-repl-node"
repl_node_type                   = "n2-standard-2"
repl_node_zone                   = "us-central1-a"
repl_node_image                  = "projects/datamotivedev/global/images/dm-repl-gcp-1-4-0-2695"

# Datamotive windows prep node properties. Specify the Image id as shared by Datamotive & count for the number of nodes you want to deploy. Modify other fields with caution.
prep_create_vm                   = "true"
prep_node_count                  = 2
prep_node_name                   = "dm-prep-node"
prep_node_type                   = "n2-standard-2"
prep_node_zone                   = "us-central1-a"
prep_node_image                  = "projects/datamotivedev/global/images/dm-win-prep-22-1-2-2-2574"

# User SSH Keys which will attached to the deploy nodes
ssh_keys                         = ""