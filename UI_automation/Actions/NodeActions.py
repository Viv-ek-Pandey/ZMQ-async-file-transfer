from Constants.ApiConstants import ApiConstants
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
from Utilities.XLUtils import addTestResultToReportSheet
from Utilities.utils import getUpdatedData, isNodePresent
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
import traceback


class NodeActions(CommonWebPageActions):

    def __init__(self, driver):

        super().__init__(driver)
        self.driver = driver


    def addNode(self, data, filepath, logger):
        try:
            '''
            Add Node
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.ADD_NODE_INITIATED)
            name = data.get('name')
            hostName = data.get('hostname')
            uname = data.get('username')
            password = data.get('password')
            nodeType = data.get('nodeType')
            platformType = data.get('platformType')

            # check if all the required fields are available
            if name and hostName and uname and password and nodeType and platformType:
                logger.info(Constants.VALID_NODE_FIELDS)
                # To find the node table
                self.findElement((By.XPATH, XpathConstants.NODE_TABLE_XPATH))
                # To click add button 
                self.onClick((By.XPATH, XpathConstants.ADD_BUTTON_XPATH))
                # enter node name
                self.sendInputKeys(
                    (By.XPATH, XpathConstants.NODE_NAME_XPATH), name)
                # enter hostname
                self.sendInputKeys(
                    (By.XPATH, XpathConstants.HOSTNAME_XPATH), hostName)
                # enter username
                self.sendInputKeys(
                    (By.XPATH, XpathConstants.NODE_USERNAME_XPATH), uname)
                # enter password
                self.sendInputKeys(
                    (By.XPATH, XpathConstants.NODE_PASSWORD_XPATH), password)
                # enter node type
                self.singleSelectFromDropdown(
                    (By.XPATH, XpathConstants.NODE_TYPE_XPATH), nodeType)
                # enter platform type
                self.singleSelectFromDropdown(
                    (By.XPATH, XpathConstants.NODE_PLATFORM_TYPE_XPATH), platformType)
                # click configure button
                self.onClick(
                    (By.XPATH, XpathConstants.CONFIGURE_BUTTON_XPATH))
                messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                # Close message popup
                self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                closeButton = self.findElement((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                if closeButton:
                    self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                # add the test result into the excel file
                logger.info(messagePopup)
                addTestResultToReportSheet(filepath, Constants.NODE_TEST, Constants.NODE_ADD_HEADER, data, messagePopup)
                if Constants.NODE_CONFIGURED in messagePopup:
                    return Constants.PASSED
                else:
                    return Constants.FAILED
            else:
                addTestResultToReportSheet(filepath, Constants.NODE_TEST, Constants.NODE_ADD_HEADER, data, Constants.INVALID_NODE_FIELDS)
                logger.warning(Constants.INVALID_NODE_FIELDS)
                return Constants.FAILED

        except Exception:
            logger.error(traceback.format_exc())
    

    def editNode(self, data, logger, filepath):
        try:
            '''
            Edit Node
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.NODE_EDIT_INITIATED_SUCCESSFULLY)
            response = getUpdatedData(self, ApiConstants.GET_NODE_LIST)
            nodePresent = isNodePresent(self, data["name"])
            hostName = data.get('hostname')
            uname = data.get('username')
            password = data.get('password')
            if nodePresent:
                logger.info(Constants.NODE_FOUND)
                for ind, res in enumerate(response):
                    if res["name"] == data["name"]:
                        # checks the checkbox to edit node
                        self.onClick(
                            (By.XPATH, XpathConstants.NODE_CHECKBOX_XPATH.format(ind)))
                        # To click on edit button
                        self.onClick(
                            (By.XPATH, XpathConstants.EDIT_XPATH))
                        if hostName and uname and password:
                            logger.info(Constants.VALID_NODE_FIELDS)
                            # To find the node table
                            self.findElement((By.XPATH, XpathConstants.NODE_TABLE_XPATH))
                            # Clear hostName
                            self.clearInputFields((By.XPATH, XpathConstants.HOSTNAME_XPATH))
                            # to enter hostName
                            self.sendInputKeys(
                                (By.XPATH, XpathConstants.HOSTNAME_XPATH), hostName)
                            # Clear username
                            self.clearInputFields((By.XPATH, XpathConstants.NODE_USERNAME_XPATH))
                            # to enter username
                            self.sendInputKeys(
                                (By.XPATH, XpathConstants.NODE_USERNAME_XPATH), uname)
                            # Clear password'''
                            self.clearInputFields((By.XPATH, XpathConstants.NODE_PASSWORD_XPATH))
                            # to enter password
                            self.sendInputKeys(
                                (By.XPATH, XpathConstants.NODE_PASSWORD_XPATH), password)
                            # Click on configure button
                            self.onClick(
                                (By.XPATH, XpathConstants.CONFIGURE_BUTTON_XPATH))
                            messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                            # Close message popup
                            self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                            closeButton = self.findElement((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                            if closeButton:
                                self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                            logger.info(messagePopup)
                            addTestResultToReportSheet(filepath, Constants.NODE_TEST, Constants.NODE_HEADER, data, messagePopup)
                            if Constants.NODE_CONFIGURED in messagePopup:
                                return Constants.PASSED
                            else:
                                return Constants.FAILED
                        else:
                            logger.info(Constants.INVALID_NODE_FIELDS)
                            addTestResultToReportSheet(filepath, Constants.NODE_TEST, Constants.NODE_HEADER,
                                                       data, Constants.INVALID_NODE_FIELDS)
                            return Constants.FAILED
            else:
                logger.info(Constants.NODE_NOT_FOUND)
                addTestResultToReportSheet(filepath, Constants.NODE_TEST, Constants.NODE_HEADER, data,
                                       Constants.NODE_NOT_FOUND)
                return Constants.FAILED

        except Exception:
            logger.error(traceback.format_exc())
    
    
    def offlineNode(self, data, logger, filepath):
        try:
            '''
            Offline Node
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.NODE_OFFLINE_INITIATED_SUCCESSFULLY)
            response = getUpdatedData(self, ApiConstants.GET_NODE_LIST)
            nodePresent = isNodePresent(self, data["name"])
            if nodePresent:
                logger.info(Constants.NODE_FOUND)
                for ind, res in enumerate(response):
                    if res["name"] == data["name"]:
                        # checks the checkbox to delete node
                        self.onClick(
                            (By.XPATH, XpathConstants.NODE_CHECKBOX_XPATH.format(ind)))
                        # click on offline button to offline node
                        self.onClick(
                            (By.XPATH, XpathConstants.NODE_OFFLINE_BUTTON_XPATH))
                        # Click on confirm button
                        self.onClick(
                            (By.XPATH, XpathConstants.CONFIRM_BUTTON_XPATH))
                        messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                        # close sucess message popup
                        self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                        closeButton = self.findElement((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                        if closeButton:
                            self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                        logger.info(messagePopup)
                        addTestResultToReportSheet(filepath, Constants.NODE_TEST, Constants.NODE_HEADER, data, messagePopup)
                        if Constants.NODE_OFFLINE_SUCCESSFULLY.format(data["name"]) in messagePopup:
                            return Constants.PASSED
                        else:
                            return Constants.FAILED
            else:
                logger.info(Constants.NODE_NOT_FOUND)
                addTestResultToReportSheet(filepath, Constants.NODE_TEST, Constants.NODE_HEADER, data,
                                       Constants.NODE_NOT_FOUND)
                return Constants.FAILED

        except Exception:
            logger.error(traceback.format_exc())


    def onlineNode(self, data, logger, filepath):
        try:
            '''
            Online Node
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.NODE_ONLINE_INITIATED_SUCCESSFULLY)
            response = getUpdatedData(self, ApiConstants.GET_NODE_LIST)
            nodePresent = isNodePresent(self, data["name"])
            if nodePresent:
                logger.info(Constants.NODE_FOUND)
                for ind, res in enumerate(response):
                    if res["name"] == data["name"]:
                        # checks the checkbox to delete node
                        self.onClick(
                            (By.XPATH, XpathConstants.NODE_CHECKBOX_XPATH.format(ind)))
                        # click on offline button to offline node
                        self.onClick(
                            (By.XPATH, XpathConstants.NODE_ONLINE_BUTTON_XPATH))
                        # Click confirm button
                        self.onClick(
                            (By.XPATH, XpathConstants.CONFIRM_BUTTON_XPATH))
                        messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                        # Close success message popup
                        self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                        closeButton = self.findElement((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                        if closeButton:
                            self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                        logger.info(messagePopup)
                        addTestResultToReportSheet(filepath, Constants.NODE_TEST, Constants.NODE_HEADER, data, messagePopup)
                        if Constants.NODE_ONLINE_SUCCESSFULLY.format(data["name"]) in messagePopup:
                            return Constants.PASSED
                        else:
                            return Constants.FAILED
            else:
                logger.info(Constants.NODE_NOT_FOUND)
                addTestResultToReportSheet(filepath, Constants.NODE_TEST, Constants.NODE_HEADER, data,
                                       Constants.NODE_NOT_FOUND)
                return Constants.FAILED

        except Exception:
            logger.error(traceback.format_exc())
    
    
    def deleteNode(self, data, logger, filepath):
        try:
            '''
            Delete Node
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.NODE_DELETE_INITIATED_SUCCESSFULLY)
            response = getUpdatedData(self, ApiConstants.GET_NODE_LIST)
            nodePresent = isNodePresent(self, data["name"])
            if nodePresent:
                logger.info(Constants.NODE_FOUND)
                for ind, res in enumerate(response):
                    if res["name"] == data["name"]:
                        # checks the checkbox to delete node
                        self.onClick(
                            (By.XPATH, XpathConstants.NODE_CHECKBOX_XPATH.format(ind)))
                        # click on remove button to delete node
                        self.onClick(
                            (By.XPATH, XpathConstants.REMOVE_BUTTON_XPATH))
                        # click on confirm button to delete node
                        self.onClick(
                            (By.XPATH, XpathConstants.CONFIRM_BUTTON_XPATH))
                        messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                        # Close message popup
                        self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                        closeButton = self.findElement((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                        if closeButton:
                            self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                        logger.info(messagePopup)
                        addTestResultToReportSheet(filepath, Constants.NODE_TEST, Constants.NODE_HEADER, data, messagePopup)
                        if Constants.NODE_DELETE_SUCCESSFULLY in messagePopup:
                            return Constants.PASSED
                        else:
                            return Constants.FAILED
            else:
                logger.info(Constants.NODE_NOT_FOUND)
                addTestResultToReportSheet(filepath, Constants.NODE_TEST, Constants.NODE_HEADER, data, Constants.NODE_NOT_FOUND)
                return Constants.FAILED

        except Exception:
            logger.error(traceback.format_exc())
