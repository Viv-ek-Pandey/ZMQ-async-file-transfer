from Constants.ApiConstants import ApiConstants
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from Utilities.utils import getApiResponse
from Actions.PplanActions import PplanActions
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
import traceback


class ReverseActions(CommonWebPageActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.ProtectionPlanActions = PplanActions(self.driver)


    def executeReverse(self, data, filepath, logger):
        try:
            '''
            this function will execute reverse
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.REVERSE_INITIATED)
            protectionPlanName = data["protectionPlan"]
            reverseSuffix = data["reverseSuffix"]
            protectionPlans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
            for eachProtectionPlan in protectionPlans:
                if protectionPlanName == eachProtectionPlan["name"]:
                    logger.info(Constants.REVERSE_STARTED_WITH_PROTECTION_PLAN.format(protectionPlanName))
                    # To click configure section
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    # To click actual protection plan section
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
                    # Click on actual protection plan name
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlanName)))
                    # Click on Actions
                    self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                    # Click on reverse
                    self.onClick((By.XPATH, XpathConstants.REVERSE_BUTTON_XPATH))
                    # To find modal content
                    self.findElement((By.XPATH, XpathConstants.MODAL_CONTENT_XPATH))
                    # Click on next
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click on next
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click on next
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Enter Suffix value
                    self.sendInputKeys((By.XPATH, XpathConstants.REVERSE_SUFFIX_XPATH), reverseSuffix)
                    # Click on next
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click on next
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click on next
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click on finish
                    self.onClick((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
                    messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                    # Close popup message
                    self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                    # To click configure section
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    logger.info(messagePopup)
                    addTestResultToReportSheet(
                        filepath, Constants.REVERSE_TEST, Constants.HEADER, data, messagePopup)
                    if Constants.REVERSE_CONFIGURED in messagePopup:
                        return Constants.PASSED
                    else:
                        return Constants.FAILED

            logger.error(Constants.PROTECTION_PLAN_NOT_FOUND)
            addTestResultToReportSheet(filepath, Constants.REVERSE_TEST, Constants.HEADER, data, Constants.PROTECTION_PLAN_NOT_FOUND)
        
        except Exception:
            logger.error(traceback.format_exc())
