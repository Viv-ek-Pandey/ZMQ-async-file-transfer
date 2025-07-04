Pre-requisites:
	1. vSphere user with credentials having permissions as defined in Datamotive deployment guide.
	2. Name of Datacenter, Compute cluster/ESXi Host, Datastore & Virtual Network where the Datamotive management VM needs to be deployed.

Procedure:
	1. Download & Install Terraform on system from where the Datamotive deployment scripts need to be executed.
	2. Verify Terraform is accessible through local shell.
	3. Unzip Datamotive Terraform Deployer, "datamotive-deployer.zip".
	4. In the local shell, navigate to the directory datamotive-deployer.
	5. Edit file vmware.tfvars and assign values for variables
		- vsphere_server: Hostname or IP address of vCenter Server
		- vsphere_username: Username of vSphere user created for Datamotive as part of pre-requisite
		- vsphere_password: Password of vSphere user created for Datamotive as part of pre-requisite
		- datacenter_name: Name of vSphere Datacenter where the Datamotive Management VM needs to be deployed
		- datastore_name: Name of vSphere Datastore where the Datamotive Management VM needs to be deployed
		- compute_cluster_name: Name of vSphere Compute Cluster where the Datamotive Management VM needs to be deployed
		- esxi_host_name: ESXi host name within the specified compute cluster where the Datamotive Management VM needs to be deployed
		- network_name: Name of virtual network to associate Datamotive Management VM with
	6. Save the file and exit.
	7. Execute command: "terraform init".
	8. Execute command: "terraform plan -var-file ./vmware.tfvars". Validate the output which shows which all resources will be created in the environment
	9. Once validated, execute command: "terraform apply -var-file ./vmware.tfvars". This will create configured resources in the given infrastructure. The configuration details will be printed on console. It can be redirected to an output file as well.