#!/bin/bash

ls | egrep -- "${1}"| while read line
do
	newname="`echo "${line}" | sed -- "s/${1}/${2}/g"`"
	echo "${line} -> ${newname}"
	mv -- "${line}" "${newname}"
done

