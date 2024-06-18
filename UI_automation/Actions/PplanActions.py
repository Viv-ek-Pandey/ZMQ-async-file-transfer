from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from Utilities.utils import validateIfGivenSiteIsPresent, configureProtectionPlan, checkJobStatusOfVirtualMachine
from Utilities.XLUtils import addTestResultToReportSheet
import traceback


class PplanActions(CommonWebPageActions):
    
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    
    def addProtectionPlan(self, data, filepath, logger):
        try:
            '''
            Add Protection Plan
            data: json data received from json file
            filepath: absolute file path where reports willbe created
            logger: logger object
            '''
            logger.info(Constants.PROTECTION_PLAN_CREATION_INITIATED_SUCCESSFULLY)
            # To find the protection plan table
            self.findElement((By.XPATH, XpathConstants.TABLE_XPATH))
            validateGivenSiteIsPresent = validateIfGivenSiteIsPresent(self, data, logger)
            if not validateGivenSiteIsPresent:
                addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST,
                                       Constants.PROTECTION_PLAN_HEADER, data, Constants.SITE_NOT_PRESENT)
                logger.error(Constants.SITE_NOT_PRESENT)
                return Constants.FAILED
            else:
                logger.info(Constants.SITE_PRESENT)
                # Click on Configure
                self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                # Click on Protection Plan
                self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
                # click on Add protection Plan button
                self.onClick((By.XPATH, XpathConstants.ADD_BUTTON_XPATH))
                # call configureProtectionPlan function from utils
                status = configureProtectionPlan(self, data, filepath, logger)
                addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER, data, Constants.PROTECTION_PLAN_CREATED)
                logger.info(Constants.PROTECTION_PLAN_CREATED)
                return status

        except Exception:
            logger.error(traceback.format_exc())

    
    def editProtectionPlan(self, data, filepath, logger):
        try:
            '''
            Edit Protection Plan
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.PROTECTION_PLAN_EDIT_INITIATED_SUCCESSFULLY)
            planName = data["protectionPlanName"]
            # Click on Configure
            self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
            # Click on Protection Plan
            self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
            checkIfPlanIsPresent = self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(planName)))
            if not checkIfPlanIsPresent:
                addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST,
                                       Constants.PROTECTION_PLAN_HEADER, planName, Constants.PROTECTION_PLAN_NOT_FOUND)
                logger.error(Constants.PROTECTION_PLAN_NOT_FOUND)
                return Constants.FAILED
            else:
                logger.info(Constants.PROTECTION_PLAN_PRESENT)
                # Click on Particular Plan
                self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(planName)))
                # Click Actions
                self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                # Click Edit
                self.onClick((By.XPATH, XpathConstants.EDIT_BUTTON_XPATH))
                # call configureProtectionPlan function from utils
                status = configureProtectionPlan(self, data, filepath, logger)
                addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER, data, Constants.PROTECTION_PLAN_EDIT)
                logger.info(Constants.PROTECTION_PLAN_EDIT)
                return status

        except Exception:
            logger.error(traceback.format_exc())
    
    
    def stopProtectionPlan(self, data, filepath, logger):
        try:
            '''
            Stop Protection Plan
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            protectionPlan = data["pplanName"]
            logger.info(Constants.PROTECTION_PLAN_STOP_INITIATED_SUCCESSFULLY)
            checkIfPlanIsPresent = self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlan)))
            if not checkIfPlanIsPresent:
                addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER, data, Constants.PROTECTION_PLAN_NOT_FOUND)
                logger.error(Constants.PROTECTION_PLAN_NOT_FOUND)
            else:
                logger.info(Constants.PROTECTION_PLAN_PRESENT)
                    # Click on Particular Plan
                self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlan)))
                protectionPlanRunning = self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_RUNNING_XPATH))
                if protectionPlanRunning:
                    # Click Actions
                    self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                    # Click Stop
                    self.onClick((By.XPATH, XpathConstants.STOP_BUTTON_XPATH))
                    messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH))
                    messagePopup = messagePopup.text
                    self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_ELEMENT_XPATH))
                    addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER, data, messagePopup)
                    logger.info(messagePopup)
                    if Constants.PROTECTION_PLAN_STOP in messagePopup:
                        return Constants.PASSED
                    else:
                        return Constants.FAILED
                else:
                    protectionPlanStop = self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_STOP_XPATH))
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_ELEMENT_XPATH))
                    if protectionPlanStop:
                        addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER, data, Constants.PROTECTION_PLAN_ALREADY_STOP)
                        logger.warning(Constants.PROTECTION_PLAN_ALREADY_STOP)
                        return Constants.PASSED

        except Exception:
            logger.error(traceback.format_exc())
    
    
    def startProtectionPlan(self, data, filepath, logger):
        try:
            '''
            Start Protection Plan
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            protectionPlan = data["pplanName"]
            logger.info(Constants.PROTECTION_PLAN_START_INITIATED_SUCCESSFULLY)
            checkIfPlanIsPresent = self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlan)))
            if not checkIfPlanIsPresent:
                addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER, data, Constants.PROTECTION_PLAN_NOT_FOUND)
                logger.error(Constants.PROTECTION_PLAN_NOT_FOUND)
            else:
                logger.info(Constants.PROTECTION_PLAN_PRESENT)
                # Click on Particular Plan
                self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlan)))
                protectionPlanStop = self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_STOP_XPATH))
                if protectionPlanStop:
                    # Click Actions
                    self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                    # Click Start
                    self.onClick((By.XPATH, XpathConstants.START_BUTTON_XPATH))
                    messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH))
                    messagePopup = messagePopup.text
                    self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                    # click protection plan
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_ELEMENT_XPATH))
                    addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER, data, messagePopup)
                    logger.info(messagePopup)
                    if Constants.PROTECTION_PLAN_START in messagePopup:
                        return Constants.PASSED
                    else:
                        return Constants.FAILED
                else:
                    protectionPlanRunning = self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_RUNNING_XPATH))
                    # click protection plan
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_ELEMENT_XPATH))
                    if protectionPlanRunning:
                        addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER, data, Constants.PROTECTION_PLAN_ALREADY_STARTED)
                        logger.warning(Constants.PROTECTION_PLAN_ALREADY_STARTED)
                        return Constants.PASSED
        
        except Exception:
            logger.error(traceback.format_exc())

    
    def deleteProtectionPlan(self, data, filepath, logger):
        try:
            '''
            Delete Protection Plan
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            protectionPlan = data["pplanName"]
            virtualMachine = data["virtualMachine"]
            logger.info(Constants.PROTECTION_PLAN_DELETE_INITIATED_SUCCESSFULLY)
            checkIfPlanIsPresent = self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlan)))
            if not checkIfPlanIsPresent:
                addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER, data, Constants.PROTECTION_PLAN_NOT_FOUND)
                logger.error(Constants.PROTECTION_PLAN_NOT_FOUND)
            else:
                logger.info(Constants.PROTECTION_PLAN_PRESENT)
                # Click on Particular protection Plan'''
                self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlan)))
                protectionPlanRunning = self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_RUNNING_XPATH))
                if protectionPlanRunning:
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
                        checkJobStatusOfVirtualMachine(self, machine, filepath, logger)
                    self.scrollTopToFindElement()
                    # Click Actions
                    self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                    # Click Stop
                    self.onClick((By.XPATH, XpathConstants.STOP_BUTTON_XPATH))
                    # Click Actions
                    self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                    # Click Remove
                    self.onClick((By.XPATH, XpathConstants.REMOVE_XPATH))
                    # click confirm button
                    self.onClick((By.XPATH, XpathConstants.CONFIRM_BUTTON_XPATH))
                    messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH))
                    messagePopup = messagePopup.text
                    # click protection plan
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_ELEMENT_XPATH))
                    addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER, data, messagePopup)
                    logger.info(messagePopup)
                    if Constants.PROTECTION_PLAN_DELETE in messagePopup:
                        return Constants.PASSED
                    else:
                        return Constants.FAILED
                else:
                    protectionPlanStop = self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_STOP_XPATH))
                    if protectionPlanStop:
                        # Click Actions
                        self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                        # Click Remove
                        self.onClick((By.XPATH, XpathConstants.REMOVE_XPATH))
                        # click confirm 
                        self.onClick((By.XPATH, XpathConstants.CONFIRM_BUTTON_XPATH))
                        messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH))
                        messagePopup = messagePopup.text
                        # click protection plan
                        self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_ELEMENT_XPATH))
                        addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER, data, messagePopup)
                        logger.info(messagePopup)
                        if Constants.PROTECTION_PLAN_DELETE in messagePopup:
                            return Constants.PASSED
                        else:
                            return Constants.FAILED
        
        except Exception:
            logger.error(traceback.format_exc())
