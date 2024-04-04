import json
import unittest
from Constants.Constants import Constants
from Actions.ReplicationJobsActions import ReplicationJobsActions
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import getLogger, loadFilePath, login
from Utilities.XLUtils import addTestResultToReportSheet, suiteReportHeader


class ReplicationJobsTestSuite(ParametrizedTestCase):
    """This function will call only once at starting of the suit to set up browser"""

    @classmethod
    def setUpClass(cls):
        setupBrowser(cls)
        cls.ReplicationAction = ReplicationJobsActions(cls.driver)
        cls.logger = getLogger()

    '''This function will call before calling each method, it will login to setup and will create report file as well'''

    def setUp(self):
        filePath = loadFilePath(self.param["datafilename"])
        with open(filePath) as f:
            self.TestCases = json.load(f)
        self.logger = self.param["logger"]
        self.reportFileName = self.param["reportFileName"]
        self.reportFilePath = loadFilePath(f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.REPLICATION_TEST)
        if not createSheet:
            self.logger.warning("Report File Not found")
        login(self, self.param["setup"], self.ReplicationAction, "jobs/replication")

    '''This function will call method monitor_protection_plan_replication_jobs from ReplicationJobsActions'''

    def test_monitor_protection_plan_replication(self):
        if self.TestCases.get("test_protection_plan_monitor_replication") is not None:
            execute_test_case = self.TestCases["test_protection_plan_monitor_replication"]["executeTestCase"]
            Test_Case_Name = list(self.TestCases.keys())[0]
            if execute_test_case:
                suiteReportHeader(self.reportFilePath, Constants.REPLICATION_TEST,
                                  Constants.REPLICATION_HEADER, Constants.REPLICATION_TEST_SHEET_NAME)
                for machine in self.TestCases["test_protection_plan_monitor_replication"]["data"]:
                    self.ReplicationAction.monitor_protection_plan_replication_jobs(machine, self.reportFilePath,
                                                                                    self.logger, Test_Case_Name)
            else:
                self.logger.warning("Skipped Monitor Replication addition test case")
        else:
            self.logger.warning("Monitor Replication addition test case is not added ")

    '''This function will call only once at ending of the suit to quit browser'''

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
