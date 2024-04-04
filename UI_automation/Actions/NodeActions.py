from Constants.ApiConstants import ApiConstants
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
from Utilities.XLUtils import addTestResultToReportSheet
from Utilities.utils import getApiResponse
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class NodeActions(CommonWebPageActions):

    def __init__(self, driver):

        super().__init__(driver)
        self.driver = driver

    def add_node(self, data, filepath, logger):
        """loop through the test data"""
        name = data.get('name')
        hostname = data.get('hostname')
        uname = data.get('username')
        password = data.get('password')
        node_type = data.get('nodeType')
        platform_type = data.get('platformType')
        result = Constants.FAILED
        isClean = True

        '''check if all the required fields are available'''
        if name and hostname and uname and password and node_type and platform_type:

            '''To find the node table'''
            self.findElement((By.XPATH, XpathConstants.NODE_TABLE_XPATH))
            ''' fill all the fields in the node modal  '''

            self.onClick((By.XPATH, XpathConstants.ADD_BUTTON_XPATH))
            self.sendInputKeys(
                (By.XPATH, XpathConstants.NODE_NAME_XPATH), name)
            self.sendInputKeys(
                (By.XPATH, XpathConstants.HOSTNAME_XPATH), hostname)
            self.sendInputKeys(
                (By.XPATH, XpathConstants.NODE_USERNAME_XPATH), uname)
            self.sendInputKeys(
                (By.XPATH, XpathConstants.NODE_PASSWORD_XPATH), password)
            self.singleSelectFromDropdown(
                (By.XPATH, XpathConstants.NODE_TYPE_XPATH), node_type)
            self.singleSelectFromDropdown(
                (By.XPATH, XpathConstants.NODE_PLATFORM_TYPE_XPATH), platform_type)

            del self.driver.requests

            ''' after validating click on configure button '''
            self.onClick(
                (By.XPATH, XpathConstants.CONFIGURE_BUTTON_XPATH))

            response = getApiResponse(self, ApiConstants.GET_NODE_LIST)

            '''if there is any error on any field then it will be captured in validateNodeFields function'''
            validate = self.validateNodeFields()

            if validate:

                '''if error in the response then close the error message on the ui screen'''
                if isinstance(response, str):
                    isClean = False
                    '''if error message appears on the screen close the error message to move further'''
                    crossBtn = self.findElement(
                        (By.XPATH, XpathConstants.ERROR_MESSAGE_POPUP_XPATH))
                    if crossBtn is not None:
                        self.onClick(
                            (By.XPATH, XpathConstants.ERROR_MESSAGE_POPUP_XPATH))

                    '''close node modal'''
                    self.onClick(
                        (By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                    result = response

                    '''add the error to the log'''
                    logger.error(f"Node creation failed for node {name} : {response}")

                elif isinstance(response, dict):
                    '''if node created successfully then also info message come on the ui need to close that info 
                    message as well to move further'''
                    if response.get('name') is not None or response.get('name') == name:
                        self.onClick(
                            (By.XPATH, XpathConstants.SUCCESS_MESSAGE_POPUP_XPATH))
                        logger.info("response created successfully")
                        result = Constants.SUCCESS
            else:
                isClean = False
                '''if validation fails then need to close the modal'''
                self.onClick(
                    (By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                result = Constants.FAILED_FIELD.format(validate)
                logger.warning(f"Validation failed for node {name} fields")
        else:
            isClean = False
            '''if one of the required fields is not provided the log the warning message i  n the log file'''
            logger.warning("One or more node field is not provided")
            result = Constants.FAILED_NODE_FIELD_NOT_PROVIDED

        '''add the test result into the excel file'''
        addTestResultToReportSheet(
            filepath, Constants.NODE_TEST, Constants.NODE_HEADER, data, result)
        return isClean

    def delete_node(self, data):
        response = self.getUpdatedNodeData()
        isNodePresent = self.isNodePresent(data)
        if len(response) != 0 and isNodePresent:
            name = data
            result = ""
            isDeleted = False
            if name:
                for ind, res in enumerate(response):
                    if res["name"] == name:
                        nodeID = res["id"]
                        '''checks the checkbox to delete node'''
                        self.onClick(
                            (By.XPATH, XpathConstants.NODE_CHECKBOX_XPATH.format(ind)))
                        '''click on remove button to delete node'''
                        self.onClick(
                            (By.XPATH, XpathConstants.REMOVE_BUTTON_XPATH))
                        '''click on confirm button to delete node'''
                        self.onClick(
                            (By.XPATH, XpathConstants.CONFIRM_BUTTON_XPATH))

                        nodeURL = ApiConstants.GET_NODE_WITH_ID
                        nodeURL = nodeURL.replace("id", f"{nodeID}")
                        nodeRes = getApiResponse(self, nodeURL)

                        if 'Failed' in nodeRes:
                            self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                            result = Constants.NODE_NOT_DELETED
                            self.logger.error(result)

                        isNodePresent = self.findElement((By.XPATH, XpathConstants.NODE_NAME_XPATH.format(name)))
                        if isNodePresent is None:
                            isDeleted = True
                            self.logger.info(f"Successfully deleted {name} node")
                            result = Constants.NODE_DELETED
                        break

            if not isDeleted:
                return {"status": False, "result": result}
            else:
                return {"status": True, "result": result}

        else:
            self.logger.warning(f" {data} Node not found ")
            return {"status": False, "result": "Node not found"}

    def getUpdatedNodeData(self):
        """get updated data as we land on the nodes screen"""

        '''delete the previous node data in order to start fresh'''
        del self.driver.requests

        '''click on refresh icon to get the fresh data on UI screen'''
        self.onAnimationClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))

        return getApiResponse(self, ApiConstants.GET_NODE_LIST)

    def validateNodeFields(self):
        """ validate node fields """

        validate = ''
        try:
            ele = self.driver.find_element(
                By.XPATH, XpathConstants.HOSTNAME_ERROR_XPATH)
            validate = False
        except NoSuchElementException:
            validate = True

        try:
            ele = self.driver.find_element(
                By.XPATH, XpathConstants.NAME_ERROR_XPATH)
            validate = False
        except NoSuchElementException:
            validate = True

        try:
            ele = self.driver.find_element(
                By.XPATH, XpathConstants.NODE_USERNAME_ERROR_XPATH)
            validate = False
        except NoSuchElementException:
            validate = True

        try:
            ele = self.driver.find_element(
                By.XPATH, XpathConstants.NODE_PASSWORD_ERROR_XPATH)
            validate = False
        except NoSuchElementException:
            validate = True

        try:
            ele = self.driver.find_element(
                By.XPATH, XpathConstants.NODE_TYPE_ERROR_XPATH)
            validate = False
        except NoSuchElementException:
            validate = True
        return validate

    def isNodePresent(self, nodeName):
        node = self.findElement((By.XPATH, XpathConstants.NODE_XPATH.format(nodeName)))
        return node
