#!/bin/bash

function usage {
	echo "$0 BACKUP_PATH /path/to/backup daily source"
	echo "$0 BACKUP_PATH /path/to/backup weekly|monthly"
	exit 3
}

function remove_old_backups {
	echo "Deleting old backups"
	i=0
	ls -t ${BACKUP_PATH}/$1/ | while read line; do
		i=$(($i+1))
		if [ $i -gt 5 ]; then
			echo "Deleting: ${BACKUP_PATH}/$1/$line"
			rm -r "${BACKUP_PATH}/$1/$line"
		fi
	done
}

if [ $# -lt 2 ]; then
	usage
fi

BACKUP_PATH="$1"
LOCKFILE="/var/lock/backup.lock"
LASTBACKUP="${BACKUP_PATH}/daily/`ls -t ${BACKUP_PATH}/daily/ | head -n 1`"
DATE=`date +%d.%m.%y`

echo "STARTING ${2} BACKUP"

echo "Waiting for lockfile to be free"
while [ -e $LOCKFILE ]; do
	sleep 2
done


touch $LOCKFILE

case "$2" in
	daily)
		if [ $# -ne 3 ]; then
			usage
		fi

		SRC="$3"
		NEWBACKUP="${BACKUP_PATH}/daily/${DATE}"
		echo "Backing up ${SRC} to ${NEWBACKUP}"

		if [ -e ${NEWBACKUP} ]; then
			echo "Backup \"$NEWBACKUP\" already exists!"
			rm $LOCKFILE
			exit 1
		fi

		if [ "${LASTBACKUP}" != "${BACKUP_PATH}/daily/" ]; then
			echo "Hardlinking most recent backup: ${LASTBACKUP}"
			cp -al "${LASTBACKUP}" "${NEWBACKUP}"
		else
			echo "creating first backup"
			mkdir "${NEWBACKUP}"
		fi
		if [ -e "${SRC}/exclude.txt" ]; then
			echo "rsync with exclude file"
			rsync -q --exclude-from="${SRC}/exclude.txt" -a --delete "${SRC}" "$NEWBACKUP"
		else
			echo "rsync with no exclude file"	
			rsync -q -a --delete "${SRC}" "${NEWBACKUP}"
		fi

		echo "Setting last modified time to now"
		touch "${NEWBACKUP}"

		remove_old_backups daily

	;;
	weekly|monthly)
		if [ $# -ne 2 ]; then
			usage
		fi
		NEWBACKUP="${BACKUP_PATH}/${2}/"
		echo "Hardlinking most recent backup ${LASTBACKUP} to ${NEWBACKUP}"
		cp -al "${LASTBACKUP}" "${NEWBACKUP}"

		remove_old_backups ${2}
	;;
	*)
		usage
	;;
esac

if [ -e $LOCKFILE ]; then
	rm $LOCKFILE
fi

