#!/usr/bin/env python

# Copyright 2011 Nathan Overall
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# rsstorrents.py version 2.0

# script to parse an rss feed of torrents and add them as they become availble
# the script relies on being called at regular intervals usually via cron

import subprocess, sys, os, re
import feedparser
import time
import calendar
import json

DATAFILE = '/etc/rsstorrents.json'

class AddTorrentException(Exception):
	def __init__(self, error_text):
		self.error_text = error_text
	def __str__(self):
		return self.error_text.decode('ascii')

class NoSuchFeedException(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return "No Such Feed: %s" % self.value

def showrss(data,last_updated):
	torrents = []
	for entry in data.entries:
		if entry.updated_parsed > last_updated:
			torrents.append(entry['links'][0]['href'])
	return torrents

def ezrss(data,last_updated):
	torrents = []
	for entry in data.entries:
		if entry.updated_parsed > last_updated:
			# either get a magnet or torrent link
			if 'magneturi' in  entry.keys() and _check_magnet(entry['magneturi']):
				torrents.append(entry['magneturi'])
			elif 'link' in entry.keys():
				torrents.append(entry['link'])
	return torrents

func_mapper = [ 
	{
		'url':r'^http://www.ezrss.it/search/index.php\?(((show_name|show_name_exact|date|quality|quality_exact|release_group)=[^&]*|simple)&)*mode=rss$',
		'func':ezrss
	},{
		'url':r'^http://showrss.karmorra.info/feeds/[0-9]*.rss',
		'func':showrss
	}
]

def _check_magnet(magnet):
	if re.match(r'^magnet\:\?xt=urn:btih:[A-Z0-9]{32}(&[^=]*=[^&]*)*$',magnet):
		return True
	else:
		return False

def _read_datafile():
	data = {}
	if(os.path.exists(DATAFILE)):
		try:
			data = json.load(open(DATAFILE))
		except Exception, e:
			if open(DATAFILE).read() != "":
				raise
	return data

def _write_datafile(data):
	f = open(DATAFILE, 'w')
	data = json.dumps(data, f, indent=4)
	f.write(data)
	f.flush()
	f.close()

def _add_torrent(torrent):
	args = ["/usr/local/bin/transmission-remote","localhost","-a","%s" % torrent]
	(output,errors) = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
	if output != "" and not output.find('success'):
		raise AddTorrentException(output.split(': ',1)[1].replace("\"",""))
	elif errors != "":
		raise AddTorrentException(errors)

def check_feeds():
	print "Starting Check: %s" % time.ctime()
	data = _read_datafile()
	for key in data:
		feed = data[key]
		name = key
		url = feed['url']
		last_updated = time.gmtime(feed['last_updated'])

		print "Checking: %s" % name
		
		# go fetch the rss feed
		rss = feedparser.parse(url)

		if rss['status'] == 503:
			print 'Error: Feed returned 503 (Service Unavailable)'
			data[name]['status'] = 'Error: Feed returned 503 (Service Unavailable)'
			continue
		
		matched = False

		for m in func_mapper:
			if re.match(m['url'],url):
				matched = True
				for torrent in m['func'](rss,last_updated):
					print "Adding: %s" % torrent
					try:
						_add_torrent(torrent)
					except AddTorrentException, e:
						data[name]['status'] = str(e)
						_write_datafile(data)
						raise
				data[name]['last_updated'] = time.time()
				data[name]['status'] = 'updated last %s' % time.strftime("on the %d %b %Y at %H:%M:%S", time.localtime())
				break
		if not matched:
			data[name]['status'] = 'url matches no known rss torrent services'

	_write_datafile(data)

def add_feed(name,url):
	data = _read_datafile()
	data[name] = { 'url':url, 'status':'Feed never checked', 'last_updated': time.time() }
	_write_datafile(data)

def reset_feed(name):
	data = _read_datafile()
	try:
		data[name]['last_updated'] = 0
		data[name]['status'] = 'feed has been reset'
		_write_datafile(data)
		return
	except:
		for i in data:
			if info == data[i]['url']:
				data[i]['last_updated'] = 0
				data[i]['status'] = 'feed has been reset'
				_write_datafile(data)
				return
	raise NoSuchFeedException(info)

def remove_feed(info):
	data = _read_datafile()
	try:
		del data[info]
		_write_datafile(data)
		return
	except:
		for i in data:
			if info == data[i]['url']:
				del data[i]
				_write_datafile(data)
				return
	raise NoSuchFeedException(info)

def list_feeds():
	data = _read_datafile()
	for i in data:
		name = i
		url = data[i]['url']
		if 'status' in data[i]:
			status = data[i]['status']
		else:
			status = 'Unknown'

		print "%s:\n\tstatus: %s\n\turl: %s\n" % (name,status,url)

def arg_add(args):
	add_feed(args.name, args.url)

def arg_reset(args):
	reset_feed(args.info)

def arg_remove(args):
	remove_feed(args.info)

def arg_list(args):
	list_feeds()

def arg_check(args):
	check_feeds()

def main():
	import argparse

	mode_parser = argparse.ArgumentParser()
	subparsers = mode_parser.add_subparsers(title='actions',dest='action')
	add_parser = subparsers.add_parser('add', description='to update a feed use the same name', help='add or update a feed')
	add_parser.add_argument('name',help='name this feed')
	add_parser.add_argument('url',help='url to rss feed')
	add_parser.set_defaults(func=arg_add)
	reset_parser = subparsers.add_parser('reset', help='cause the next check to download all previous torrents on a feed')
	reset_parser.add_argument('info',metavar='(name|url)',
			help='name or url of feed to reset')
	reset_parser.set_defaults(func=arg_reset)
	remove_parser = subparsers.add_parser('remove', 
			help='remove a feed via it\'s name or url')
	remove_parser.add_argument('info',metavar='(name|url)',
			help='name or url of feed to remove')
	remove_parser.set_defaults(func=arg_remove)
	list_parser = subparsers.add_parser('list', help='list all feeds being checked')
	list_parser.set_defaults(func=arg_list)
	check_parser = subparsers.add_parser('check', help='check all feeds now')
	check_parser.set_defaults(func=arg_check)

	args = mode_parser.parse_args()
	args.func(args)	

if __name__ == "__main__":
	main()
