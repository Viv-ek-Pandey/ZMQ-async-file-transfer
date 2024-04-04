from time import sleep
from Constants.ApiConstants import ApiConstants
from Utilities.utils import getApiResponse
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from Utilities.utils import getLogger

class AlertActions(CommonWebPageActions):

    def __init__(self, driver):

        super().__init__(driver)
        self.driver = driver
        self.logger = getLogger()

    def ack_vm_alerts(self,jsonData):
        alertList = self.getUpdatedAlertsData() or []
        print(alertList,"list")
        for data in jsonData:
            title = data.get('alertTitle')
            self.sendInputKeys((By.XPATH,"//input[@id='datableSearch']"),title)
            self.onEnter((By.XPATH, "//input[@id='datableSearch']"))
            if len(alertList) > 0:
                for record in alertList:
                    description = record.get('description')
                alertid = record.get('id')
                print(description)
                if(description == title):
                    print("onclick")
                    self.onClick((By.XPATH,f"//i[@id='alert-popover-key-{alertid}']"))
                break;
            else:
                self.logger.warning("No alert data found")
            sleep(20)
    
    def getUpdatedAlertsData(self):
        '''delete the previous node data in order to start fresh'''
        del self.driver.requests

        '''click on refresh icon to get the fresh data on UI screen'''
        self.onClick((By.XPATH, "//button[@id='datagridColFilter']"))
        self.onClick((By.XPATH, "//a[normalize-space()='Apply']"))
        res =getApiResponse(self, ApiConstants.FETCH_ALERTS_LIST)
        print(res,"apires")
        return res
