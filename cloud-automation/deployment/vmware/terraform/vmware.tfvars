# vSphere vCenter Server where the Datamotive nodes will be deployed.
vsphere_server              = "198.244.129.75"
vsphere_username            = "administrator@vsphere.local"
vsphere_password            = "2vG6V4Sq$#Rl)qim"

# VM placement information
datacenter_name             = "Your_datancenter_name"
datastore_name              = "Your_datastore_name"
compute_cluster_name        = "Your_compute_cluster_name"
esxi_host_name              = "Your_esxi_hostname"
network_name                = "Your_network_name"

# Datamotive management node properties. Specify the OVA as shared by Datamotive. Modify other fields with caution.
mgmt_create_from_repository = "true"
mgmt_server_name            = "datamotive-mgmt-server"
mgmt_server_ova             = "https://carnival-builds.s3.us-east-2.amazonaws.com/dm-mgmt-VMware-1.2.2-2623.ova"
#mgmt_server_ova            = "c:\\dm-mgmt-VMware-1.0.0-1826.ova"