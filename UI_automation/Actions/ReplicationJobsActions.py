from time import sleep
from Constants.XpathConstants import XpathConstants
from Utilities.utils import getCellValue
from Utilities.CommonWebPageActions import CommonWebPageActions
from selenium.webdriver.common.by import By
from Utilities.utils import getApiResponse
from Utilities.utils import getLogger
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants


class ReplicationJobsActions(CommonWebPageActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        self.logger = getLogger()

    '''This function will take data from json file'''

    def monitor_protection_plan_replication_jobs(self, machine, filepath, logger, Test_Case_Name=None):
        """Click on Virtual Machine Icon"""
        self.onAnimationClick(
            (By.XPATH, XpathConstants.VIRTUAL_MACHINE_ICON_XPATH))
        self.findElement((By.XPATH, XpathConstants.REPLICATION_VM_LIST_TABLE_XPATH))
        return self.check_job_status_of_virtual_machine(machine, filepath, Test_Case_Name)

    '''This function will enter virtual machine and search for result'''

    def enter_virtual_machine(self, virtual_machine):
        """Clear search box to enter the data"""
        self.clearInputFields((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))
        '''Enter data into search box'''
        self.sendInputKeys((By.XPATH, XpathConstants.SEARCH_BOX_XPATH), virtual_machine)
        self.onEnter((By.XPATH, XpathConstants.SEARCH_BOX_XPATH))

    '''This function will check job status of virtual machine'''

    def check_job_status_of_virtual_machine(self, machine, filepath, Test_Case_Name):
        self.enter_virtual_machine(machine)
        getSearchVmList = f"api/v1/jobs/replication/vms?limit=100&searchstr={machine}&searchcol=vmName,status,syncStatus"
        getApiResponse(self, getSearchVmList)
        '''It will find the status of particular virtual machine'''
        status = getCellValue(self, 'Job Status', 0)
        job_status = status.lstrip()
        output_of_job_status = self.check_job_status(machine, job_status, filepath, Test_Case_Name)
        return output_of_job_status

    '''Depending on the status below function will re-execute the code'''

    def check_job_status(self, machine, job_status, filepath, Test_Case_Name):
        if job_status == Constants.RUNNING:
            sleep(60)
            self.onClick((By.XPATH, XpathConstants.REFRESH_BUTTON_XPATH))
            return self.check_job_status_of_virtual_machine(machine, filepath, Test_Case_Name)
        elif job_status == Constants.COMPLETED:
            if Test_Case_Name == "test_protection_plan_monitor_replication":
                addTestResultToReportSheet(filepath, Constants.REPLICATION_TEST, Constants.REPLICATION_HEADER, machine,
                                           Constants.COMPLETED)
            self.logger.info("Replication Job Completed")
            return "Completed"
        else:
            if Test_Case_Name == "test_protection_plan_monitor_replication":
                addTestResultToReportSheet(
                    filepath, Constants.REPLICATION_TEST, Constants.REPLICATION_HEADER, machine, Constants.FAILED)
            self.logger.info("Replication Job Failed")
            return "Failed"
