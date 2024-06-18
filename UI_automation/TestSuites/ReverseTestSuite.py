import json
import unittest
from Actions.ReverseActions import ReverseActions
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login
from Utilities.XLUtils import getOrCreateSheet, createSummarySheet, summaryHeader, addTestResultToReportSheet
from Constants.Constants import Constants
from Utilities.XLUtils import suiteReportHeader
import os


class ReverseTestSuite(ParametrizedTestCase):


    @classmethod
    def setUpClass(cls):
        '''
        This function will call only once at starting of the suit to set up browse
        '''
        setupBrowser(cls)
        cls.reverseActions = ReverseActions(cls.driver)


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
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.REVERSE_TEST)
        if not createSheet:
            self.logger.warning(Constants.REPORT_FILE_NOT_FOUND)
        login(self, self.param["setup"], self.reverseActions, Constants.PROTECTION_PLAN_ACTION, key="targeturl")


    def testProtectionPlanReverse(self):
        '''
        This function will call method executeReverse from RevereseActions
        '''
        if self.TestCases.get("testReverse") is not None:
            execute_test_case = self.TestCases["testReverse"]["executeTestCase"]
            if execute_test_case:
                suiteReportHeader(self.reportFilePath, Constants.REVERSE_TEST,
                                  Constants.HEADER, Constants.REVERSE_TEST_SHEET_NAME)
                result = []
                for data in self.TestCases["testReverse"]["data"]:
                    testCaseStatus = self.reverseActions.executeReverse(data, self.reportFilePath, self.logger)
                    result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.FAILED)
            else:
                self.logger.warning("Skipped Reverse test case")
        else:
            self.logger.warning("Reverse test case no added")


    @classmethod
    def tearDownClass(cls):
        '''
        This function always will get called at the end to close the browser
        '''
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
