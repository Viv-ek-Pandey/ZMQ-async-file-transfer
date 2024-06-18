from datetime import datetime
from urllib.parse import quote
import json
import os
from time import sleep
from selenium.webdriver.common.by import By
from seleniumwire.utils import decode
from Constants.Constants import Constants
from selenium.common.exceptions import TimeoutException
from Constants.ApiConstants import ApiConstants
from Utilities.XLUtils import createWorkBook
import logging
from seleniumwire.utils import decode as sw_decode
from Constants.XpathConstants import XpathConstants
from selenium.webdriver.support.select import Select
from Utilities.XLUtils import addTestResultToReportSheet
import ssl
from pyVim.connect import SmartConnect, Disconnect
import atexit
from pyVmomi import vim


def login(self, setup, pageAction=None, goToPage=None, key=None):
    '''
    this function will log in to datamotive node with provided credentials
    '''
    setupIp = ''
    if len(pageAction.getCookies()) == 0:
        if key != None:
            self.driver.get(setup[key])
            setupIp = setup[key]
        else:
            self.driver.get(setup["sourceurl"])
            setupIp = setup["sourceurl"]
        pageAction.sendInputKeys((By.XPATH, XpathConstants.NODE_USERNAME_XPATH), setup["username"])
        pageAction.sendInputKeys((By.XPATH, XpathConstants.UI_PASSWORD_TEXTBOX_XPATH), setup["password"])
        pageAction.onClick((By.XPATH, XpathConstants.LOGIN_BUTTON_XPATH))
        getApiResponse(self, ApiConstants.LOGIN_API)
        url = f"{setupIp}/{goToPage}"
        self.driver.get(url)


def getApiResponse(self, api):
    '''
    This will get the response received from the provided api url
    '''
    try:
        encodedApi = quote(api, safe=':/?=&,')
        request = self.driver.wait_for_request(encodedApi, timeout=60)
        if request.response:
            bodyjson = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
            decodeBody = bodyjson.decode('utf-8')
            res = json.loads(decodeBody)
            return res
    except TimeoutException as ex:
        return None


def getResponseFromResponseArray(self, api):
    '''
    Browser has value of the previously executed url below function will give the response for the provided url
    '''
    try:
        data = []
        encodedApi = quote(api, safe=':/?=&,')
        for request in self.driver.requests:
            if request.response and encodedApi in request.url:
                data = sw_decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                data = data.decode("utf8")
                data = json.loads(data)
                break
        return data
    except TimeoutException as ex:
        return None


def loadFilePath(filename):
    '''
    This function will search for the filename provided in the parameter and return its path
    '''
    path = os.path.realpath(
        os.path.join(os.path.dirname(__file__), '..', f'{filename}'))
    return path


def createReportFile():
    ''''
    This will create report directory and report file based on  that particular time every time code gets executed
    '''
    if not os.path.exists(Constants.REPORT_DIR_path):
        os.makedirs(Constants.REPORT_DIR_path)
    now = datetime.now()
    fileName = 'report' + now.strftime("%d-%m-%Y-%H-%M-%S") + '.xlsx'
    createWorkBook(os.path.join(Constants.REPORT_DIR_path, fileName))

    return fileName


def getLogger():
    '''
    This will create logger object which we can use to add logs to the file
    '''
    # to get the name of the test case file name at runtime
    logger = logging.getLogger(__name__)
    # FileHandler class to set the location of log file
    fileHandler = logging.FileHandler('logfile.log', mode='w')
    # Formatter class to set the format of log file
    formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                                  '%m-%d %H:%M:%S')
    # object of FileHandler gets formatting info from setFormatter #method
    fileHandler.setFormatter(formatter)
    # logger object gets formatting, path of log file info with addHandler method
    logger.addHandler(fileHandler)
    # setting logging level to INFO
    logger.setLevel(logging.INFO)
    return logger


def getCellValue(self, key, index=None):
    '''
    On UI there is a lot of tables to get value in the cell of the table below function is used
    '''
    table = self.findElement((By.CLASS_NAME, 'table'))
    tableHead = table.find_elements(by=By.CSS_SELECTOR, value='thead')
    ind = 0
    for h in tableHead:
        row = h.find_elements(by=By.CSS_SELECTOR, value='tr')
        for r in row:
            header = r.find_elements(by=By.CSS_SELECTOR, value='th')
            for i, cel in enumerate(header):
                txt = cel.text
                if txt == key:
                    ind = i
                    break
    tBody = table.find_elements(by=By.CSS_SELECTOR, value='tbody')

    if index is not None:
        for body in tBody:
            row = body.find_elements(by=By.CSS_SELECTOR, value='tr')
            cells = row[index].find_elements(by=By.CSS_SELECTOR, value='th')
            val = cells[ind].text
            return val
    else:
        for body in tBody:
            row = body.find_elements(by=By.CSS_SELECTOR, value='tr')
            for r in row:
                cells = r.find_elements(by=By.CSS_SELECTOR, value='th')
                val = cells[ind].text
                return val


def getCell(self, key, index):
    table = self.findElement((By.XPATH, "//div[@class='col-sm-12']//div[@class='container-fluid']//table[@class='table table-bordered responsiveTable']"))
    tableHead = table.find_elements(by=By.CSS_SELECTOR, value='thead')
    ind = 0
    listOfTableData = []
    listOfStatus = []
    for h in tableHead:
        row = h.find_elements(by=By.CSS_SELECTOR, value='tr')
        for r in row:
            header = r.find_elements(by=By.CSS_SELECTOR, value='th')
            for i, cel in enumerate(header):
                txt = cel.text
                if txt == key:
                    ind = i
                    break
    tBody = table.find_elements(by=By.CSS_SELECTOR, value='tbody')
    if index is not None:
        for body in tBody:
            row = body.find_elements(by=By.CSS_SELECTOR, value='tr')
            cells = row[index].find_elements(by=By.XPATH, value='//th[@class="itemRendererContainer"]')
            for cell in cells:
                val = cell.text
                listOfTableData.append(val)
    for eachCellValue in listOfTableData:
        value = eachCellValue.lstrip()
        if value == 'Running' or value == 'Completed' or value == 'Failed' or value == 'Partially-completed':
            listOfStatus.append(value)
    return listOfStatus[0]

