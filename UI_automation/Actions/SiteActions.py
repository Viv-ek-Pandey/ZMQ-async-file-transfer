from Constants.ApiConstants import ApiConstants
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
from Utilities.XLUtils import addTestResultToReportSheet
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from Utilities.utils import getApiResponse
from selenium.common.exceptions import NoSuchElementException


class SiteActions(CommonWebPageActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    """Add Sites"""
    def add_site(self, data, logger):

        """To find the site table"""

        self.findElement((By.XPATH, XpathConstants.SITE_TABLE_XPATH))

        ''' get all the input fields data  '''
        name = data.get('name')
        description = data.get('description')
        sitetype = data.get('siteType')
        platformtype = data.get('platformType')
        node = data.get('node')
        result = ''
        nodeName = node.split(' ')

        '''check if the node name provided in the json data is present in the UI or has been added'''
        isNodePresent = self.checkGivenNodePresent(nodeName[0])

        '''if given node is present then perform further operations'''
        if isNodePresent:

            '''first fill in all the fields which are common in all platforms i.e vmware, aws, gcp and azure'''
            if name and description and sitetype and platformtype and node:
                ''' click on new button in site page'''
                self.onClick((By.XPATH, XpathConstants.ADD_BUTTON_XPATH))

                ''' fill in all the common inputs fields '''

                self.sendInputKeys((By.XPATH, XpathConstants.SITE_NAME_XPATH), name)
                self.sendInputKeys((By.XPATH, XpathConstants.SITE_DESCRIPTION_XPATH), description)
                self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_TYPE_XPATH), sitetype)
                self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_PLATFORM_TYPE_XPATH),
                                              platformtype)
                self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_NODE_XPATH), node)

                '''for the fields which are different as per platform fill them'''
                resObj = self.setOtherSiteFields(data, logger)
                return resObj

        else:
            result = Constants.NODE_NOT_FOUND
            logger.error(result)
            return {"status": False, "result": result}

    def delete_site(self, delTestData, filepath, logger):

        """Delete sites"""

        site = getApiResponse(self, ApiConstants.GET_SITES)
        if len(site) != 0:
            for d in delTestData:
                result = ''
                siteName = d
                isNodePresent = self.checkGivenSitePresent(siteName)
                if isNodePresent is not None:
                    found = False
                    for ind, res in enumerate(site):
                        if res["name"] == siteName:
                            self.scrollToFindElement(
                                (By.XPATH, XpathConstants.SITE_CHECKBOX_XPATH.format(ind)))
                            self.onClick(
                                (By.XPATH, XpathConstants.SITE_CHECKBOX_XPATH.format(ind)))
                            self.scrollToFindElement(
                                (By.XPATH, XpathConstants.REMOVE_BUTTON_XPATH))
                            self.onClick(
                                (By.XPATH, XpathConstants.REMOVE_BUTTON_XPATH))
                            self.onClick(
                                (By.XPATH, XpathConstants.CONFIRM_BUTTON_XPATH))
                            found = True
                            break
                    if found:
                        result = Constants.SITE_DELETED
                    else:
                        result = Constants.SITE_NAME_NOT_FOUND
                else:
                    result = Constants.NODE_NOT_FOUND
                    logger.warning("Failed: {siteName} node not found")
                addTestResultToReportSheet(
                    filepath, Constants.SITE_TEST, Constants.SITE_DELETE_HEADER, d, result)

    def setOtherSiteFields(self, data, logger):
        """set site fields and configure site"""

        '''' get field data '''
        vcenter = data.get('vCenterServer')
        uname = data.get('Username')
        passrd = data.get('password')
        platformType = data.get('platformType')
        region = data.get('region')
        zone = data.get('zone')
        accessKey = data.get('accessKey')
        secretKey = data.get('secretKey')
        projectId = data.get('projectId')
        siteName = data['name']
        result = ''
        ''' fill in the data in inputs based on platform type'''
        match platformType:
            case Constants.VMware:
                if vcenter and uname and passrd:

                    self.sendInputKeys(
                        (By.XPATH, XpathConstants.VCENTER_XPATH), vcenter)
                    self.sendInputKeys(
                        (By.XPATH, XpathConstants.SITE_VCENTER_USERNAME_XPATH), uname)
                    self.sendInputKeys(
                        (By.XPATH, XpathConstants.SITE_VCENTER_PASSWORD_XPATH), passrd)
                else:
                    result = Constants.FIELDS_NOT_PROVIDED.format(siteName)
                    logger.warning(result)
                    return {"status": False, "result": result}

            case Constants.AWS:
                if region and accessKey and secretKey and zone:
                    self.singleSelectFromDropdown(
                        (By.XPATH, XpathConstants.SITE_AWS_REGION_XPATH), region)
                    self.singleSelectFromDropdown(
                        (By.XPATH, XpathConstants.SITE_AWS_ZONE_XPATH), zone)
                    self.sendInputKeys(
                        (By.XPATH, XpathConstants.ACCESS_KEY_XPATH), accessKey)
                    self.sendInputKeys(
                        (By.XPATH, XpathConstants.SECRET_KEY_XPATH), secretKey)
                else:
                    result = Constants.FIELDS_NOT_PROVIDED.format(siteName)
                    logger.warning(result)
                    return {"status": False, "result": result}

            case Constants.GCP:
                if region and zone and projectId:
                    self.singleSelectFromDropdown(
                        (By.XPATH, "//select[@id='configureSite.platformDetails.region']"), region)
                    self.singleSelectFromDropdown(
                        (By.XPATH, "//select[@id='configureSite.platformDetails.availZone']"), zone)
                    self.sendInputKeys(
                        (By.XPATH, "//input[@id='configureSite.platformDetails.projectId']"), projectId)
                else:
                    result = Constants.FIELDS_NOT_PROVIDED.format(siteName)
                    logger.warning(result)
                    return {"status": False, "result": result}

        ''' after filling in all the fields click on configure button'''
        resObj = self.configureSite(siteName, logger)
        return resObj

    def configureSite(self, siteName, logger):
        """configure site by clicking on configure button"""

        del self.driver.requests
        self.onClick((By.XPATH, XpathConstants.CONFIGURE_BUTTON_XPATH))
        status = False
        result = ""
        ''' below code will only get the api response for the url which we have provided '''
        siteResp = getApiResponse(self, ApiConstants.GET_SITES)
        '''  once all the fields are fill in check for validation i.e there is no red warnings for the inputs '''

        validate = self.validatedSiteField()

        if validate:
            if len(siteResp) != 0:
                if isinstance(siteResp, str):
                    '''after getting the resp we need to check if it's a str that means error if there is error need 
                    to close the wizard'''
                    self.onClick((By.XPATH, XpathConstants.ERROR_MESSAGE_POPUP_XPATH))
                    self.onClick(
                        (By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                    result = Constants.FAILD.format(siteResp)
                    logger.error(result)
                else:
                    isSiteCreated = self.checkGivenSitePresent(siteName)
                    if isSiteCreated:
                        status = True
                        result = Constants.SITE_CREATED.format(siteName)
                    else:
                        result = Constants.SITE_NOT_CREATED.format(siteName)
                    logger.info(result)
        else:

            ''' if the validation fails then  need to close the wizard'''
            result = Constants.VALIDATION_FAILED.format(siteName)
            logger.error(result)
            self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))

        return {"status": status, "result": result}

    def validatedSiteField(self):

        """check if all the required fields in the site is set and the fields does not have any errors"""

        validate = False
        try:
            self.driver.find_element(
                By.XPATH, XpathConstants.SITE_NAME_ERROR_XPATH)
            return False
        except NoSuchElementException:
            validate = True

        try:
            self.driver.find_element(
                By.XPATH, XpathConstants.SITE_DESCRIPTION_ERROR_XPATH)
            return False
        except NoSuchElementException:
            validate = True

        try:
            self.driver.find_element(By.CLASS_NAME, "is-invalid")
            return False
        except NoSuchElementException:
            validate = True

        try:
            self.driver.find_element(
                By.XPATH, XpathConstants.VCENTER_ERROR_XPATH)
            return False
        except NoSuchElementException:
            validate = True

        try:
            self.driver.find_element(
                By.XPATH, XpathConstants.SITE_VCENTER_USERNAME_ERROR_XPATH)
            return False
        except NoSuchElementException:
            validate = True

        try:
            self.driver.find_element(
                By.XPATH, XpathConstants.SITE_VCENTER_PASSWORD_ERROR_XPATH)
            return False
        except NoSuchElementException:
            validate = True

        return validate

    def checkGivenNodePresent(self, node):
        """check if the specified node exists on the UI"""
        '''click on node tab search if the mentioned node is present
            if present move back to site tab and start adding site as per the node'''

        '''Click On Configure'''
        self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
        '''Click On Node'''
        self.onClick((By.XPATH, XpathConstants.NODE_SECTION_XPATH))

        '''as we move to node tab wait for node data to be fetch then search if the node is present'''
        self.findElement((By.XPATH, XpathConstants.NODE_TABLE_XPATH))
        isNodePresent = self.findElement((By.XPATH, XpathConstants.NODE_XPATH.format(node)))
        self.onClick((By.XPATH, XpathConstants.SITE_SECTION_XPATH))
        self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))

        """To find the site table"""
        self.findElement((By.XPATH, XpathConstants.SITE_TABLE_XPATH))
        return isNodePresent

    def checkGivenSitePresent(self, site):
        """check if the specified site exists on the UI"""
        '''click on refresh button to get the latest UI'''
        self.onAnimationClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))
        '''as we do refresh wait for site api call'''

        self.findElement((By.XPATH, XpathConstants.SITE_TABLE_XPATH))
        isNodePresent = self.findElement((By.XPATH, XpathConstants.SITE_XPATH.format(site)))
        if isNodePresent is None:
            isNodePresent = self.findElement((By.XPATH, XpathConstants.SITE_URL_XPATH.format(site)))
        return isNodePresent
