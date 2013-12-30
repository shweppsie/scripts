#!/bin/bash

NAME="openttd"

if [ $UID -ne 0 ]; then
	echo "Not root!"
	exit 1
fi

# comment this line to not run minecraft in a screen
SCREEN="/usr/bin/screen -d -m -S ${NAME}"

USER='gameserver'
BIN="/usr/games/openttd -D"

COMMAND="${SCREEN} ${BIN}"

RES=`ps aux | grep -i "${COMMAND}" | grep -v 'grep' | wc -l`
if [ ${RES} -eq 0 ]; then
	sudo -Hu ${USER} ${COMMAND}
else
	echo "${NAME} is already running!"
fi

sleep 2

echo "\"sudo screen -r gameserver/${NAME}\" to reconnect terminal"
