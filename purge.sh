#!/bin/bash

if [[ "$1" = "" ]]
then
	echo "Usage: purge [-d] DIRECTORY"
fi

DRYRUN=0

while getopts ":d" opt; do
	case $opt in
		d)
			DRYRUN=1
			;;
		\?)
			print "Usage: purge [-d] DIRECTORY"
			;;
	esac
done

shift $((OPTIND-1))

if [ $DRYRUN -eq 1 ]
then
	echo "Dry Run Enabled"
fi

for ARG in "$@"
do
	echo "Processing $ARG"
	find $1 -name report.txt | while read line
	do
		cat "$line" | tail -n 1 | grep "success!" > /dev/null
		if [ $? -eq 0 ];
		then
			line="`dirname "$line"`"
			if [ $DRYRUN -eq 0 ]
			then
				echo Deleting: $line
				rm -r "$line"
			else
				echo Deletable: $line
			fi
		fi
	done
done

echo "Removing Empty Directories"
find -depth -type d -empty -exec echo {}\; rmdir {} \;
echo "Done"
