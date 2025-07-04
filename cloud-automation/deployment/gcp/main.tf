#Service Account
resource "google_service_account" "service_account" {
  account_id   = var.account_id
  display_name = var.display_name
  count        = var.create_pre_req ? 1 : 0
}

data "google_service_account" "service_account_details" {
  account_id   = var.account_id
  count        = var.create_pre_req ? 0 : 1
}

#Role
resource "google_project_iam_custom_role" "custom_role" {
  role_id = var.role_id
  project = var.project
  title   = var.title
  count   = var.create_pre_req ? 1 : 0
  permissions = [
    "compute.addresses.list",
    "compute.diskTypes.get",
    "compute.diskTypes.list",
    "compute.disks.create",
    "compute.disks.createSnapshot",
    "compute.disks.delete",
    "compute.disks.get",
    "compute.disks.list",
    "compute.disks.use",
    "compute.firewalls.list",
    "compute.instances.attachDisk",
    "compute.instances.create",
    "compute.instances.delete",
    "compute.instances.detachDisk",
    "compute.instances.get",
    "compute.instances.list",
    "compute.instances.setMetadata",
    "compute.instances.setTags",
    "compute.instances.start",
    "compute.instances.stop",
    "compute.instances.updateDisplayDevice",
    "compute.networks.updatePolicy",
    "compute.projects.get",
    "compute.snapshots.create",
    "compute.snapshots.delete",
    "compute.snapshots.useReadOnly",
    "compute.subnetworks.get",
    "compute.subnetworks.list",
    "compute.subnetworks.use",
    "compute.subnetworks.useExternalIp",
    "compute.zoneOperations.get"
  ]
}

#Add IAM Role to Service Account
resource "google_service_account_iam_binding" "example_binding" {
 service_account_id = google_service_account.service_account[count.index].id
 role               = google_project_iam_custom_role.custom_role[count.index].name
 members            = ["${google_service_account.service_account[count.index].member}"]
 count              = var.create_pre_req ? 1 : 0
}

#Firewall Rules
resource "google_compute_firewall" "mgmt_firewall_ingress" {
  name          = var.mgmt_firewall_ingress_name
  network       = var.network
  direction     = "INGRESS"
  source_ranges = var.mgmt_firewall_source_range
  source_tags   = var.mgmt_firewall_tag_name
  count         = var.create_pre_req ? 1 : 0
  allow {
    protocol = "tcp"
    ports    = ["3308", "5000", "5001", "5002", "5003", "5004", "22"]
  }
}
resource "google_compute_firewall" "mgmt_firewall_egress" {
  name               = var.mgmt_firewall_egress_name
  network            = var.network
  direction          = "EGRESS" 
  target_tags        = var.mgmt_firewall_tag_name
  destination_ranges = var.mgmt_firewall_destination_range
  count              = var.create_pre_req ? 1 : 0
  allow {
    protocol = "tcp"
    ports    = ["5000", "5001", "5002", "5003", "5004", "5005", "443", "3308", "5985", "5986", "902"]
  }
}
resource "google_compute_firewall" "prep_firewall_ingress" {
  name          = var.prep_firewall_ingress_name
  network       = var.network
  direction     = "INGRESS"
  source_ranges = var.prep_firewall_source_range
  source_tags   = var.prep_firewall_tag_name
  count         = var.create_pre_req ? 1 : 0
  allow {
    protocol = "tcp"
    ports    = ["5985", "5986", "3389"]
  }
}
resource "google_compute_firewall" "prep_firewall_egress" {
  name               = var.prep_firewall_egress_name
  network            = var.network
  direction          = "EGRESS"
  target_tags        = var.prep_firewall_tag_name
  destination_ranges = var.prep_firewall_destination_range
  count              = var.create_pre_req ? 1 : 0
  allow {
    protocol = "all"
  }
}
#VMs
#VM-1
resource "google_compute_instance" "mgmt_server" {
  name         = var.mgmt_server_name
  machine_type = var.mgmt_server_type
  zone         = var.mgmt_server_zone
  count        = var.mgmt_create_vm ? 1 : 0
  tags         = var.mgmt_firewall_tag_name
  network_interface {
    network    = var.network
    subnetwork = var.subnet
    dynamic "access_config" {
      for_each = var.associate_public_ip == false ? [] : [1]
      content {
         
      }
    }
  }

  boot_disk {
    initialize_params {
      image = var.mgmt_server_image
    }
  }

  metadata = {
    ssh-keys = var.ssh_keys
  }

  service_account {
    email = length(google_service_account.service_account) > 0 ? google_service_account.service_account[count.index].email : data.google_service_account.service_account_details[count.index].email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"] # Provides access to all Google Cloud Platform APIs with the role attached to service account
  }
}
#VM-2
resource "google_compute_instance" "repl_node" {
  name         = format("%s-%s", var.repl_node_name, uuid())
  machine_type = var.repl_node_type
  zone         = var.repl_node_zone
  count        = var.repl_create_vm ? var.repl_node_count : 0
  tags         = var.mgmt_firewall_tag_name
  network_interface {
    network    = var.network
    subnetwork = var.subnet
    dynamic "access_config" {
      for_each = var.associate_public_ip == false ? [] : [1]
      content {
         
      }
    }
  }

  boot_disk {
    initialize_params {
      image = var.repl_node_image
    }
  }

  metadata = {
    ssh-keys = var.ssh_keys
  }
   service_account {
    email = length(google_service_account.service_account) > 0 ? google_service_account.service_account[0].email : data.google_service_account.service_account_details[0].email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"] # Provides access to all Google Cloud Platform APIs with the role attached to service account
  }
}

#VM-3
resource "google_compute_instance" "prep_node" {
  name         = format("%s-%s", var.prep_node_name, uuid())
  machine_type = var.prep_node_type
  zone         = var.prep_node_zone
  count        = var.prep_create_vm ? var.prep_node_count : 0
  tags         = var.prep_firewall_tag_name
  network_interface {
    network    = var.network
    subnetwork = var.subnet
    dynamic "access_config" {
      for_each = var.associate_public_ip == false ? [] : [1]
      content {
         
      }
    }
  }

  boot_disk {
    initialize_params {
      image = var.prep_node_image
    }
  }

  metadata = {
    ssh-keys = var.ssh_keys
  }

   service_account {
    email = length  (google_service_account.service_account) > 0 ? google_service_account.service_account[0].email : data.google_service_account.service_account_details[0].email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"] # Provides access to all Google Cloud Platform APIs with the role attached to service account
  }
}