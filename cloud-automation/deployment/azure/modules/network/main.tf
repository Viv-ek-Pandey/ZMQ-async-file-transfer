#Resource Group

data "azurerm_resource_group" "resource_group" {
  name = var.resource_group_name
}

#Vnet

data "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  resource_group_name = data.azurerm_resource_group.resource_group.name
}

#Subnet

data "azurerm_subnet" "subnet" {
  name                 = var.subnet_name
  virtual_network_name = data.azurerm_virtual_network.vnet.name
  resource_group_name  = data.azurerm_resource_group.resource_group.name
}

#Network Interface IDs

#Mgmt
resource "azurerm_public_ip" "mgmt" {
  count               = var.associate_public_ip && var.mgmt_create_vm ? 1 : 0
  name                = format("%s-%s", var.mgmt_vm_name, "public-ip")
  location            = var.location
  resource_group_name = data.azurerm_resource_group.resource_group.name
  allocation_method   = "Static"
}
resource "azurerm_network_interface" "mgmt" {
  count               = var.mgmt_create_vm ? 1 : 0
  name                = format("%s-%s", var.mgmt_vm_name, "nic")
  location            = var.location
  resource_group_name = data.azurerm_resource_group.resource_group.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = data.azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = var.associate_public_ip ? azurerm_public_ip.mgmt[count.index].id : null
  }
}
#Repl
resource "azurerm_public_ip" "repl" {
  count               = var.associate_public_ip && var.repl_create_vm ? var.repl_node_count : 0
  name                = format("%s-%s-%s", var.repl_vm_name, "public-ip",uuid())
  location            = var.location
  resource_group_name = data.azurerm_resource_group.resource_group.name
  allocation_method   = "Static"
}
resource "azurerm_network_interface" "repl" {
  count               = var.repl_create_vm ? var.repl_node_count : 0
  name                = format("%s-%s-%s", var.repl_vm_name, "nic",uuid())
  location            = var.location
  resource_group_name = data.azurerm_resource_group.resource_group.name

  #dynamic "ip_configuration" {
  #  for_each = [1]
  #  content {
  #    name                          = "internal"
  #    subnet_id                     = data.azurerm_subnet.subnet.id
  #    private_ip_address_allocation = "Dynamic"
  #    public_ip_address_id          = azurerm_public_ip.repl[count.index].id
  # }
  #}
  ip_configuration {
      name                          = "internal"
      subnet_id                     = data.azurerm_subnet.subnet.id
      private_ip_address_allocation = "Dynamic"
	    primary						            = true
      public_ip_address_id          = var.associate_public_ip ? azurerm_public_ip.repl[count.index].id : null
  }
}
#Prep
resource "azurerm_public_ip" "prep" {
  count               = var.associate_public_ip && var.prep_create_vm ? var.prep_node_count : 0
  name                = format("%s-%s-%s", var.prep_vm_name, "public-ip",uuid())
  location            = var.location
  resource_group_name = data.azurerm_resource_group.resource_group.name
  allocation_method   = "Static"
}
resource "azurerm_network_interface" "prep" {
  count               = var.prep_create_vm ? var.prep_node_count : 0
  name                = format("%s-%s-%s", var.prep_vm_name, "nic",uuid())
  location            = var.location
  resource_group_name = data.azurerm_resource_group.resource_group.name

  #dynamic "ip_configuration" {
  #  for_each = [1]
  #  content {
  #    name                          = "internal"
  #    subnet_id                     = data.azurerm_subnet.subnet.id
  #    private_ip_address_allocation = "Dynamic"
  #    #public_ip_address_id         = azurerm_public_ip.prep[count.index].id
  #  }
  #}

  ip_configuration {
      name                          = "internal"
      subnet_id                     = data.azurerm_subnet.subnet.id
      private_ip_address_allocation = "Dynamic"
	    primary						            = true
      public_ip_address_id          = var.associate_public_ip ? azurerm_public_ip.prep[count.index].id: null
  }
}
