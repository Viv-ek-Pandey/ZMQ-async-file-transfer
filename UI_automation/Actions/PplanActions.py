from time import sleep
from Constants.ApiConstants import ApiConstants
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from Utilities.utils import getApiResponse, getLogger, getResponseFromResponseArray
from Utilities.XLUtils import addTestResultToReportSheet


class PplanActions(CommonWebPageActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.logger = getLogger()

    def test_pplan_add(self, data, filepath, logger):
        """To find the protection plan table"""
        self.findElement((By.XPATH, XpathConstants.TABLE_XPATH))
        validateGivenSitesPresent = self.validateGivenSitesPresent(data)
        if not validateGivenSitesPresent:
            self.logger.warning("Site Not Present")
            return False
        ''' click on Add protection Plan button'''
        self.onClick((By.XPATH, XpathConstants.ADD_BUTTON_XPATH))

        '''Get site response from browser and set protection plan wizard first step i.e. general step'''
        sites = getApiResponse(self, 'api/v1/sites')
        resObj = self.setGeneralInfoPage(sites, data)
        if not resObj:
            self.logger.error(f"Protection plan with name {data['pplanName']} not created")
            return False
        else:
            '''Get all the site data which is required to make api calls from general step'''

            vmwareFolderDataurl = resObj["vmwareFolderDataurl"]
            recoverySiteName = resObj["recoverySiteName"]
            networkUrl = resObj["networkUrl"]
            protectionSiteName = resObj["protectionSiteName"]
            recoverySiteId = resObj["recoverySiteId"]
            vmListResp = resObj["vmListResp"]
            result = Constants.PROTECTION_PLAN_CREATED

            '''select virtual machine from the protected infra'''
            updatedJsonVmData = self.setVMFromVMList(data, vmListResp, protectionSiteName)
            network = getResponseFromResponseArray(self, networkUrl)
            if network is not None:
                ''' set recovery configuration of virtual machine'''
                if isinstance(updatedJsonVmData, list):
                    self.setRecoveryConfigs(updatedJsonVmData, recoverySiteName, recoverySiteId, vmwareFolderDataurl)
                else:
                    self.logger.warning("Recovery configuration of virtual machine could not be set ")
                    return False

                '''enter boot delay'''
                self.clearInputFields((By.XPATH, XpathConstants.BOOT_DELAY_XPATH))
                self.sendInputKeys((By.XPATH, XpathConstants.BOOT_DELAY_XPATH), data["bootdelay"])
                self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))

                '''enter replication interval, check encryptiononwire checkbox'''
                self.singleSelectFromDropdown((By.XPATH, XpathConstants.REPLICATION_MINUTE_INTERVAL_XPATH), "10 Minutes")
                self.onAnimationClick((By.XPATH, XpathConstants.ENCRYPTION_ON_WIRE_CHECKBOX_XPATH))
                self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                self.onClick((By.XPATH, XpathConstants.FINISH_BUTTON_XPATH))
                self.onClick((By.XPATH, XpathConstants.SUCCESS_MESSAGE_POPUP_XPATH))
                sleep(10)
                self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                addTestResultToReportSheet(filepath, Constants.PROTECTION_PLAN_TEST,
                                           Constants.PROTECTION_PLAN_HEADER, data, result)
                logger.info(Constants.PROTECTION_PLAN_CREATED)
                return True
            else:
                self.logger.warning("pplan not reacted : network issue")
                return False

    def setGeneralInfoPage(self, sites, jsonTestData):

        """set general page data in plan wizard it takes two parameters sites (got from browser api response) and
        data (got from json)"""
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
                self.logger.error("protection plan not got created site id not found")
                return False
            '''Set Plan name, recovery site ,protection site fields'''
            self.sendInputKeys((By.XPATH, XpathConstants.PROTECTION_PLAN_NAME_TEXTBOX_XPATH), pplanName)
            vmListUrl = ApiConstants.GET_PPLAN_VM_LIST.replace("protectionId", f'{protectionSiteId}')
            self.singleSelectFromDropdown((By.XPATH, XpathConstants.PROTECTION_SITE_NAME_XPATH), protectionName)
            sleep(5)
            self.singleSelectFromDropdown((By.XPATH, XpathConstants.RECOVERY_SITE_NAME), recoveryName)
            vmListResp = getApiResponse(self, vmListUrl)
            sleep(5)
            self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
            return {"protectionSiteId": protectionSiteId, "recoverySiteName": recoverySiteName,
                    "protectionSiteName": protectionSiteName, "networkUrl": networkUrl,
                    "vmwareFolderDataurl": vmwareFolderDataurl, "recoverySiteId": recoverySiteId,
                    "vmListResp": vmListResp}
        else:
            self.logger.error(f'In {jsonTestData["pplanName"]} pplan, site data not found')
            return False

    def setVMFromVMList(self, jsontestData, vmListResp, protectionSiteName):

        """This function will set vm from protection it takes jsontestData (data got from json), vmListUrl (url for
        fetching vm list) and protectionSiteName"""

        updatedJsonVmData = []
        jsonTestVMsInfo = jsontestData["recoveryConfigs"]
        '''This function will get all the vm list from protected infrastructure'''
        for jsonVm in jsonTestVMsInfo:
            '''loop through response data array and check if json vm name is same as one of response vm data 
            if so update founded vm moref in json data for further operation'''
            for vml in vmListResp:
                general = jsonVm["general"]
                if vml["name"] == general["name"]:
                    moref = vml["moref"]
                    self.clearInputFields((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
                    '''Search in vm list page '''
                    self.sendInputKeys((By.XPATH, XpathConstants.SEARCH_BOX_XPATH), general["name"])
                    sleep(2)
                    self.onEnter((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))

                    '''For selecting vm vmware, azure has tree view and other platform has normal grid view'''

                    if protectionSiteName == Constants.VMware:
                        '''check on searched vm '''
                        self.onAnimationClick((By.XPATH, XpathConstants.VMWARE_VM_CHECKBOX_XPATH.format(moref)))
                        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                        self.onClick((By.XPATH, XpathConstants.BACK_BUTTON_XPATH))
                    else:
                        '''check on searched vm '''
                        self.onAnimationClick((By.XPATH, XpathConstants.AWS_VM_CHECKBOX_XPATH))
                        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                        self.onClick((By.XPATH, XpathConstants.BACK_BUTTON_XPATH))

                    '''Json data does not contain vm moref as it comes from infra and we will require it for further operation
                    thus need to update it in json data and pass'''

                    general["moref"] = vml["moref"]
                    updatedJsonVmData.append(jsonVm)
                    break

        '''click on next page'''
        sleep(3)
        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))

        '''return json data with moref of vm updated in it'''
        return updatedJsonVmData

    '''To set recovery configuration of selected virtual machine'''

    def setRecoveryConfigs(self, jsonVmArray, recoverySiteName, recoverySiteId, folderDataUrl):
        """First vm recovery configuration by default is opened thus below code first close it
        and then if we go in platform specific configuration it will start from opening recovery configuration"""

        element = self.findElement(
            (By.XPATH, XpathConstants.ARROW_BUTTON_XPATH))
        if element is not None:
            self.onClick((By.XPATH, XpathConstants.ARROW_BUTTON_XPATH))

        '''different target platform has different fields to fill '''
        match recoverySiteName:
            case Constants.VMware:
                self.setVMwareRecoveryConfiguration(
                    recoverySiteId, jsonVmArray, folderDataUrl)

    '''This will set recovery configuration of virtual machine for VMware platform '''

    def setVMwareRecoveryConfiguration(self, recoverySiteId, jsonVmArray, folderDataUrl):

        for data in jsonVmArray:

            '''extracting all the json data '''
            general = data["general"]
            networks = data["network"]
            name = general['name']
            vmMoref = general["moref"]
            compute = general["compute"]
            storage = general["storage"]
            cpu = general["cpu"]
            memory = general["memory"]
            datacenterId = ''
            folderPath = general['folderPath'].split('/')

            '''For vmware to fetch folder data we need to datacenter ID and it come from below api response and 
            from that first data will be datacenter ID'''
            folderData = getResponseFromResponseArray(self, folderDataUrl)
            for fold in folderData:
                if fold['name'] == folderPath[0]:
                    datacenterId = fold["id"]

            '''scroll until it find the element with mentioned xpath '''

            self.scrollToFindElement(
                (By.XPATH, XpathConstants.VIRTUAL_MACHINE_NAME_XPATH.format(vmMoref)))
            ''' click on vm's name and open vm configuration, click on general title to fill general data '''

            self.onClick((By.XPATH, XpathConstants.VIRTUAL_MACHINE_NAME_XPATH.format(vmMoref)))
            self.onClick((By.XPATH, XpathConstants.GENERAL_TAB_XPATH.format(vmMoref)))
            self.onClick((By.XPATH, XpathConstants.LOCATION_FOLDER_PATH_XAPTH.format(vmMoref)))
            for i, name in enumerate(folderPath):
                if i == (len(folderPath) - 1):
                    self.goToVmwareFolderPath(
                        folderData, name, recoverySiteId, vmMoref, True, datacenterId)
                else:
                    folderData = self.goToVmwareFolderPath(
                        folderData, name, recoverySiteId, vmMoref, False)

            self.singleSelectFromDropdown(
                (By.XPATH, XpathConstants.GUEST_OS_XPATH.format(vmMoref)), "Rhel")
            self.searchSelectFromDropdown((By.XPATH, XpathConstants.FIRMAWARE_TYPE_XPATH.format(vmMoref)),
                                          'BIOS')
            self.searchSelectFromDropdown(
                (By.XPATH, XpathConstants.COMPUTE_XPATH.format(vmMoref)), compute)
            self.searchSelectFromDropdown(
                (By.XPATH, XpathConstants.STORAGE_XPATH.format(vmMoref)), storage)
            self.clearInputFields(
                (By.XPATH, XpathConstants.CPU_XPATH.format(vmMoref)))
            self.sendInputKeys(
                (By.XPATH, XpathConstants.CPU_XPATH.format(vmMoref)), 4)
            self.onClick((By.XPATH, XpathConstants.NETWORK_TAB_XPATH.format(vmMoref)))

            '''set vm networks'''
            self.setNetworks(networks, vmMoref)

        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))

    def goToVmwareFolderPath(self, folderData, name, recoverySiteId, moref, select, datacenterId=None):
        """for vmware as target to select target folder"""
        res = []
        for i, fol in enumerate(folderData):
            folId = fol["id"]
            folName = fol["name"]
            if folName == name:
                if select:
                    sleep(3)
                    self.findElement((By.XPATH, XpathConstants.LOCATION_FOLDER_PATH_CHECKBOX_XPATH.format(moref, folId)))
                    sleep(3)
                    self.onAnimationClick(
                        (By.XPATH, XpathConstants.LOCATION_FOLDER_PATH_CHECKBOX_XPATH.format(moref, folId)))
                    computUrl = ApiConstants.GET_VMWARE_COMPUTE.replace(
                        "siteId", f"{recoverySiteId}")
                    computUrl = computUrl.replace("dataCenter", datacenterId)
                    self.onClick(
                        (By.XPATH, XpathConstants.OK_BUTTON_XPATH))
                    sleep(5)
                    getResponseFromResponseArray(self, computUrl)
                else:
                    getVmwareFolURL = ApiConstants.GET_VMWARE_FOLDER_LIST.replace(
                        "recoverySiteId", f"{recoverySiteId}")
                    getVmwareFolURL = getVmwareFolURL.replace("id", fol["id"])
                    self.onClick((By.XPATH, XpathConstants.DATACENTER_ARROW_BUTTON))
                    sleep(5)
                    res = getResponseFromResponseArray(self, getVmwareFolURL)
                    break
        return res

    def setNetworks(self, networks, vmMoref):
        """fill network configuration by looping through"""
        for ind, net in enumerate(networks):
            network = net["network"]
            adapterType = net["adapterType"]
            self.onClick(
                (By.XPATH, XpathConstants.CONFIG_XPATH.format(vmMoref, ind)))
            self.searchSelectFromDropdown(
                (By.XPATH, XpathConstants.NETWORK_TEXTBOX_XPATH.format(vmMoref, ind)), network)
            self.singleSelectFromDropdown(
                (By.XPATH, XpathConstants.ADAPTER_TYPE_TEXTBOX_XPATH.format(vmMoref, ind)), adapterType)
            self.onClick(
                (By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))

    def validateGivenSitesPresent(self, data):

        """Validated if the site data given in plan data file is present on the UI"""
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
        self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
        self.findElement((By.XPATH, XpathConstants.TABLE_XPATH))
        if isProtectionSitePresent is None and isRecoverySitePresent is None:
            self.logger.warning("Site Not Present")
            return False
        return True
