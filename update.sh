#!/bin/bash

cd ~/src

find ./ -maxdepth 1 -mindepth 1 -type d | while read LINE; do
	cd "$LINE";
	if [ $? -ne 0 ]; then
		continue
	fi

	ls ".git" &> /dev/null
	if [ $? -ne 0 ]; then
		cd ..
		continue
	fi

	echo -n "Processing $LINE"

	out=`cat .git/config | grep "github.com"`
	if [ $? -eq 0 ]; then
		echo -n " from github.com"
	fi

	out=`cat .git/config | grep "git.shweppsie.com"`
	if [ $? -eq 0 ]; then
		echo -n " from git.shweppsie.com"
	fi

	echo "..."

	git up
	git status | grep -oE "(modified: .*|Your branch is ahead of .*)"
	echo ""
	cd ..
done
