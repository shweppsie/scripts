#!/usr/bin/env python

import os, sys, time
import subprocess
import argparse

class Log:
	def __init__(self, logfile):
		self.fileno = sys.stdout.fileno
		if logfile != None:
			self.logfile = open(logfile,'a')
		else:
			self.logfile = sys.stdout

	def write(self, text):
		output = ('%s: %s\n' % (time.asctime(), text))
		self.logfile.write(output)
		self.logfile.flush()

	def close(self):
		self.logfile.flush()
		self.logfile.close()

def parse_args():
	parser = argparse.ArgumentParser(description='Transfer files')
	parser.add_argument('--stop-time', dest='stop_time', default=30,
			help="hour to stop downloads")
	parser.add_argument('--log', dest='logfile',
			help="output to stdout")
	parser.add_argument('source', help="Rsync source path")
	parser.add_argument('destination', help="Rsync destination path")
	return parser.parse_args()

# parse arguments
args = parse_args()

# deal with optional arguments
stop_hour = int(args.stop_time)
logfile = args.logfile

# deal with mandatory arguments
source = args.source
destination = args.destination

# prepare logging
log = Log(logfile)

# check time
if time.localtime().tm_hour >= stop_hour:
	log.write("Not Starting. Already after stop time of %d:00." % stop_hour)
	exit(1)
else:
	log.write('\nStarting Download')
	if stop_hour < 24:
		log.write('Using a stop time of %d:00' % stop_hour)

DOWNLOADS_FILE = os.path.join(destination,'downloads.txt')

downloads = ['/usr/bin/rsync','--size-only','-r','-vv','--password-file','.donbot.rsync']
download_files = []

for i in open(DOWNLOADS_FILE).read().split('\n'):
	i = i.split('#')[0].strip()
	if i != '':
		download_files.append('%s/%s' % (source, i))

if len(download_files) == 0:
	log.write("Nothing to download")
	exit(0)

downloads.extend(download_files)

downloads.append(destination)

log.write(repr(downloads))

for i in xrange(5):
	p = subprocess.Popen(downloads,stderr=log.logfile,stdout=log.logfile)
	# program has terminated?
	while p.poll() == None:
		# quit if it's after 7am
		if time.localtime().tm_hour >= stop_hour:
			p.terminate()
			time.sleep(10)
			if p.poll:
				p.kill()
			log.write("Stopping...7am limit reached")
			exit(1)
		#re-check in a minute
		time.sleep(60)
	if p.returncode == 0:
		log.write("Downloads Completed Successfully")
		exit(0)
	else:
		# wait 5 minutes and try again
		log.write("Application Quit with Error Code")
		log.write("Waiting 5 minutes and trying again")

		time.sleep(5*60)

		log.write("Retrying")

log.write("Giving up after 5 attempts")
sys.stderr.write("%s: Giving up after 5 attempts" % time.asctime())

log.close()

exit(1)

