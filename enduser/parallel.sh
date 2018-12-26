#!/bin/bash
FIFONAME="/run/shm/partest"
mkfifo "$FIFONAME" &> /dev/null
# print n largest 
echo "echo $(date) && sleep 2"
while true; do
	while read line; do
		echo "echo $(date) && sleep 2"
	done < $FIFONAME
done
rm "$FIFONAME"
