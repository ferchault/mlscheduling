#!/bin/bash
if [ $# -ne 2 ]
then
	echo "Usage: $0 TIMELIMIT_SECONDS TASKFILE"
	exit 1
fi

# find time limit
LIMIT=$(echo $1 | sed 's/\..*//')
NOW=$(date +%s | sed 's/\..*//')
DEADLINE=$(($LIMIT + $NOW))
echo $DEADLINE

cat $2 | sort -k1 -n -r | while read taskline;
do
	NOW=$(date +%s | sed 's/\..*//')
	IFS=' ' read -r duration cmd <<< "$taskline"
	if [ "$(($NOW + $duration))" -lt "$DEADLINE" ]
	then
		echo $cmd
	fi
done
