import json
from Actions.CleanupActions import CleanupActions
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet, createSummarySheet, summaryHeader, addTestResultToReportSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login
from Constants.Constants import Constants
import unittest
import os


class CleanupTestRecoveryTestSuite(ParametrizedTestCase):


    @classmethod
    def setUpClass(cls):
        '''
        This function will call only once at starting of the suite to set up browser
        '''
        setupBrowser(cls)
        cls.CleanupActions = CleanupActions(cls.driver)


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
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.CLEANUP_TEST)
        if not createSheet:
            self.logger.warning(Constants.REPORT_FILE_NOT_FOUND)
        login(self, self.param["setup"], self.CleanupActions, goToPage=Constants.PROTECTION_PLAN_ACTION, key="targeturl")


    def testCleanup(self):
        '''
        This function will call method cleanup from CleanupAction
        '''
        if self.TestCases.get("testCleanup") is not None:
            executeTestCase = self.TestCases["testCleanup"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.CLEANUP_TEST,
                                  Constants.HEADER, Constants.CLEANUP_TEST_SHEET_NAME)
                result = []
                for data in self.TestCases.get("testCleanup")["data"]:
                    testCaseStatus = self.CleanupActions.cleanup(data, self.reportFilePath, self.logger)
                    result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.FAILED)
            else:
                self.logger.warning("Skipped Cleanup")
        else:
            self.logger.warning("Cleanup Test Case not added")


    @classmethod
    def tearDownClass(cls):
        '''
        This function always will get called at the end to close the browser
        '''
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
