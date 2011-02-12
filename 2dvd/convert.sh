#!/bin/bash

mencoder -oac lavc -ovc lavc -of mpeg -mpegopts format=dvd -vf scale=720:576,harddup -srate 48000 -af lavcresample=48000 -lavcopts vcodec=mpeg2video:vrc_buf_size=1835:vrc_maxrate=9800:vbitrate=5000:keyint=15:aspect=16/9:acodec=ac3:abitrate=192 -ofps 25 -o ./output.mpg "$1"

dvdauthor -o ./dvd -x /home/nathan/Dropbox/scripts/avi2dvd/dvd.xml

rm output.mpg

genisoimage -o dvd.iso -dvd-video ./dvd

rm -r ./dvd

