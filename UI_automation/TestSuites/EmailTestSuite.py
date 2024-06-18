import json
from Actions.EmailActions import EmailActions
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet, createSummarySheet, summaryHeader, addTestResultToReportSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login
from Constants.Constants import Constants
import unittest
import os


class EmailTestSuite(ParametrizedTestCase):

    @classmethod
    def setUpClass(cls):
        '''
        This function will call only once at starting of the suite to set up browser
        '''
        setupBrowser(cls)
        cls.EmailActions = EmailActions(cls.driver)


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
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.EMAIL_TEST)
        if not createSheet:
            self.logger.warning(Constants.REPORT_FILE_NOT_FOUND)
        login(self, self.param["setup"], self.EmailActions, goToPage=Constants.SETTINGS)
    

    def testEmail(self):
        '''
        This function will call method email from EmailActions
        '''
        if self.TestCases.get("testEmail") is not None:
            executeTestCase = self.TestCases["testEmail"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.EMAIL_TEST,
                                  Constants.EMAIL_HEADER, Constants.EMAIL_TEST_SHEET_NAME)
                result = []
                for data in self.TestCases.get("testEmail")["data"]:
                    testCaseStatus = self.EmailActions.email(data, self.reportFilePath, self.logger)
                    result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.FAILED)
            else:
                self.logger.warning("Skipped Email")
        else:
            self.logger.warning("Email Test Case not added")
    

    def testRecipientEmail(self):
        '''
        This function will call method emailRecipients from EmailActions
        '''
        if self.TestCases.get("testRecipientEmail") is not None:
            executeTestCase = self.TestCases["testRecipientEmail"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.EMAIL_TEST,
                                  Constants.EMAIL_RECIPIENT_HEADER, Constants.EMAIL_RECIPIENT_TEST_SHEET_NAME)
                result = []
                for data in self.TestCases.get("testRecipientEmail")["data"]:
                    testCaseStatus = self.EmailActions.emailRecipients(data, self.reportFilePath, self.logger)
                    result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.FAILED)
            else:
                self.logger.warning("Skipped Recipient Email")
        else:
            self.logger.warning("Email Recipient Test Case not added")


    @classmethod
    def tearDownClass(cls):
        '''
        This function always will get called at the end to close the browser
        '''
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()

