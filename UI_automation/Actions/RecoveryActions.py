from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from Utilities.utils import getApiResponse, setVirtualMachineCredentials, checkJobStatusOfVirtualMachine
from Actions.ReplicationJobsActions import ReplicationJobsActions
from Actions.CleanupActions import CleanupActions
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants
from Constants.ApiConstants import ApiConstants
from Constants.XpathConstants import XpathConstants
import traceback


class RecoveryActions(CommonWebPageActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.ReplicationAction = ReplicationJobsActions(self.driver)
        self.CleanupAction = CleanupActions(self.driver)
        self.driver = driver


    def executeTestRecovery(self, data, filepath, logger, testCaseName=None):
        try:
            '''
            This function will check replication of existing virtual machine is completed or not and after that it will call 
            fill_test_recovery_data
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.TEST_RECOVERY_INITIATED_SUCCESSFULLY)
            self.findElement((By.XPATH, XpathConstants.TABLE_XPATH))
            protectionPlanName = data["protectionPlan"]
            virtualMachineList = data["virtualMachine"]
            protectionPlans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
            resultList = []
            for eachProtectionPlan in protectionPlans:
                if protectionPlanName == eachProtectionPlan["name"]:
                    logger.info(Constants.TEST_RECOVERY_STARTED_WITH_PROTECTION_PLAN.format(protectionPlanName))
                    # To click configure section
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    # To click actual protection plan section
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
                    # To click actual protection plan element
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlanName)))
                    # To find and click on Actions
                    self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                    # To click on test recovery
                    self.onClick((By.XPATH, XpathConstants.TEST_RECOVRY_BUTTON_XPATH))
                    # To find modal content
                    self.findElement((By.XPATH, XpathConstants.MODAL_CONTENT_XPATH))
                    for eachVirtualMachine in virtualMachineList:
                        setVirtualMachineCredentials(self, eachVirtualMachine)
                        # Click next button
                    # click next button
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click next button'''
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click next button
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click Finish button
                    self.onClick((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
                    # Close popup message
                    self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                    # To Click on Configure section
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    # Scroll to find element Recovery Jobs
                    self.scrollToFindElement((By.XPATH, XpathConstants.RECOVERY_JOBS_XPATH))
                    # click recovery jobs 
                    self.onClick((By.XPATH, XpathConstants.RECOVERY_JOBS_XPATH))
                    # Click on Virtual Machine Icon
                    self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_DATA_XPATH))
                    self.findElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
                    self.onAnimationClick((By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
                    # Find Virtual Machine List Table
                    self.findElement((By.XPATH, XpathConstants.VM_LIST_TABLE_XPATH))
                    for virtualMachine in virtualMachineList:
                        output = checkJobStatusOfVirtualMachine(self, virtualMachine, filepath, logger, testCaseName)
                        if output == Constants.COMPLETED:
                            logger.info(Constants.TEST_RECOVERY_COMPLETED.format(virtualMachine))
                            addTestResultToReportSheet(filepath, Constants.TEST_RECOVERY, Constants.HEADER, data,
                                           Constants.TEST_RECOVERY_COMPLETED.format(virtualMachine))
                            resultList.append(Constants.TRUE)
                        elif output == Constants.PARTIALLY_COMPLETED:
                            logger.info(Constants.TEST_RECOVERY_PARTIALLY_COMPLETED.format(virtualMachine))
                            addTestResultToReportSheet(filepath, Constants.TEST_RECOVERY, Constants.HEADER, data,
                                           Constants.TEST_RECOVERY_PARTIALLY_COMPLETED.format(virtualMachine))
                            resultList.append(Constants.FALSE)
                        else:
                            logger.error(Constants.TEST_RECOVERY_FAILED.format(virtualMachine))
                            addTestResultToReportSheet(filepath, Constants.TEST_RECOVERY, Constants.HEADER, data, Constants.TEST_RECOVERY_FAILED.format(virtualMachine))
                            resultList.append(Constants.FALSE)
                    # at the end we need to clear virtual machine list
                    virtualMachineList.clear()
                    if Constants.FALSE not in resultList:
                        return Constants.PASSED
                    else:
                        return Constants.FAILED

            logger.error(Constants.PROTECTION_PLAN_NOT_FOUND)
            addTestResultToReportSheet(filepath, Constants.TEST_RECOVERY, Constants.HEADER, data, Constants.PROTECTION_PLAN_NOT_FOUND)

        except Exception:
            logger.error(traceback.format_exc())



    def executeRecovery(self, data, filepath, testCaseName, logger):
        try:
            '''
            This function will execute recovery
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.RECOVERY_INITIATED_SUCCESSFULLY)
            protectionPlans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
            protectionPlanName = data["protectionPlan"]
            virtualMachine = data["virtualMachine"]
            resultList = []
            for eachProtectionPlan in protectionPlans:
                if protectionPlanName == eachProtectionPlan["name"]:
                    logger.info(Constants.RECOVERY_STARTED_WITH_PROTECTION_PLAN.format(protectionPlanName))
                    # To click configure
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    # To click Protection Plan section
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
                    # To click actual protection plan element
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlanName)))
                    # To click on Actions
                    self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                    # To click on Recover
                    self.onClick((By.XPATH, XpathConstants.ADD_BUTTON_XPATH))
                    self.waitUntil((By.XPATH, XpathConstants.RECOVERY_WORKLOAD_XPATH))
                    for each_machine in virtualMachine:
                        setVirtualMachineCredentials(self, each_machine)
                    # Click Next button
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click Next button
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click Finish button
                    self.onClick((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
                    # To close message popup
                    self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                    # Scroll to find element Recovery Jobs and Click on it
                    self.scrollToFindElement((By.XPATH, XpathConstants.RECOVERY_JOBS_XPATH))
                    self.onClick((By.XPATH, XpathConstants.RECOVERY_JOBS_XPATH))
                    # To find and click on virtual machine icon
                    self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_DATA_XPATH))
                    self.findElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
                    self.onAnimationClick((By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
                    # To click configure section
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    self.waitUntil((By.XPATH, XpathConstants.TABLE_XPATH))
                    for eachVirtualMachine in virtualMachine:
                        status = checkJobStatusOfVirtualMachine(self, eachVirtualMachine, filepath, logger, testCaseName)
                        if status == Constants.COMPLETED:
                            logger.info(Constants.RECOVERY_JOB_COMPLETED.format(virtualMachine))
                            addTestResultToReportSheet(filepath, Constants.TEST_RECOVERY, Constants.HEADER, data, 
                            Constants.RECOVERY_JOB_COMPLETED.format(virtualMachine))
                            resultList.append("True")
                        elif status == Constants.PARTIALLY_COMPLETED:
                            logger.error(Constants.RECOVERY_JOB_PARTIALLY_COMPLETED.format(virtualMachine))
                            addTestResultToReportSheet(filepath, Constants.TEST_RECOVERY, Constants.HEADER, data, 
                            Constants.RECOVERY_JOB_PARTIALLY_COMPLETED.format(virtualMachine))
                            resultList.append("False")
                        else:
                            logger.error(Constants.RECOVERY_JOB_FAILED.format(virtualMachine))
                            addTestResultToReportSheet(filepath, Constants.TEST_RECOVERY, Constants.HEADER, data,
                            Constants.RECOVERY_JOB_FAILED.format(virtualMachine))
                            resultList.append("False")
                    if "False" not in resultList:
                        return Constants.PASSED
                    else:
                        return Constants.FAILED

            logger.error(Constants.PROTECTION_PLAN_NOT_FOUND)
            addTestResultToReportSheet(filepath, Constants.TEST_RECOVERY, Constants.HEADER, data, Constants.PROTECTION_PLAN_NOT_FOUND)
        
        except Exception:
            logger.error(traceback.format_exc())
