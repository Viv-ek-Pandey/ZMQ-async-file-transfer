data "vsphere_datacenter" "datacenter" {
  name = var.datacenter_name
}

data "vsphere_datastore" "datastore" {
  name          = var.datastore_name
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_compute_cluster" "cluster" {
  name          = var.compute_cluster_name
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_resource_pool" "default" {
  name          = format("%s%s", data.vsphere_compute_cluster.cluster.name, "/Resources")
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_host" "host" {
  name          = var.esxi_host_name
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

data "vsphere_network" "network" {
  name          = var.network_name
  datacenter_id = data.vsphere_datacenter.datacenter.id
}

## Remote OVF/OVA Source
data "vsphere_ovf_vm_template" "dm-mgmt-ova-remote" {
  name              = var.mgmt_server_name
  disk_provisioning = "thin"
  resource_pool_id  = data.vsphere_resource_pool.default.id
  datastore_id      = data.vsphere_datastore.datastore.id
  host_system_id    = data.vsphere_host.host.id
  remote_ovf_url    = var.mgmt_server_ova 
  ovf_network_map = {
    "VM Network" : data.vsphere_network.network.id
  }
}

## Local OVF/OVA Source
/*
data "vsphere_ovf_vm_template" "dm-mgmt-ova-local" {
  name              = var.mgmt_server_name
  count                = var.mgmt_create_from_repository ? 0 : 1
  disk_provisioning = "thin"
  resource_pool_id  = data.vsphere_resource_pool.default.id
  datastore_id      = data.vsphere_datastore.datastore.id
  host_system_id    = data.vsphere_host.host.id
  local_ovf_path    = var.mgmt_server_ova
  ovf_network_map   = {
    "VM Network" : data.vsphere_network.network.id
  }
}
*/

## Deployment of VM from Remote OVF
resource "vsphere_virtual_machine" "dm-mgmt-server-repository" {
  name                 = var.mgmt_server_name
  datacenter_id        = data.vsphere_datacenter.datacenter.id
  datastore_id         = data.vsphere_datastore.datastore.id
  host_system_id       = data.vsphere_host.host.id
  resource_pool_id     = data.vsphere_resource_pool.default.id
  num_cpus             = data.vsphere_ovf_vm_template.dm-mgmt-ova-remote.num_cpus
  num_cores_per_socket = data.vsphere_ovf_vm_template.dm-mgmt-ova-remote.num_cores_per_socket
  memory               = data.vsphere_ovf_vm_template.dm-mgmt-ova-remote.memory
  guest_id             = data.vsphere_ovf_vm_template.dm-mgmt-ova-remote.guest_id
  scsi_type            = data.vsphere_ovf_vm_template.dm-mgmt-ova-remote.scsi_type

  dynamic "network_interface" {
    for_each = data.vsphere_ovf_vm_template.dm-mgmt-ova-remote.ovf_network_map
    content {
      network_id = network_interface.value
    }
  }
  wait_for_guest_net_timeout = 0
  wait_for_guest_ip_timeout  = 0

  ovf_deploy {
    allow_unverified_ssl_cert = false
    remote_ovf_url            = data.vsphere_ovf_vm_template.dm-mgmt-ova-remote.remote_ovf_url
    disk_provisioning         = data.vsphere_ovf_vm_template.dm-mgmt-ova-remote.disk_provisioning
    ovf_network_map           = data.vsphere_ovf_vm_template.dm-mgmt-ova-remote.ovf_network_map
  }

  vapp {
    properties = {
      "guestinfo.hostname"       = "datamotive-mgmt-console",
      "guestinfo.ipaddress"      = "172.16.11.101",
      "guestinfo.netmask"        = "255.255.255.0",
      "guestinfo.gateway"        = "172.16.11.1",
      "guestinfo.dns"            = "172.16.11.4",
      "guestinfo.root_password"  = "Datamotive@123",
      "guestinfo.ssh"            = "True"
    }
  }

  lifecycle {
    ignore_changes = [
      annotation,
      disk[0].io_share_count,
      vapp[0].properties,
    ]
  }
}

## Deployment of VM from Local OVF
/*
resource "vsphere_virtual_machine" "dm-mgmt-server-local" {
  name                 = var.mgmt_server_name
  count                = var.mgmt_create_from_repository ? 0 : 1 
  datacenter_id        = data.vsphere_datacenter.datacenter.id
  datastore_id         = data.vsphere_datastore.datastore.id
  host_system_id       = data.vsphere_host.host.id
  resource_pool_id     = data.vsphere_resource_pool.default.id
  num_cpus             = data.vsphere_ovf_vm_template.dm-mgmt-ova-local.num_cpus
  num_cores_per_socket = data.vsphere_ovf_vm_template.dm-mgmt-ova-local.num_cores_per_socket
  memory               = data.vsphere_ovf_vm_template.dm-mgmt-ova-local.memory
  guest_id             = data.vsphere_ovf_vm_template.dm-mgmt-ova-local.guest_id
  scsi_type            = data.vsphere_ovf_vm_template.dm-mgmt-ova-local.scsi_type

  dynamic "network_interface" {
    for_each = data.vsphere_ovf_vm_template.dm-mgmt-ova-local.ovf_network_map
    content {
      network_id = network_interface.value
    }
  }
  wait_for_guest_net_timeout = 0
  wait_for_guest_ip_timeout  = 0

  ovf_deploy {
    allow_unverified_ssl_cert = true
    local_ovf_path            = data.vsphere_ovf_vm_template.dm-mgmt-ova-local.local_ovf_path
    disk_provisioning         = data.vsphere_ovf_vm_template.dm-mgmt-ova-local.disk_provisioning
    ovf_network_map           = data.vsphere_ovf_vm_template.dm-mgmt-ova-local.ovf_network_map
  }

  vapp {
    properties = {
      "guestinfo.hostname"       = "datamotive-mgmt-console",
      "guestinfo.ipaddress"      = "172.16.11.102",
      "guestinfo.netmask"        = "255.255.255.0",
      "guestinfo.gateway"        = "172.16.11.1",
      "guestinfo.dns"            = "172.16.11.4",
      "guestinfo.root_password"  = "Datamotive@123",
      "guestinfo.ssh"            = "True"
    }
  }

  lifecycle {
    ignore_changes = [
      annotation,
      disk[0].io_share_count,
      vapp[0].properties,
    ]
  }
}
*/