import json
import unittest
from Actions.NodeActions import NodeActions
from Constants.Constants import Constants
from Utilities.XLUtils import addTestResultToReportSheet, suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login


class NodeTestSuite(ParametrizedTestCase):

    @classmethod
    def setUpClass(cls):
        setupBrowser(cls)
        cls.NodeAction = NodeActions(cls.driver)

    def setUp(self):
        filePath = loadFilePath(self.param[Constants.DATAFILENAME])
        with open(filePath) as f:
            self.TestCases = json.load(f)
        self.logger = self.param["logger"]
        self.reportFileName = self.param[Constants.REPORT_FILENAME]
        self.reportFilePath = loadFilePath(
            f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.NODE_TEST)
        if not createSheet:
            self.logger.warning("Report File Not found")
        login(self, self.param["setup"], self.NodeAction, "nodes")

    def test_node_add(self):
        if self.TestCases.get("test_node_add") is not None:
            executeTestCase = self.TestCases["test_node_add"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.NODE_TEST,
                                  Constants.NODE_HEADER, Constants.NODE_ADDITION_TEST_SHEET_NAME)
                for test in self.TestCases["test_node_add"]["data"]:
                    with self.subTest(test=test):
                        status = self.NodeAction.add_node(test, self.reportFilePath, self.logger)
                        self.assertEqual(status, True)
            else:
                self.logger.warning("Skippped Node addition test")
        else:
            self.logger.warning("Node Add test cases not added")

    def test_node_delete(self):
        if self.TestCases.get("test_node_delete") is not None:
            executeTestCase = self.TestCases["test_node_delete"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.NODE_TEST,
                                  Constants.NODE_DELTE_HEADER, Constants.NODE_DELETE_TEST_HEADER)
                for test in self.TestCases["test_node_delete"]["data"]:
                    with self.subTest(test=test):
                        resObj = self.NodeAction.delete_node(test)
                        addTestResultToReportSheet(self.reportFilePath, Constants.NODE_TEST,
                                                   Constants.NODE_DELTE_HEADER, test, resObj["result"])
                        self.assertEqual(resObj["status"], True)
            else:
                self.logger.warning("Skippped Node Deletion test")
        else:
            self.logger.warning("Node Delete test cases not added")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
