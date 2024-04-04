import json
import unittest
from Constants.Constants import Constants
from Actions.AlertActions import AlertActions
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import getLogger, loadFilePath, login


class AlertTestSuite(ParametrizedTestCase):

    @classmethod
    def setUpClass(cls):
        setupBrowser(cls)
        cls.AlertActions = AlertActions(cls.driver)
        cls.logger = getLogger()

    def setUp(self):
        filePath = loadFilePath(self.param[Constants.DATAFILENAME])
        with open(filePath) as f:
            self.TestCases = json.load(f)
        self.reportFileName = self.param[Constants.REPORT_FILENAME]
        self.reportFilePath = loadFilePath(
            f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        getOrCreateSheet(self.reportFilePath, Constants.ALERT_TEST)
        login(self, self.param["setup"], self.AlertActions, Constants.ALERT_PAGE)

    def test_ack_vm_rename(self):
        if (self.TestCases.get("vm_rename_alert") != None):
            executeTestCase = self.TestCases["vm_rename_alert"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.ALERT_TEST,
                                  Constants.ALER_HEADER, Constants.ALERT_TEST_SHEET_NAME)
                self.AlertActions.ack_vm_alerts(self.TestCases["vm_rename_alert"]["data"])
            else:
                self.logger.warning("Skippped vm rename alert test")
        else:
            self.logger.warning("vm rename alert test cases not added")


    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
