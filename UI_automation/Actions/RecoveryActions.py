from time import sleep
from Utilities.utils import getLogger
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from Utilities.utils import getApiResponse
from Utilities.utils import getCell
from Actions.ReplicationJobsActions import ReplicationJobsActions
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants
from Constants.ApiConstants import ApiConstants
from Constants.XpathConstants import XpathConstants


class RecoveryActions(CommonWebPageActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.ReplicationAction = ReplicationJobsActions(self.driver)
        self.driver = driver
        self.logger = getLogger()
        self.Virtual_Machine_List = []

    '''This function will check replication of existing virtual machine is completed or not and after that it will call 
    fill_test_recovery_data'''

    def executeTestRecovery(self, data, filepath, logger, Test_Case_Name=None):
        self.findElement((By.XPATH, XpathConstants.TABLE_XPATH))
        Protection_Plan_Name = data["protection_plan"]
        Virtual_Machine = data["virtual_machine"]
        Protection_Plans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
        if len(Protection_Plans) != 0 and Protection_Plan_Name == data["protection_plan"]:
            '''Click on Jobs fields'''
            self.onClick((By.XPATH, XpathConstants.JOBS_SECTION_XPATH))
            '''Click on Replication'''
            self.onClick((By.XPATH, XpathConstants.REPLICATION_SECTION_XPATH))
            for each_machine in Virtual_Machine:
                '''Click on Virtual Machine icon'''
                self.onAnimationClick(
                    (By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
                out = self.ReplicationAction.check_job_status_of_virtual_machine(each_machine, filepath,
                                                                                 Test_Case_Name)
                if out == "Completed":
                    self.Virtual_Machine_List.append(each_machine)
            self.fill_test_recovery_data(data, filepath, self.Virtual_Machine_List, Test_Case_Name)
        else:
            logger.warning("Protection Plan not found")

    '''This function will search each of virtual machine and select it'''

    def search_virtual_machine(self, machine):
        """Clear search box fieds"""
        self.clearInputFields((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
        self.onEnter((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
        '''Enter data into search box'''
        self.sendInputKeys((By.XPATH, XpathConstants.SEARCH_BOX_XPATH), machine)
        self.onEnter((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
        '''It will find username textbox'''
        self.findElement((By.XPATH, XpathConstants.USERNAME_TEXTBOX_XPATH))
        '''Enter values into username textbox'''
        self.sendInputKeys((By.XPATH, XpathConstants.USERNAME_TEXTBOX_XPATH), "username")
        '''It will find password textbox'''
        self.findElement((By.XPATH, XpathConstants.PASSWORD_TEXTBOX_XPATH))
        '''Enter values into password textbox'''
        self.sendInputKeys((By.XPATH, XpathConstants.PASSWORD_TEXTBOX_XPATH), "password")
        self.onClick((By.XPATH, XpathConstants.TEST_RECOVERY_VM_CHECKBOX_XPATH))

    '''This function will fill test recovery data'''

    def fill_test_recovery_data(self, data, filepath, virtual_machine_list, Test_Case_Name):
        Protection_Plan_Name = data["protection_plan"]
        """ To click configure"""
        self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
        """ To click Protection Plan section"""
        self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
        """ To click actual protection plan element"""
        self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(Protection_Plan_Name)))
        """ To click on Actions"""
        self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
        """ To click on test recovery"""
        self.onClick((By.XPATH, XpathConstants.TEST_RECOVRY_BUTTON_XPATH))
        self.waitUntil((By.XPATH, XpathConstants.TEST_RECOVERY_WORKLOAD_XPATH))
        for each_virtual_machine in virtual_machine_list:
            self.search_virtual_machine(each_virtual_machine)
        self.waitUntil((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        '''Click next button'''
        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        self.waitUntil((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
        self.waitUntil((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
        '''Click Finish button'''
        self.onClick((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
        '''To find Jobs fields'''
        self.findElement((By.XPATH, XpathConstants.JOBS_SECTION_XPATH))
        '''Click on Jobs fields'''
        self.onClick((By.XPATH, XpathConstants.JOBS_SECTION_XPATH))
        '''Click on rec'''
        self.onClick((By.XPATH, XpathConstants.RECOVERY_SECTION_XPATH))
        self.onAnimationClick(
            (By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
        self.waitUntil((By.XPATH, XpathConstants.TABLE_XPATH))
        for each_virtual_machine in virtual_machine_list:
            self.check_status_of_vm(each_virtual_machine, data, filepath, Test_Case_Name)

    '''This function will check status of virtual machine'''

    def check_status_of_vm(self, machine, data, filepath, Test_Case_Name=None):
        self.ReplicationAction.enter_virtual_machine(machine)
        getSearchVmList = f"api/v1/jobs/replication/vms?limit=100&searchstr={machine}&searchcol=vmName,status,syncStatus"
        out = getApiResponse(self, getSearchVmList)
        result_of_job_status = getCell(self, "Job Status", 0)
        status = result_of_job_status.find_elements(by=By.XPATH, value=XpathConstants.RECOVERY_TABLE_ITEM_XPATH)
        status_of_job = status[3].text
        updated_status = status_of_job.lstrip()
        job_status = self.check_job_status(machine, updated_status, data, filepath, Test_Case_Name)
        return job_status

    '''Depending on the status below function will re-execute the code'''

    def check_job_status(self, machine, job_status, data, filepath, Test_Case_Name=None):
        if job_status == Constants.RUNNING:
            sleep(60)
            self.onClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))
            return self.check_status_of_vm(machine, data, filepath, Test_Case_Name)
        elif job_status == Constants.COMPLETED:
            if Test_Case_Name == "test_test_recovery":
                self.logger.info("Test Recovery Job Completed")
                addTestResultToReportSheet(filepath, Constants.TEST_RECOVERY, Constants.TEST_RECOVERY_HEADER, data,
                                           Constants.COMPLETED)
            return "Completed"
        else:
            if Test_Case_Name == "test_test_recovery":
                self.logger.error("Test Recovery Job Failed")
                addTestResultToReportSheet(
                    filepath, Constants.TEST_RECOVERY, Constants.TEST_RECOVERY_HEADER, data, Constants.FAILED)
            return "Failed"

    '''This function will execute recovery'''

    def executeRecovery(self, jsonTestData, filepath, Test_Case_Name):
        Protection_Plans = getApiResponse(self, ApiConstants.GET_PPLAN_LIST)
        for data in jsonTestData:
            Protection_Plan_Name = data["protection_plan"]
            Virtual_Machine = data["virtual_machine"]
            if len(Protection_Plans) != 0:
                if Protection_Plan_Name == data["protection_plan"]:
                    """ To click configure"""
                    self.onClick((By.XPATH, XpathConstants.CONFIGURE_SECTION_XPATH))
                    """ To click Protection Plan section"""
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_SECTION_XPATH))
                    """ To click actual protection plan element"""
                    self.waitUntil((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(Protection_Plan_Name)))
                    self.onClick((By.XPATH, XpathConstants.PROTECTION_PLAN_XPATH.format(Protection_Plan_Name)))
                    """ To click on Actions"""
                    self.onClick((By.XPATH, XpathConstants.ACTIONS_BUTTON_XPATH))
                    """ To click on Recover"""
                    self.onClick((By.XPATH, XpathConstants.RECOVERY_BUTTON_XPATH))
                    self.waitUntil((By.XPATH, XpathConstants.RECOVERY_WORKLOAD_XPATH))
                    for each_machine in Virtual_Machine:
                        self.search_virtual_machine(each_machine)
                    '''Click Next button'''
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    self.onClick((By.XPATH, XpathConstants.NEXT_BUTTON_XPATH))
                    '''Click Finish button'''
                    self.onClick((By.XPATH, XpathConstants.SAVE_BUTTON_XPATH))
                    self.findElement((By.XPATH, XpathConstants.SUCCESS_MESSAGE_POPUP_XPATH))
                    self.onClick((By.XPATH, XpathConstants.SUCCESS_MESSAGE_POPUP_XPATH))
                    '''To find Jobs fields'''
                    self.findElement((By.XPATH, XpathConstants.JOBS_SECTION_XPATH))
                    '''Click On Jobs fields'''
                    self.onClick((By.XPATH, XpathConstants.JOBS_SECTION_XPATH))
                    '''Click on Recovery'''
                    self.onClick((By.XPATH, XpathConstants.RECOVERY_SECTION_XPATH))
                    '''Click on Virtual Machine icon'''
                    self.onAnimationClick(
                        (By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
                    self.waitUntil((By.XPATH, XpathConstants.TABLE_XPATH))
                    for each_virtual_machine in Virtual_Machine:
                        self.check_status_of_vm(each_virtual_machine, filepath, Test_Case_Name)
            self.logger.info("Recovery Job Completed")
