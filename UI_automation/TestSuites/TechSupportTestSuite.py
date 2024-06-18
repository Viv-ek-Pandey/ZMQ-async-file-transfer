import json
from Actions.TechSupportActions import TechSupportActions
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login
from Constants.Constants import Constants
import unittest
import os


class TechSupportTestSuite(ParametrizedTestCase):


    @classmethod
    def setUpClass(cls):
        '''
        This function will call only once at starting of the suite to set up browser
        '''
        setupBrowser(cls)
        cls.TechSupportActions = TechSupportActions(cls.driver)


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
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.TECH_SUPPORT_TEST)
        if not createSheet:
            self.logger.warning(Constants.REPORT_FILE_NOT_FOUND)
        login(self, self.param["setup"], self.TechSupportActions, goToPage=Constants.SETTINGS)


    def testTechSuport(self):
        '''
        This function will call method techSupport from TechSupportActions
        '''
        if self.TestCases.get("testTechSupport") is not None:
            executeTestCase = self.TestCases["testTechSupport"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.TECH_SUPPORT_TEST,
                                  Constants.TECH_SUPPORT_HEADER, Constants.TECH_SUPPORT_TEST_SHEET_NAME)
                for data in self.TestCases.get("testTechSupport")["data"]:
                    self.TechSupportActions.techSupport(data, self.reportFilePath, self.logger)
            else:
                self.logger.warning("Skipped Tech Support")
        else:
            self.logger.warning("Tech Support Test Case not added")


    @classmethod
    def tearDownClass(cls):
        '''
        This function always will get called at the end to close the browser
        '''
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()