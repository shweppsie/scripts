#!/bin/bash

ls | grep '^[sS]eason [0-9]$' | while read line
do
	newname=`echo "${line}" | sed 's/[Ss]eason \([0-9]\)/Season 0\1/'`
	echo "${line} -> ${newname}"
	mv "${line}" "${newname}"
done
