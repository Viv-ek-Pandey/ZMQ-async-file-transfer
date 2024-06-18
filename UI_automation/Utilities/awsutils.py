import boto3
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants

def awsInfraCreation(data, filepath, logger):
    accessKey = data["awsAccessKey"]
    secretkey = data["awsSecretKey"]
    regionName = data["regionName"]
    imageId = data["imageId"]
    minCount = data["minCount"]
    maxCount = data["maxCount"]
    instanceType = data["instanceType"]
    keyName = data["keyName"]
    instanceNames = data["instanceNames"]
    securityGroupIds = data["securityGroupIds"][0]
    instnaceIDs = []
    instances = [] 
    # Initialize a session using Amazon EC2
    session = boto3.Session(
    aws_access_key_id = accessKey,
    aws_secret_access_key = secretkey,
    region_name = regionName  
    )
    for name in instanceNames:
        # Initialaize EC2 resource
        ec2Resource = session.resource('ec2')
        instance = ec2Resource.create_instances(
            ImageId = imageId,  
            MinCount = minCount,  
            MaxCount = maxCount,  
            InstanceType = instanceType,  
            KeyName = keyName, 
            SecurityGroupIds = [securityGroupIds],  
            TagSpecifications=
            [
                {
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name','Value': name} ]
                }
            ]
        )[0]
        instnaceIDs.append(instance.id)
        instances.append(instance)
        logger.info(Constants.AWS_INSTANCE_CREATED.format(name))
        addTestResultToReportSheet(filepath, Constants.INFRA_TEST, Constants.INFRA_HEADER, data, 
                                                    Constants.AWS_INSTANCE_CREATED.format(name))
    return instnaceIDs


def awsInfraDelete(data, filepath, logger, instnaceIDs):
    accessKey = data["awsAccessKey"]
    secretkey = data["awsSecretKey"]
    regionName = data["regionName"]
    # Initialize a session using Amazon EC2
    session = boto3.Session(
    aws_access_key_id = accessKey,
    aws_secret_access_key = secretkey,
    region_name = regionName  
    )
    ec2Client = session.client('ec2')
    if len(instnaceIDs) == 0:
        logger.error(Constants.AWS_INFRA_NOT_CREATED)
        return Constants.FAILED
    else:
        deleteInstance = ec2Client.terminate_instances(InstanceIds = instnaceIDs)
        for instanceID in deleteInstance['TerminatingInstances']:
            logger.info(Constants.AWS_INSTANCE_DELETED.format(instanceID['InstanceId']))
            addTestResultToReportSheet(filepath, Constants.INFRA_TEST, Constants.INFRA_HEADER, data, 
                                    Constants.AWS_INSTANCE_DELETED.format(instanceID['InstanceId']))
        instnaceIDs.clear()
        return Constants.PASSED