from Constants.XpathConstants import XpathConstants
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from Utilities.utils import getApiResponse, checkJobStatusOfVirtualMachine
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants
from Constants.ApiConstants import ApiConstants
import traceback


class ReplicationJobsActions(CommonWebPageActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver


    def monitorProtectionPlanReplicationOfVirtualMachineJobs(self, data, filepath, logger, testCaseName=None):
        try:
            '''
            this function will check the replication of virtual machine jobs
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.REPLICATION_INITIATED_SUCCESSFULLY_FOR_VIRTUAL_MACHINE_JOBS)
            protectionPlans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
            protectionPlanName = data["protectionPlan"]
            virtualMachine = data["virtualMachine"]
            resultList = []
            for eachProtectionPlan in protectionPlans:
                if protectionPlanName == eachProtectionPlan["name"]:
                    logger.info(Constants.REPLICATION_STARTED_WITH_PROTECTION_PLAN.format(protectionPlanName))
                    # To click configure section
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    # To click actual protection plan section
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
                    # To find and click actual protection plan element
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlanName)))
                    # Scroll to find replication jobs
                    self.scrollToFindElement((By.XPATH, XpathConstants.REPLICATION_JOBS_XPATH))
                    virtualMachineIcon = self.findElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
                    if not virtualMachineIcon:
                        self.onClick((By.XPATH, XpathConstants.REPLICATION_JOBS_XPATH))
                    # To find and click on virtual machine icon"
                    self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_DATA_XPATH))
                    self.findElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
                    self.onAnimationClick((By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
                    # To find virtual machine table
                    self.findElement((By.XPATH, XpathConstants.VM_LIST_TABLE_XPATH))
                    # To find and click Configure section
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    for machine in virtualMachine:
                        status = checkJobStatusOfVirtualMachine(self, machine, filepath, logger, testCaseName)
                        if status == Constants.COMPLETED:
                            addTestResultToReportSheet(filepath, Constants.REPLICATION_TEST, Constants.HEADER, data,
                                           Constants.REPLICATION_JOB_COMPLETED.format(machine))
                            logger.info(Constants.REPLICATION_JOB_COMPLETED.format(machine))
                            resultList.append("True")
                        elif status == Constants.PARTIALLY_COMPLETED:
                            addTestResultToReportSheet(filepath, Constants.REPLICATION_TEST, Constants.HEADER, data,
                                           Constants.REPLICATION_JOB_PARTIALLY_COMPLETED.format(machine))
                            logger.info(Constants.REPLICATION_JOB_PARTIALLY_COMPLETED.format(machine))
                            resultList.append("False")
                        else:
                            addTestResultToReportSheet(filepath, Constants.REPLICATION_TEST, Constants.HEADER, data, Constants.REPLICATION_JOB_FAILED.format(machine))
                            logger.error(Constants.REPLICATION_JOB_FAILED.format(machine))
                            resultList.append("False")
                    if "False" not in resultList:
                        return Constants.PASSED
                    else:
                        return Constants.FAILED

            logger.error(Constants.PROTECTION_PLAN_NOT_FOUND)
            addTestResultToReportSheet(filepath, Constants.REPLICATION_TEST, Constants.HEADER, data, Constants.PROTECTION_PLAN_NOT_FOUND)
        
        except Exception:
            logger.error(traceback.format_exc())

    
    def monitorProtectionPlanReplicationOfDisksJobs(self, data, filepath, logger, testCaseName=None):
        try:
            '''
            this function will check the replication of disks jobs
            data: json data received from json fil
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.REPLICATION_INITIATED_SUCCESSFULLY_FOR_DISKS_JOBS)
            protectionPlans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
            protectionPlanName = data["protectionPlan"]
            virtualMachine = data["virtualMachine"]
            resultList = []
            for eachProtectionPlan in protectionPlans:
                if protectionPlanName == eachProtectionPlan["name"]:
                    logger.info(Constants.REPLICATION_STARTED_WITH_PROTECTION_PLAN.format(protectionPlanName))
                    # To click configure section
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    # To click actual protection plan section
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
                    # To find and click actual protection plan element
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlanName)))
                    # Scroll to find replication jobs and Click replication jobs
                    self.scrollToFindElement((By.XPATH, XpathConstants.REPLICATION_JOBS_XPATH))
                    disksJobs = self.findElement((By.XPATH, XpathConstants.DISKS_JOBS_ICON_XPATH))
                    if not disksJobs:
                        self.onClick((By.XPATH, XpathConstants.REPLICATION_JOBS_XPATH))
                    # To find and click on virtual machine icon
                    self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_DATA_XPATH))
                    self.findElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
                    self.onAnimationClick((By.XPATH, XpathConstants.DISKS_JOBS_ICON_XPATH))
                    # To find virtual machine table
                    self.findElement((By.XPATH, XpathConstants.VM_LIST_TABLE_XPATH))
                    # To find and click Configure section
                    self.findElement((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    for machine in virtualMachine:
                        status = checkJobStatusOfVirtualMachine(self, machine, filepath, logger, testCaseName)
                        if status == Constants.COMPLETED:
                            addTestResultToReportSheet(filepath, Constants.REPLICATION_TEST, Constants.HEADER, data,
                                           Constants.REPLICATION_JOB_COMPLETED.format(machine))
                            logger.info(Constants.REPLICATION_JOB_COMPLETED.format(machine))
                            resultList.append(Constants.TRUE)
                        elif status == Constants.PARTIALLY_COMPLETED: 
                            addTestResultToReportSheet(filepath, Constants.REPLICATION_TEST, Constants.HEADER, data,
                                           Constants.REPLICATION_JOB_PARTIALLY_COMPLETED.format(machine))
                            logger.info(Constants.REPLICATION_JOB_PARTIALLY_COMPLETED.format(machine))
                            resultList.append(Constants.FALSE)
                        else:
                            addTestResultToReportSheet(filepath, Constants.REPLICATION_TEST, Constants.HEADER, data, Constants.REPLICATION_JOB_FAILED.format(machine))
                            logger.error(Constants.REPLICATION_JOB_FAILED.format(machine))
                            resultList.append(Constants.FALSE)     
                    if Constants.FALSE not in resultList:
                        return Constants.PASSED
                    else:
                        return Constants.FAILED

            logger.error(Constants.PROTECTION_PLAN_NOT_FOUND)
            addTestResultToReportSheet(filepath, Constants.REPLICATION_TEST, Constants.HEADER, data, Constants.PROTECTION_PLAN_NOT_FOUND)

        except Exception:
            logger.error(traceback.format_exc())
    