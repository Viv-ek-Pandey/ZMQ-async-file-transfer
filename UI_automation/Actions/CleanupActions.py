from selenium.webdriver.common.by import By
from Utilities.CommonWebPageActions import CommonWebPageActions
from Constants.ApiConstants import ApiConstants
from Utilities.utils import getApiResponse
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
from Utilities.utils import getCellValue
import traceback


class CleanupActions(CommonWebPageActions):

    def __init__(self, driver):

        super().__init__(driver)
        self.driver = driver


    def cleanup(self, data, filepath, logger):
        try:
            '''
            This function will execute cleanup activity
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.CLEANUP_INITIATED_SUCCESSFULLY)
            protectionPlans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
            protectionPlanName = data["protectionPlan"]
            virtualMachine = data["virtualMachine"]
            resultList = []
            for eachProtectionPlan in protectionPlans:
                if protectionPlanName == eachProtectionPlan["name"]:
                    logger.info(Constants.CLEANUP_STARTED_WITH_PROTECTION_PLAN.format(protectionPlanName))
                    # To click configure section
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    # To find and click actual protection plan section
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
                    # To find and click actual protection plan element
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlanName)))
                    # To click on Actions
                    self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                    # To click on Cleanup
                    self.onClick((By.XPATH, XpathConstants.CLEANUP_BUTTON_XPATH))
                    # Find Modal Content is visible
                    self.findElement((By.XPATH, XpathConstants.MODAL_CONTENT_XPATH))
                    for eachMachine in virtualMachine:
                        # Clear search box
                        self.clearInputFields((By.XPATH, XpathConstants.RECOVERY_SITE_OPERATIONS_SEARCH_BOX_XPATH))
                        self.onEnter((By.XPATH, XpathConstants.RECOVERY_SITE_OPERATIONS_SEARCH_BOX_XPATH))
                        # Enter data into search box
                        self.sendInputKeys((By.XPATH, XpathConstants.RECOVERY_SITE_OPERATIONS_SEARCH_BOX_XPATH), eachMachine)
                        self.onEnter((By.XPATH, XpathConstants.RECOVERY_SITE_OPERATIONS_SEARCH_BOX_XPATH))
                        # Click Virtual Machine checkbox
                        self.onClick((By.XPATH, XpathConstants.TEST_RECOVERY_VM_CHECKBOX_XPATH))
                    # Click Next
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    # Click Finish
                    self.onClick((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
                    # Close Popup Message
                    self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                    # Click Monitor Section
                    self.onClick((By.XPATH, XpathConstants.MONITOR_SECTION_XPATH))
                    # Click Event Section
                    self.onClick((By.XPATH, XpathConstants.EVENT_SECTION_XAPTH))
                    # Wait Until Search box is not visible
                    self.findElement((By.XPATH, XpathConstants.EVENTS_TABLE_XPATH))
                    self.findElement((By.XPATH, XpathConstants.EVENT_SEARCH_BOX_XPATH))
                    # Clear Search Box
                    for eachMachine in virtualMachine:
                    # Clear search box
                        self.clearInputFields((By.XPATH, XpathConstants.EVENT_SEARCH_BOX_XPATH))
                        self.onEnter((By.XPATH, XpathConstants.EVENT_SEARCH_BOX_XPATH))
                        # Enter data into search box
                        self.sendInputKeys((By.XPATH, XpathConstants.EVENT_SEARCH_BOX_XPATH), eachMachine)
                        self.onEnter((By.XPATH, XpathConstants.EVENT_SEARCH_BOX_XPATH))
                        # To find event table
                        self.findElement((By.XPATH, XpathConstants.EVENTS_TABLE_XPATH))
                        self.findElement((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                        self.onClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))
                        result = getCellValue(self, 'Description', 0)
                        logger.info(result)
                        addTestResultToReportSheet(filepath, Constants.CLEANUP_TEST, Constants.HEADER, data, result)
                        if Constants.CLEANUP_COMPLETED_SUCCESSFULLY.format(eachMachine) in result:
                            resultList.append(Constants.TRUE)
                        else:
                            resultList.append(Constants.FALSE)
                    if Constants.FALSE not in resultList:
                        return Constants.PASSED
                    else:
                        return Constants.FAILED

            logger.error(Constants.PROTECTION_PLAN_NOT_FOUND)
            addTestResultToReportSheet(filepath, Constants.CLEANUP_TEST, Constants.HEADER, data, Constants.PROTECTION_PLAN_NOT_FOUND)

        except Exception:
            logger.error(traceback.format_exc())