def getUpdatedData(self, data):
        '''
        get updated data as we land on the nodes screen
        '''
        # delete the previous node data in order to start fresh
        del self.driver.requests
        # click on refresh icon to get the fresh data on UI screen
        self.onAnimationClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))
        return getApiResponse(self, data)

def isNodePresent(self, nodeName):
        node = self.findElement((By.XPATH, XpathConstants.NODE_XPATH.format(nodeName)))
        return node

def checkNodeAndClickSiteSection(self, node):
        '''
        check if the specified node exists on the UI
        click on node tab search if the mentioned node is present
        if present move back to site tab and start adding site as per the node
        Click On Configure
        '''
        self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
        # Click On Node
        self.onClick((By.XPATH, XpathConstants.NODE_SECTION_XPATH))
        self.findElement((By.XPATH, XpathConstants.NODE_TABLE_XPATH))
        isNodePresent = self.findElement((By.XPATH, XpathConstants.NODE_XPATH.format(node)))
        self.onClick((By.XPATH, XpathConstants.SITE_SECTION_XPATH))
        self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
        # To find the site table
        self.findElement((By.XPATH, XpathConstants.SITE_TABLE_XPATH))
        return isNodePresent

def checkGivenSitePresent(self, site):
        '''
        check if the specified site exists on the UI
        click on refresh button to get the latest UI
        '''
        self.onAnimationClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))
        self.findElement((By.XPATH, XpathConstants.SITE_TABLE_XPATH))
        isNodePresent = self.findElement((By.XPATH, XpathConstants.SITE_XPATH.format(site)))
        if isNodePresent is None:
            isNodePresent = self.findElement((By.XPATH, XpathConstants.SITE_URL_XPATH.format(site)))
        return isNodePresent

def setOtherSiteFields(self, data, logger):
        '''
        set site fields and configure site
        get field data 
        '''
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
        # fill in the data in inputs based on platform type
        match platformType:
            case Constants.VMware:
                if vcenter and uname and passrd:
                    self.clearInputFields((By.XPATH, XpathConstants.VCENTER_XPATH))
                    self.sendInputKeys((By.XPATH, XpathConstants.VCENTER_XPATH), vcenter)
                    self.clearInputFields((By.XPATH, XpathConstants.SITE_VCENTER_USERNAME_XPATH))
                    self.sendInputKeys((By.XPATH, XpathConstants.SITE_VCENTER_USERNAME_XPATH), uname)
                    self.clearInputFields((By.XPATH, XpathConstants.SITE_VCENTER_PASSWORD_XPATH))
                    self.sendInputKeys((By.XPATH, XpathConstants.SITE_VCENTER_PASSWORD_XPATH), passrd)
                else:
                    logger.warning(Constants.INVALID_SITE_FIELDS.format(siteName))

            case Constants.AWS:
                if region and accessKey and secretKey and zone:
                    self.findElement((By.XPATH, XpathConstants.DROPDOWN_XPATH.format(region)))
                    self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_AWS_REGION_XPATH), region)
                    self.findElement((By.XPATH, XpathConstants.DROPDOWN_XPATH.format(zone)))
                    self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_AWS_ZONE_XPATH), zone)
                    self.clearInputFields((By.XPATH, XpathConstants.ACCESS_KEY_XPATH))
                    self.sendInputKeys((By.XPATH, XpathConstants.ACCESS_KEY_XPATH), accessKey)
                    self.clearInputFields((By.XPATH, XpathConstants.SECRET_KEY_XPATH))
                    self.sendInputKeys((By.XPATH, XpathConstants.SECRET_KEY_XPATH), secretKey)
                else:
                    logger.warning(Constants.INVALID_SITE_FIELDS.format(siteName))

            case Constants.GCP:
                if region and zone and projectId:
                    self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_AWS_REGION_XPATH), region)
                    self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_AWS_ZONE_XPATH ), zone)
                    self.clearInputFields((By.XPATH, XpathConstants.PROJECT_ID_XPATH))
                    self.sendInputKeys((By.XPATH, XpathConstants.PROJECT_ID_XPATH), projectId)
                else:
                    logger.warning(Constants.INVALID_SITE_FIELDS.format(siteName))

            case Constants.AZURE:
                subscriptionId = data["subscriptionId"]
                storageAccount = data["storageAccount"]
                tenantID = data["tenantID"]
                clientID = data["clientID"]
                if region and subscriptionId and storageAccount and tenantID and clientID and secretKey:
                    self.singleSelectFromDropdown((By.XPATH, XpathConstants.SITE_AWS_REGION_XPATH), region)
                    self.clearInputFields((By.XPATH, XpathConstants.PROJECT_ID_XPATH))
                    self.sendInputKeys((By.XPATH, XpathConstants.PROJECT_ID_XPATH), subscriptionId)
                    self.clearInputFields((By.XPATH, XpathConstants.STORAGE_ACCOUNT_XPATH))
                    self.sendInputKeys((By.XPATH, XpathConstants.STORAGE_ACCOUNT_XPATH), storageAccount)
                    self.clearInputFields((By.XPATH, XpathConstants.TENANT_ID_XPATH))
                    self.sendInputKeys((By.XPATH, XpathConstants.TENANT_ID_XPATH), tenantID)
                    self.clearInputFields((By.XPATH, XpathConstants.CLIENT_ID_XPATH))
                    self.sendInputKeys((By.XPATH, XpathConstants.CLIENT_ID_XPATH), clientID)
                    self.clearInputFields((By.XPATH, XpathConstants.SECRET_KEY_XPATH))
                    self.sendInputKeys((By.XPATH, XpathConstants.SECRET_KEY_XPATH), secretKey)
                else:
                    logger.warning(Constants.INVALID_SITE_FIELDS.format(siteName))

