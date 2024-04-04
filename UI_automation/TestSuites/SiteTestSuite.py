import json
import unittest
from Actions.SiteActions import SiteActions
from Constants.Constants import Constants
from Utilities.XLUtils import addTestResultToReportSheet, suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login


class SiteTestSuite(ParametrizedTestCase):

    @classmethod
    def setUpClass(cls):
        setupBrowser(cls)
        cls.SiteAction = SiteActions(cls.driver)

    def setUp(self):
        filePath = loadFilePath(self.param["datafilename"])
        with open(filePath, encoding="utf-8") as f:
            self.TestCases = json.load(f)
        self.logger = self.param["logger"]
        self.reportFileName = self.param["reportFileName"]
        self.reportFilePath = loadFilePath(
            f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.SITE_TEST)
        if not createSheet:
            self.logger.warning("Report File Not found")
        login(self, self.param["setup"], self.SiteAction, "sites")

    def test_site_add(self):
        if self.TestCases.get("test_site_add") is not None:
            executeTestCase = self.TestCases["test_site_add"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.SITE_TEST,
                                  Constants.SITE_HEADER, "Site Addition Test Case")
                for test in self.TestCases["test_site_add"]["data"]:
                    with self.subTest(test=test):
                        resObj=self.SiteAction.add_site(test,self.logger)
                        addTestResultToReportSheet(self.reportFilePath, Constants.SITE_TEST, Constants.SITE_HEADER, test, resObj["result"])
                        self.assertEqual(resObj["status"], True )

    def test_site_delete(self):
        if self.TestCases.get("test_site_delete") is not None:
            executeTestCase = self.TestCases["test_site_delete"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.SITE_TEST,
                                  Constants.SITE_DELETE_HEADER, "Site edition Test Case")
                self.SiteAction.delete_site(self.TestCases.get(
                    "test_site_delete")["data"], self.reportFilePath,self.logger)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
