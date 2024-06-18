from selenium.webdriver.common.by import By
from Utilities.CommonWebPageActions import CommonWebPageActions
from Constants.ApiConstants import ApiConstants
from Utilities.utils import getApiResponse
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
from Utilities.utils import getCellValue
import traceback

class TechSupportActions(CommonWebPageActions):

    def __init__(self, driver):

        super().__init__(driver)
        self.driver = driver


    def techSupport(self, data, filepath, logger):
        try:
            '''
            This function will generate tech support
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            description = data["description"]
            logger.info(Constants.TECH_SUPPORT_INITIATED_SUCCESSFULLY)
            if description:
                # To click settings section
                self.onClick((By.XPATH, XpathConstants.SETTINGS_SECTION_XPATH))
                # To click tech support 
                self.onClick((By.XPATH, XpathConstants.TECH_SUPPORT_XPATH))
                # click on generate 
                self.onClick((By.XPATH, XpathConstants.ADD_BUTTON_XPATH))
                self.clearInputFields((By.XPATH, XpathConstants.DESCRIPTION_INPUT_TEXTBOX))
                # to enter hostName
                self.sendInputKeys((By.XPATH, XpathConstants.DESCRIPTION_INPUT_TEXTBOX), description)
                # click on generate 
                self.onClick((By.XPATH, XpathConstants.GENERATE_BUNDLE_BUTTON_XPATH))
                messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                closeButton = self.findElement((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                if closeButton:
                    self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                logger.info(messagePopup)
                addTestResultToReportSheet(filepath, Constants.TECH_SUPPORT_TEST, Constants.TECH_SUPPORT_HEADER, data, messagePopup)
            else:
                logger.error(Constants.INVALID_TECH_SUPPORT_FIELDS)
                addTestResultToReportSheet(filepath, Constants.TECH_SUPPORT_TEST, Constants.TECH_SUPPORT_HEADER, data, Constants.INVALID_TECH_SUPPORT_FIELDS)
            logger.info(Constants.TECH_SUPPORT_GENERATED_SUCCESSFULLY)

        except Exception:
            logger.error(traceback.format_exc())
