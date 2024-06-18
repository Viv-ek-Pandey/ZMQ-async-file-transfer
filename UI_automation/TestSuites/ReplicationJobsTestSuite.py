import json
import unittest
from Constants.Constants import Constants
from Actions.ReplicationJobsActions import ReplicationJobsActions
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet, createSummarySheet, summaryHeader, addTestResultToReportSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login
from Utilities.XLUtils import suiteReportHeader
import os


class ReplicationJobsTestSuite(ParametrizedTestCase):


    @classmethod
    def setUpClass(cls):
        '''This function will call only once at starting of the suit to set up browser
        '''
        setupBrowser(cls)
        cls.ReplicationAction = ReplicationJobsActions(cls.driver)


    def setUp(self):
        '''
        This function will call before calling each method, it will login to setup and will create report file as well
        '''
        self.logger = self.param["logger"]
        filePath = loadFilePath(self.param[Constants.DATAFILENAME])
        if os.path.exists(filePath):
            with open(filePath) as f:
                self.TestCases = json.load(f)
        else:
            self.logger.info(Constants.JSON_FILE_NOT_FOUND)
        self.reportFileName = self.param[Constants.REPORT_FILENAME]
        self.reportFilePath = loadFilePath(f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        summary = createSummarySheet(self.reportFilePath)
        if summary:
            getOrCreateSheet(self.reportFilePath, Constants.SUMMARY)
            header = summaryHeader(self.reportFilePath)
            if header:
                suiteReportHeader(self.reportFilePath, Constants.SUMMARY,
                                Constants.SUMMARY_HEADER, Constants.SUMMARY_TEST_SHEET_NAME)
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.REPLICATION_TEST)
        if not createSheet:
            self.logger.warning(Constants.REPORT_FILE_NOT_FOUND)
        login(self, self.param["setup"], self.ReplicationAction, Constants.PROTECTION_PLAN_ACTION)


    def testMonitorProtectionPlanReplicationOfVirtualMachineJobs(self):
        '''
        This function will call method monitorProtectionPlanReplicationOfVirtualMachineJobs from ReplicationJobsActions
        '''
        if self.TestCases.get("testMonitorProtectionPlanReplicationOfVirtualMachineJobs") is not None:
            execute_test_case = self.TestCases["testMonitorProtectionPlanReplicationOfVirtualMachineJobs"]["executeTestCase"]
            testCaseName = list(self.TestCases.keys())[0]
            if execute_test_case:
                suiteReportHeader(self.reportFilePath, Constants.REPLICATION_TEST,
                                  Constants.HEADER, Constants.REPLICATION_OF_VIRTUAL_MACHINES_JOB_TEST_SHEET_NAME)
                result = []
                for data in self.TestCases["testMonitorProtectionPlanReplicationOfVirtualMachineJobs"]["data"]:
                    testCaseStatus = self.ReplicationAction.monitorProtectionPlanReplicationOfVirtualMachineJobs(data, self.reportFilePath,
                                                                                    self.logger, testCaseName)
                    result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.FAILED)
            else:
                self.logger.warning("Skipped Monitor Replication Of Virtual Machine test case")
        else:
            self.logger.warning("Monitor Replication Of Virtual Machine test case is not added")


    def testMonitorProtectionPlanReplicationOfDisksJobs(self):
        '''
        This function will call method monitorProtectionPlanReplicationOfDisksJobs from ReplicationJobsActions
        '''
        if self.TestCases.get("testMonitorProtectionPlanReplicationOfDisksJobs") is not None:
            execute_test_case = self.TestCases["testMonitorProtectionPlanReplicationOfDisksJobs"]["executeTestCase"]
            testCaseName = list(self.TestCases.keys())[0]
            if execute_test_case:
                suiteReportHeader(self.reportFilePath, Constants.REPLICATION_TEST,
                                  Constants.HEADER, Constants.REPLICATION_OF_DISKS_JOBS_TEST_SHEET_NAME)
                result = []
                for data in self.TestCases["testMonitorProtectionPlanReplicationOfDisksJobs"]["data"]:
                    testCaseStatus = self.ReplicationAction.monitorProtectionPlanReplicationOfDisksJobs(data, self.reportFilePath,
                                                                                    self.logger, testCaseName)
                    result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.FAILED)
            else:
                self.logger.warning("Skipped Monitor Replication Of Disk Jobs test case")
        else:
            self.logger.warning("Monitor Replication Of Disk Jobs test case is not added")


    @classmethod
    def tearDownClass(cls):
        '''
        This function will call only once at ending of the suit to quit browser
        '''
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
