#!/bin/bash

if [ $# -ne 1 ]; then
	echo "Usage"
	exit 1
fi

cd "$1"

for artist in *; do
	echo "Fetching artist art for '$artist'"
	if [ -d "$artist" ]; then
		wget --no-verbose -O "$artist/artist.png" "`/src/albumidentify/src/renamealbum/lastfm.py artist "$artist" 'image' | tail -n 1`"
	fi
	echo ""
done
