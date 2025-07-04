#Resource Group

data "azurerm_resource_group" "resource_group" {
  name = var.resource_group_name
}

#Network Module
module network{
  source                 = "./modules/network"
  resource_group_name    = var.resource_group_name
  vnet_name              = var.vnet_name
  subnet_name            = var.subnet_name
  location               = var.location
  repl_create_vm         = var.repl_create_vm
  prep_create_vm         = var.prep_create_vm
  mgmt_create_vm         = var.mgmt_create_vm
  repl_node_count        = var.repl_node_count
  prep_node_count        = var.prep_node_count
  associate_public_ip    = var.associate_public_ip
  storage_account_create = var.storage_account_create
  security_group_create  = var.security_group_create
  mgmt_vm_name           = var.mgmt_vm_name
  repl_vm_name           = var.repl_vm_name
  prep_vm_name           = var.prep_vm_name
}
#Network Security Groups
resource "azurerm_network_security_group" "mgmt" {
  count               = var.security_group_create ? 1 : 0
  name                = var.mgmt_security_group
  location            = data.azurerm_resource_group.resource_group.location
  resource_group_name = data.azurerm_resource_group.resource_group.name
}
resource "azurerm_network_security_rule" "mgmt_inbound" {
  count                       = var.security_group_create ? 1 : 0
  name                        = format("%s-%s", var.mgmt_inbound_name, count.index)
  priority                    = 100 * (count.index + 1)
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_ranges     = var.mgmt_inbound_allowed_ports
  source_address_prefix       = var.mgmt_source_address_prefix
  destination_address_prefix  = var.mgmt_destination_address_prefix
  resource_group_name         = data.azurerm_resource_group.resource_group.name
  network_security_group_name = azurerm_network_security_group.mgmt[count.index].name
}
resource "azurerm_network_security_rule" "mgmt_outbound" {
 count                        = var.security_group_create ? 1 : 0
  name                        = format("%s-%s", var.mgmt_outbound_name, count.index)
  priority                    = 100 * (count.index + 1)
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_ranges     = var.mgmt_outbound_allowed_ports
  source_address_prefix       = var.mgmt_source_address_prefix
  destination_address_prefix  = var.mgmt_destination_address_prefix
  resource_group_name         = data.azurerm_resource_group.resource_group.name
  network_security_group_name = azurerm_network_security_group.mgmt[count.index].name
}
resource "azurerm_network_security_group" "prep" {
  count               = var.security_group_create ? 1 : 0
  name                = var.prep_security_group
  location            = data.azurerm_resource_group.resource_group.location
  resource_group_name = data.azurerm_resource_group.resource_group.name
}
resource "azurerm_network_security_rule" "prep_inbound" {
  count                       = var.security_group_create ? 1 : 0
  name                        = format("%s-%s", var.prep_inbound_name, count.index)
  priority                    = 100 * (count.index + 1)
  direction                   = "Inbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_ranges     = var.prep_inbound_allowed_ports
  source_address_prefix       = var.prep_source_address_prefix
  destination_address_prefix  = var.prep_destination_address_prefix
  resource_group_name         = data.azurerm_resource_group.resource_group.name
  network_security_group_name = azurerm_network_security_group.prep[count.index].name
}
resource "azurerm_network_security_rule" "prep_outbound" {
  count                       = var.security_group_create ? 1 : 0
  name                        = format("%s-%s", var.prep_outbound_name, count.index)
  priority                    = 100 * (count.index + 1)
  direction                   = "Outbound"
  access                      = "Allow"
  protocol                    = "Tcp"
  source_port_range           = "*"
  destination_port_ranges     = length(var.prep_outbound_allowed_ports) > 0 ? var.prep_outbound_allowed_ports : null
  source_address_prefix       = var.prep_source_address_prefix
  destination_address_prefix  = var.prep_destination_address_prefix
  resource_group_name         = data.azurerm_resource_group.resource_group.name
  network_security_group_name = azurerm_network_security_group.prep[count.index].name
}

#Storage Pool

resource "azurerm_storage_account" "storage_account" {
  count                    = var.storage_account_create ? 1 : 0
  name                     = var.storage_account_name
  resource_group_name      = data.azurerm_resource_group.resource_group.name
  location                 = var.location
  account_tier             = var.storage_account_tier
  account_replication_type = var.storage_account_replication_type
}

