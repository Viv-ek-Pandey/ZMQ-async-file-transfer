class ApiConstants():
    LOGIN_API = 'api/v1/login'

    GET_PPLAN_VM_LIST = "api/v1/sites/protectionId/vms"
    GET_NETWORK = "api/v1/sites/recoverySiteId/networks"
    GET_SITES = "api/v1/sites"

    GET_VMWARE_DATACENTER = "api/v1/sites/recoverySiteId/resources?type=Datacenter"
    GET_VMWARE_FOLDER_LIST = "api/v1/sites/recoverySiteId/resources?type=Folder&entity=id"

    GET_NODE_WITH_ID = "api/v1/nodes/id"
    GET_NODE_LIST = "api/v1/nodes"

    GET_VMWARE_COMPUTE = 'api/v1/sites/siteId/resources?type=ClusterComputeResource,ComputeResource&entity=dataCenter'
    GET_VMWARE_NETWORK = 'api/v1/sites/siteId/resources?type=Network,DistributedVirtualPortgroup&entity=hostId'

    GET_VM_REPLICATION_LIST = 'api/v1/jobs/replication/vms?limit=100'

    GET_PPLAN_LIST = "api/v1/protection/plans"
    GET_PPLAN_BY_ID = 'api/v1/protection/plans/ID'

    UPLOAD_SCRIPT = "/api/v1/script"

    RECOVERY_API = 'api/v1/recover'
    FETCH_ALERTS_LIST = 'api/v1/alerts?limit=100'

    GET_VM_LIST = "api/v1/jobs/replication/vms?limit=100&searchstr={}&searchcol=vmName,status,syncStatus"