def setProtectionPlanGeneralInformation(self, sites, jsonTestData, logger):
        '''
        set general page data in plan wizard it takes two parameters sites (got from browser api response) and
        data (got from json)
        '''
        if sites is not None:
            recoverySiteId = ''
            protectionSiteId = ''
            recoverySiteName = ''
            protectionSiteName = ''
            networkUrl = ''
            pplanName = jsonTestData.get("pplanName")
            protectionName = jsonTestData.get("protection")
            recoveryName = jsonTestData.get("recovery")
            for site in sites:
                if site["name"] == jsonTestData["recovery"]:
                    recoverySiteId = site["id"]
                    recoverySiteName = site["platformDetails"]["platformType"]
                elif site["name"] == jsonTestData["protection"]:
                    protectionSiteId = site["id"]
                    protectionSiteName = site["platformDetails"]["platformType"]

            if recoverySiteId != '':
                networkUrl = ApiConstants.GET_NETWORK.replace(
                    "recoverySiteId", f'{recoverySiteId}')
                vmwareFolderDataurl = ApiConstants.GET_VMWARE_DATACENTER.replace(
                    "recoverySiteId", f'{recoverySiteId}')
            else:
                logger.error(Constants.PROTECTION_PLAN_NOTCREATED_SITE_ID_NOT_FOUND)
                return False
            # Set Plan name, recovery site ,protection site fields
            self.clearInputFields((By.XPATH, XpathConstants.PROTECTION_PLAN_NAME_TEXTBOX_XPATH))
            self.sendInputKeys((By.XPATH, XpathConstants.PROTECTION_PLAN_NAME_TEXTBOX_XPATH), pplanName)
            vmListUrl = ApiConstants.GET_PPLAN_VM_LIST.replace("protectionId", f'{protectionSiteId}')
            self.singleSelectFromDropdown((By.XPATH, XpathConstants.PROTECTION_SITE_NAME_XPATH), protectionName)
            self.singleSelectFromDropdown((By.XPATH, XpathConstants.RECOVERY_SITE_NAME), recoveryName)
            vmListResp = getApiResponse(self, vmListUrl)
            self.findElement((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
            self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
            return {"protectionSiteId": protectionSiteId, "recoverySiteName": recoverySiteName,
                    "protectionSiteName": protectionSiteName, "networkUrl": networkUrl,
                    "vmwareFolderDataurl": vmwareFolderDataurl, "recoverySiteId": recoverySiteId,
                    "vmListUrl": vmListUrl, "vmListResp": vmListResp}
        else:
            logger.error(f'In {jsonTestData["pplanName"]} pplan, site data not found')
            return False

def setVMwareVirtualMachine(self, jsontestData, vmListResp, protectionSiteName, logger):
        '''
        This function will set vm from protection it takes jsontestData (data got from json), vmListUrl (url for
        fetching vm list) and protectionSiteName
        '''
        updatedJsonVmData = []
        jsonTestVMsInfo = jsontestData["recoveryConfigs"]
        # This function will get all the vm list from protected infrastructure
        for jsonVm in jsonTestVMsInfo:
            # loop through response data array and check if json vm name is same as one of response vm data 
            # if so update founded vm moref in json data for further operation
            for vml in vmListResp:
                general = jsonVm["general"]
                if vml["name"] == general["name"]:
                    moref = vml["moref"]
                    searchVirtualMachine(self, general["name"])
                    # check on searched vm 
                    vmwareCheckBox = self.findElement((By.XPATH, XpathConstants.VM_CHECKBOX_XPATH.format(general["name"])))
                    if vmwareCheckBox:
                        self.onAnimationClick((By.XPATH, XpathConstants.VM_CHECKBOX_XPATH.format(general["name"])))
                    else:
                        self.onAnimationClick((By.XPATH, XpathConstants.AWS_VM_CHECKBOX_XPATH))
                    # Json data does not contain vm moref as it comes from infra and we will require it for further operation
                    # thus need to update it in json data and pass
                    general["moref"] = vml["moref"]
                    updatedJsonVmData.append(jsonVm)
                    break
        if not updatedJsonVmData:
            logger.error("Didn't get virtual machine list")
        else:
            # click on next page
            self.findElement((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
            self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
            # return json data with moref of vm updated in it
            return updatedJsonVmData


def setRecoveryConfiguration(self, logger, jsonVmArray, recoverySiteName, recoverySiteId=None, folderDataUrl=None):
        '''
        To set recovery configuration of selected virtual machine'
        First vm recovery configuration by default is opened thus below code first close it
        and then if we go in platform specific configuration it will start from opening recovery configuration
        '''
        element = self.findElement(
            (By.XPATH, XpathConstants.ARROW_BUTTON_XPATH))
        if element is not None:
            self.onClick((By.XPATH, XpathConstants.ARROW_BUTTON_XPATH))
        # different target platform has different fields to fill
        match recoverySiteName:
            case Constants.VMware:
                setVMwareRecoveryConfiguration(self, recoverySiteId, jsonVmArray, folderDataUrl, logger)
            case Constants.AWS:
                setAWSRecoveryConfiguration(self, jsonVmArray, logger)
            case Constants.AZURE:
                setAzureRecoveryConfiguration(self, jsonVmArray, logger)


def setVMwareRecoveryConfiguration(self, recoverySiteId, jsonVmArray, folderDataUrl, logger):
        '''
        This will set recovery configuration of virtual machine for VMware platform 
        '''
        for data in jsonVmArray:
            '''extracting all the json data '''
            general = data["general"]
            networks = data["network"]
            name = general['name']
            vmMoref = general["moref"]
            compute = general["compute"]
            storage = general["storage"]
            guestOS = general["guestOs"]
            firmwareType = general["firmwareType"]
            cpu = general["cpu"]
            memory = general["memory"]
            datacenterId = ''
            folderPath = general['folderPath'].split('/')

            # For vmware to fetch folder data we need to datacenter ID and it come from below api response and 
            # from that first data will be datacenter ID
            folderData = getResponseFromResponseArray(self, folderDataUrl)
            for fold in folderData:
                if fold['name'] == folderPath[0]:
                    datacenterId = fold["id"]
            if general and compute and storage and cpu:
                # scroll until it find the element with mentioned xpath 
                self.scrollToFindElement(
                    (By.XPATH, XpathConstants.VIRTUAL_MACHINE_NAME_XPATH.format(vmMoref)))
                # click on vm's name and open vm configuration, click on general title to fill general data
                self.onClick((By.XPATH, XpathConstants.VIRTUAL_MACHINE_NAME_XPATH.format(vmMoref)))
                self.onClick((By.XPATH, XpathConstants.GENERAL_TAB_XPATH.format(vmMoref)))
                self.onClick((By.XPATH, XpathConstants.LOCATION_FOLDER_PATH_XAPTH.format(vmMoref)))
                for i, name in enumerate(folderPath):
                    if i == (len(folderPath) - 1):
                        goToVmwareFolderPath(self, folderData, name, recoverySiteId, vmMoref, True, logger, datacenterId)
                    else:
                        folderData = goToVmwareFolderPath(self, folderData, name, recoverySiteId, vmMoref, False, logger)
                guestOs = Select(self.findElement((By.XPATH, XpathConstants.GUEST_OS_XPATH.format(vmMoref))))
                guestOs = guestOs.first_selected_option
                guestOs= guestOs.text
                if guestOs == "":
                    self.singleSelectFromDropdown(
                        (By.XPATH, XpathConstants.GUEST_OS_XPATH.format(vmMoref)), guestOS)
                firmwareTypeValue = Select(self.findElement((By.XPATH, XpathConstants.FIRMAWARE_TYPE_XPATH.format(vmMoref))))
                firmwareTypeValue = firmwareTypeValue.first_selected_option
                firmwareTypeValue = firmwareTypeValue.text
                if firmwareTypeValue == "":
                    self.searchSelectFromDropdown((By.XPATH, XpathConstants.FIRMAWARE_TYPE_XPATH.format(vmMoref)), firmwareType)
                self.searchSelectFromDropdown(
                    (By.XPATH, XpathConstants.COMPUTE_XPATH.format(vmMoref)), compute)
                self.searchSelectFromDropdown(
                    (By.XPATH, XpathConstants.STORAGE_XPATH.format(vmMoref)), storage)
                self.clearInputFields(
                    (By.XPATH, XpathConstants.CPU_XPATH.format(vmMoref)))
                self.sendInputKeys(
                    (By.XPATH, XpathConstants.CPU_XPATH.format(vmMoref)), cpu)
                self.onClick((By.XPATH, XpathConstants.NETWORK_TAB_XPATH.format(vmMoref)))
            else:
                logger.error("VMware Recovery Configuration Data not found")
            if networks and vmMoref:
                '''set vm networks'''
                setVMwareNetworks(self, networks, vmMoref, logger)
            else:
                logger.error("VMware Network Not Found ")
        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))

def goToVmwareFolderPath(self, folderData, name, recoverySiteId, moref, select, logger, datacenterId=None):
        '''
        for vmware as target to select target folder
        '''
        res = []
        if select:
            self.findElement((By.XPATH, XpathConstants.LOCATION_FOLDER_PATH_CHECKBOX_XPATH.format(moref, Constants.folId)))
            sleep(Constants.THREE_SECONDS)
            self.onAnimationClick((By.XPATH, XpathConstants.LOCATION_FOLDER_PATH_CHECKBOX_XPATH.format(moref, Constants.folId)))
            self.findElement((By.XPATH, XpathConstants.OK_BUTTON_XPATH))
            self.onClick((By.XPATH, XpathConstants.OK_BUTTON_XPATH))
        else:
            getVmwareFolURL = ApiConstants.GET_VMWARE_FOLDER_LIST.replace("recoverySiteId", f"{recoverySiteId}")
            getVmwareFolURL = getVmwareFolURL.replace("id", fol["id"])
            self.onClick((By.XPATH, XpathConstants.DATACENTER_ARROW_BUTTON))
            res = getResponseFromResponseArray(self, getVmwareFolURL)
        if res is None:
            logger.error("Result is empty")
        else:
            return res

def setVMwareNetworks(self, networks, vmMoref, logger):
        '''
        fill network configuration by looping through
        '''
        for ind, net in enumerate(networks):
            network = net["network"]
            adapterType = net["adapterType"]
            if network and adapterType:
                self.onClick(
                    (By.XPATH, XpathConstants.CONFIG_XPATH.format(vmMoref, ind)))
                self.searchSelectFromDropdown(
                    (By.XPATH, XpathConstants.NETWORK_TEXTBOX_XPATH.format(vmMoref, ind)), network)
                self.singleSelectFromDropdown(
                    (By.XPATH, XpathConstants.ADAPTER_TYPE_TEXTBOX_XPATH.format(vmMoref, ind)), adapterType)
                self.onClick((By.XPATH, XpathConstants.NETWORK_SAVE_BUTTON.format(vmMoref, ind)))
            else:
                logger.error("VMware Network data not found")

def setAWSVM(self, data, virtualMachineList, vmlisturl, recoveryConfigs, logger):
        recoveryConfigs = data["recoveryConfigs"]
        general = recoveryConfigs[0]["general"]
        name = general["name"]
        updatedJsonVmData = []
        for eachMachine in virtualMachineList:
            searchVirtualMachine(self, eachMachine)
            # Click Checkbox
            AWS_Checkbox = self.findElement((By.XPATH, XpathConstants.AWS_VM_CHECKBOX_XPATH))
            if AWS_Checkbox:
                self.onAnimationClick((By.XPATH, XpathConstants.AWS_VM_CHECKBOX_XPATH))
            else:
                self.onAnimationClick((By.XPATH, XpathConstants.VM_CHECKBOX_XPATH.format(eachMachine)))
        # Click Next
        self.findElement((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        vmListResp = getApiResponse(self, vmlisturl)
        for jsonVm in recoveryConfigs:
            # loop through response data array and check if json vm name is same as one of response vm data 
            # if so update founded vm moref in json data for further operation
            for vml in vmListResp:
                general = jsonVm["general"]
                if vml["name"] == general["name"]:
                    moref = vml["moref"]
                    general["moref"] = vml["moref"]
                    updatedJsonVmData.append(jsonVm)
                    break
        if not updatedJsonVmData:
            logger.error("Didn't get virtual machine list")
        else:
            return updatedJsonVmData

def setAWSRecoveryConfiguration(self, jsonVmArray, logger):
        for data in jsonVmArray:
            general = data["general"]
            networks = data["network"]
            name = general['name']
            vmMoref = general["moref"]
            guestOs = general["guestOs"]
            firmwareType = general["firmwareType"]
            instanceType = general["instanceType"]
            volumeType = general["volumeType"]
            if general and guestOs and firmwareType and instanceType and volumeType:
                self.findElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_NAME_XPATH.format(vmMoref)))
                self.scrollToFindElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_NAME_XPATH.format(vmMoref)))
                # click on vm's name and open vm configuration, click on general title to fill general data 
                self.onClick((By.XPATH, XpathConstants.VIRTUAL_MACHINE_NAME_XPATH.format(vmMoref)))
                self.onClick((By.XPATH, XpathConstants.GENERAL_TAB_XPATH.format(vmMoref)))
                guestOS = Select(self.findElement((By.XPATH, XpathConstants.GUEST_OS_XPATH.format(vmMoref))))
                guestOS = guestOS.first_selected_option
                guestOS= guestOS.text
                if guestOS == "":
                    self.singleSelectFromDropdown(
                        (By.XPATH, XpathConstants.GUEST_OS_XPATH.format(vmMoref)), guestOs)
                firmwareTypeValue = Select(self.findElement((By.XPATH, XpathConstants.FIRMAWARE_TYPE_XPATH.format(vmMoref))))
                firmwareTypeValue = firmwareTypeValue.first_selected_option
                firmwareTypeValue = firmwareTypeValue.text
                if firmwareTypeValue == '':
                    self.searchSelectFromDropdown((By.XPATH, XpathConstants.FIRMAWARE_TYPE_XPATH.format(vmMoref)),
                                                  firmwareType)
                self.searchSelectFromDropdown((By.XPATH, XpathConstants.INSTANCE_TYPE_XPATH.format(vmMoref)),
                                              instanceType)
                self.singleSelectFromDropdown((By.XPATH, XpathConstants.VOLUME_TYPE_XPATH.format(vmMoref)),
                                              volumeType)
            else:
                logger.error("AWS Recovery Configuration Data not found")
            if vmMoref and networks:
                setAWSNetwork(self, networks, vmMoref, logger)
            else:
                logger.error("AWS Network Not Found")
        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))

