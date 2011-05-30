#!/bin/bash

if [ -e "$1" ]; then
	curl -d paste_code="`cat <($1)`" http://pastebin.com/api_public.php
else
	curl -d paste_code="$1" http://pastebin.com/api_public.php
fi
echo ""
