class Constants():
    REPORT_DIR = "report"
    REPORT_DIR_path = "report"

    # TestSuite Test SheetName 
    NODE_TEST = "NodeTest"
    SITE_TEST = "SiteTest"
    PROTECTION_PLAN_TEST = "ProtectionPlanTest"
    TECH_SUPPORT_TEST = "TechsupportTest"
    REPLICATION_TEST = "ReplicationTest"
    RECOVERY = 'Recovery'
    SCRIPT_TEST = "ScriptTest"
    ALERT_TEST = "AlertTest"
    TEST_RECOVERY = "Test Recovery"
    CLEANUP_TEST = "CleanupTest"
    MIGRATE_TEST = "MigrateTest"
    REVERSE_TEST = "ReverseTest"
    EMAIL_TEST = "EmailTest"
    SUMMARY = "Summary"
    INFRA_TEST = "InfraTest"

    # Test Suite Report Headers
    NODE_ADD_HEADER = ['id', 'Name', 'Hostname', 'Username', 'Password', 'Platform Type', 'Node Type', 'Status']
    NODE_HEADER = ['id', "Name", "Status"]
    SITE_HEADER = ['id', 'Name', 'Description', 'SiteType', 'PlatformType', 'Node', 'Status']
    SITE_DELETE_HEADER = ['id', 'Name', 'Status']
    PROTECTION_PLAN_HEADER = ['id', 'pplanName', 'Status']
    TECH_SUPPORT_HEADER = ['id', 'Description', 'Status']
    SCRIPT_TEST_HEADER = ['Description', 'status']
    HEADER = ['id', 'protectionPlan', 'virtualMachine', 'jobStatus']
    EMAIL_HEADER = ['id', 'emailAddress', 'emailPassword', 'smtpHost', 'smtpPort', 'recipientEmail', 'status']
    EMAIL_RECIPIENT_HEADER = ['id', 'emailAddress', 'status']
    SUMMARY_HEADER = ['id', 'status']
    INFRA_HEADER = ['id', 'name']

    VMware = 'VMware'
    AWS = 'AWS'
    GCP = 'GCP'
    AZURE = 'Azure'

    # logs constants 

    INFO = "INFO"
    WARNING = 'WARNING'
    DEBUG = 'DEBUG'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

    CHROME = 'chrome'
    FIREFOX = 'firefox'
    OPERA = 'Opera'
    EDGE = 'edge'

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
    EMAIL = "Email"
    TECH_SUPPORT = "TechSupport"
    INFRA_CREATION = "InfraCreation"

    # Test Suite Constants
    DATAFILENAME = "datafilename"
    REPORT_FILENAME = "reportFileName"

    # Test result sheet name
    NODE_ADDITION_TEST_SHEET_NAME = "Node Addition Test Cases"
    NODE_EDIT_TEST_SHEET_NAME = "Node Edit Test Cases"
    NODE_OFFLINE_TEST_SHEET_NAME = "Node Offline Test Cases"
    NODE_ONLINE_TEST_SHEET_NAME = "Node Online Test Cases"
    NODE_DELETE_TEST_SHEET_NAME = "Node Deletion Test Cases"
    SITE_ADDITION_TEST_SHEET_NAME = "Site Addition Test Case"
    SITE_EDITION_TEST_SHEET_NAME = "Site Edition Test Case"
    SITE_DELETION_TEST_SHEET_NAME = "Site Deletion Test Case"
    SCRIPT_UPLOAD_TEST_SHEET_NAME = "Script Upload Test Cases"
    PROTECTION_PLAN_ADDITION_TEST_SHEET_NAME = "Protection Plan Addition Test Cases"
    PROTECTION_PLAN_EDIT_TEST_SHEET_NAME = "Protection Plan Edit Test Cases"
    PROTECTION_PLAN_STOP_TEST_SHEET_NAME = "Protection Plan Stop Test Cases"
    PROTECTION_PLAN_START_TEST_SHEET_NAME = "Protection Plan Start Test Cases"
    PROTECTION_PLAN_DELETE_TEST_SHEET_NAME = "Protection Plan Delete Test Cases"
    ALERT_TEST_SHEET_NAME = "Alert Test Cases"
    REPLICATION_OF_VIRTUAL_MACHINES_JOB_TEST_SHEET_NAME = "Protection Plan Monitor Replication Of Virtual Machine Jobs"
    REPLICATION_OF_DISKS_JOBS_TEST_SHEET_NAME = "Protection Plan Monitor Replication Of Disks Jobs"
    RECOVERY_TEST_SHEET_NAME = "Test Recovery"
    RECOVERY_SHEET_NAME = "Full Recovery"
    CLEANUP_TEST_SHEET_NAME = "Cleanup Test Case"
    MIGRATE_TEST_SHEET_NAME = "Migrate Test Case"
    REVERSE_TEST_SHEET_NAME = "Reverse Test Case"
    EMAIL_TEST_SHEET_NAME = "Email Test Case"
    EMAIL_RECIPIENT_TEST_SHEET_NAME = "Email Recipient Test Case"
    TECH_SUPPORT_TEST_SHEET_NAME = "Tech Support Test Case"
    SUMMARY_TEST_SHEET_NAME = "Summary"
    INFRA_CREATION_TEST_SHEET_NAME = "Infra Creation Test Case"
    INFRA_DELETION_TEST_SHEET_NAME = "Infra Deletion Test Case"

    # URL Constants
    NODE_PAGE = "nodes"
    SITE_PAGE = "sites"
    PPLAN_PAGE = "protection/plans"
    ALERT_PAGE = "monitor/alerts"
    REPLICATION_JOBS_PAGE = "jobs/replication"

    # Sleep Constants
    THREE_SECONDS = 3
    FIVE_SECONDS = 5
    TEN_SECONDS = 10
    FIFTEEN_SECONDS = 15
    TWENTY_SECONDS = 20
    THIRTY_SECONDS = 30
    ONE_MINUTE = 60
    TWO_MINUTE = 120
    THREE_MINUTE = 180
    FOUR_MINUTE = 240
    FIVE_MINUTE = 300

    # Result
    SUCCESS = "Success"
    FAILED = "Failed"
    COMPLETED = "Completed"
    RUNNING = "Running"
    TRUE = "True"
    FALSE = "False"
    PARTIALLY_COMPLETED = "Partially-completed"
    FAILED_FIELD = "Failed : {}"
    ADD_NODE_INITIATED = "Node Addition Initiated"
    ADD_NODE_COMPLETED = "Node Addition Completed"
    NODE_CREATED_SUCCESSFULLY = "Node created successfully"
    NODE_CONFIGURED = "Node configured successfully."
    NODE_EDIT_INITIATED_SUCCESSFULLY = "Node Edit Initiated Successfully"
    NODE_EDIT_SUCCESSFULLY = "Node Edit Completed Successfully"
    NODE_OFFLINE_INITIATED_SUCCESSFULLY = "Node Offline Initiated Successfully"
    NODE_OFFLINE_SUCCESSFULLY = "Node {} status changed successfully to offline."
    NODE_ONLINE_INITIATED_SUCCESSFULLY = "Node Online Initiated Successfully"
    NODE_ONLINE_SUCCESSFULLY = "Node {} status changed successfully to online"
    NODE_NOT_FOUND = "Failed: Node not found"
    NODE_DELETE_INITIATED_SUCCESSFULLY = "Node Delete Initiated Successfully"
    NODE_DELETE_SUCCESSFULLY = "Node deleted successfully"
    NODE_NOT_DELETED = "node {} could not be deleted : {}"
    INVALID_NODE_FIELDS = "Failed : Proper node fields not provided"
    VALID_NODE_FIELDS = "Proper node fields provided"
    NODE_CREATION_FAILED = "Node creation failed for node {} :  {}"
    NODE_FOUND = 'Success: Node found'
    SITE_DELETED = "Site configuration deleted."
    SITE_NAME_NOT_FOUND = "Failed : Site Name not found"
    INVALID_SITE_FIELDS = "Failure: fields not provided for {}"
    VALID_SITE_FIELDS = "Proper Site fields provided"
    SITE_ADD_INITIATED_SUCCESSFULLY = "Site Add Initiated Successfully"
    SITE_CREATED = "Site configuration successful"
    SITE_EDIT = "Site Edited Successfully"
    SITE_NOT_PRESENT = "Site is Not Present"
    SITE_PRESENT = "Site is Present"
    SITE_NOT_CREATED = "site {} not created"
    SITE_EDIT_INITIATED_SUCCESSFULLY = "Site Edit Initiated Successfully"
    SITE_DELETE_INITIATED_SUCCESSFULLY = "Site Delete Initiated Successfully"
    VALIDATION_FAILED = "Failure : Validation Failed for {}"
    PROTECTION_PLAN_CREATION_INITIATED_SUCCESSFULLY = "Protection Plan Creation Initiated Successfully"
    PROTECTION_PLAN_CREATED = "Protection plan configured successfully."
    PROTECTION_PLAN_NOT_FOUND = "Protection Plan Not Found"
    PROTECTION_PLAN_EDIT_INITIATED_SUCCESSFULLY = "Protection Plan Edit Initiated Successfully"
    PROTECTION_PLAN_EDIT = "Protection Plan Edited Successfully"
    PROTECTION_PLAN_DELETE_INITIATED_SUCCESSFULLY = "Protection Plan Delete Initiated Successfully"
    PROTECTION_PLAN_DELETE = "Protection Plan deleted successfully"
    PROTECTION_PLAN_ALREADY_STOP = "Protection Plan already Stopped"
    PROTECTION_PLAN_STOP_INITIATED_SUCCESSFULLY = "Protection Plan Stop Initiated Successfully"
    PROTECTION_PLAN_STOP = "Protection Plan stopped successfully"
    PROTECTION_PLAN_START_INITIATED_SUCCESSFULLY = "Protection Plan Start Initiated Successfully"
    PROTECTION_PLAN_START = "Protection Plan started successfully"
    PROTECTION_PLAN_ALREADY_STARTED = "Protection Plan already Started"
    PROTECTION_PLAN_PRESENT = "Protection Plan is Present"
    CLEANUP_COMPLETED_SUCCESSFULLY = "Successfully removed test recovered instances for : {}"
    CLEANUP_INITIATED_SUCCESSFULLY = "Cleanup Initiated Successfully"
    CLEANUP_STARTED_WITH_PROTECTION_PLAN = "Cleanup Started Successfully with {}"
    MIGRATE_INITIATED_SUCCESSFULLY = "Migrate Initiated Successfully"
    MIGRATE_COMPLETED_SUCCESSFULLY = "Migrate Completed Successfully"
    MIGRATE_STARTED_WITH_PROTECTION_PLAN = "Migrate Started Successfully with {}"
    MIGRATION_INIT = "migration_init"
    MIGRATION_INIT_SUCCESS = "migration_init_success"
    MIGRATION_GOT_FAILED = "{} Migration Job Failed"
    MIGRATION_COMPLETED = "{} Migration Job Completed"
    MIGRATION_PARTIALLY_COMPLETED = "{} Migration Job Partially Completed"
    INIT_MIGRATION_FAILED = "INIT Migration Failed"
    RECOVERY_CONFIGURATION_NOT_SET = "Recovery configuration of virtual machine could not be set"
    PROTECTION_PLAN_NOT_CREATED = "pplan not reacted : network issue"
    PROTECTION_PLAN_NOTCREATED_SITE_ID_NOT_FOUND = "protection plan not got created site id not found"
    TEST_RECOVERY_INITIATED_SUCCESSFULLY = "Test Recovery Initiated Successfully"
    TEST_RECOVERY_STARTED_WITH_PROTECTION_PLAN = "Test Recovery Started Successfully with {}"
    TEST_RECOVERY_COMPLETED = "{} Test Recovery Job Completed"
    TEST_RECOVERY_TEST_CASE_COMPLETED = "Test Recovery Test Case Completed"
    TEST_RECOVERY_FAILED = "{} Test Recovery Job Failed"
    TEST_RECOVERY_PARTIALLY_COMPLETED = "{} Test Recovery Job Partially Completed"
    RECOVERY_JOB_COMPLETED = "{} Recovery Job Completed"
    RECOVERY_INITIATED_SUCCESSFULLY = "Recovery Initiated Successfully"
    RECOVERY_TEST_CASE_COMPLETED_SUCCESSFULLY = "Recovery Test Case Completed Successfully"
    RECOVERY_STARTED_WITH_PROTECTION_PLAN = "Recovery Started Successfully with {}"
    RECOVERY_JOB_PARTIALLY_COMPLETED = "{} Recovery Job Partially Completed"
    RECOVERY_JOB_FAILED = "{} Recovery Job Failed"
    REPLICATION_INITIATED_SUCCESSFULLY_FOR_VIRTUAL_MACHINE_JOBS = "Replication Initiated Successfully for Virtual Machine Jobs"
    REPLICATION_COMPLETED_SUCCESSFULLY_FOR_VIRTUAL_MACHINE_JOBS = "Replication Completed Successfully for Virtual Machine Jobs"
    REPLICATION_INITIATED_SUCCESSFULLY_FOR_DISKS_JOBS = "Replication Initiated Successfully for Disks Jobs"
    REPLICATION_COMPLETED_SUCCESSFULLY_FOR_DISKS_JOBS = "Replication Completed Successfully for Disks Jobs"
    REPLICATION_STARTED_WITH_PROTECTION_PLAN = "Replication Started Successfully with {}"
    REPLICATION_JOB_COMPLETED = "{} Replication Job Completed"
    REPLICATION_JOB_PARTIALLY_COMPLETED = "{} Replication Job Partially Completed"
    REPLICATION_JOB_FAILED = "{} Replication Job Failed"
    REPLICATION_FAILED = "Replication Failed For any of the Virtual Machine"
    REVERSE_INITIATED = "Reverse Initiated Successfully"
    REVERSE_COMPLETED = "Reverse Completed Successfully"
    REVERSE_STARTED_WITH_PROTECTION_PLAN = "Reverse Started Successfully with {}"
    REVERSE_CONFIGURED = " Reverse Protection Plan Configured Successfully."
    JSON_FILE_NOT_FOUND = "Json file not found"
    REPORT_FILE_NOT_FOUND = "Report File Not found"
    EMAIL_INITIATED_SUCCESSFULLY = "Email Initiated Successfully"
    EMAIL_RECIPIENT_INITIATED_SUCCESSFULLY = "Email Recipient Initiated Successfully"
    EMAIL_CONFIGURATION_COMPLETED_SUCCESSFULLY = "Email Configured Successfully"
    EMAIL_RECIPIENT_CONFIGURATION_COMPLETED_SUCCESSFULLY = "Email Recipient Configured Successfully"
    INVALID_EMAIL_FIELDS = "Failed : Proper email fields not provided"
    TECH_SUPPORT_INITIATED_SUCCESSFULLY = "Tech Support Initiated Successfully"
    INVALID_TECH_SUPPORT_FIELDS = "Failed : Proper tech support fields not provided"
    TECH_SUPPORT_GENERATED_SUCCESSFULLY = "Tech Support generated Successfully"
    EMAIL_CONFIGURED = "Email settings configured successfully."
    EMAIL_RECIEPIENT_CONFIGURED = "Email recipient info saved successfully."
    AWS_INFRA_CREATAION_INITIATED_SUCCESSFULLY = "AWS Infra Creation Initiated Successfully"
    AWS_INSTANCE_CREATED = "AWS Instance Created with Name {}"
    AWS_INFRA_DELETE_INITIATED_SUCCESSFULLY = "AWS Infra Delete Initiated Successfully"
    AWS_INSTANCE_DELETED = "AWS Instance Deleted with ID {}"
    AWS_INFRA_NOT_CREATED = "AWS infra nott created"
    VMWARE_INFRA_CREATAION_INITIATED_SUCCESSFULLY = "VMWARE Infra Creation Initiated Successfully"
    VMWARE_CREATED_SUCCESSFULLY = "Vmware VM {} created successfully"
    COMPUTE_NOT_FOUND = "Compute not found" 
    DATACENTER_NOT_FOUND = "Datacenter not found"
    DATASTORE_NOT_FOUND = "Datastore not found"
    TEMPLATE_NOT_FOUND = "Template not found"
    VMWARE_INFRA_DELETE_INITIATED_SUCCESSFULLY = "VMware Infra Delete Initiated Successfully"
    VMWARE_VM_DELETED_SUCCESSFULLY = "Vmware VM {} deleted successfully"
    VIRTUAL_MACHINE_NOT_FOUND = "Vmware VM {} not found"

    # Page Actions
    NODE_ACTION = "nodes"
    SITE_ACTION = "sites"
    PROTECTION_PLAN_ACTION = "protection/plans"
    SETTINGS = "settings"

    # ID 
    folId = "datacenter-3"

    # Test Case Result
    PASSED = "PASSED"
    FAILED = "FAILED"
