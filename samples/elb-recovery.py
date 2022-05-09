import boto3

class ElbConfigurator:
    # Parameters
    src_lb_arn="arn:aws:elasticloadbalancing:us-west-2:116356930974:loadbalancer/app/App-LB1/177da756cf0214c9"
    src_region="us-west-2"
    target_region="us-east-2"
    src_elb_client=None
    target_elb_client=None
    target_ec2_client=None
    elb_config={}

    def __init__(self):
        pass

#---------------------------------------------------------------AWS Functions-----------------------------------------------
    # Initialize Source & Recovery site connections
    def initialize(self):
        print("Initializing AWS Client...")
        self.src_elb_client=boto3.client('elbv2')
        self.target_ec2_client=boto3.client('ec2', region_name=self.target_region)
        self.target_elb_client=boto3.client('elbv2', region_name=self.target_region)
    
    # Create ELB on target region with security groups & subnets mapped to target_instances. Rest of the properties should be same as ELB, elb_name on source site
    def replicate_elb(self, elb_name, target_instance_ids):
        print("Replicating ELB from source to target...")
        source_elb=self.get_load_balancers(elb_name)
        # Prepare recovery subnets
        recovery_subnets=[]
        source_entities=self.get_targets(source_elb['LoadBalancerArn'])
        for source_entity in source_entities:
            # TODO: Prepare target entity instance id list based on source entity ids from the Datamotive input
            target_instance_ids.append(source_entity['Target']['Id'])
        #Test code
        target_instance_ids=["i-07b17a4951c4f0766", "i-046459727fa133821", "i-008ecc3dfef39a501"]
        # Fetch all instances for target instance ids
        target_instances=self.get_instances(target_instance_ids, self.target_ec2_client)

        # Prepare recovery subnets
        recovery_subnets.extend(self.get_recovery_subnets(target_instances))
        #print("Subnets: ", recovery_subnets)

        # Prepare recovery security groups
        recovery_sgs=[]
        for target in target_instances:
            recovery_sgs.extend(self.get_recovery_sg(target))
        # Remove duplicates coming from different instances
        recovery_sgs = list(set(recovery_sgs))
        #print("Security Groups: ", recovery_sgs)

        elb_config=self.create_elb_config(source_elb, recovery_subnets, recovery_sgs)
        print("Creating ELB in {} region with Config: {}".format(self.target_region, elb_config))
        created_lb=self.target_elb_client.create_load_balancer(**elb_config)
        print("Created LB: {}".format(created_lb))

        # Create target group with recovery instances. Recovery instances have to be in running state before adding to a target group
        resp=self.add_elb_targets(target_instances, created_lb, source_elb)



    # Add Instances to ELB & create listener rules for them
    def add_elb_targets(self, target_instances, target_elb, source_elb):
        print("Adding targets to ELB")
        # Fetch source target group for reading it's properties & create new TG on target site
        src_tg=self.get_target_group(source_elb["LoadBalancerArn"], self.src_elb_client)
        dest_tg=self.create_target_group(src_tg, target_elb["VpcId"])
        print("Created target group on recovery site")
        
        # Register targets to Target Group. Targets have to be in running state for this operation
        resp=self.add_targets_to_target_group(target_instances, dest_tg, self.target_elb_client)
        print("Added recovery instances to newly created target group")

        # TODO: Create Listener create_listener()
        src_listener=self.get_listeners(source_elb["LoadBalancerArn"], self.src_elb_client)
        trg_listener=None
        if src_listener:
            trg_listener=self.create_listener(target_elb["LoadBalancerArn"], dest_tg, src_listener, self.target_elb_client)

    # Create Listener
    def create_listener(self, elb_arn, target_group, src_listener, elb_client):
        print("\n \n Source Listener: ", src_listener)
        config={}
        config["LoadBalancerArn"]=elb_arn
        config["Protocol"]=src_listener["Protocol"]
        config["Port"]=src_listener["Port"]
        if "SslPolicy" in src_listener:
            config["SslPolicy"]=src_listener["SslPolicy"]
        actions=[]
        src_actions=src_listener["DefaultActions"]
        for src_action in src_actions:
            action={}
            action["Type"]=src_action["Type"]
            action["TargetGroupArn"]=target_group["TargetGroupArn"]
            if "Order" in src_action:
                action["Order"]=src_action["Order"]
            if "RedirectConfig" in src_action:
                action["RedirectConfig"]=src_action["RedirectConfig"]
            if "FixedResponseConfig" in src_action:
                action["FixedResponseConfig"]=src_action["FixedResponseConfig"]
            if action["Type"] == "forward":
                forward_config={}
                target_groups=[]
                fw_rule_tg={}
                fw_rule_tg["TargetGroupArn"]=target_group["TargetGroupArn"]
                fw_rule_tg["Weight"]=123
                target_groups.append(fw_rule_tg)
                forward_config["TargetGroups"]=target_groups
                action["ForwardConfig"]=forward_config
            actions.append(action)
        config["DefaultActions"]=actions
        listener=elb_client.create_listener(**config)


    # Create Target Group based on source Target Group in given VPC
    def create_target_group(self, source_tg, vpc_id):
        # Copy all properties & empty out source references
        dest_target_group_config=source_tg
        dest_tg_name="DM-Recovered-"+source_tg["TargetGroupName"]
        dest_target_group_config["Name"]=dest_tg_name
        dest_target_group_config["VpcId"]=vpc_id
        del dest_target_group_config["TargetGroupName"]
        del dest_target_group_config["TargetGroupArn"]
        del dest_target_group_config["LoadBalancerArns"]
        # Create Target Group: create_target_group()
        dest_tgs=self.target_elb_client.create_target_group(**dest_target_group_config)
        dest_tg={}
        for tg in dest_tgs["TargetGroups"]:
            if tg["TargetGroupName"] == dest_tg_name:
                dest_tg = tg
                break
        print("Created TG in destination region: ", tg)
        return tg

    # Add targets to target group
    def add_targets_to_target_group(self, target_instances, target_group, target_elb_client):
        #print("Registering targets {} to target group {}".format(target_instances, target_group))
        filter={}
        filter["TargetGroupArn"]=target_group["TargetGroupArn"]
        filter["Targets"]=[]
        for target in target_instances:
            filter_target={}
            filter_target["Id"]=target["InstanceId"]
            filter["Targets"].append(filter_target)
            #filter_target["Port"]=80
        register_resp=target_elb_client.register_targets(**filter)
        print("Registered Targets with Target Group. ",register_resp)

    # Fetching LBs
    def get_load_balancers(self, elb_name, elb_client):
        if elb_name:
            name_filter={}
            name_filter["Names"]=[elb_name]
            lbs=elb_client.describe_load_balancers(**name_filter)
        else:
            lbs=elb_client.describe_load_balancers()
        lb=lbs['LoadBalancers']
        return lb[0]

    # Fetching target groups for the LB
    def get_target_group(self, elb_arn, elb_client):
        if elb_arn:
            target_filter={}
            target_filter["LoadBalancerArn"]=elb_arn
            targets=elb_client.describe_target_groups(**target_filter)
        else:
            targets=elb_client.describe_target_groups()
        target_group=targets['TargetGroups']
        return target_group[0]

    # Fetch targets within a target group
    def get_targets(self, elb_arn, elb_client):
        if elb_arn:
            target_group=self.get_target_groups(elb_arn)
            if target_group:
                filter={}
                filter["TargetGroupArn"]=target_group["TargetGroupArn"]
                targets=elb_client.describe_target_health(**filter)
            else:
                targets=elb_client.describe_target_health(**filter)            
        return targets['TargetHealthDescriptions']    

    # Get EC2 instances 
    def get_instances(self, instance_ids, ec2_client):
        print("Fetching EC2 instances for instance ids: ", instance_ids)
        target_instances=[]                
        filter={}
        filter["InstanceIds"]=instance_ids
        reservations=ec2_client.describe_instances(**filter)["Reservations"]
        for reservation in reservations:
            target_instances.append(reservation["Instances"][0])                 
        return target_instances 

    # Fetch Listeners
    def get_listeners(self, elb_arn, elb_client):
        listeners=None
        if elb_arn:
            filter={}
            filter["LoadBalancerArn"]=elb_arn
            listeners=elb_client.describe_listeners(**filter)
            return listeners['Listeners'][0]
        else:
            return None

    # Fetch Listener Rules
    def get_rules(self, listener_arn):
        roles=None
        if listener_arn:
            filter={}
            filter["ListenerArn"]=listener_arn
            rules=self.src_elb_client.describe_rules(**filter)
            return rules['Rules'][0]
        else:
            return None

    # Create ELB configuration
    def create_elb_config(self, source_elb, recovery_subnets, recovery_sgs):
        elb_config={}
        elb_config["Name"]="DM-Recovered-"+source_elb["LoadBalancerName"]
        elb_config["Type"]=source_elb["Type"]
        elb_config["Scheme"]=source_elb["Scheme"]
        elb_config["Subnets"]=recovery_subnets
        elb_config["SecurityGroups"]=recovery_sgs
        #elb_config["Tags"]=source_elb["Type"]
        return elb_config 

