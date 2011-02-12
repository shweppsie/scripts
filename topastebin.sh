#!/bin/bash

#curl -d paste_code="`cat \"$1\"`" http://pastebin.com/api_public.php

curl -d paste_code="`cat <($1)`" http://pastebin.com/api_public.php
