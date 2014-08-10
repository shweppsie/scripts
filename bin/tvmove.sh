#!/bin/bash

for file in "$@"
do
    name="`basename "${file}"`"
    
    if echo $name | egrep -q '.* - [0-9]*x[0-9]* - .*';
    then
    	# Get the show name
		show=`echo ${name} | sed 's/\(.*\) - [0-9]*x[0-9]* - .*/\1/g'`
		
		# Put the at the end of the show name
		show=`echo ${show} | sed 's/^The \(.*\)/\1, The/g'`

		# Get the season number
    	season=`echo ${name} | sed 's/.* - \([0-9]*\)x[0-9]* - .*/\1/g'`

		# catch specials
		if [ $season -eq 0 ]
		then
			season="Specials"
		else
			# Pad the season number to 2 digits
			season=`printf "%02d\n" $season`
			season="Season ${season}"
		fi


    	echo "${name} -> ${show}/${season}/"
		mkdir -vp "/stuff/shared/videos/tv/${show}/${season}/"
    	mv -i "${file}" "/stuff/shared/videos/tv/${show}/${season}/"
	else
		echo "Name does not match regex: ${name}"
    fi
done
