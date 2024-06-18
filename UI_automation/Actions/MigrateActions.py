from selenium.webdriver.common.by import By
from Utilities.CommonWebPageActions import CommonWebPageActions
from Constants.ApiConstants import ApiConstants
from Utilities.utils import getApiResponse, setVirtualMachineCredentials, checkMigrationStatus
from Actions.RecoveryActions import RecoveryActions
from Actions.ReplicationJobsActions import ReplicationJobsActions
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
import traceback


class MigrateActions(CommonWebPageActions):

    def __init__(self, driver):

        super().__init__(driver)
        self.driver = driver
        self.RecoveryActions = RecoveryActions(self.driver)
        self.ReplicationJobsActions = ReplicationJobsActions(self.driver)


    def migrate(self, data, filepath, logger):
        try:
            '''
            This function will execute migrate activity
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.MIGRATE_INITIATED_SUCCESSFULLY)
            protectionPlans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
            protectionPlanName = data["protectionPlan"]
            virtualMachine = data["virtualMachine"]
            for eachProtectionPlan in protectionPlans:
                if protectionPlanName == eachProtectionPlan["name"]:
                    logger.info(Constants.MIGRATE_STARTED_WITH_PROTECTION_PLAN.format(protectionPlanName))
                    # To click configure section
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    # To click actual protection plan section
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
                    # To click actual protection plan element
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlanName)))
                    # To click on Actions
                    self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                    # To click on Migrate
                    self.onClick((By.XPATH, XpathConstants.MIGRATE_BUTTON_XPATH))
                    # To find modal content
                    self.findElement((By.XPATH, XpathConstants.MODAL_CONTENT_XPATH))
                    # To search each virtual machine
                    for eachMachine in virtualMachine:
                        # search and select each machine
                        setVirtualMachineCredentials(self, eachMachine)
                    # To find and check auto migration checkbox
                    self.onClick((By.XPATH, XpathConstants.AUTO_MIGRATION_CHECKBOX_XPATH))
                    # Click Next button
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click Next button
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click Finish button
                    self.onClick((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
                    # Close popup message
                    self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                    # To click configure section
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    # To find and click refresh button 
                    self.onClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))
                    # Call check status function
                    status = checkMigrationStatus(self, virtualMachine, data, filepath, logger)
                    logger.info(Constants.MIGRATE_COMPLETED_SUCCESSFULLY)
                    return status

            logger.error(Constants.PROTECTION_PLAN_NOT_FOUND)
            addTestResultToReportSheet(filepath, Constants.MIGRATE_TEST, Constants.HEADER, data,  Constants.PROTECTION_PLAN_NOT_FOUND)

        except Exception:
            logger.error(traceback.format_exc())