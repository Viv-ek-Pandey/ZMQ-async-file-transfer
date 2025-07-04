output "repl_network_interfaces" {
  value = azurerm_network_interface.repl[*].id
}
output "prep_network_interfaces" {
  value = azurerm_network_interface.prep[*].id
}
output "mgmt_network_interfaces" {
  value = azurerm_network_interface.mgmt[*].id
}
