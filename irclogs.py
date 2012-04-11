#!/usr/bin/env python

import os, gzip, re, hashlib, sys
from time import strftime, strptime, mktime

# start and end of each html file
start = """<html><head><style type="text/css">
		html {
			color: white;
			background-color: black;
		}
		p {
			margin:0px;
			font-family: Fixed, monospace;
		}
		A:link { color: #99CCFF; }
		A:visited { color: #993300; }
		A.geek:link { color: #FFFF99; }
</style></head><body>"""
end = """</body></html>"""

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

	def __str__(self):
		return "%s %s: <%s> %s" % (self.get_time(),self.channel,self.user,self.text)

	def get_day(self):
		return self.time[2]

	def get_channel(self,nohash=False):
		if nohash and self.channel.startswith("#"):
			return self.channel[1:]
		else:
			return self.channel

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
			urls = url.findall(text)
			for link in urls:
				if link.startswith('http://geek.cn/') and self.user == 'tinybot':
					text = text.replace(link,'<a class="geek" href="%s">%s</a>' % (link,link))
				else:
					text = text.replace(link,'<a href="%s">%s</a>' % (link,link))
			return text

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
log = {}

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
					
					log[mktime(time)] = item
	finally:
		f.close()

# we use the time in seconds since the epoch
# to index the dictionary. Therefore sorting
# the keys, sorts all the log items we've
# read in.
keys = log.keys()
keys.sort()

# varibles used to keep track of stuff as
# we process each log item
count = 0
cur_day = 0
out_file = None

# what was the timestamp of the last item we processed
last_entry = 0
if os.path.exists(UPDATE_FILE):
	last_entry = float(open(UPDATE_FILE,'r').read())

# process items
for i in keys:
	# ignore stuff we've already processed
	if i <= last_entry:
		continue

	item = log[i]
	item_day = item.get_day()
	
	# create a new file if we've changed day
	if cur_day != item_day:
		cur_day = item_day
		
		# end the last file
		if out_file is not None:
			out_file.write(end)
			out_file.close()
		
		# create directory if necessary
		chandir = os.path.join(OUTDIR,item.get_channel(nohash=True))
		if not os.path.isdir(chandir):
			os.makedirs(chandir)

		filename = os.path.join(chandir,item.get_date())+'.html'
		
		# append or create file
		out_file = open(filename,'a')
		out_file.write(start)
	
	# actually write out the log entry
	out_file.write("<p>%s <span style=\"color: %s\">&lt%s&gt</span> %s</p>" % (item.get_time(),item.get_user_color(),item.get_user(),item.get_text()))
	count += 1

	# remember the last item
	last_entry = i

# don't update files if we did nothing
if out_file is not None:
	# end the last file
	out_file.write(end)
	out_file.close()

# save the timestamp from the last item
output = open(UPDATE_FILE, 'w')
output.write(str(i))
output.close()

#print "Processed %s lines" % count
