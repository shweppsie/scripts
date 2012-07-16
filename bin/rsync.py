#!/usr/bin/env python

import sys, time
import subprocess
import argparse

def log(text, start=False):
	global log
	if start:
		logger.write('\n')
	logger.write('%s: %s\n' % (time.asctime(), text))
	logger.flush()

def parse_args():
	parser = argparse.ArgumentParser(description='Transfer files')
	parser.add_argument('--stop-time', dest='stop_time', default=7,
			help="Hour to stop downloads")
	parser.add_argument('--stdout', dest='stdout', action='store_true',
			help="output to stdout")
	parser.add_argument('source', help="Rsync source path")
	parser.add_argument('destination', help="Rsync destination path")
	return parser.parse_args()

args = parse_args()

#first arg is source
source = args.source

# open logfile
if args.stdout:
	logger = sys.stdout
else:
	logger = open('/var/log/downloads/downloads.log','a')

stop_hour = int(args.stop_time)

if time.localtime().tm_hour >= stop_hour:
	log("Not Starting. Already after stop time of %d:00." % stop_hour)
	exit(1)
else:
	log('Starting Download',start=True)
	log('Using a stop time of %d:00' % stop_hour)

DOWNLOADS_FILE = '/stuff/shared/downloads/donbot/downloads.txt'

downloads = ['/usr/bin/rsync','--size-only','-r','-vv','--password-file','.donbot.rsync']
download_files = []

for i in open(DOWNLOADS_FILE).read().split('\n'):
	i = i.split('#')[0].strip()
	if i != '':
		download_files.append('%s/%s' % (source, i))

if len(download_files) == 0:
	log("Nothing to download")
	exit(0)

downloads.extend(download_files)

downloads.append(args.destination)

log(repr(downloads))

for i in xrange(5):
	p = subprocess.Popen(downloads,stderr=logger,stdout=logger)
	# program has terminated?
	while p.poll() == None:
		# quit if it's after 7am
		if time.localtime().tm_hour >= stop_hour:
			p.terminate()
			time.sleep(10)
			if p.poll:
				p.kill()
			log("Stopping...7am limit reached")
			exit(1)
		#re-check in a minute
		time.sleep(60)
	if p.returncode == 0:
		log("Downloads Completed Successfully")
		exit(0)
	else:
		# wait 5 minutes and try again
		log("Application Quit with Error Code")
		log("Waiting 5 minutes and trying again")

		time.sleep(5*60)

		log("Retrying")

log("Giving up after 5 attempts")
print "%s: Giving up after 5 attempts" % time.asctime()

exit(1)

