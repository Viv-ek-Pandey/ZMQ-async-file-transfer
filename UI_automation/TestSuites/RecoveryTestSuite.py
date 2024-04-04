import json
import unittest
from Constants.Constants import Constants
from Actions.RecoveryActions import RecoveryActions
from Utilities.utils import getLogger
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login


class RecoveryTestSuite(ParametrizedTestCase):
    """This function will call only once at starting of the suite to set up browser"""

    @classmethod
    def setUpClass(cls):
        setupBrowser(cls)
        cls.RecoveryActions = RecoveryActions(cls.driver)
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
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.TEST_RECOVERY)
        if not createSheet:
            self.logger.warning("Report File Not found")
        login(self, self.param["setup"], self.RecoveryActions, goToPage="protection/plans", key="targeturl")

    '''This function will call method executeTestRecovery from RecoveryAction'''

    def test_test_recovery(self):
        if self.TestCases.get("test_test_recovery") is not None:
            executeTestCase = self.TestCases["test_test_recovery"]["executeTestCase"]
            Test_Case_Name = list(self.TestCases.keys())[0]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.TEST_RECOVERY,
                                  Constants.TEST_RECOVERY_HEADER, Constants.RECOVERY_TEST_SHEET_NAME)
                for data in self.TestCases.get("test_test_recovery")["data"]:
                    self.RecoveryActions.executeTestRecovery(data, self.reportFilePath, Test_Case_Name, self.logger)
            else:
                self.logger.warning("Skipped Test Recovery ")
        else:
            self.logger.warning("Skipped test recovery ")

    '''This function will call method executeRecovery from RecoveryAction'''

    def test_virtual_machine_recovery(self):
        if self.TestCases.get("test_recovery") is not None:
            executeTestCase = self.TestCases["test_recovery"]["executeTestCase"]
            Test_Case_Name = list(self.TestCases.keys())[1]
            if executeTestCase:
                self.RecoveryActions.executeRecovery(self.TestCases.get("test_recovery")["data"], self.reportFilePath,
                                                     Test_Case_Name)
            else:
                self.logger.warning("Skipped Recovery")
        else:
            self.logger.warning("Skipped recovery")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
