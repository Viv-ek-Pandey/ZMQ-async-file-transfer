#!/bin/bash

# set /A index=0

rm -rf DM_TEST*
index=0

while :
do
base64 /dev/urandom | head -c 10000000 > DM_TEST_$index
((index+=1))
if [[ $index -eq 10 ]]
then
rm -rf DM_TEST*
index=0
fi
echo "File created sleeping for 20 seconds"
sleep 20
done
