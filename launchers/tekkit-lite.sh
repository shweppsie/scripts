#!/bin/bash

# java -Xmx3G -Xms2G -jar TekkitLite.jar nogui

# App Specific Variables
START_MEM='1024M'
MAX_MEM='1024M'
JAR='/scratch/tekkit-lite/TekkitLite.jar'

if [ $UID -ne 0 ]; then
	echo "Not root!"
	exit 1
fi

NAME='minecraft-tekkit-lite' # name of screen session
USER='gameserver' # user to run application as
WD="/scratch/tekkit-lite/" # working directory will be set to this
BIN="/usr/bin/java" # binary to run
ARGS="-Xms${START_MEM} -Xmx${MAX_MEM} -jar ${JAR} nogui" # arguments

# comment this line to not run minecraft in a screen
SCREEN="/usr/bin/screen -d -m -S ${NAME}"

cd "$WD"

COMMAND="${SCREEN} ${BIN} ${ARGS}"

RES=`ps aux | grep -i "${COMMAND}" | grep -v 'grep' | wc -l`
if [ ${RES} -eq 0 ]; then
	sudo -Hu ${USER} ${COMMAND}
else
	echo "Server is already running!"
fi

sleep 2

echo "\"sudo screen -r gameserver/${NAME}\" to reconnect terminal"
