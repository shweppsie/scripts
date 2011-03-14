#!/bin/bash

LOCKFILE="/var/lock/backup.lock"
LOGDIR="/var/log/backup"
BACKUP_DIR="/stuff/backup"

function usage {
	echo "$0 name daily source"
	echo "$0 name weekly|monthly"
	exit 3
}

function remove_old_backups {
	echo "Deleting old backups"
	i=0
	ls -t ${BACKUP_DIR}/$1/ | while read line; do
		i=$(($i+1))
		if [ $i -gt 5 ]; then
			echo "Deleting: ${BACKUP_DIR}/${1}/${line}"
			rm -r "${BACKUP_DIR}/${1}/${line}"
		fi
	done
}

if [ $# -lt 2 ]; then
	usage
fi

DATE=`date +%y.%m.%d`
BACKUP_NAME="${1}"
BACKUP_TYPE="${2}"
BACKUP_DIR="${BACKUP_DIR}/${BACKUP_NAME}/"
TMPBACKUP="${BACKUP_DIR}/daily/incomplete"
LOGDIR="${LOGDIR}/${BACKUP_NAME}/${BACKUP_TYPE}"

if [ ! -e "$LOGDIR" ]; then
	mkdir -p "$LOGDIR"
fi

LOGPATH="${LOGDIR}/${DATE}.log"

#redirect output to a log file
exec 1>>"${LOGPATH}"
#exec 2>&1

echo "${DATE}: ${BACKUP_TYPE} BACKUP OF ${BACKUP_NAME}" | tr '[:lower:]' '[:upper:]'

echo "Waiting for lockfile to become free..."
i=0
while [ -e $LOCKFILE ]; do
	i=$(($i+1))
	if [ $i -gt 360 ]; then
		echo "Lockfile did not become free after 30mins. Quiting..." | tee -a "${LOGPATH}" >&2
		exit 1
	fi
	sleep 5
done
echo "Lockfile became free. Starting backup..."
touch $LOCKFILE

if [ -e $TMPBACKUP ]; then
	echo "Removing old incomplete backup: ${TMPBACKUP}"
	rm -rf ${TMPBACKUP} 2>&1
fi

LASTBACKUP="${BACKUP_DIR}/daily/`ls -t ${BACKUP_DIR}/daily/ | head -n 1`"

case "$BACKUP_TYPE" in
	daily)
		if [ $# -ne 3 ]; then
			usage
		fi

		SRC="${3}"
		NEWBACKUP="${BACKUP_DIR}/daily/${DATE}"

		echo "Backing up ${SRC} to ${NEWBACKUP}"

		if [ -e ${NEWBACKUP} ]; then
			echo "ERROR: Backup \"$NEWBACKUP\" already exists!" | tee -a "${LOGPATH}" >&2
			rm $LOCKFILE
			exit 1
		fi

		if [ "${LASTBACKUP}" != "${BACKUP_DIR}/daily/" ]; then
			echo "Hardlinking most recent backup: ${LASTBACKUP}"
			ionice -c 3 cp -al "${LASTBACKUP}" "${TMPBACKUP}" 2>&1
			if [ $? -ne 0 ]; then
				"ERROR: cp Failed" | tee -a "${LOGPATH}" >&2
				rm $LOCKFILE
				exit $?
			fi
		else
			echo "creating first backup"
			mkdir -p "${TMPBACKUP}"
		fi

		exclude=""
		if [ "${SRC}" == "/" ]; then
			exclude="/exclude.txt"
		else
			exclude="${SRC}/exclude.txt"
		fi
		if [ -e "${exclude}" ]; then
			echo "Begginning rsync with exclude file: ${exclude}"
		else
			echo "Begginning rsync with no exclude file"
			exclude=""
		fi
		ionice -c 3 rsync -a --delete --exclude-from="${exclude}" "${SRC}" "${TMPBACKUP}" 2>&1
		if [ $? -ne 0 ]; then
			echo "ERROR: rsync Failed with return code: $?" | tee -a "${LOGPATH}" >&2
			rm $LOCKFILE
			exit $?
		fi

		echo "Moving Backup into place"
		mv ${TMPBACKUP} "${NEWBACKUP}"
		
		echo "Setting last modified time to now"
		touch "${NEWBACKUP}"

		remove_old_backups daily
	;;
	weekly|monthly)
		if [ $# -ne 2 ]; then
			usage
		fi
		NEWBACKUP="${BACKUP_DIR}/${BACKUP_TYPE}/"
		echo "Hardlinking most recent backup ${LASTBACKUP} to ${NEWBACKUP}"
		cp -al "${LASTBACKUP}" "${NEWBACKUP}" 2>&1
		if [ $? -ne 0 ]; then
			"ERROR: cp Failed" | tee -a "${LOGPATH}" >&2
			rm $LOCKFILE
			exit $?
		fi


		remove_old_backups ${2}
	;;
	*)
		usage
	;;
esac

if [ -e $LOCKFILE ]; then
	rm $LOCKFILE
fi

DATE=`date +%y.%m.%d`
echo "${DATE}: BACKUP COMPLETE"
