/*#IAM

output "access_key" {
  description = "Access key of the IAM user. Kindly note this key. It will be required while configuring Datamotive node."
  value = aws_iam_access_key.user_access_key.id
}
output "secret_key" {
  description = "Secret key of the IAM user. Kindly note this key. It will be required while configuring Datamotive node."
  value     = nonsensitive(aws_iam_access_key.user_access_key.secret)
  #sensitive = true
}

#VMs

output "mgmt-server-details" {
  description = "Datamotive management server. This is the node where all the management operations will be performed. The node can be accessed at URL."
  #value = "https://${aws_instance.mgmt-server[*].id}:5000"
  value = {
    Name = aws_instance.mgmt-server[*].tags["Name"]
    ID   = aws_instance.mgmt-server[*].id
	#URL  = "https://${aws_instance.mgmt-server[*].id}:5000"
  }
}
output "repl-node-details" {
  description = "Datamotive management server. This is the node where all the management operations will be performed. The node can be accessed at URL."
  value = {
    Name = aws_instance.repl-node[*].tags["Name"]
    ID   = aws_instance.repl-node[*].id
  }
}
output "dedup-node-details" {
  value = {
    Name = aws_instance.dedup-node[*].tags["Name"]
    ID   = aws_instance.dedup-node[*].id
  }
}
output "prep-node-details" {
  value = {
    Name = aws_instance.prep-node[*].tags["Name"]
    ID   = aws_instance.prep-node[*].id
  }
}


output "policy_arn" {
  value = aws_iam_policy.iam_policy.arn
}

#Security Groups

output "mgmt_security_group" {
  value = {
    Name = aws_security_group.security_group_1.name
    ID   = aws_security_group.security_group_1.id
  }
}
output "repl_security_group" {
  value = {
    Name = aws_security_group.security_group_2.name
    ID   = aws_security_group.security_group_2.id
  }
}
output "dedup_security_group" {
  value = {
    Name = aws_security_group.security_group_3.name
    ID   = aws_security_group.security_group_3.id
  }
}
output "prep_security_group" {
  value = {
    Name = aws_security_group.security_group_4.name
    ID   = aws_security_group.security_group_4.id
  }
}
*/