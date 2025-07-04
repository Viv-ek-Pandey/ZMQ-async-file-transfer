#Service Account

output "service_account" {
  value = google_service_account.service_account[*].name
}

#Role

output "custom_role" {
  value = google_project_iam_custom_role.custom_role[*].name
}

#VMs

output "mgmt_server" {
  value = {
    Name = google_compute_instance.mgmt_server[*].name
    ID   = google_compute_instance.mgmt_server[*].id
  }
}
output "repl_node" {
  value = {
    Name = google_compute_instance.repl_node[*].name
    ID   = google_compute_instance.repl_node[*].id
  }
}
output "prep_node" {
  value = {
    Name = google_compute_instance.prep_node[*].name
    ID   = google_compute_instance.prep_node[*].id
  }
}