def setAWSNetwork(self, networks, vmMoref, logger):
        for ind, net in enumerate(networks):
            vpc = net["vpc"]
            subnet = net["subnet"]
            securityGroups = net["securityGroups"]
            if vpc and subnet and securityGroups:
                # Click on network
                self.onClick((By.XPATH, XpathConstants.NETWORK_TAB_XPATH.format(vmMoref)))
                # Click on Config
                self.onClick((By.XPATH, XpathConstants.CONFIG_XPATH.format(vmMoref, ind)))
                self.singleSelectFromDropdown(
                    (By.XPATH, XpathConstants.VPC_XPATH.format(vmMoref, ind)), vpc)
                self.singleSelectFromDropdown(
                    (By.XPATH, XpathConstants.SUBNET_XPATH.format(vmMoref, ind)), subnet)
                self.onAnimationClick((By.XPATH, XpathConstants.AUTO_PUBLIC_IP_CHECKBOX.format(vmMoref, ind)))
                self.clearInputFields(
                    (By.XPATH, XpathConstants.PRIVATE_IP_XPATH.format(vmMoref, ind)))
                self.scrollToFindElement((By.XPATH, XpathConstants.SECURITY_GROUP_XPATH.format(vmMoref, ind)))
                self.singleSelectFromDropdown(
                    (By.XPATH, XpathConstants.SECURITY_GROUP_XPATH.format(vmMoref, ind)), securityGroups)
                self.onClick(
                    (By.XPATH, XpathConstants.NETWORK_SAVE_BUTTON.format(vmMoref, ind)))
            else:
                logger.error("AWS Network data not found")

