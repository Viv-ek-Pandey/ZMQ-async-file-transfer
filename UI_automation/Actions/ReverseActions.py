from time import sleep
from Constants.ApiConstants import ApiConstants
from Utilities.utils import getLogger, getResponseFromResponseArray
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from Utilities.utils import getApiResponse
from Actions.PplanActions import PplanActions
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants


class ReverseActions(CommonWebPageActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.logger = getLogger()
        self.ProtectionPlanActions = PplanActions(self.driver)

    def executeReverse(self, data, filepath, logger):
        protectionPlanName = data["pplanName"]
        virtualMachines = data["virtualMachines"]
        reverseSuffix = data["reverseSuffix"]
        recoveryConfigs = data["recoveryConfigs"][0]
        instanceType = recoveryConfigs["general"]["instanceType"]
        encryptionKMSKey = recoveryConfigs["general"]["encryptionKMSKey"]
        VPC = recoveryConfigs["network"][0]["VPC"]
        Subnet = recoveryConfigs["network"][0]["Subnet"]
        protection_plans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
        if len(protection_plans) != 0:
            self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(protectionPlanName)))
            '''Click on Actions'''
            self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
            '''Click on reverse'''
            self.onClick((By.XPATH, XpathConstants.REVERSE_BUTTON_XPATH))
            '''Click on next'''
            self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
            if recoveryConfigs:
                self.findElement((By.XPATH, XpathConstants.GENERAL_TAB))
                self.onClick((By.XPATH, XpathConstants.GENERAL_TAB))
                '''Select Instance Type'''
                # self.singleSelectFromDropdown((By.XPATH, "//div[@class=' css-k6pgh1']"), instanceType)
                '''Select Encryption KMS Key'''
                self.singleSelectFromDropdown((By.XPATH, XpathConstants.KMS_KEY),encryptionKMSKey)
                'Click on network'''
                self.onClick((By.XPATH, XpathConstants.NETWORK_XPATH))
                '''Click on Config'''
                self.onClick((By.XPATH, XpathConstants.CONFIG))
                '''Select VPC'''
                self.singleSelectFromDropdown((By.XPATH, XpathConstants.VPC_XPATH),
                                              VPC)
                '''Select Subnet'''
                self.singleSelectFromDropdown((By.XPATH,
                                               XpathConstants.SUBNET_XPATH),
                                              Subnet)
                '''Clear Private IP'''
                self.clearInputFields((By.XPATH,
                                       XpathConstants.PRIVATE_IP_XPATH))
                '''Click On Save button'''
                self.onClick((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
            '''Click Next'''
            self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
            self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
            '''Enter Suffix value'''
            self.sendInputKeys((By.XPATH, XpathConstants.REVERSE_SUFFIX_XPATH), reverseSuffix)
            '''Click Next'''
            self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
            self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
            '''Click Finish button'''
            sleep(3)
            self.onClick((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
            sleep(3)
            logger.info(Constants.REVERSE_INITIATED)
            addTestResultToReportSheet(
                filepath, Constants.REVERSE_TEST, Constants.REVERSE_HEADER, data, Constants.REVERSE_INITIATED)
        else:
            self.logger.error("protection plan list not found")
