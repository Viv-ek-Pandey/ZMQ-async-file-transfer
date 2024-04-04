from Utilities.utils import getLogger
from selenium.webdriver.common.by import By
from Utilities.CommonWebPageActions import CommonWebPageActions
from Constants.ApiConstants import ApiConstants
from Utilities.utils import getApiResponse
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants


class CleanupActions(CommonWebPageActions):

    def __init__(self, driver):

        super().__init__(driver)
        self.driver = driver
        self.logger = getLogger()

    '''This function will execute cleanup activity'''

    def cleanup(self, jsonTestData, filepath, logger):
        Protection_Plans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
        for data in jsonTestData:
            Protection_Plan_Name = data["protection_plan"]
            Virtual_Machine = data["virtual_machine"]
            if len(Protection_Plans) != 0 and Protection_Plan_Name == data["protection_plan"]:
                """ To click actual protection plan element"""
                self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(Protection_Plan_Name)))
                """ To click on Actions"""
                self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                """ To click on Cleanup"""
                self.onClick((By.XPATH, XpathConstants.CLEANUP_BUTTON_XPATH))
                for each_machine in Virtual_Machine:
                    '''Clear search box'''
                    self.clearInputFields((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
                    self.onEnter((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
                    '''Enter data into search box'''
                    self.sendInputKeys((By.XPATH, XpathConstants.SEARCH_BOX_XPATH), each_machine)
                    self.onEnter((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
                    '''Click Virtual Machine checkbox'''
                    self.onClick((By.XPATH, XpathConstants.TEST_RECOVERY_VM_CHECKBOX_XPATH))
                '''Click Next'''
                self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                '''Click Finish'''
                self.onClick((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
            logger.info("Cleanup Initiated successfully")
            addTestResultToReportSheet(filepath, Constants.CLEANUP_TEST, Constants.CLEANUP_HEADER, data,
                                       Constants.COMPLETED)

