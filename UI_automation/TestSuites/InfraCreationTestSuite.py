import json
from Actions.InfraCreationActions import InfraCreationActions
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet, createSummarySheet, summaryHeader, addTestResultToReportSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login
from Constants.Constants import Constants
import unittest
import os


class InfraCreationTestSuite(ParametrizedTestCase):

    @classmethod
    def setUpClass(cls):
        '''
        This function will call only once at starting of the suite to set up browser
        '''
        setupBrowser(cls)
        cls.InfraCreationAction = InfraCreationActions(cls.driver)


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
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.INFRA_TEST)
        if not createSheet:
            self.logger.warning(Constants.REPORT_FILE_NOT_FOUND)
    

    def testInfraCreation(self):
        '''
        This function will call method infraCreation from InfraCreationActions
        '''
        if self.TestCases.get("testInfraCreation") is not None:
            executeTestCase = self.TestCases["testInfraCreation"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.INFRA_TEST,
                                  Constants.INFRA_HEADER, Constants.INFRA_CREATION_TEST_SHEET_NAME)
                result = []
                for data in self.TestCases.get("testInfraCreation")["data"]:
                    platform = data["platform"]
                    if platform == "":
                        continue
                    testCaseStatus = self.InfraCreationAction.infraCreation(data, self.reportFilePath, self.logger)
                    result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.FAILED)
            else:
                self.logger.warning("Skipped Infra Creation")
        else:
            self.logger.warning("Infra Creation Test Case not added")
    
    def testInfraDeletion(self):
        '''
        This function will call method infraDelete from InfraCreationActions
        '''
        if self.TestCases.get("testInfraDelete") is not None:
            executeTestCase = self.TestCases["testInfraDelete"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.INFRA_TEST,
                                  Constants.INFRA_HEADER, Constants.INFRA_DELETION_TEST_SHEET_NAME)
                result = []
                for data in self.TestCases.get("testInfraDelete")["data"]:
                    platform = data["platform"]
                    if platform == "":
                        continue
                    testCaseStatus = self.InfraCreationAction.infraDelete(data, self.reportFilePath, self.logger)
                    result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, data, Constants.FAILED)
            else:
                self.logger.warning("Skipped Infra Deleteion")
        else:
            self.logger.warning("Infra Deleteion Test Case not added")


    @classmethod
    def tearDownClass(cls):
        '''
        This function always will get called at the end to close the browser
        '''
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()

