#!/bin/bash

# get 20 pages (50 links per page)
for i in {1..20}; do
	echo "Downloading page [http://www.newgrounds.com/audio/browse/page/${i}]" 1>&2
	curl -s "http://www.newgrounds.com/audio/browse/page/${i}" | grep -P '\t<a href="/audio/listen/[0-9]*">[^<]*</a></td>' | sed 's@.*/listen/\([0-9]*\)">\([^<]*\).*@\1\t\2@g'
	sleep 1
done | sort | uniq | while read line; do
	suffix="`echo "$line" | cut -f 1`"
	filename="`echo "$line" | cut -f 2`"
	echo "Downloading [http://www.newgrounds.com/audio/download/${suffix}]..."
	curl -s "http://www.newgrounds.com/audio/download/${suffix}" > "${filename}.mp3"
	sleep 1
done

