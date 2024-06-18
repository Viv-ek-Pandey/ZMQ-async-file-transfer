import json
import unittest
from Constants.Constants import Constants
from Actions.RecoveryActions import RecoveryActions
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet, createSummarySheet, summaryHeader, addTestResultToReportSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login
import os


class RecoveryTestSuite(ParametrizedTestCase):


    @classmethod
    def setUpClass(cls):
        '''This function will call only once at starting of the suite to set up browser
        '''
        setupBrowser(cls)
        cls.RecoveryActions = RecoveryActions(cls.driver)


    def setUp(self):
        '''
        This function will call at the starting before calling each method, it will login to setup and will create 
        report file as well
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
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.TEST_RECOVERY)
        if not createSheet:
            self.logger.warning(Constants.REPORT_FILE_NOT_FOUND)
        login(self, self.param["setup"], self.RecoveryActions, goToPage=Constants.PROTECTION_PLAN_ACTION, key="targeturl")


    def testTestRecovery(self):
        '''
        This function will call method executeTestRecovery from RecoveryAction
        '''
        if self.TestCases.get("testTestRecovery") is not None:
            executeTestCase = self.TestCases["testTestRecovery"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.TEST_RECOVERY,
                                  Constants.HEADER, Constants.RECOVERY_TEST_SHEET_NAME)
                result = []
                for data in self.TestCases.get("testTestRecovery")["data"]:
                    testCaseName = list(self.TestCases.keys())[0]
                    testCaseStatus= self.RecoveryActions.executeTestRecovery(data, self.reportFilePath, self.logger, testCaseName)
                    result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.FAILED)
            else:
                self.logger.warning("Skipped Test Recovery ")
        else:
            self.logger.warning("Skipped test recovery ")


    def testVirtualMachineRecovery(self):
        '''
        This function will call method executeRecovery from RecoveryAction
        '''
        if self.TestCases.get("testRecovery") is not None:
            executeTestCase = self.TestCases["testRecovery"]["executeTestCase"]
            testCaseName = list(self.TestCases.keys())[1]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.TEST_RECOVERY,
                                  Constants.HEADER, Constants.RECOVERY_SHEET_NAME)
                result = []
                for data in self.TestCases.get("testRecovery")["data"]:
                    testCaseStatus = self.RecoveryActions.executeRecovery(data, self.reportFilePath,
                                                         testCaseName, self.logger)
                    result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.FAILED)
            else:
                self.logger.warning("Skipped Recovery")
        else:
            self.logger.warning("Skipped recovery")


    @classmethod
    def tearDownClass(cls):
        '''
        This function always will get called at the end to close the browser
        '''
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
