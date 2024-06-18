import json
import unittest
from Actions.SiteActions import SiteActions
from Constants.Constants import Constants
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet, createSummarySheet, summaryHeader, addTestResultToReportSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login
import os


class SiteTestSuite(ParametrizedTestCase):


    @classmethod
    def setUpClass(cls):
        '''
        This function will call only once at starting of the suit to set up browser
        '''
        setupBrowser(cls)
        cls.SiteAction = SiteActions(cls.driver)


    def setUp(self):
        '''
        This function will call before calling each method, it will login to setup and will create report file as well
        '''
        self.logger = self.param["logger"]
        filePath = loadFilePath(self.param[Constants.DATAFILENAME])
        if os.path.exists(filePath):
            with open(filePath, encoding="utf-8") as f:
                self.TestCases = json.load(f)
        else:
            self.logger.info(Constants.JSON_FILE_NOT_FOUND)
        self.reportFileName = self.param[Constants.REPORT_FILENAME]
        self.reportFilePath = loadFilePath(
            f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        summary = createSummarySheet(self.reportFilePath)
        if summary:
            getOrCreateSheet(self.reportFilePath, Constants.SUMMARY)
            header = summaryHeader(self.reportFilePath)
            if header:
                suiteReportHeader(self.reportFilePath, Constants.SUMMARY,
                                Constants.SUMMARY_HEADER, Constants.SUMMARY_TEST_SHEET_NAME)
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.SITE_TEST)
        if not createSheet:
            self.logger.warning(Constants.REPORT_FILE_NOT_FOUND)
        login(self, self.param["setup"], self.SiteAction, Constants.SITE_ACTION)


    def testAddSite(self):
        '''
        This function will call method addSite from SiteActions
        '''
        if self.TestCases.get("testSiteAdd") is not None:
            executeTestCase = self.TestCases["testSiteAdd"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.SITE_TEST,
                                  Constants.SITE_HEADER, Constants.SITE_ADDITION_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testSiteAdd"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.SiteAction.addSite(test, self.logger, self.reportFilePath)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
            else:
                self.logger.warning("Skipped Site addition test")
        else:
            self.logger.warning("Site Add test cases not added")
    

    def testEditSite(self):
        '''
        This function will call method editSite from SiteActions
        '''
        if self.TestCases.get("testSiteEdit") is not None:
            executeTestCase = self.TestCases["testSiteEdit"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.SITE_TEST,
                                  Constants.SITE_HEADER, Constants.SITE_EDITION_TEST_SHEET_NAME)
                result = []
                testCaseStatus = self.SiteAction.editSite(self.TestCases.get(
                    "testSiteEdit")["data"], self.logger, self.reportFilePath)
                result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, self.TestCases.get(
                    "testSiteEdit")["data"][0]["id"], testCaseStatus)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, self.TestCases.get(
                    "testSiteEdit")["data"][0]["id"], testCaseStatus)
                
            else:
                self.logger.warning("Skipped Site edition test")
        else:
            self.logger.warning("Site Edit test case not added")


    def testSiteDelete(self):
        '''
        This function will call method deleteSite from SiteActions
        '''
        if self.TestCases.get("testSiteDelete") is not None:
            executeTestCase = self.TestCases["testSiteDelete"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.SITE_TEST,
                                  Constants.SITE_DELETE_HEADER, Constants.SITE_DELETION_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testSiteDelete"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.SiteAction.deleteSite(test, self.logger, self.reportFilePath)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
                
            else:
                self.logger.warning("Skipped Site Deletion test")
        else:
            self.logger.warning("Site Delete test cases not added")


    @classmethod
    def tearDownClass(cls):
        '''
        This function always will get called at the end to close the browser
        '''
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