def setAzureRecoveryConfiguration(self, jsonVmArray, logger):
        for data in jsonVmArray:
            general = data["general"]
            vmMoref = general["moref"]
            networks = data["network"]
            guestOs = general["guestOs"]
            firmwareType = general["firmwareType"]
            resourceGroups = general["resourceGroups"]
            availabilityZone = general["availabilityZone"]
            vmSize = general["vmSize"]
            volumeType = general["volumeType"]
            if general and vmMoref and guestOs and firmwareType and resourceGroups and availabilityZone and vmSize and volumeType:
                self.scrollToFindElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_NAME_XPATH.format(vmMoref)))
                # click on vm's name and open vm configuration, click on general title to fill general data
                self.onClick((By.XPATH, XpathConstants.VIRTUAL_MACHINE_NAME_XPATH.format(vmMoref)))
                self.onClick((By.XPATH, XpathConstants.GENERAL_TAB_XPATH.format(vmMoref)))
                guestOS = Select(self.findElement((By.XPATH, XpathConstants.GUEST_OS_XPATH.format(vmMoref))))
                guestOS = guestOS.first_selected_option
                guestOS = guestOS.text
                if guestOS == "":
                    self.singleSelectFromDropdown(
                        (By.XPATH, XpathConstants.GUEST_OS_XPATH.format(vmMoref)), guestOs)
                firmwareValueType = Select(
                    self.findElement((By.XPATH, XpathConstants.FIRMAWARE_TYPE_XPATH.format(vmMoref))))
                firmwareValueType = firmwareValueType.first_selected_option
                firmwareValueType = firmwareValueType.text
                if firmwareValueType == '':
                    self.searchSelectFromDropdown((By.XPATH, XpathConstants.FIRMAWARE_TYPE_XPATH.format(vmMoref)),
                                                  firmwareType)
                self.searchSelectFromDropdown(
                    (By.XPATH, XpathConstants.RESOURCE_GROUP_XPATH.format(vmMoref)), resourceGroups)
                self.singleSelectFromDropdown(
                    (By.XPATH, XpathConstants.AVAILABILITY_ZONE_XPATH.format(vmMoref)), availabilityZone)
                self.searchSelectFromDropdown(
                    (By.XPATH, XpathConstants.INSTANCE_TYPE_XPATH.format(vmMoref)), vmSize)
                self.singleSelectFromDropdown(
                    (By.XPATH, XpathConstants.VOLUME_TYPE_XPATH.format(vmMoref)), volumeType)
            else:
                logger.error("Azure Recovery Configuration Data not found")
            if vmMoref and networks:
                setAzureNetwork(self, networks, vmMoref, logger)
            else:
                logger.error("Azure Network Not Found")
        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))

