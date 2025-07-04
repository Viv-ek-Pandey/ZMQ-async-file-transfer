Pre-requisites:
	1. AWS IAM User with access & secret key having permissions for IAM User creation, IAM Policy Creation, IAM Policy assignment to IAM user, EC2 instance creation & EC2 Security Group Creation.
	2. ID of the region where the Datamotive nodes will be deployed.
	3. VPC and subnet ID where the Datamotive nodes will be deployed
	4. SSH Key Name which will be associated with the Datamotive nodes.

Procedure:
	1. Download & Install Terraform on system from where the Datamotive deployment scripts need to be executed.
	2. Verify Terraform is accessible through local shell.
	3. Unzip Datamotive Terraform Deployer.
	4. In the local shell, navigate to the directory datamotive-deployer.
	5. Edit file aws.tfvars and assign values for variables 
		
		- region: AWS Region ID where the Datamotive nodes will be deployed. E.g. For Singapore region the value is "ap-southeast-1"
		- VPC & Subnet ID - AWS VPC and subnet ID where the Datamotive nodes will be deployed.
		- SSH key name - SSH Key Name which will be associated with the Datamotive nodes.

		- access_key & secret key: Access key for user which has permissions for , "secret_key". The values for region
		- IAM username & IAM policy name - New IAM user for the 
		- create_security_group - Flag to determine whether to create security groups
		- assign_public_IP - Flag to determine whether to associate public ip
		- Flags to create Management, Replication & Prep nodes
		- AMI ID for all the nodes.
		- Instance type for all nodes
	6. Save the file and exit.
	7. Execute command: "terraform init". Once this command is successful, it will initialize terraform with required AWS session.
	8. Execute command: "terraform plan -var-file ./aws.tfvars". Validate the output which shows which all resources will be created in the environment
	9. Once validated, execute command: "terraform apply -var-file ./aws.tfvars". This will create configured resources in the given infrastructure. The configuration details will be printed on console. It can be redirected to an output file as well.
	10.From the output of above command, note the values for fields "access_key" & for secret key run the command " terraform console" & "> nonsensitive(aws_iam_access_key.user_access_key[0].secret)" These will be required while configuring the solution. 
	11. The output of the command provides AWS ID & Name for each resource which it created. If there are any environment related errors, fix them and re-execute this command.
	12. If you want to create only specific nodes at any later point in time e.g. create new replication or prep nodes. You can enable the same in the configuration file "aws.tfvars" and execute below commands.
		- Execute below commands
			terraform state rm aws_instance.repl-node
			terraform state rm aws_instance.prep-node
		- If prep node is required Make prep_create_vm = "true" & Change the prep node count as per requirement and if not required make it false &  Change the count to 0.
		- If replication node is required Make repl_create_vm = "true" & Change the prep node count as per requirement and if not required make it false &  Change the count to 0.
		- Run "Terraform plan -var-file aws.tfvars"
		- Run "Terraform apply -var-file aws.tfvars"  type yes when prompted.