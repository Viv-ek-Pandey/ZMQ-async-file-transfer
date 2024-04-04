import json
from Actions.CleanupActions import CleanupActions
from Utilities.utils import getLogger
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login
from Constants.Constants import Constants
import unittest


class CleanupTestRecoveryTestSuite(ParametrizedTestCase):
    """This function will call only once at starting of the suite to set up browser"""

    @classmethod
    def setUpClass(cls):
        setupBrowser(cls)
        cls.CleanupActions = CleanupActions(cls.driver)
        cls.logger = getLogger()

    '''This function will call at the starting before calling each method, it will login to setup and will create 
        report file as well'''

    def setUp(self):
        filePath = loadFilePath(self.param["datafilename"])
        with open(filePath) as f:
            self.TestCases = json.load(f)
        self.logger = self.param["logger"]
        self.reportFileName = self.param["reportFileName"]
        self.reportFilePath = loadFilePath(f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.CLEANUP_TEST)
        if not createSheet:
            self.logger.warning("Report File Not found")
        login(self, self.param["setup"], self.CleanupActions, goToPage="protection/plans", key="targeturl")

    '''This function will call method cleanup from CleanupAction'''

    def test_cleanup(self):
        if self.TestCases.get("test_cleanup") is not None:
            executeTestCase = self.TestCases["test_cleanup"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.CLEANUP_TEST,
                                  Constants.CLEANUP_HEADER, Constants.CLEANUP_TEST_SHEET_NAME)
                self.CleanupActions.cleanup(self.TestCases.get("test_cleanup")["data"], self.reportFilePath, self.logger)
            else:
                self.logger.warning("Skipped Cleanup")
        else:
            self.logger.warning("Cleanup Test Case not added")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
