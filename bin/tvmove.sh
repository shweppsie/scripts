#!/bin/bash

if [ "$1" == "--auto" ]; then
	auto=true
	shift
else
	auto=false
fi

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

		dest="/stuff/shared/videos/tv/${show}/${season}"

		# check for rejects
		if [ "$auto" == true ]
		then
			if ! grep -Fxq "${show}" /stuff/shared/downloads/auto.txt
			then
				echo "Not in auto file, moving to /stuff/shared/downloads/rejects/"
				dest="/stuff/shared/downloads/rejects"
			fi
		fi

		# check for dups
		if [ -e "${dest}/${name%.*}"* ]
		then
			echo "Duplicate!"

			new="`du -shm "${file}"`"
			old="`du -shm "${dest}/${name%.*}"*`"

			new="`echo $new | cut -f 1 -d' '`"
			old_name="`echo $old | cut -f 2- -d' '`"
			old="`echo $old | cut -f 1 -d' '`"

			if [ $new -eq $old ]
			then
				echo "Files are the same size, Removing new file: ${file}"
				rm -v "${file}"
				continue
			elif [ $new -le $old ]
			then
				echo "Old file is bigger, Removing new file: ${file}"
				rm -v "${file}"
				continue
			else
				echo "New file is bigger, Removing old file: ${old_name}"
				rm -v "${old_name}"
			fi
		fi

		mkdir -vp "${dest}/"
    	mv -vi "${file}" "${dest}/"
	else
		echo "Name does not match regex: ${name}"
    fi
done
