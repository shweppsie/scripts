#!/usr/bin/env python

import os, gzip, re, hashlib, sys
from time import strftime, strptime, mktime, localtime

TEST = False

# start and end of each html file
start = \
"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
	<head>
		<title>IRC Logs</title>
		<link href="/styles/log.css" rel="stylesheet" type="text/css">
		<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
	</head>
	<body>
"""
# Don't modify end unless you know what you're doing!!!
end = \
"""	</body>
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
		self.time = strptime(time, '%a %b %d %H:%M:%S %Y')
		self.channel = channel
		self.user = user
		self.host = host
		self.text = text

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return '"%s %s: <%s> %s"' % (self.get_time(),self.channel,self.user,self.text)

	def get_channel(self,nohash=False):
		channel = None
		if nohash and self.channel.startswith("#"):
			channel = self.channel[1:]
		else:
			channel = self.channel
		return self.__fix_html(channel)

	def get_ticks(self):
		return mktime(self.time)

	def get_time(self):
		return strftime("%a %d %b %Y %X",self.time)

	def get_year(self):
		return self.time.tm_year

	def get_month(self):
		return self.time.tm_mon

	def get_day(self):
		return self.time.tm_mday

	def get_date(self):
		return strftime("%Y-%m-%d",self.time)

	def get_user(self):
		return self.__fix_html(self.user)

	def get_user_color(self):
		return "#%s%s%s" % (hashlib.md5(self.user).hexdigest()[0:2], hashlib.md5(self.user).hexdigest()[2:4], hashlib.md5(self.user).hexdigest()[4:6])

	def get_host(self):
		return self.host

	def get_text(self,raw=False):
		if raw:
			return self.text
		else:
			text = self.__fix_html(self.text)
			urls = url.findall(text)
			for link in urls:
				if link.startswith('http://geek.cn/') and self.user == 'tinybot':
					text = text.replace(link,'<a class="geek" href="%s">%s</a>' % (link,link))
				else:
					text = text.replace(link,'<a href="%s">%s</a>' % (link,link))
			return text

	def __fix_html(self, text):
		html_escape_table = {
			"&": "&amp;",
			'"': "&quot;",
			"'": "&apos;",
			">": "&gt;",
			"<": "&lt;",
		}
		return "".join(html_escape_table.get(c,c) for c in text)

################################################
#                   FUNCTIONS                  #
################################################

def get_lines(log):
	entries = {}

	# get_ticks returns the time in seconds
	# since the epoch. We then sort the list
	# based on this.
	sorted(log, key=lambda line: line.get_ticks())

	for line in log:
		chan = line.get_channel(nohash=True)
		year = line.get_year()
		month = line.get_month()
		day = line.get_day()
		if chan not in entries:
			entries[chan] = {}
		if year not in entries[chan]:
			entries[chan][year] = {}
		if month not in entries[chan][year]:
			entries[chan][year][month] = {}
		if day not in entries[chan][year][month]:
			entries[chan][year][month][day] = []
		entries[chan][year][month][day].append(line)
	return entries

def write_day(chan,year,month,day,lines):
	global TEST

	# create directory if necessary
	chandir = os.path.join(OUTDIR,channel,"%04d-%02d" % (year,month))
	if not os.path.isdir(chandir):
		os.makedirs(chandir)

	date = "%04d-%02d-%02d" % (year, month, day)
	filename = os.path.join(chandir,date)+'.html'

	if TEST:
		print "FILE: %s" % filename
		out_file = sys.stdout
	else:
		# create or append file
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

	# write the items out
	for line in lines:
		out_file.write("\t\t<p>%s <span style=\"color: %s\">&lt;%s&gt;</span> %s</p>\n" % (line.get_time(),line.get_user_color(),line.get_user(),line.get_text()))
		last_update = line.get_ticks()

	# write the end to the file
	out_file.write(end)

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
new_last_update = 0
try:
	if os.path.exists(UPDATE_FILE):
		output = open(UPDATE_FILE,'r')
		last_update = float(output.read())
		new_last_update = last_update
		output.close()
except:
	pass

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
					time = res.group(1)
					channel = channel
					user = res.group(3)
					host = res.group(4)
					text = res.group(5)

					item = LogEntry(time,channel,user,host,text)

					# only get newer lines
					if item.get_ticks() > last_update:
						if item.get_ticks() > new_last_update:
							new_last_update = item.get_ticks()
						log.append(item)
	finally:
		f.close()

# break the log into days
log = get_lines(log)

# write out the logs
for channel in log.keys():
	for year in log[channel].keys():
		for month in log[channel][year].keys():
			for day in log[channel][year][month].keys():
				write_day(channel, year, month, day, log[channel][year][month][day])

#TODO: Building some nice index pages

# save the timestamp from the last item
if not TEST:
	output = open(UPDATE_FILE,'w')
	output.write(str(new_last_update))
	output.close()

