#!/bin/sh
if [ $# -eq 0 ]; then
    echo "Please pass protection plan name as parameter"
	return
fi
export MYSQL_PWD="321@evitomataD";

# delete corresponding volume infos
plan="select id from protection_plans where name='${1}'"
re="select id from recovery_entity_infos where protection_plan_id=(${plan})"
mysql -u "root" -D datamotive -e "delete from volume_infos where recovery_entity_id IN (${re});"

# delete corresponding recovery entities
mysql -u "root" -D datamotive -e "delete from recovery_entity_infos where protection_plan_id=(${plan});"

# remove plan
mysql -u "root" -D datamotive -e "DELETE FROM protection_plans WHERE name = '$1'; "



