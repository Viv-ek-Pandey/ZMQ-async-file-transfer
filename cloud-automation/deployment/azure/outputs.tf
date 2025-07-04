output "mgmt-server-details" {
  description = "Datamotive management server. This is the node where all the management operations will be performed. The node can be accessed at URL."
  value = {
    Name = azurerm_virtual_machine.mgmt[*].name
    ID   = azurerm_virtual_machine.mgmt[*].id
  }
}
output "repl-node-details" {
  description = "Datamotive replication server. This is the node where all the replication operations will be performed."
  value = {
    Name = azurerm_virtual_machine.repl[*].name
    ID   = azurerm_virtual_machine.repl[*].id
  }
}
output "prep-node-details" {
    description = "Datamotive prep node. This is the node where all the recovery operations will be performed."
  value = {
    Name = azurerm_virtual_machine.prep[*].name
    ID   = azurerm_virtual_machine.prep[*].id
  }
}