#---------------------------------------------------------------DM Functions-----------------------------------------------
    # Get recovery subnets, one from each AZ from given recovery instances
    def get_recovery_subnets(self, recovery_instances):
        recovery_subnets=[]
        azs=[]
        filter={}
        filter["InstanceIds"]=recovery_instances
        reservations=self.target_ec2_client.describe_instances(**filter)["Reservations"]
        #print("Fetched instances {}".format(recovery_instances))
        for recovery_instance in recovery_instances:
            az=recovery_instance["Placement"]["AvailabilityZone"]
            if(az in azs):
                print("AZ: {} already present in list. Skipping it".format(az))
                continue
            else:
                print("AZ: {} not present in list.".format(az))
                azs.append(az)
                nw_interfaces=recovery_instance["NetworkInterfaces"]
                # Take only the first network subnet as LB doesn't allow to bind to multiple subnets from same AZ
                recovery_subnets.append(nw_interfaces[0]["SubnetId"])
        # Remove duplicates coming from different instances
        recovery_subnets = list(set(recovery_subnets))
        return recovery_subnets

    # Get recovery security groups from recovery instances
    def get_recovery_sg(self, recovery_instance):
        recovery_sg=[]
        sgs=recovery_instance["SecurityGroups"]
        for sg in sgs:
            recovery_sg.append(sg["GroupId"])
        recovery_sg = list(set(recovery_sg))
        return recovery_sg

