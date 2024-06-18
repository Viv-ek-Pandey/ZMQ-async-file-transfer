import json
import unittest
from Actions.PplanActions import PplanActions
from Constants.Constants import Constants
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet, suiteReportHeader, createSummarySheet, summaryHeader, addTestResultToReportSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login
import os


class PplanTestSuite(ParametrizedTestCase):


    @classmethod
    def setUpClass(cls):
        '''
        This function will call only once at starting of the suite to set up browser
        '''
        setupBrowser(cls)
        cls.PplanActions = PplanActions(cls.driver)


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
        self.reportFilePath = loadFilePath(
            f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        summary = createSummarySheet(self.reportFilePath)
        if summary:
            getOrCreateSheet(self.reportFilePath, Constants.SUMMARY)
            header = summaryHeader(self.reportFilePath)
            if header:
                suiteReportHeader(self.reportFilePath, Constants.SUMMARY,
                                Constants.SUMMARY_HEADER, Constants.SUMMARY_TEST_SHEET_NAME)
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.PROTECTION_PLAN_TEST)
        if not createSheet:
            self.logger.warning(Constants.REPORT_FILE_NOT_FOUND)
        login(self, self.param["setup"], self.PplanActions, Constants.PROTECTION_PLAN_ACTION)


    def testProtectionPlanAdd(self):
        '''
        This function will call method addProtectionPlan from PplanActions
        '''
        if self.TestCases.get("testProtectionPlanAdd") is not None:
            executeTestCase = self.TestCases["testProtectionPlanAdd"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.PROTECTION_PLAN_TEST,
                                  Constants.PROTECTION_PLAN_HEADER, Constants.PROTECTION_PLAN_ADDITION_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testProtectionPlanAdd"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.PplanActions.addProtectionPlan(test, self.reportFilePath, self.logger)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
            else:
                self.logger.warning("Skipped Protection Plan addition test")
        else:
            self.logger.warning("Protection Plan Add test cases not added")
    

    def testProtectionPlanEdit(self):
        '''
        This function will call method editProtectionPlan from PplanActions
        '''
        if self.TestCases.get("testProtectionPlanEdit") is not None:
            executeTestCase = self.TestCases["testProtectionPlanEdit"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.PROTECTION_PLAN_TEST,
                                Constants.PROTECTION_PLAN_HEADER, Constants.PROTECTION_PLAN_EDIT_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testProtectionPlanEdit"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.PplanActions.editProtectionPlan(test, self.reportFilePath, self.logger)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
            else:
                self.logger.warning("Skipped Protection Plan Edit test")
        else:
            self.logger.warning("Protection Plan Edit test cases not added")

    
    def testProtectionPlanStop(self):
        '''
        This function will call method stopProtectionPlan from PplanActions
        '''
        if self.TestCases.get("testProtectionPlanStop") is not None:
            executeTestCase = self.TestCases["testProtectionPlanStop"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.PROTECTION_PLAN_TEST,
                                  Constants.PROTECTION_PLAN_HEADER, Constants.PROTECTION_PLAN_STOP_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testProtectionPlanStop"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.PplanActions.stopProtectionPlan(test, self.reportFilePath, self.logger)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
                        
            else:
                self.logger.warning("Skipped Protection Plan Stop test")
        else:
            self.logger.warning("Protection Plan Stop test cases not added")
    

    def testStartProtectionPlan(self):
        '''
        This function will call method startProtectionPlan from PplanActions
        '''
        if self.TestCases.get("testProtectionPlanStart") is not None:
            executeTestCase = self.TestCases["testProtectionPlanStart"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.PROTECTION_PLAN_TEST,
                                  Constants.PROTECTION_PLAN_HEADER, Constants.PROTECTION_PLAN_START_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testProtectionPlanStart"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.PplanActions.startProtectionPlan(test, self.reportFilePath, self.logger)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
            else:
                self.logger.warning("Skipped Protection Plan Stop test")
        else:
            self.logger.warning("Protection Plan Stop test cases not added")


    def testTestProtectionPlanDelete(self):
        '''
        This function will call method deleteProtectionPlan from PplanActions
        '''
        if self.TestCases.get("testProtectionPlanDelete") is not None:
            executeTestCase = self.TestCases["testProtectionPlanDelete"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.PROTECTION_PLAN_TEST,
                                  Constants.PROTECTION_PLAN_HEADER, Constants.PROTECTION_PLAN_DELETE_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testProtectionPlanDelete"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.PplanActions.deleteProtectionPlan(test, self.reportFilePath, self.logger)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
            else:
                self.logger.warning("Skipped Protection Plan Delete test")
        else:
            self.logger.warning("Protection Plan Delete test cases not added")


    @classmethod
    def tearDownClass(cls):
        '''
        This function always will get called at the end to close the browser
        '''
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
