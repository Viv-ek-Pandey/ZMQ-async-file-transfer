import json
import unittest
from Actions.ReverseActions import ReverseActions
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.conftest import setupBrowser
from Utilities.utils import getLogger, loadFilePath, login
from Utilities.XLUtils import getOrCreateSheet
from Constants.Constants import Constants
from Utilities.XLUtils import suiteReportHeader


class ReverseTestSuite(ParametrizedTestCase):

    @classmethod
    def setUpClass(cls):
        setupBrowser(cls)
        cls.reverseActions = ReverseActions(cls.driver)
        cls.logger = getLogger()

    def setUp(self):
        filePath = loadFilePath(self.param["datafilename"])
        with open(filePath) as f:
            self.TestCases = json.load(f)
        self.logger = self.param["logger"]
        self.setup = self.param["setup"]
        self.reportFileName = self.param["reportFileName"]
        self.reportFilePath = loadFilePath(f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.REVERSE_TEST)
        if not createSheet:
            self.logger.warning("Report File Not found")
        login(self, self.param["setup"], self.reverseActions, "protection/plans", key="targeturl")

    def test_pplan_Reverse(self):
        if self.TestCases.get("test_reverse") is not None:
            execute_test_case = self.TestCases["test_reverse"]["executeTestCase"]
            if execute_test_case:
                suiteReportHeader(self.reportFilePath, Constants.REVERSE_TEST,
                                  Constants.REVERSE_HEADER, Constants.REVERSE_TEST_SHEET_NAME)
                for data in self.TestCases["test_reverse"]["data"]:
                    self.reverseActions.executeReverse(data, self.reportFilePath, self.logger)
            else:
                self.logger.warning("Skipped Reverse test case")
        else:
            self.logger.warning("Reverse test case no added")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