#Initialize connection
config = ElbConfigurator()
config.initialize()

#Fetch ELB
src_lb=config.get_load_balancers("App-LB1", config.src_elb_client)
src_lb_arn=src_lb['LoadBalancerArn']
trg_lb=config.get_load_balancers("DM-Recovered-App-LB1", config.target_elb_client)
trg_lb_arn=trg_lb['LoadBalancerArn']

#print("Fetched LB: ", src_lb)

#Fetch Target Groups
#target_group=config.get_target_group(lb_arn)
#print('Fetched Target Group: ', target_group)

#Fetch Targets
#targets=config.get_targets(lb_arn)
#print("Fetched targets")
#for target in targets:
#    print("Target ID:", target['Target']['Id'])

#Fetch Listeners
#listeners=config.get_listeners(lb_arn)
#print("Listener Arn: {} \nListener Port: {} \nListener Protocol: {} \nAction Type: {} \nTargetGroupArn: {}".
#format(listeners['ListenerArn'], listeners['Port'], listeners['Protocol'], listeners['DefaultActions'][0]['Type'], 
#listeners['DefaultActions'][0]['TargetGroupArn']))

#Fetch Rules
#rules=config.get_rules(listeners['ListenerArn'])
#print("Rule Arn: {} \nPriority: {} \nAction Type: {} \nAction Target Group: {}".
#format(rules['RuleArn'], rules['Priority'], rules['Actions'][0]['Type'], rules['Actions'][0]['TargetGroupArn']))

#Fetch Recovery Instance Subnet
#subnet=config.get_recovery_subnet("i-07b17a4951c4f0766")
#print("Recovery Subnet ID: ", subnet)

#config.replicate_elb("App-LB1", [])
#config.add_elb_targets([],target_elb=config.get_load_balancers("DM-Recovered-App-LB1", config.target_elb_client), 
#source_elb=config.get_load_balancers("App-LB1", config.src_elb_client))

target_instances=config.get_instances(["i-07b17a4951c4f0766", "i-046459727fa133821", "i-008ecc3dfef39a501"], config.target_ec2_client)
#target_group=config.create_target_group(config.get_target_group(lb_arn, config.src_elb_client), "vpc-1be26170")
#resp=config.add_targets_to_target_group(target_instances, target_group, config.target_elb_client)
resp=config.add_elb_targets(target_instances, trg_lb, src_lb)
print("Target addition response: ", resp)
