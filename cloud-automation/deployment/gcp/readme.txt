Pre-requisites:
- Service Account with key json file with access to the GCP Project 
- ID of the region where the Datamotive nodes will be deployed.
- Network and subnet configured
- SSH key pair.
- Details of images from GCP shared by Datamotive. 

Procedure:
1. Download & Install Terraform on system from where the Datamotive deployment scripts need to be executed.
2. Verify Terraform is accessible through local shell.
3. Unzip Datamotive Terraform Deployer.
4. In the local shell, navigate to the directory datamotive-deployer.
5. Replace credentials.json file with the your service account credentials.json                
6. Edit file gcp.tfvars and assign values for variables
region                           = "us-central-1" #Region where nodes needs to be deployed
project                          = "datamotive-project" #target project ID
network                          = "default"  #Name of the network where the nodes needs to be deployed

account_id                       = "terraform-dm-service" # service account ID which terraform will create for node
display_name                     = "terraform-dm-service" #service account display name
role_id                          = "dmrole" #Role created by terraform 
title                            = "terraform-datamotive"  #Role Title
mgmt_create_vm/ repl_create_vm/ prep_create_vm  = "true" #set it true if those particular nodes needs to be deployed
mgmt_server_name                 = "dm-mgmt-server-terraform" #Desired name to be given to management node
repl_node_name                   = "dm-repl-node-terraform"  #Desired name given to the replication node
dedup_node_name                  = "dm-dedup-node"  #Desired name given to the dedupe node
prep_node_name                   = "dm-prep-node-terraform" #Desired name given to the prep node
repl_node_count                  = 1  #Number of replication nodes that needs to be deployed 
prep_node_count                  = 0 #Number of prep nodes that needs to be deployed

7. Save the file and exit.
8. Execute command: "terraform init". Once this command is successful, it will initialize terraform with required GCP session.
9. Execute command: "terraform plan -var-file ./gcp.tfvars". Validate the output which shows which all resources will be created in the environment
10. Once validated, execute command: "terraform apply -var-file ./gcp.tfvars". This will create configured resources in the given infrastructure. The configuration details will be printed on console. It can be redirected to an output file as well.
11. If all the nodes are being deployed at once set the following as true - 
mgmt_create_vm                   = "true" 
repl_create_vm                   = "true"
dedup_create_vm                  = "false"
prep_create_vm                   = "true" 
repl_node_count                  = 1
prep_node_count                  = 1
12. The output of the command provides name for each resource which it created. If there are any environment related errors, fix them and re-execute this command.

13.If you are deploying new prep/repl node then follow below steps ( Assuming mgmt & repl nodes are already deplyed)
1.Run the below commands
        terraform state rm google_compute_instance.repl_node
        terraform state rm google_compute_instance.prep_node
2. Make prep_create_vm = "true"  &  Change the prep node count to 1 ( count as per requirement) to deploy prep node node
3.  Make repl_create_vm = "true" &  count to 1 ( count as per requirement) to deploy repl node.
4. Run "Terraform plan -var-file gcp.tfvars"   type yes when prompted
5. Run "Terraform apply -var-file gcp.tfvars"  type yes when prompted.