def setAzureNetwork(self, networks, vmMoref, logger):
        for ind, net in enumerate(networks):
            network = net["network"]
            subnet = net["subnet"]
            securityGroups = net["securityGroups"]
            publicIP = net["publicIP"]
            if network and subnet and securityGroups:
                # Click on network
                self.onClick((By.XPATH, XpathConstants.NETWORK_TAB_XPATH.format(vmMoref)))
                # Click on Config
                self.onClick((By.XPATH, XpathConstants.CONFIG_XPATH.format(vmMoref, ind)))
                # Select Network
                self.searchSelectFromDropdown(
                    (By.XPATH, XpathConstants.NETWORK_TEXTBOX_XPATH.format(vmMoref, ind)), network)
                # Select Subnet
                self.singleSelectFromDropdown(
                    (By.XPATH, XpathConstants.SUBNET_XPATH.format(vmMoref, ind)), subnet)
                # Clear PrivateIP
                self.clearInputFields(
                    (By.XPATH, XpathConstants.PRIVATE_IP_XPATH.format(vmMoref, ind)))
                # Select Public IP
                self.singleSelectFromDropdown(
                    (By.XPATH, XpathConstants.PUBLIC_IP_XPATH.format(vmMoref, ind)), publicIP)
                # Select Securiy Groups
                self.searchSelectFromDropdown(
                    (By.XPATH, XpathConstants.SEARCH_SECURITY_GROUP_XPATH.format(vmMoref, ind)), securityGroups)
                # Click on Save Button
                self.onClick(
                    (By.XPATH, XpathConstants.NETWORK_SAVE_BUTTON.format(vmMoref, ind)))
            else:
                logger.error("Azure Network data not found")

