from Utilities.utils import getLogger
from selenium.webdriver.common.by import By
from Utilities.CommonWebPageActions import CommonWebPageActions
from Constants.ApiConstants import ApiConstants
from Utilities.utils import getApiResponse, getCellValue
from Actions.RecoveryActions import RecoveryActions
from Actions.ReplicationJobsActions import ReplicationJobsActions
from time import sleep
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants


class MigrateActions(CommonWebPageActions):

    def __init__(self, driver):

        super().__init__(driver)
        self.driver = driver
        self.logger = getLogger()
        self.RecoveryActions = RecoveryActions(self.driver)
        self.ReplicationJobsActions = ReplicationJobsActions(self.driver)

    '''This function will execute migrate activity'''

    def migrate(self, jsonTestData, filepath, logger):
        Protection_Plans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
        for data in jsonTestData:
            Protection_Plan_Name = data["protection_plan"]
            Virtual_Machine = data["virtual_machine"]
            if len(Protection_Plans) != 0 and Protection_Plan_Name == data["protection_plan"]:
                """ To click actual protection plan element"""
                self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(Protection_Plan_Name)))
                """ To click on Actions"""
                self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                """ To click on Migrate"""
                self.onClick((By.XPATH, XpathConstants.MIGRATE_BUTTON_XPATH))
                for each_machine in Virtual_Machine:
                    self.RecoveryActions.search_virtual_machine(each_machine)
                self.findElement((By.XPATH, XpathConstants.AUTO_MIGRATION_CHECKBOX_XPATH))
                self.onClick((By.XPATH, XpathConstants.AUTO_MIGRATION_CHECKBOX_XPATH))
                self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                self.onClick((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
                self.findElement((By.XPATH, XpathConstants.SUCCESS_MESSAGE_POPUP_XPATH))
                self.onClick((By.XPATH, XpathConstants.SUCCESS_MESSAGE_POPUP_XPATH))
                sleep(3)
                self.onClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))
                self.check_status(Virtual_Machine, data, filepath)
            else:
                logger.warning("Protection Plan not found")

    '''This function will check status of migration'''

    def check_status(self, machine, data, filepath):
        self.scrollToFindElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_SECTION_XPATH))
        result_of_status = getCellValue(self, "Status", 0)
        return self.monitor_migration(result_of_status, machine, data, filepath)

    '''Depending upon status below code will re-execute'''

    def monitor_migration(self, result, machine, data, filepath):
        if result == Constants.MIGRATION_INIT:
            sleep(60)
            self.onClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))
            return self.check_status(machine, data, filepath)
        elif result == Constants.MIGRATION_INIT_SUCCESS:
            self.waitUntil((By.XPATH, XpathConstants.JOBS_SECTION_XPATH))
            self.onClick((By.XPATH, XpathConstants.JOBS_SECTION_XPATH))
            self.onClick((By.XPATH, XpathConstants.RECOVERY_SECTION_XPATH))
            self.onAnimationClick((By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
            sleep(10)
            for each_virtual_machine in machine:
                Status = self.RecoveryActions.check_status_of_vm(each_virtual_machine, data, filepath)
                addTestResultToReportSheet(filepath, Constants.MIGRATE_TEST, Constants.CLEANUP_HEADER, data,
                                           Status)
            self.logger.info("Migration Job Completed")
        else:
            addTestResultToReportSheet(filepath, Constants.MIGRATE_TEST, Constants.CLEANUP_HEADER, data,
                                       Constants.MIGRATION_GOT_FAILED)
            self.logger.error("Migration Init got failed")
