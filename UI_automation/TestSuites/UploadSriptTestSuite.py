import json
import unittest
from Actions.ScriptActions import ScriptActions
from Constants.Constants import Constants
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import getLogger, loadFilePath, login


class UploadScriptTestSuite(ParametrizedTestCase):

    @classmethod
    def setUpClass(cls):
        setupBrowser(cls)
        cls.ScriptActions = ScriptActions(cls.driver)
        cls.logger = getLogger()

    def setUp(self):
        filePath = loadFilePath(self.param[Constants.DATAFILENAME])
        with open(filePath) as f:
            self.TestCases = json.load(f)
        self.reportFileName = self.param[Constants.REPORT_FILENAME]
        self.reportFilePath = loadFilePath(
            f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        getOrCreateSheet(self.reportFilePath, Constants.SCRIPT_TEST)
        login(self, self.param["setup"], self.ScriptActions, "settings/scripts")

    def test_upload_script(self):
        if (self.TestCases.get("test_script") != None):
            executeTestCase = self.TestCases["test_script"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.SCRIPT_TEST,
                                  Constants.SCRIPT_TEST_HEADER, Constants.SCRIPT_UPLOAD_TEST_SHEET_NAME)
                self.ScriptActions.uploadScript(
                    self.TestCases["test_script"]["data"],self.reportFilePath)
            else:
                self.logger.warning("Skippped script addition test")
        else:
            self.logger.warning("script Add test cases not added")


    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
