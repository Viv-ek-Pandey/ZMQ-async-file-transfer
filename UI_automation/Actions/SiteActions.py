from Constants.ApiConstants import ApiConstants
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
from Utilities.XLUtils import addTestResultToReportSheet
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from Utilities.utils import checkNodeAndClickSiteSection, checkGivenSitePresent, getUpdatedData, setOtherSiteFields
import traceback


class SiteActions(CommonWebPageActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

   
    def addSite(self, data, logger, filepath):
        try:
            '''
            Add Sites
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            To find the site table
            '''
            logger.info(Constants.SITE_ADD_INITIATED_SUCCESSFULLY)
            self.findElement((By.XPATH, XpathConstants.SITE_TABLE_XPATH))

            # get all the input fields data 
            name = data.get('name')
            description = data.get('description')
            siteType = data.get('siteType')
            platformType = data.get('platformType')
            node = data.get('node')
            nodeName = node.split(' (')

            # check if the node name provided in the json data is present in the UI or has been added
            nodePresent = checkNodeAndClickSiteSection(self, nodeName[0])

            # if given node is present then perform further operations
            if nodePresent:
                logger.info(Constants.NODE_FOUND)
                # first fill in all the fields which are common in all platforms i.e vmware, aws, gcp and azure
                if name and description and siteType and platformType and node:
                    logger.info(Constants.VALID_SITE_FIELDS)
                    # click on new button in site page
                    self.onClick((By.XPATH, XpathConstants.ADD_BUTTON_XPATH))
                    # clear site name textbox
                    self.clearInputFields((By.XPATH, XpathConstants.SITE_NAME_XPATH))
                    # enter site name
                    self.sendInputKeys((By.XPATH, XpathConstants.SITE_NAME_XPATH), name)
                    # clear site description 
                    self.clearInputFields((By.XPATH, XpathConstants.SITE_DESCRIPTION_XPATH))
                    # enter site site description
                    self.sendInputKeys((By.XPATH, XpathConstants.SITE_DESCRIPTION_XPATH), description)
                    # select site type
                    self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_TYPE_XPATH), siteType)
                    # select platfrom type
                    self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_PLATFORM_TYPE_XPATH), platformType)
                    # select node
                    self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_NODE_XPATH), node)
                    # for the fields which are different as per platform fill them
                    setOtherSiteFields(self, data, logger)
                    # click configure button
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_BUTTON_XPATH))
                    messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                    # Close success message popup
                    self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                    closeButton = self.findElement((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                    if closeButton:
                        self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                    logger.info(messagePopup)
                    addTestResultToReportSheet(filepath, Constants.SITE_TEST, Constants.SITE_HEADER, data, messagePopup)
                    if Constants.SITE_CREATED in messagePopup:
                        return Constants.PASSED
                    else:
                        return Constants.FAILED
                else:
                    logger.info(Constants.INVALID_SITE_FIELDS.format(name))
                    addTestResultToReportSheet(filepath, Constants.SITE_TEST, Constants.SITE_HEADER, data, Constants.INVALID_SITE_FIELDS.format(name))
                    return Constants.FAILED
            else:
                self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                logger.error(Constants.NODE_NOT_FOUND)
                addTestResultToReportSheet(filepath, Constants.SITE_TEST, Constants.SITE_HEADER, data, Constants.NODE_NOT_FOUND)
                return Constants.FAILED

        except Exception:
            logger.error(traceback.format_exc())


    def editSite(self, data, logger, filepath):
        try:
            '''
            Edit Site
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.SITE_EDIT_INITIATED_SUCCESSFULLY)
            siteCount = 0
            for test in data:
                # To find the site table
                self.findElement((By.XPATH, XpathConstants.SITE_TABLE_XPATH))
                # get all the input fields data  
                name = test.get('name')
                description = test.get('description')
                siteType = test.get('siteType')
                platformType = test.get('platformType')
                node = test.get('node')
                # check if the node name provided in the json data is present in the UI or has been added
                isSitePresent = checkGivenSitePresent(self, name)
                # if given node is present then perform further operations
                if isSitePresent:
                    logger.info(Constants.SITE_PRESENT)
                    # first fill in all the fields which are common in all platforms i.e vmware, aws, gcp and azure
                    if name and description and siteType and platformType and node:
                        logger.info(Constants.VALID_SITE_FIELDS)
                        # click site checkbox
                        self.onClick((By.XPATH, XpathConstants.SITE_CHECKBOX_XPATH.format(siteCount)))
                        # click on new button in site page'''
                        self.onClick((By.XPATH, XpathConstants.EDIT_XPATH))
                        # clear site name 
                        self.clearInputFields((By.XPATH, XpathConstants.SITE_NAME_XPATH))
                        # enter site name
                        self.sendInputKeys((By.XPATH, XpathConstants.SITE_NAME_XPATH), name)
                        # clear site description 
                        self.clearInputFields((By.XPATH, XpathConstants.SITE_DESCRIPTION_XPATH))
                        # enter site site description
                        self.sendInputKeys((By.XPATH, XpathConstants.SITE_DESCRIPTION_XPATH), description)
                        # select site type
                        self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_TYPE_XPATH), siteType)
                        # select site type
                        self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_PLATFORM_TYPE_XPATH),platformType)
                        # select node
                        self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_NODE_XPATH), node)
                        # for the fields which are different as per platform fill them
                        setOtherSiteFields(self, test, logger)
                        # click configure button
                        self.onClick((By.XPATH, XpathConstants.CONFIGURE_BUTTON_XPATH))
                        messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                        # Close success message popup
                        self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                        closeButton = self.findElement((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                        if closeButton:
                            self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                        siteCount = siteCount + 1
                        logger.info(messagePopup)
                        addTestResultToReportSheet(filepath, Constants.SITE_TEST, Constants.SITE_HEADER, test, messagePopup)
                        if Constants.SITE_CREATED in messagePopup:
                            return Constants.PASSED
                        else:
                            return Constants.FAILED
                    else:
                        logger.info(Constants.INVALID_SITE_FIELDS.format(name))
                        addTestResultToReportSheet(filepath, Constants.SITE_TEST, Constants.SITE_HEADER, test, Constants.INVALID_SITE_FIELDS.format(name))
                        return Constants.FAILED

                else:
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    logger.error(Constants.SITE_NOT_PRESENT)
                    addTestResultToReportSheet(filepath, Constants.SITE_TEST, Constants.SITE_HEADER, test, Constants.SITE_NOT_PRESENT)
                    return Constants.FAILED

        except Exception:
            logger.error(traceback.format_exc())


    def deleteSite(self, data, logger, filepath):
        try:
            '''
            Delete sites
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            logger.info(Constants.SITE_DELETE_INITIATED_SUCCESSFULLY)
            site = getUpdatedData(self, ApiConstants.GET_SITES)
            isSitePresent = checkGivenSitePresent(self, data["name"])
            if isSitePresent:
                logger.info(Constants.SITE_PRESENT)
                for ind, res in enumerate(site):
                    if res["name"] == data["name"]:
                        # checks the checkbox to delete site
                        self.onClick((By.XPATH, XpathConstants.SITE_CHECKBOX_XPATH.format(ind)))
                        # Click on Remove button
                        self.onClick((By.XPATH, XpathConstants.REMOVE_BUTTON_XPATH))
                        # Click Confirm button
                        self.onClick((By.XPATH, XpathConstants.CONFIRM_BUTTON_XPATH))
                        messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                        # Close message popup
                        self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
                        closeButton = self.findElement((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                        if closeButton:
                            self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                        logger.info(messagePopup)
                        addTestResultToReportSheet(filepath, Constants.SITE_TEST, Constants.SITE_DELETE_HEADER, data, messagePopup)
                        if Constants.SITE_DELETED in messagePopup:
                            return Constants.PASSED
                        else:
                            return Constants.FAILED
            else:
                logger.error(Constants.SITE_NOT_PRESENT)
                addTestResultToReportSheet(filepath, Constants.SITE_TEST, Constants.SITE_DELETE_HEADER, data, Constants.SITE_NOT_PRESENT)
                return Constants.FAILED

        except Exception:
            logger.error(traceback.format_exc())
            