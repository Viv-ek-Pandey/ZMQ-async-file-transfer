#IAM

resource "aws_iam_user" "iam_user" {
  count = var.iam_create ? 1 : 0
  name  = var.iam_user
}
resource "aws_iam_access_key" "user_access_key" {
  count  = var.iam_create ? 1 : 0
  user   = aws_iam_user.iam_user[count.index].name
}
resource "aws_iam_policy" "iam_policy" {
  count  = var.iam_create ? 1 : 0
  name   = var.iam_policy
  policy = file("./iam-policy.json")
}
resource "aws_iam_user_policy_attachment" "iam_policy_attachment" {
  count      = var.iam_create ? 1 : 0
  policy_arn = aws_iam_policy.iam_policy[count.index].arn
  user       = aws_iam_user.iam_user[count.index].name
}

#Security Groups

#Security Group 1
resource "aws_security_group" "security_group_mgmt" {
  count       = var.security_group_create ? 1 : 0
  name        = var.mgmt_security_group_name
  description = "Management Server_security_group"
  vpc_id      = var.vpc_id
}
resource "aws_security_group_rule" "security_group_mgmt_inbound_Database" {
  count             = var.security_group_create ? 1 : 0
  type              = "ingress"
  from_port         = 3308
  to_port           = 3308
  protocol          = "tcp"
  cidr_blocks       = var.mgmt_security_group_cidr
  security_group_id = aws_security_group.security_group_mgmt[count.index].id
}
resource "aws_security_group_rule" "security_group_mgmt_inbound_Replication" {
   count            = var.security_group_create ? 1 : 0
  type              = "ingress"
  from_port         = 5000
  to_port           = 5005
  protocol          = "tcp"
  cidr_blocks       = var.mgmt_security_group_cidr
  security_group_id = aws_security_group.security_group_mgmt[count.index].id
}
resource "aws_security_group_rule" "security_group_mgmt_inbound_SSH" {
   count            = var.security_group_create ? 1 : 0
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = var.mgmt_security_group_cidr
  security_group_id = aws_security_group.security_group_mgmt[count.index].id
}
resource "aws_security_group_rule" "security_group_mgmt_outbound_Replication" {
   count            = var.security_group_create ? 1 : 0
  type              = "egress"
  from_port         = 5000
  to_port           = 5005
  protocol          = "tcp"
  cidr_blocks       = var.mgmt_security_group_cidr
  security_group_id = aws_security_group.security_group_mgmt[count.index].id
}
resource "aws_security_group_rule" "security_group_mgmt_outbound_Database" {
   count            = var.security_group_create ? 1 : 0
  type              = "egress"
  from_port         = 3308
  to_port           = 3308
  protocol          = "tcp"
  cidr_blocks       = var.mgmt_security_group_cidr
  security_group_id = aws_security_group.security_group_mgmt[count.index].id
}
resource "aws_security_group_rule" "security_group_mgmt_outbound_https" {
  count             = var.security_group_create ? 1 : 0
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = var.mgmt_security_group_cidr
  security_group_id = aws_security_group.security_group_mgmt[count.index].id
}
resource "aws_security_group_rule" "security_group_mgmt_outbound_prep" {
  count             = var.security_group_create ? 1 : 0
  type              = "egress"
  from_port         = 5985
  to_port           = 5986
  protocol          = "tcp"
  cidr_blocks       = var.mgmt_security_group_cidr
  security_group_id = aws_security_group.security_group_mgmt[count.index].id
}

#Prep Node security group 
resource "aws_security_group" "security_group_prep" {
  count       = var.security_group_create ? 1 : 0
  name        = var.prep_security_group_name
  description = "Windows_Prep Node_security_group"
  vpc_id      = var.vpc_id
}
resource "aws_security_group_rule" "security_group_prep_inbound_WinRM" {
  count             = var.security_group_create ? 1 : 0
  type              = "ingress"
  from_port         = 5985
  to_port           = 5986
  protocol          = "tcp"
  cidr_blocks       = var.prep_security_group_cidr
  security_group_id = aws_security_group.security_group_prep[count.index].id
}
resource "aws_security_group_rule" "security_group_prep_inbound_RDP" {
  count             = var.security_group_create ? 1 : 0
  type              = "ingress"
  from_port         = 3389
  to_port           = 3389
  protocol          = "tcp"
  cidr_blocks       = var.prep_security_group_cidr
  security_group_id = aws_security_group.security_group_prep[count.index].id
}
resource "aws_security_group_rule" "security_group_prep_outbound_all" {
  count             = var.security_group_create ? 1 : 0
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = var.prep_security_group_cidr
  security_group_id = aws_security_group.security_group_prep[count.index].id
}

#VMs
#Management Node
resource "aws_instance" "mgmt-server" {
  count                       = var.mgmt_create_instance ? 1 : 0
  ami                         = var.mgmt_server_ami
  instance_type               = var.mgmt_instance_type
  subnet_id                   = var.subnet_id
  key_name                    = var.ssh_key_name
  associate_public_ip_address = var.associate_public_ip_address
  vpc_security_group_ids      = [aws_security_group.security_group_mgmt[0].id]
  tags = {
    #Name = format("%s-%s", var.mgmt_server_name, formatdate("YYYY-MM-DD_HH:MM:SS", timestamp()))
    Name = var.mgmt_server_name
  }
}
#Replication Node
resource "aws_instance" "repl-node" {
  count                       = var.repl_create_instance ? var.repl_node_count : 0
  ami                         = var.repl_node_ami
  instance_type               = var.repl_instance_type
  subnet_id                   = var.subnet_id
  key_name                    = var.ssh_key_name
  associate_public_ip_address = var.associate_public_ip_address
  vpc_security_group_ids      = [aws_security_group.security_group_mgmt[0].id]
  tags = {
    #Name = format("%s-%s", var.repl_node_name, formatdate("YYYY-MM-DD_HH:MM:SS", timestamp()))
    Name = format("%s-%s", var.repl_node_name, uuid())
  }
}
#Prep Node
resource "aws_instance" "prep-node" {
  count                       = var.prep_create_instance ? var.prep_node_count : 0
  ami                         = var.prep_node_ami
  instance_type               = var.prep_instance_type
  subnet_id                   = var.subnet_id
  associate_public_ip_address = var.associate_public_ip_address
  vpc_security_group_ids      = [aws_security_group.security_group_prep[0].id]
  tags = {
    #Name = format("%s-%s", var.prep_node_name, formatdate("YYYY-MM-DD_HH:MM:SS", timestamp()))
    Name = format("%s-%s", var.prep_node_name, uuid())
  }
}
