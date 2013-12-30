#!/bin/bash

# App Specific Variables
START_MEM='1024M'
MAX_MEM='1024M'
JAR='/scratch/craftbukkit/craftbukkit-1.2.5-R4.1-MCPC-SNAPSHOT-162.jar'

if [ $UID -ne 0 ]; then
	echo "Not root!"
	exit 1
fi

NAME='minecraft-craftbukkit' # name of screen session
USER='gameserver' # user to run application as
WD="/scratch/tekkit/" # working directory will be set to this
BIN="/usr/bin/java" # binary to run
ARGS="-Xms${START_MEM} -Xmx${MAX_MEM} -jar ${JAR}" # arguments

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
