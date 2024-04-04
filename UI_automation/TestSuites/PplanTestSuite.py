import json
import unittest
from Actions.PplanActions import PplanActions
from Constants.Constants import Constants
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import addTestResultToReportSheet, getOrCreateSheet, suiteReportHeader
from Utilities.conftest import setupBrowser
from Utilities.utils import getLogger, loadFilePath, login


class PplanTestSuite(ParametrizedTestCase):

    @classmethod
    def setUpClass(cls):
        setupBrowser(cls)
        cls.PplanActions = PplanActions(cls.driver)
        cls.logger = getLogger()

    def setUp(self):
        filePath = loadFilePath(self.param["datafilename"])
        with open(filePath) as f:
            self.TestCases = json.load(f)
        self.logger = self.param["logger"]
        self.reportFileName = self.param["reportFileName"]
        self.reportFilePath = loadFilePath(
            f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.PROTECTION_PLAN_TEST)
        if not createSheet:
            self.logger.warning("Report File Not found")
        login(self, self.param["setup"], self.PplanActions, "protection/plans")

    def test_pplan_add(self):
        if self.TestCases.get("test_pplan_add") is not None:
            suiteReportHeader(self.reportFilePath, Constants.PROTECTION_PLAN_TEST,
                              Constants.PROTECTION_PLAN_HEADER, Constants.PROTECTION_PLAN_ADDITION_TEST_SHEET_NAME)
            for test in self.TestCases["test_pplan_add"]["data"]:
                with self.subTest(test=test):
                    resObj = self.PplanActions.test_pplan_add(test, self.reportFilePath, self.logger)
                    self.assertEqual(resObj, True)
        else:
            self.logger.warning("Protection Plan Add test cases not added")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
