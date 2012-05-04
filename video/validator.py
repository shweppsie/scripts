#!/usr/bin/env python

import sys,os,re

#TODO: add different modes: movie and tv
#TODO: detect empty folders
#TODO: detect missing episodes from a Season

VIDEO=['.avi','.mp4','.mkv','.mov','.wmv','.divx','.m4v','.mpg','.iso','.flv']
THUMB=['.jpg','.png','.srt']
SPECIAL=['.mp3']

def status(reason,path):
	print "%s: %s" % (reason,path)

def failed(path, reason):
	status("Failed (%s)" % reason,path)
	return 1

def passed(path):
	status("Passed",path)
	return 0

def processMovie(path, debug=False):
	return 0

def processTV(path,debug=False):
	fullpath = path
	path, filename = os.path.split(path)
	path, seasondir = os.path.split(path)
	path, seriesname = os.path.split(path)

	if seriesname.startswith('The '):
		return failed(fullpath,"Series does not follow spec")

	if seriesname.endswith(', The'):
		seriesname = "The %s" % seriesname[:-5]

	# check name on season folder
	try:
		seasonnum = re.match(r'Season ([0-9]{2})',seasondir).group(1)
	except AttributeError, e:
		return failed(fullpath,"Season Folder Name does not meet spec")
		
	# check filename
	match = re.match(r'(.*) - ([0-9]{1,2}x([0-9]{2}))( - .*)?\.[^.]+$',filename)
	if not match:
		return failed(fullpath,"Filename does not meet spec")
	
	# compare file series name and dir series name
	if seriesname != match.group(1):
		return failed(fullpath, "Series Names do not match")

	# compare file season number and dir season number
	if int(match.group(2).split('x')[0]) != int(seasonnum):
			return failed(fullpath,"File and folder Season Number do not match")

	if debug:
		return passed(fullpath)
	else:
		return 0

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description='Process command line arguments.')

	parser.add_argument('--debug',action='store_true',dest='debug',default=False,
		help='Enable debug mode')
	parser.add_argument('directory',help='Directory to validate')

	args = parser.parse_args()

	path = args.directory

	if not os.path.exists(path):
		print "Path does not exist: %s" % path
		sys.exit(1)

	if os.path.isfile(path):
		sys.exit(processTV(path))

	for (d, folders, files) in os.walk(os.path.abspath(path)):
		files = sorted(files)
		for i in files:
			processTV("%s/%s" % (d,i),args.debug)
