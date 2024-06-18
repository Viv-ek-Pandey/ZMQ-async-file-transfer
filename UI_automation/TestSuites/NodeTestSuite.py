import json
import unittest
from Actions.NodeActions import NodeActions
from Constants.Constants import Constants
from Utilities.XLUtils import suiteReportHeader
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.XLUtils import getOrCreateSheet, createSummarySheet, summaryHeader, addTestResultToReportSheet
from Utilities.conftest import setupBrowser
from Utilities.utils import loadFilePath, login
import os
# from Utilities.XLUtils import 


class NodeTestSuite(ParametrizedTestCase):


    @classmethod
    def setUpClass(cls):
        '''
        This function will call only once at starting of the suite to set up browser
        '''
        setupBrowser(cls)
        cls.NodeAction = NodeActions(cls.driver)


    def setUp(self):
        '''
        This function will call at the starting before calling each method, it will login to setup and will create 
        report file as well
        '''
        self.logger = self.param["logger"]
        filePath = loadFilePath(self.param[Constants.DATAFILENAME])
        if os.path.exists(filePath):
            with open(filePath) as f:
                self.TestCases = json.load(f)
        else:
            self.logger.info(Constants.JSON_FILE_NOT_FOUND)
        self.reportFileName = self.param[Constants.REPORT_FILENAME]
        self.reportFilePath = loadFilePath(
            f'{Constants.REPORT_DIR}\\{self.reportFileName}')
        summary = createSummarySheet(self.reportFilePath)
        if summary:
            getOrCreateSheet(self.reportFilePath, Constants.SUMMARY)
            header = summaryHeader(self.reportFilePath)
            if header:
                suiteReportHeader(self.reportFilePath, Constants.SUMMARY,
                                Constants.SUMMARY_HEADER, Constants.SUMMARY_TEST_SHEET_NAME)
        createSheet = getOrCreateSheet(self.reportFilePath, Constants.NODE_TEST)
        if not createSheet:
            self.logger.warning(Constants.REPORT_FILE_NOT_FOUND)
        login(self, self.param["setup"], self.NodeAction, Constants.NODE_ACTION)


    def testNodeAdd(self):
        '''
        This function will call method addNode from NodeActions 
        '''
        if self.TestCases.get("testNodeAdd") is not None:
            executeTestCase = self.TestCases["testNodeAdd"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.NODE_TEST,
                                  Constants.NODE_ADD_HEADER, Constants.NODE_ADDITION_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testNodeAdd"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.NodeAction.addNode(test, self.reportFilePath, self.logger)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
            else:
                self.logger.warning("Skipped Node addition test")
        else:
            self.logger.warning("Node Add test cases not added")
    

    def testNodeEdit(self):
        '''
        This function will call method editNode from NodeActions
        '''
        if self.TestCases.get("testNodeEdit") is not None:
            executeTestCase = self.TestCases["testNodeEdit"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.NODE_TEST,
                                  Constants.NODE_HEADER, Constants.NODE_EDIT_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testNodeEdit"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.NodeAction.editNode(test, self.logger, self.reportFilePath)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
            else:
                self.logger.warning("Skipped Node Edit test")
        else:
            self.logger.warning("Node Edit test cases not added")


    def testNodeOffline(self):
        '''
        This function will call method offlineNode from NodeActions
        '''
        if self.TestCases.get("testnNodeOffline") is not None:
            executeTestCase = self.TestCases["testnNodeOffline"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.NODE_TEST,
                                  Constants.NODE_HEADER, Constants.NODE_OFFLINE_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testnNodeOffline"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.NodeAction.offlineNode(test, self.logger, self.reportFilePath)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
            else:
                self.logger.warning("Skipped Node Offline test")
        else:
            self.logger.warning("Node Offline test not added")
    

    def testNodeOnline(self):
        '''
        This function will call method onlineNode from NodeActions
        '''
        if self.TestCases.get("testNodeOnline") is not None:
            executeTestCase = self.TestCases["testNodeOnline"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.NODE_TEST,
                                  Constants.NODE_HEADER, Constants.NODE_ONLINE_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testNodeOnline"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.NodeAction.onlineNode(test, self.logger, self.reportFilePath)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
            else:
                self.logger.warning("Skipped Node Offline test")
        else:
            self.logger.warning("Node Offline test not added")


    def testRemoveNode(self):
        '''
        This function will call method deleteNode from NodeActions
        '''
        if self.TestCases.get("testNodeDelete") is not None:
            executeTestCase = self.TestCases["testNodeDelete"]["executeTestCase"]
            if executeTestCase:
                suiteReportHeader(self.reportFilePath, Constants.NODE_TEST,
                                  Constants.NODE_HEADER, Constants.NODE_DELETE_TEST_SHEET_NAME)
                result = []
                for test in self.TestCases["testNodeDelete"]["data"]:
                    with self.subTest(test=test):
                        testCaseStatus = self.NodeAction.deleteNode(test, self.logger, self.reportFilePath)
                        result.append(testCaseStatus)
                if Constants.FAILED not in result:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.PASSED)
                else:
                    addTestResultToReportSheet(self.reportFilePath, Constants.SUMMARY, Constants.SUMMARY_HEADER, test, Constants.FAILED)
            else:
                self.logger.warning("Skipped Node Deletion test")
        else:
            self.logger.warning("Node Delete test cases not added")


    @classmethod
    def tearDownClass(cls):
        '''
        This function always will get called at the end to close the browser
        '''
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
