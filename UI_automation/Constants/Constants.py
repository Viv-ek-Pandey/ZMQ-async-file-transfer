class Constants():
    REPORT_DIR = "report"
    REPORT_DIR_path = "report"

    '''  TestSuite Test SheetName  '''
    NODE_TEST = "NodeTest"
    SITE_TEST = "SiteTest"
    PROTECTION_PLAN_TEST = "ProtectionPlanTest"
    TECH_SUPPORT = "TechsupportTest"
    REPLICATION_TEST = "ReplicationTest"
    RECOVERY = 'Recovery'
    SCRIPT_TEST = "ScriptTest"
    ALERT_TEST = "AlertTest"
    TEST_RECOVERY = "Test Recovery"
    CLEANUP_TEST = "CleanupTest"
    MIGRATE_TEST = "MigrateTest"
    REVERSE_TEST = "ReverseTest"

    ''' Test Suite Report Headers '''
    NODE_HEADER = ['Name', 'Hostname', 'Username', 'Password', 'Platform Type', 'Node Type', 'Status']
    NODE_DELTE_HEADER = ["Name", "Status"]
    SITE_HEADER = ['Name', 'Description', 'SiteType', 'PlatformType', 'Node', 'Status']
    SITE_DELETE_HEADER = ['Name', 'Status']
    PROTECTION_PLAN_HEADER = ['pplanName', 'Status']
    TECH_SUPPORT_HEADER = ['Description', 'Status']
    SCRIPT_TEST_HEADER = ['Description', 'status']
    REPLICATION_HEADER = ['Virtual_Machine', 'Job_Status']
    TEST_RECOVERY_HEADER = ['Protection_plan', 'Virtual_machine', 'Job_Status']
    CLEANUP_HEADER = ['Protection_plan', 'Virtual_machine', 'Status']
    REVERSE_HEADER = ['virtualMachines', 'Status']

    VMware = 'VMware'
    AWS = 'AWS'
    GCP = 'GCP'
    AZURE = 'AZURE'

    '''  logs constants '''

    INFO = "INFO"
    WARNING = 'WARNING'
    DEBUG = 'DEBUG'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

    CHROME = 'chrome'
    FIREFOX = 'firefox'
    OPERA = 'Opera'
    EDGE = 'edge'

    PARTIALLY_COMPLETED = 'partially-completed'

    NODE = "Node"
    SITE = "Site"
    PROTECTION_PLAN = "Protection_Plan"
    REPLICATION = "Replication"
    REPLICATION_JOBS = "ReplicationJobs"
    RECOVERY = "Recovery"
    REVERSE = "Reverse"
    UPLOAD_SCRIPTS = "UploadScript"
    ALERTS = "Alert"
    CLEANUP = "Cleanup"
    MIGRATE = "Migrate"

    '''Test Suite Constants'''
    DATAFILENAME = "datafilename"
    REPORT_FILENAME = "reportFileName"

    ''''Test result sheet name'''
    NODE_ADDITION_TEST_SHEET_NAME = "Node Addition Test Cases"
    NODE_DELETE_TEST_HEADER = "Node Deletion Test Cases"
    SCRIPT_UPLOAD_TEST_SHEET_NAME = "Script Upload Test Cases"
    PROTECTION_PLAN_ADDITION_TEST_SHEET_NAME = "Protection Plan Addition Test Cases"
    ALERT_TEST_SHEET_NAME = "Alert Test Cases"
    REPLICATION_TEST_SHEET_NAME = "Protection Plan Monitor Replication"
    RECOVERY_TEST_SHEET_NAME = "Test Recovery"
    CLEANUP_TEST_SHEET_NAME = "Cleanup Test Case"
    MIGRATE_TEST_SHEET_NAME = "Migrate Test Case"
    REVERSE_TEST_SHEET_NAME = "Reverse Test Case"

    '''URL Constants'''
    NODE_PAGE = "nodes"
    SITE_PAGE = "sites"
    PPLAN_PAGE = "protection/plans"
    ALERT_PAGE = "monitor/alerts"
    REPLICATION_JOBS_PAGE = "jobs/replication"

    '''Sleep Constants'''
    TWENTY_SECONDS = 20
    THIRTY_SECONDS = 30
    ONE_MINUTE = 60
    TWO_MINUTE = 120
    THREE_MINUTE = 180
    FOUR_MINUTE = 240
    FIVE_MINUTE = 300

    '''Result'''
    SUCCESS = "Success"
    FAILED = "Failed"
    COMPLETED = "Completed"
    RUNNING = "Running"
    FAILED_FIELD = "Failed : {}"
    NODE_NOT_FOUND = 'Failed: Node not found'
    NODE_DELETED = "Successfully deleted {} node"
    NODE_NOT_DELETED = "node {} could not be deleted : {}"
    FAILED_NODE_FIELD_NOT_PROVIDED = "Failed : Proper node fields not provided"
    SITE_DELETED = "Success : Site Deleted"
    SITE_NAME_NOT_FOUND = "Failed : Site Name not found"
    FIELDS_NOT_PROVIDED = "Failure: fields not provided for {}"
    SITE_CREATED = "{} created successfully"
    SITE_NOT_CREATED = "site {} not created"
    VALIDATION_FAILED = "Failure : Validation Failed for {}"
    PROTECTION_PLAN_CREATED = "Protection Plan Created Successfully"
    MIGRATION_INIT = "migration_init"
    MIGRATION_INIT_SUCCESS = "migration_init_success"
    MIGRATION_GOT_FAILED = "Migration got failed"
    REVERSE_INITIATED = "Reverse Initiated Successfully"

