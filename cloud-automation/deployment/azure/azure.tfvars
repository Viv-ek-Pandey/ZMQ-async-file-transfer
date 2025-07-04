
# Credentials of Azure User which will be used for creating the infrastructure
client_id                             = "02ec3e2f-7100-447d-b664-58fef589b843"
client_secret                         = "P9B8Q~YR7ykt8avLDfFmCz1Cn86n8s-~n8Iq9crd"
subscription_id                       = "ec3961da-684c-4d99-bafb-5d89ab2477ed"
tenant_id                             = "f9a974ea-9ad8-4bc1-92d4-a4b4b638ae13"

# Datamotive storage account properties. Specify the storage account name, account tier type and other properties
storage_account_create                = "true"
storage_account_name                  = "dmstoragesp"
storage_account_tier                  = "Standard" // Standard, Premium
storage_account_replication_type      = "LRS" // LRS, GRS, RAGRS, ZRS, GZRS and RAGZRS

# Azure Resource group, Region, Virtual Network and subnet where the Datamotive nodes will be deployed.
resource_group_name                   = "test-sourav"
location                              = "Central India"
vnet_name                             = "Test-sourav-vnet"
subnet_name                           = "default"

# Flag to indicate whether to create security groups
security_group_create                 = "true"

# Datamotive Security group details for Management/Replication nodes
mgmt_security_group                   = "dm-mgmt-sg"
mgmt_inbound_name                     = "dm-mgmt-inbound"
mgmt_outbound_name                    = "dm-mgmt-outbound"
mgmt_source_address_prefix            = "0.0.0.0/0"
mgmt_inbound_allowed_ports            = [3308, 5000, 5001, 5002, 5003, 22]
mgmt_destination_address_prefix       = "0.0.0.0/0"
mgmt_outbound_allowed_ports           = [5000, 5001, 5002, 5003, 5005, 443, 3308, 5985, 5986]

# Datamotive Security group details for Management/Replication nodes
prep_inbound_name                     = "dm-prep-inbound"
prep_outbound_name                    = "dm-prep-outbound"
prep_security_group                   = "dm-prep-sg"
prep_source_address_prefix            = "0.0.0.0/0"
prep_inbound_allowed_ports            = [5985, 5986, 3389]
prep_destination_address_prefix       = "0.0.0.0/0"
prep_outbound_allowed_ports           = [65535]

# Flag to indicate if deployed nodes should have public ip or not.
associate_public_ip                   = "true"

# Datamotive nodes disk type property
node_disk_type                        = "Standard_LRS" // Standard_LRS, StandardSSD_LRS, Premium_LRS

# Datamotive management node properties. Specify the image name as shared by Datamotive. Modify other fields with caution.
mgmt_create_vm                        = "true"
mgmt_vm_name                          = "dm-mgmt"
mgmt_vm_size                          = "Standard_B2ms"
mgmt_user_name                        = "dmadmin"
mgmt_user_password                    = "PassworD@123"
mgmt_disable_password_authentication  = "false"
mgmt_image_offer                      = "Datamotive-EazyMigrate"
mgmt_image_sku                        = "datamotive-management-node"
mgmt_image_id                         = "/subscriptions/ec3961da-684c-4d99-bafb-5d89ab2477ed/resourceGroups/carnival/providers/Microsoft.Compute/galleries/DM_Carnival/images/datamotive-management-node/versions/1.4.2695"
mgmt_plan_name                        = "cis-ubuntulinux2004-l1-gen1"
mgmt_plan_publisher                   = "center-for-internet-security-inc"
mgmt_plan_product                     = "cis-ubuntu"

# Datamotive replication node properties. Specify the image details as shared by Datamotive & count for the number of nodes you want to deploy. Modify other fields with caution.
repl_create_vm                        = "true"
repl_node_count                       = 1
repl_vm_name                          = "dm-repl"
repl_vm_size                          = "Standard_B2ms"
repl_user_name                        = "dmadmin"
repl_user_password                    = "PAssword@123"
repl_disable_password_authentication  = "false"
repl_image_offer                      = "Datamotive-EazyMigrate"
repl_image_sku                        = "datamotive-management-node"
repl_image_id                         = "/subscriptions/ec3961da-684c-4d99-bafb-5d89ab2477ed/resourceGroups/carnival/providers/Microsoft.Compute/galleries/DM_Carnival/images/datamotive-replication-node/versions/1.4.2695"
repl_plan_name                        = "cis-ubuntulinux2004-l1-gen1"
repl_plan_publisher                   = "center-for-internet-security-inc"
repl_plan_product                     = "cis-ubuntu"

# Datamotive prep node properties. Specify the image and plan details as shared by Datamotive & count for the number of nodes you want to deploy. Modify other fields with caution.
prep_create_vm                        = "true"
prep_node_count                       = 1
prep_vm_name                          = "dm-prep"
prep_vm_size                          = "Standard_B2ms"
prep_user_name                        = "dmadmin"
prep_user_password                    = "PasSword@123"
prep_image_offer                      = "Datamotive-EazyMigrate"
prep_image_sku                        = "datamotive-management-node"
prep_image_id                         = "/subscriptions/ec3961da-684c-4d99-bafb-5d89ab2477ed/resourceGroups/carnival/providers/Microsoft.Compute/galleries/DM_Carnival/images/datamotive-prep-node-22/versions/1.2.2574"
prep_plan_name                        = "cis-windows-server2022-l1-gen2"
prep_plan_publisher                   = "center-for-internet-security-inc"
prep_plan_product                     = "cis-windows-server"