resource "azurerm_network_interface_security_group_association" "mgmt_association" {
    count                      = var.mgmt_create_vm ? 1 : 0
    network_interface_id       = module.network.mgmt_network_interfaces[count.index]
    network_security_group_id  = azurerm_network_security_group.mgmt[0].id
}

#VMs
resource "azurerm_virtual_machine" "mgmt" {
  count                 = var.mgmt_create_vm ? 1 : 0
  name                  = var.mgmt_vm_name
  location              = var.location
  resource_group_name   = data.azurerm_resource_group.resource_group.name
  vm_size               = var.mgmt_vm_size
  network_interface_ids = module.network.mgmt_network_interfaces
  delete_os_disk_on_termination = true
  storage_image_reference {
    id             = var.mgmt_image_id
  }
  storage_os_disk {
    name              = format("%s-%s", var.mgmt_vm_name, "osdisk")
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = var.node_disk_type
  }

  plan {
    name           = var.mgmt_plan_name
    publisher      = var.mgmt_plan_publisher
    product        = var.mgmt_plan_product
  }
  os_profile {
    computer_name  = var.mgmt_vm_name
    admin_username = var.mgmt_user_name
    admin_password = var.mgmt_user_password
  }
  
  os_profile_linux_config {
    disable_password_authentication = var.mgmt_disable_password_authentication
  }
}

resource "azurerm_network_interface_security_group_association" "repl_association" {
    count                      = var.repl_create_vm ? var.repl_node_count : 0
    network_interface_id       = module.network.repl_network_interfaces[count.index]
    network_security_group_id  = azurerm_network_security_group.mgmt[0].id
}
resource "azurerm_virtual_machine" "repl" {
  count                 = var.repl_create_vm ? var.repl_node_count : 0
  name                  = format("%s-%s", var.repl_vm_name, uuid())
  location              = var.location
  resource_group_name   = data.azurerm_resource_group.resource_group.name
  vm_size               = var.repl_vm_size

  # 🔑 Assign one NIC per VM using count.index
  network_interface_ids        = [module.network.repl_network_interfaces[count.index]]
  primary_network_interface_id = module.network.repl_network_interfaces[count.index]
  delete_os_disk_on_termination = true

  storage_image_reference {
    id        = var.repl_image_id
  }
  storage_os_disk {
    name              = format("%s-%s-%s", var.repl_vm_name, "osdisk", uuid())
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = var.node_disk_type
  }
  os_profile {
    computer_name  = var.repl_vm_name
    admin_username = var.repl_user_name
    admin_password = var.repl_user_password
  }
  plan {
    name           = var.repl_plan_name
    publisher      = var.repl_plan_publisher
    product        = var.repl_plan_product
  }
  os_profile_linux_config {
    disable_password_authentication = var.repl_disable_password_authentication
  }
}

resource "azurerm_network_interface_security_group_association" "prep_association" {
    count                      = var.prep_create_vm ? var.prep_node_count : 0
    network_interface_id       = module.network.prep_network_interfaces[count.index]
    network_security_group_id  = azurerm_network_security_group.prep[0].id
}

resource "azurerm_virtual_machine" "prep" {
  count                 = var.prep_create_vm ? var.prep_node_count : 0
  name                  = format("%s-%s", var.prep_vm_name, uuid())
  location              = var.location
  resource_group_name   = data.azurerm_resource_group.resource_group.name
  vm_size               = var.prep_vm_size
  
  # 🔧 Correct NIC assignment for each VM
  network_interface_ids        = [module.network.prep_network_interfaces[count.index]]
  primary_network_interface_id = module.network.prep_network_interfaces[count.index]
  delete_os_disk_on_termination = true

  storage_image_reference {
    id             = var.prep_image_id
  }
  storage_os_disk {
    name              = format("%s-%s-%s", var.prep_vm_name, "osdisk", uuid())
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = var.node_disk_type
  }
  os_profile {
    computer_name  = var.prep_vm_name
    admin_username = var.prep_user_name
    admin_password = var.prep_user_password
  }
  plan {
    name           = var.prep_plan_name
    publisher      = var.prep_plan_publisher
    product        = var.prep_plan_product
  }
  os_profile_windows_config {
    provision_vm_agent = true
  }
}
