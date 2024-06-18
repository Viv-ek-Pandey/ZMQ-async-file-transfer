import json
import os
import unittest
from TestSuites.NodeTestSuite import NodeTestSuite
from TestSuites.PplanTestSuite import PplanTestSuite
from TestSuites.SiteTestSuite import SiteTestSuite
from TestSuites.ReplicationJobsTestSuite import ReplicationJobsTestSuite
from TestSuites.RecoveryTestSuite import RecoveryTestSuite
from TestSuites.ReverseTestSuite import ReverseTestSuite
from TestSuites.CleanupTestRecoveryTestSuite import CleanupTestRecoveryTestSuite
from TestSuites.MigrateTestSuite import MigrateTestSuite
from Constants.Constants import Constants
from TestSuites.UploadSriptTestSuite import UploadScriptTestSuite
from TestSuites.AlertTestSuite import AlertTestSuite
from TestSuites.EmailTestSuite import EmailTestSuite
from TestSuites.TechSupportTestSuite import TechSupportTestSuite
from TestSuites.InfraCreationTestSuite import InfraCreationTestSuite
from Utilities.Parameterized import ParametrizedTestCase
from Utilities.utils import createReportFile, getLogger


MasterDataFile = os.path.realpath(os.path.join(
    os.path.dirname(__file__), 'Data', 'Master.json'))


def addTestSuites(TestSuiteName, unitTestSuite, suite, setup,logger, reportFileName=None):
    param = {"setup": setup,
             "datafilename": suite["datafilename"], "reportFileName": reportFileName,"logger": logger}
    match TestSuiteName:
        case Constants.NODE:
            unitTestSuite.addTest(
                ParametrizedTestCase.parametrize(NodeTestSuite, param=param))
        case Constants.SITE:
            unitTestSuite.addTest(
                ParametrizedTestCase.parametrize(SiteTestSuite, param=param))
        case Constants.PROTECTION_PLAN:
            unitTestSuite.addTest(ParametrizedTestCase.parametrize(
                PplanTestSuite, param=param))
        case Constants.REPLICATION_JOBS:
            unitTestSuite.addTest(ParametrizedTestCase.parametrize(
                ReplicationJobsTestSuite, param=param))
        case Constants.RECOVERY:
            unitTestSuite.addTest(ParametrizedTestCase.parametrize(
                RecoveryTestSuite, param=param))
        case Constants.CLEANUP:
            unitTestSuite.addTest(ParametrizedTestCase.parametrize(
                CleanupTestRecoveryTestSuite, param=param))
        case Constants.MIGRATE:
            unitTestSuite.addTest(ParametrizedTestCase.parametrize(
                MigrateTestSuite, param=param))
        case Constants.REVERSE:
            unitTestSuite.addTest(ParametrizedTestCase.parametrize(
                ReverseTestSuite, param=param))
        case Constants.UPLOAD_SCRIPTS:
            unitTestSuite.addTest(ParametrizedTestCase.parametrize(
                UploadScriptTestSuite, param=param))
        case Constants.ALERTS:
            unitTestSuite.addTest(ParametrizedTestCase.parametrize(
                AlertTestSuite, param=param))
        case Constants.EMAIL:
            unitTestSuite.addTest(ParametrizedTestCase.parametrize(
                EmailTestSuite, param=param))
        case Constants.TECH_SUPPORT:
            unitTestSuite.addTest(ParametrizedTestCase.parametrize(
                TechSupportTestSuite, param=param))
        case Constants.INFRA_CREATION:
            unitTestSuite.addTest(ParametrizedTestCase.parametrize(
                InfraCreationTestSuite, param=param))
        

def runTestSuites(logger):
    reportFileName = createReportFile()
    unitTestSuite = unittest.TestSuite()
    suites = Test["suites"]
    for suite in suites:
        skip = suite["executeTestSuite"]
        if not skip:
            continue
        TestSuiteName = suite["suitename"]
        addTestSuites(TestSuiteName, unitTestSuite, suite,
                      Test["setupDetails"],logger,reportFileName)
    return unitTestSuite


if __name__ == '__main__':
    
    logger = getLogger()
    with open(MasterDataFile) as f:
        SuiteTest = json.load(f)
        for Test in SuiteTest:
            suite = runTestSuites(logger)
            unittest.TextTestRunner(verbosity=2).run(suite)
