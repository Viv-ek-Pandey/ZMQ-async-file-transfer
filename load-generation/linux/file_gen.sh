#!/bin/bash

# set /A index=0

index=0

while :
do 
echo "This is just a sample line appended to create a big file iter no">>Sample_$index.txt
for i in {1,1000} 
do 
genrandom 10000 Sample_$index.txt
done
((index+=1))
if [[ $index -eq 4 ]]
then
rm -rf Sample_*.txt
index=0
echo $index
fi
echo "File created sleeping for 60 seconds"
sleep 2
done

