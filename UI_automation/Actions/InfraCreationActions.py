from Utilities.CommonWebPageActions import CommonWebPageActions
from Constants.Constants import Constants
import traceback
from Utilities.awsutils import awsInfraCreation, awsInfraDelete
from Utilities.VMwareutils import vmwareInfraCreation,vmwareInfraDelete


class InfraCreationActions(CommonWebPageActions):

    def __init__(self, driver):

        super().__init__(driver)
        self.driver = driver
        self.instnaceIDs = []

    def infraCreation(self, data, filepath, logger):
        try :
            '''
            This function will create infra for AWS
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            platform = data["platform"]
            match platform:
                case Constants.AWS:
                    logger.info(Constants.AWS_INFRA_CREATAION_INITIATED_SUCCESSFULLY)
                    instnaceIDs = awsInfraCreation(data, filepath, logger)
                    self.instnaceIDs = instnaceIDs
                    return Constants.PASSED
                
                case Constants.VMware:
                    logger.info(Constants.VMWARE_INFRA_CREATAION_INITIATED_SUCCESSFULLY)
                    status = vmwareInfraCreation(data, filepath, logger)
                    return status
                
                case Constants.GCP:
                    pass

        except Exception:
            logger.error(traceback.format_exc())
    

    def infraDelete(self, data, filepath, logger):

        try :
            '''
            This function will delete infra from AWS
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            platform = data["platform"]
            match platform:
                case Constants.AWS:
                    logger.info(Constants.AWS_INFRA_DELETE_INITIATED_SUCCESSFULLY)
                    awsStatus = awsInfraDelete(data, filepath, logger, self.instnaceIDs)
                    return awsStatus
                
                case Constants.VMware:
                    logger.info(Constants.VMWARE_INFRA_DELETE_INITIATED_SUCCESSFULLY)
                    vmwareStatus = vmwareInfraDelete(data, filepath, logger)
                    return vmwareStatus
                
                case Constants.AZURE:
                    pass
                case Constants.GCP:
                    pass

        except Exception:
            logger.error(traceback.format_exc())