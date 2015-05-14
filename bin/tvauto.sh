#!/bin/bash

# Find each directory in pyload that doesn't have and incomplete file and starts with auto
# Then run process.py on it in tv mode

find /stuff/shared/downloads/pyload/ -maxdepth 1 -name 'auto_*' '!' -exec sh -c 'ls -1 "{}"|egrep -i -q "\.(chunk)(s|[0-9]*)$"' ';' -exec /home/nathan/process.py --tv {} \;

