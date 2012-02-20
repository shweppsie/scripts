#!/bin/bash

function usage {
	echo ""
	echo "This script will try to find artist images from"
	echo "last.fm using the titles of the folder in the"
	echo "specified directory. It will then place these"
	echo "files in each folder title \"folder.jpg\"."
	exit 1
}

if [ $# -ne 1 ]; then
	echo "Usage: $0 directory"
	usage
fi

if [ -d "$1" ]; then
	cd "$1"
else
	echo "Folder \"$1\" does not exist"
	exit 1
fi

for artist in *; do
	if [ -d "$artist" ]; then
		if [ ! -e "$artist/folder.jpg" ]; then
			wget --no-verbose -O "$artist/folder.jpg" "`/src/albumidentify/src/renamealbum/lastfm.py artist "$artist" "image" | tail -n 1`" &> /dev/null
			if [ $? -ne 0 ]; then
				echo "`date +'%d/%m/%y:%H:%M:%S' $0:` Error processing \"$artist\""
			fi
		fi
	fi
done