def searchVirtualMachine(self, virtualMachine):
        self.findElement((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
        self.clearInputFields((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
        self.onEnter((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
        self.sendInputKeys((By.XPATH, XpathConstants.SEARCH_BOX_XPATH), virtualMachine)
        sleep(Constants.FIVE_SECONDS)
        self.onEnter((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
        sleep(Constants.FIVE_SECONDS)

def validateIfGivenSiteIsPresent(self, data, logger):
        '''
        Validated if the site data given in plan data file is present on the UI
        '''
        self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
        self.onClick((By.XPATH, XpathConstants.SITE_SECTION_XPATH))
        self.findElement((By.XPATH, XpathConstants.SITE_TABLE_XPATH))
        protectionSite = data["protection"]
        recoverySite = data["recovery"]
        isProtectionSitePresent = self.findElement((By.XPATH, XpathConstants.SITE_XPATH.format(protectionSite)))
        isRecoverySitePresent = self.findElement((By.XPATH, XpathConstants.SITE_XPATH.format(recoverySite)))
        if isProtectionSitePresent is None:
            isProtectionSitePresent = self.findElement((By.XPATH, XpathConstants.SITE_URL_XPATH.format(protectionSite)))
        if isRecoverySitePresent is None:
            isRecoverySitePresent = self.findElement((By.XPATH, XpathConstants.SITE_URL_XPATH.format(recoverySite)))
        self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
        sleep(Constants.THREE_SECONDS)
        self.findElement((By.XPATH, XpathConstants.TABLE_XPATH))
        if isProtectionSitePresent is None and isRecoverySitePresent is None:
            logger.warning(Constants.SITE_NOT_PRESENT)
            return False
        else:
            return True


def searchReplicationVirtualMachine(self, virtualMachine):
        '''
        This function will search virtual machine
        '''
        self.findElement((By.XPATH, XpathConstants.EVENT_SEARCH_BOX_XPATH))
        self.clearInputFields((By.XPATH, XpathConstants.EVENT_SEARCH_BOX_XPATH))
        self.onEnter((By.XPATH, XpathConstants.EVENT_SEARCH_BOX_XPATH))
        self.sendInputKeys((By.XPATH, XpathConstants.EVENT_SEARCH_BOX_XPATH), virtualMachine)
        sleep(Constants.FIVE_SECONDS)
        self.onEnter((By.XPATH, XpathConstants.EVENT_SEARCH_BOX_XPATH))
        sleep(Constants.FIVE_SECONDS)


def checkJobStatusOfVirtualMachine(self, machine, filepath, logger, Test_Case_Name = None):
        '''
        This function will check job status of virtual machine
        '''
        searchReplicationVirtualMachine(self, machine)
        # To find virtual machine table
        self.findElement((By.XPATH, XpathConstants.VM_LIST_TABLE_XPATH))
        # It will find the status of particular virtual machine
        status = getCell(self, 'Job Status', 0)
        outputOfJobStatus = checkJobStatus(self, machine, status, filepath, logger, Test_Case_Name)
        return outputOfJobStatus


def checkJobStatus(self, machine, jobStatus, filepath, logger, Test_Case_Name = None):
        '''
        Depending on the status below function will re-execute the code
        '''
        if jobStatus == Constants.RUNNING:
            sleep(Constants.ONE_MINUTE)
            self.onClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))
            return checkJobStatusOfVirtualMachine(self, machine, filepath, logger, Test_Case_Name)
        elif jobStatus == Constants.COMPLETED:
            return "Completed"
        elif jobStatus == Constants.PARTIALLY_COMPLETED:
            return "Partially-completed"
        else:
            return "Failed"


def setVirtualMachineCredentials(self, machine):
        '''
        This function will search each of virtual machine and select it
        Clear search box fields
        '''
        self.clearInputFields((By.XPATH, XpathConstants.RECOVERY_SITE_OPERATIONS_SEARCH_BOX_XPATH))
        self.onEnter((By.XPATH, XpathConstants.RECOVERY_SITE_OPERATIONS_SEARCH_BOX_XPATH))
        # Enter data into search box
        self.sendInputKeys((By.XPATH, XpathConstants.RECOVERY_SITE_OPERATIONS_SEARCH_BOX_XPATH), machine)
        self.onEnter((By.XPATH, XpathConstants.RECOVERY_SITE_OPERATIONS_SEARCH_BOX_XPATH))
        # It will find username textbox
        self.findElement((By.XPATH, XpathConstants.USERNAME_TEXTBOX_XPATH))
        # Enter values into username textbox
        self.sendInputKeys((By.XPATH, XpathConstants.USERNAME_TEXTBOX_XPATH), "username")
        # It will find password textbox
        self.findElement((By.XPATH, XpathConstants.PASSWORD_TEXTBOX_XPATH))
        # Enter values into password textbox
        self.sendInputKeys((By.XPATH, XpathConstants.PASSWORD_TEXTBOX_XPATH), "password")
        self.onClick((By.XPATH, XpathConstants.TEST_RECOVERY_VM_CHECKBOX_XPATH))


def checkMigrationStatus(self, machine, data, filepath, logger):
        '''
        This function will check status of migration
        '''
        self.scrollToFindElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_SECTION_XPATH))
        for eachMachine in machine:
            self.clearInputFields((By.XPATH, XpathConstants.PROTECTED_MACHINE_SEARCH_BOX))
            self.onEnter((By.XPATH, XpathConstants.PROTECTED_MACHINE_SEARCH_BOX))
            self.sendInputKeys((By.XPATH, XpathConstants.PROTECTED_MACHINE_SEARCH_BOX), eachMachine)
            resultOfStatus = getCellValue(self, "Status", 0)
            return monitorMigration(self, resultOfStatus, machine, data, filepath, logger)


def monitorMigration(self, result, machine, data, filepath, logger):
        '''
        Depending upon status below code will re-execute
        '''
        resultList= []
        if result == Constants.MIGRATION_INIT:
            sleep(Constants.ONE_MINUTE)
            self.onClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))
            return checkMigrationStatus(self, machine, data, filepath, logger)
        elif result == Constants.MIGRATION_INIT_SUCCESS:
            # To Click on recovery jobs
            self.onClick((By.XPATH, XpathConstants.RECOVERY_JOBS_XPATH))
            # To find and click on virtual machine icon
            self.findElement((By.XPATH, XpathConstants.PROTECTION_PLAN_DATA_XPATH))
            self.findElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
            self.onAnimationClick((By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
            # To find virtual machine table
            self.findElement((By.XPATH, XpathConstants.VIRTUAL_MACHINE_TABLE_XPATH))
            for eachVirtualMachine in machine:
                Status = checkJobStatus(self, eachVirtualMachine, data, filepath, logger)
                if Status == Constants.COMPLETED:
                    addTestResultToReportSheet(filepath, Constants.MIGRATE_TEST, Constants.HEADER, data,
                                               Constants.MIGRATION_COMPLETED.format(eachVirtualMachine))
                    logger.info(Constants.MIGRATION_COMPLETED.format(eachVirtualMachine))
                    resultList.append("True")
                elif Status == Constants.PARTIALLY_COMPLETED:
                    addTestResultToReportSheet(filepath, Constants.MIGRATE_TEST, Constants.HEADER, data,
                                               Constants.MIGRATION_PARTIALLY_COMPLETED.format(eachVirtualMachine))
                    logger.info(Constants.MIGRATION_PARTIALLY_COMPLETED.format(eachVirtualMachine))
                    resultList.append("False")
                else:
                    addTestResultToReportSheet(filepath, Constants.MIGRATE_TEST, Constants.HEADER, data,
                                               Constants.MIGRATION_GOT_FAILED.format(eachVirtualMachine))
                    logger.info(Constants.MIGRATION_GOT_FAILED.format(eachVirtualMachine))
                    resultList.append("False")
        else:
            addTestResultToReportSheet(filepath, Constants.MIGRATE_TEST, Constants.HEADER, data,
                                       Constants.INIT_MIGRATION_FAILED)
            logger.error(Constants.INIT_MIGRATION_FAILED)
            resultList.append("False")
        if "False" not in resultList:
            return Constants.PASSED
        else:
            return Constants.FAILED

def configureProtectionPlan(self, data, filepath, logger):
    recoveryConfigs = data["recoveryConfigs"]
    sites = getApiResponse(self, 'api/v1/sites')
    resObj = setProtectionPlanGeneralInformation(self, sites, data, logger)
    if not resObj:
        logger.error(f"Protection plan with name {data['pplanName']} not created")
        addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST, Constants.PROTECTION_PLAN_HEADER,
                                           data, Constants.PROTECTION_PLAN_NOT_CREATED)
        return Constants.FAILED
    else:
        # Get all the site data which is required to make api calls from general step
        vmwareFolderDataurl = resObj["vmwareFolderDataurl"]
        recoverySiteName = resObj["recoverySiteName"]
        networkUrl = resObj["networkUrl"]
        protectionSiteName = resObj["protectionSiteName"]
        recoverySiteId = resObj["recoverySiteId"]
        vmListResp = resObj["vmListResp"]
        vmListUrl = resObj["vmListUrl"]
        # Make virtual machine list
        virtualMachineList = []
        # added all virtual machines into list
        for eachMachineData in recoveryConfigs:
            name = eachMachineData["general"]["name"]
            virtualMachineList.append(name)
        match recoverySiteName:
            case Constants.AWS:
                updatedJsonVmData = setAWSVM(self, data, virtualMachineList, vmListUrl, recoveryConfigs, logger)
                # set recovery configuration
                if updatedJsonVmData:
                    setRecoveryConfiguration(self, logger, updatedJsonVmData, recoverySiteName,
                                                          virtualMachineList, logger)
                else:
                    logger.warning(Constants.RECOVERY_CONFIGURATION_NOT_SET)
                    return False
            case Constants.VMware:
                # select virtual machine from the protected infra
                updatedJsonVmData = setVMwareVirtualMachine(self, data, vmListResp, protectionSiteName, logger)
                network = getResponseFromResponseArray(self, networkUrl)
                if network is not None:
                    # set recovery configuration of virtual machine
                    if isinstance(updatedJsonVmData, list):
                        setRecoveryConfiguration(self, logger, updatedJsonVmData, recoverySiteName, recoverySiteId, vmwareFolderDataurl)
                    else:
                        logger.warning(Constants.RECOVERY_CONFIGURATION_NOT_SET)
                        return False
                else:
                    logger.warning(Constants.RECOVERY_CONFIGURATION_NOT_SET)
                    return False

            case Constants.AZURE:
                # select virtual machine
                updatedJsonVmData = setAWSVM(self, data, virtualMachineList, vmListUrl, recoveryConfigs, logger)
                # set recovery configuration
                if updatedJsonVmData:
                    setRecoveryConfiguration(self, logger, updatedJsonVmData, recoverySiteName, virtualMachineList)
                else:
                    logger.warning(Constants.RECOVERY_CONFIGURATION_NOT_SET)
                    return False
                
        # enter boot delay
        self.clearInputFields((By.XPATH, XpathConstants.BOOT_DELAY_XPATH))
        self.sendInputKeys((By.XPATH, XpathConstants.BOOT_DELAY_XPATH), data["bootdelay"])
        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        # enter replication interval, check encryptiononwire checkbox
        self.singleSelectFromDropdown((By.XPATH, XpathConstants.REPLICATION_MINUTE_INTERVAL_XPATH), "10 Minutes")
        self.onAnimationClick((By.XPATH, XpathConstants.ENCRYPTION_ON_WIRE_CHECKBOX_XPATH))
        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        nextButton = self.findElement((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        if nextButton:
            self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        self.onClick((By.XPATH, XpathConstants.FINISH_BUTTON_XPATH))
        messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
        self.findElement((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
        self.onClick((By.XPATH, XpathConstants.CLOSE_MESSAGE_POPUP_XPATH))
        self.findElement((By.XPATH, XpathConstants.TABLE_XPATH))
        self.findElement((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
        self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
        sleep(Constants.THREE_SECONDS)
        if Constants.PROTECTION_PLAN_CREATED in messagePopup:
            return Constants.PASSED
        else:
            return Constants.FAILED


def getServiceInstance(host, user, pwd, port=443):
        context = ssl._create_unverified_context()
        si = SmartConnect(host=host, user=user, pwd=pwd, port=port, sslContext=context)
        atexit.register(Disconnect, si)
        return si


def waitForTask(task):
        while task.info.state == vim.TaskInfo.State.running:
            continue

        if task.info.state == vim.TaskInfo.State.success:
            return task.info.result
        # else:
        #     raise task.info.error
