from time import sleep
from Constants.ApiConstants import ApiConstants
from Constants.Constants import Constants
from Utilities.XLUtils import addTestResultToReportSheet
from Utilities.utils import getLogger
from Utilities.utils import getApiResponse
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By

class ScriptActions(CommonWebPageActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.logger = getLogger()

    def uploadScript(self,jsonTestData,reportFileName):
        for data in jsonTestData:
            
            description = data['description']
            password = data['password']
            scriptType= data['scriptType']
            scriptFilePath=data['scriptFilePath']
            result=''
            
            self.onClick((By.XPATH,"//i[@class='fa fa-plus']"))
            self.sendInputKeys((By.XPATH,"//input[@id='scriptDescription']"),description)
            self.sendInputKeys((By.XPATH,"//input[@id='scriptPassword']"),password)
            
            if scriptType=="pre":
                self.onClick((By.XPATH,"//label[normalize-space()='Pre Script']"))
            else:
                self.onClick((By.XPATH,"//label[normalize-space()='Post Script']"))
                
            uploaded =self.uploadFile((By.XPATH,"//input[@id='fileUpload']"),scriptFilePath)
            print(uploaded,"upload")
            if uploaded:
                self.onClick((By.XPATH,"//button[normalize-space()='Close']"))
                result=uploaded
                self.logger.error(uploaded)
            else: 
                self.onClick((By.XPATH,"//button[normalize-space()='Save']"))
                res=getApiResponse(self,ApiConstants.UPLOAD_SCRIPT)
                print(res)
                print(isinstance(res,'list'))
                if not isinstance(res,'list'):
                    result=res
                    print("entered")
                    self.onClick((By.XPATH,"//button[normalize-space()='Close']"))
                    self.logger.error("script with description {description} has not uploaded successfully")
                    self.onClick((By.XPATH,"//button[normalize-space()='Close"))
                else:
                    result=f"script with description {description} has uploaded"
                    self.logger.info(result)
                sleep(5)
            
            addTestResultToReportSheet(
                    reportFileName, Constants.SCRIPT_TEST, Constants.SCRIPT_TEST_HEADER, data, result)