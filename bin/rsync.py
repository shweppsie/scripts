#!/usr/bin/env python

import subprocess
import time

DOWNLOADS_FILE = '/stuff/shared/downloads/donbot/downloads.txt'

# open logfile
log = open('/var/log/downloads/downloads.log','a')

log.write('\n%s: Starting Download\n' % time.asctime(time.localtime()))
log.flush()

downloads = ['rsync','--size-only','-r','-vv','--password-file','.donbot.rsync']
download_files = []

for i in open(DOWNLOADS_FILE).read().split('\n'):
	i = i.split('#')[0].strip()
	if i != '':
		download_files.append('nobody@donbot.shweppsie.com::downloads/torrent/complete/%s' % i)

if len(download_files) == 0:
	log.write("Nothing to download\n")
	log.flush()
	exit(0)

downloads.extend(download_files)

downloads.append('/stuff/shared/downloads/donbot/')

log.write('%s\n' % repr(downloads))
log.flush()

for i in xrange(5):
	p = subprocess.Popen(downloads,stderr=log,stdout=log)
	# program has terminated?
	while p.poll() == None:
		# quit if it's after 7am
		if time.localtime().tm_hour >= 7:
			p.terminate()
			time.sleep(10)
			if p.poll:
				p.kill()
			log.write("%s: Stopping...7am limit reached\n"% time.asctime())
			log.flush()
			exit(1)
		#re-check in a minute
		time.sleep(60)
	if p.returncode == 0:
		log.write("%s: Downloads Completed Successfully\n" % time.asctime())
		log.flush()

		# clear the downloads file
		open(DOWNLOADS_FILE,'w')

		exit(0)
	else:
		# wait 5 minutes and try again
		log.write("%s: Application Quit with Error Code\n" % time.asctime())
		log.write("%s: Waiting 5 minutes and trying again\n" % time.asctime())
		log.flush()

		time.sleep(5*60)

		log.write("%s: Retrying\n" % time.asctime())
		log.flush()

log.write("%s: Giving up after 5 attempts" % time.asctime())
log.flush()
print "%s: Giving up after 5 attempts" % time.asctime()

exit(1)

