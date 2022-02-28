#!/bin/bash
#touch data.txt
exec 3>>data.txt
while true
do
echo $(date +"%Y-%m-%d %T")>>data.txt
sleep 5
done
exec 3>>&-
