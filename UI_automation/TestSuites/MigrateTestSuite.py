import json
import unittest
from Constants.Constants import Constants
from Actions.MigrateActions import MigrateActions
from Utilities.utils import getLogger
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login


class MigrateTestSuite(ParametrizedTestCase):
    """This function will call only once at starting of the suite to set up browser"""

    @classmethod
    def setUpClass(cls):
        setupBrowser(cls)
        cls.MigrateActions = MigrateActions(cls.driver)
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
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.MIGRATE_TEST)
        if not createSheet:
            self.logger.warning("Report File Not found")
        login(self, self.param["setup"], self.MigrateActions, goToPage="protection/plans", key="targeturl")

    '''This function will call method migrate from MigrateActions'''

    def test_migrate(self):
        if self.TestCases.get("test_migrate") is not None:
            executeTestCase = self.TestCases["test_migrate"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.MIGRATE_TEST,
                                  Constants.CLEANUP_HEADER, Constants.MIGRATE_TEST_SHEET_NAME)
                self.MigrateActions.migrate(self.TestCases.get("test_migrate")["data"], self.reportFilePath, self.logger)
            else:
                self.logger.warning("Skippped Auto Migrate")
        else:
            self.logger.warning("Skippped auto migrate")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
