#!/usr/bin/env python

import os, gzip, re, hashlib, sys
from time import strftime, strptime, mktime

# start and end of each html file
start = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
	<head>
		<title>IRC Logs</title>
		<link href="/log.css" rel="stylesheet" type="text/css">
		<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
	</head>
	<body>
"""
# Don't modify end unless you know what you're doing!!!
end = """
	</body>
</html>
"""

UPDATE_FILE=os.path.expanduser("~/.irclog.lastupdate")

# regex to match items in each log line
prog = re.compile('^([A-Z][a-z]{2} [A-Z][a-z]{2} +[0-9]{1,2} [0-9:]{8} [0-9]{4}): (#[^:]*): <([^!]*)!([^>]*)> (.*)')

# regex to match url
url = re.compile('(http://[^ ]*)')

################################################
#  Class to store all the details in one line  #
#                of logged chat                #
################################################

class LogEntry:
	def __init__(self, time, channel, user, host, text):
		self.time = time
		self.channel = channel
		self.user = user
		self.host = host
		self.text = text

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return '"%s %s: <%s> %s"' % (self.get_time(),self.channel,self.user,self.text)

	def get_channel(self,nohash=False):
		if nohash and self.channel.startswith("#"):
			return self.channel[1:]
		else:
			return self.channel

	def get_ticks(self):
		return mktime(self.time)

	def get_time(self):
		return strftime("%a %d %b %Y %X",self.time)

	def get_date(self):
		return strftime("%Y-%m-%d",self.time)

	def get_user(self):
		return self.user

	def get_user_color(self):
		return "#%s%s%s" % (hashlib.md5(self.user).hexdigest()[0:2], hashlib.md5(self.user).hexdigest()[2:4], hashlib.md5(self.user).hexdigest()[4:6])

	def get_host(self):
		return self.host

	def get_text(self,raw=False):
		if raw:
			return self.text
		else:
			text = self.text
			replace = [("<","&lt;"),(">","&gt;"),("&","&amp;")]
			for i in replace:
				text = text.replace(i[0],i[1])
			urls = url.findall(text)
			for link in urls:
				if link.startswith('http://geek.cn/') and self.user == 'tinybot':
					text = text.replace(link,'<a class="geek" href="%s">%s</a>' % (link,link))
				else:
					text = text.replace(link,'<a href="%s">%s</a>' % (link,link))
			return text

################################################
#                   FUNCTIONS                  #
################################################

def get_channels(log):
	channels = {}
	for line in log:
		chan = line.get_channel(nohash=True)
		if chan not in channels:
			channels[chan] = []
		channels[chan].append(line)
	return channels

def get_days(log):
	days = {}
	for line in log:
		date = line.get_date()
		if date not in days:
			days[date] = []
		days[date].append(line)
	return days

################################################
#                    SCRIPT                    #
################################################

# check arguments
if len(sys.argv) < 3:
	print "Usage: %s logdir outdir"
	exit(1)

args = len(sys.argv)-1
INDIR=sys.argv[1:args]
OUTDIR=sys.argv[args]

# get a list of the log files
files = []
for path in INDIR:
	if not os.path.exists(path):
		print "log directory does not exist: %s" % path
		exit(1)
	filenames = os.listdir(path)
	for filename in filenames:
		filename = os.path.join(path,filename)
		if os.path.isfile(filename):
			files.append(filename)

# dictionary for storing processed log items
log = []

# We've already process everything up to this timestamp
last_update = 0
if os.path.exists(UPDATE_FILE):
	output = open(UPDATE_FILE,'r')
	last_update = float(output.read())
	output.close()

# process log files
for path in files:
	f = open(path, 'rb')
	try:
		# deal with gzip'd logs
		if path.endswith('.gz'):
			f = gzip.GzipFile(fileobj=f)
		
		data = f.read()

		for i in data.split('\n'):
			res = prog.match(i)
			if res is not None:
				channel = res.group(2)
				# only process certain channels
				if channel in ['#chat']:
					# add LogEntry item
					time = strptime(res.group(1), '%a %b %d %H:%M:%S %Y')
					channel = channel
					user = res.group(3)
					host = res.group(4)
					text = res.group(5)

					item = LogEntry(time,channel,user,host,text)
					
					if item.get_ticks() > last_update:
						log.append(item)
	finally:
		f.close()


# get_ticks returns the time in seconds
# since the epoch. We then sort the list
# based on this.
log = sorted(log, key=lambda line: line.get_ticks())

# break the log into channels
channels = get_channels(log)

# break the log into days
for chan in channels.keys():
	channels[chan] = get_days(channels[chan])

for channel in channels:
	# create directory if necessary
	chandir = os.path.join(OUTDIR,channel)
	if not os.path.isdir(chandir):
		os.makedirs(chandir)

	for day in channels[channel]:
		filename = os.path.join(chandir,day)+'.html'

		# append or create file
		if not os.path.exists(filename):
			out_file = open(filename,'w')
			out_file.write(start)
		else:
			out_file = open(filename,'rw+')
			# seek back before the end text
			out_file.seek(len(end)*(-1), os.SEEK_END)
			# truncate off the old file ending
			out_file.truncate()
			# make sure we're at the end of the file
			out_file.seek(0, os.SEEK_END)

		for item in channels[channel][day]:
			out_file.write("<p>%s <span style=\"color: %s\">&lt;%s&gt;</span> %s</p>" % (item.get_time(),item.get_user_color(),item.get_user(),item.get_text()))
			last_update = item.get_ticks()
		
		#write the end to the file
		out_file.write(end)

# save the timestamp from the last item
output = open(UPDATE_FILE,'w')
output.write(str(last_update))
output.close()

