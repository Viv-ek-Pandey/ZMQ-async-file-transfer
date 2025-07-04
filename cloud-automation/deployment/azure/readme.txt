1. Pre-requisites:
- Azure APP with necessary permissions (Contributor or Owner) to the subscription
- Resource group created in the desired Azure region
- Virtual network (VNet) and subnet configured in the resource group
- Details of Resource ID of images from Azure compute Gallery shared by Datamotive. 

Procedure:
1. Download & Install Terraform on system from where the Datamotive deployment scripts need to be executed.
2. Verify Terraform is accessible through local shell.
3. Unzip Datamotive Terraform Deployer.
4. In the local shell, navigate to the directory datamotive-deployer.
5. Edit file azure.tfvars and assign values for variables

- Subscription ID, Tenant ID, Client ID, Client secret of the Azure App 
- Resource Group: Resource group should be created by user manually and exact name should be provided.
- Region: User need to provide the region.
- Virtual Network: User need to provide the name of virtual network to associate Datamotive nodes with
- Subnet: User need to provide the desired subnet for the VM

- Storage Account: Script will create the storage account with the name you provide.
- Public IP: "True" will associate public IP, "false" will not associate public IP with nodes.
- Disk Type: Add the disk type for the datamotive node Ex. Standard SSD LRS
- VM Size: Add the VM size which datamotive supports for best performance ex. B2ms
- Management, Replication & prep node image id : Provide the image id for Management, replication & prep nodes.
6. Save the file and exit.
7. Execute command: "terraform init". Once this command is successful, it will initialize terraform with required Azure provider.
8. Execute command: "terraform plan -var-file ./azure.tfvars". Validate the output which shows which all resources will be created in the environment.
9. Before deploying the nodes, User needs to accept the CIS Images terms. For that run the below command:
    a. az vm image terms accept --urn center-for-internet-security-inc:cis-windows-server:cis-windows-server2022-l1-gen2:latest
    b. az vm image terms accept --urn center-for-internet-security-inc:cis-ubuntu:cis-ubuntulinux2004-l1-gen1:latest
10. Once validated, execute command: "terraform apply -var-file ./azure.tfvars". This will create configured resources in the given infrastructure. The configuration details will be printed on console. It can be redirected to an output file as well.
11. From the output of above command, note any relevant values, such as Azure instance name or other identifiers, which might be required while configuring the solution.
12. The output of the command provides Azure ID & Name for each resource which it created. If there are any environment related errors, fix them and re-execute this command.
13. If you want to create only specific nodes at any later point in time e.g. create new replication or prep nodes, execute below commands.
    1. Execute below commands
- terraform state rm azurerm_virtual_machine.repl
- terraform state rm azurerm_virtual_machine.prep
- terraform state rm module.network.azurerm_network_interface.repl
- terraform state rm module.network.azurerm_network_interface.prep
- terraform state rm module.network.azurerm_public_ip.repl
- terraform state rm module.network.azurerm_public_ip.prep
- terraform state rm azurerm_network_interface_security_group_association.repl_association
- terraform state rm azurerm_network_interface_security_group_association.prep_association
    2. If prep node is required Make prep_create_vm = "true" & Change the prep node count as per requirement and if not required make it false &  Change the count to 0.
    3. If replication node is required Make repl_create_vm = "true" & Change the prep node count as per requirement and if not required make it false &  Change the count to 0.
    4. Run "Terraform plan -var-file azure.tfvars"
    5. Run "Terraform apply -var-file azure.tfvars" type yes when prompted.