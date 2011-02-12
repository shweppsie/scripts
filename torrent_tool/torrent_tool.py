#!/usr/bin/env python

import os, mimetypes, sys, getopt
from bencode import bencode, bdecode
from optparse import OptionParser

def main():
	usage = """ %prog [options] oldtorrentfile
		Decodes and rewrites torrent files. Helpful for changing a tracker on a torrent although you can change any of the criteria.
	"""
	parser = OptionParser(usage=usage)
	parser.add_option("-l", "--list",
					action="store_true",
					dest="list",
					default=False,
					help="list data from torrent file")
	parser.add_option("-p", "--pieces",
					action="store_true",
					dest="pieces",
					help="show pieces when listing data in torrent file. WARNING: This creates lots of output.")
	parser.add_option("-t", "--tracker",
					action="store", 
					dest="tracker",
					help="override tracker in torrent")
	parser.add_option("-w", "--writer",
					action="store",
					dest="write",
					metavar="FILE",
					help="write new torrent file")
	(options, args) = parser.parse_args()
	
	#check number of args
	if len(args) != 1:
		parser.error("incorrect number of arguments")
	#check file type
	if mimetypes.guess_type(args[0]) != ('application/x-bittorrent', None):
		parser.error("Doesn't look like a torrent file")
	#read in torrent file	
	fd = open(args[0], 'rb')
	fdT = bdecode(fd.read())
	fd.close()
	#change tracker
	if options.tracker:
		fdT['announce'] = options.tracker
	#list contents of tracker
	if options.list:
		if options.pieces:
			list(fdT, True)
		else:
			list(fdT)
	#write a file
	if options.write:
		write(fdT, options.write)

def list(fdT, pieces=False):
	heading("fdt:info:files")
	printfiles(fdT['info']['files'])
	
	heading("fdt:info:piece length")
	print fdT['info']['piece length']

	heading("fdt:info:name")
	print fdT['info']['name']

	heading("fdt:info:pieces")
	if pieces:
		print fdT['info']['pieces']
	else:
		print "NOTE: Showing pieces produces lots of output so you have to specify -p aswell as -l..."

	heading("fdt:encoding")
	print fdT['encoding']

	heading("fdt:creation date")
	print fdT['creation date']

	heading("fdt:announce-list")
	for tracker in fdT['announce-list']:
		for track in tracker:
			print track+" ",
		print ""

	heading("fdt:created by")
	print fdT['created by']

	heading("fdt:announce")
	print fdT['announce']

def printfiles(files):
	width=0
	for file in files:
		if len(str(file['length'])) > width:
			width=len(str(file['length']))
	for file in files:
		path=""
		length=""
		for i in range(0, width-len(str(file['length']))):
			length+=" "
		length+=str(file['length'])
		for dir in file['path']:
			path+="/"+dir
		print "%s %s" % (length,path)
	
def heading(string):
	print "\n**"+string+"**"

def write(fdT, file):	
	fd = open(file, 'wb')
	fd.write(bencode(fdT))
	fd.close()

if __name__ == "__main__":
	main()		
