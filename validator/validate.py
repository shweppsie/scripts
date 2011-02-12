#!/usr/bin/python

import os, imdb, string, re, sys

ia = imdb.IMDb()

def newname_cleanup(name):
	if name.startswith('The '):
		name = name[4:]
		name += ", The"
	if name.startswith('A '):
		name = name[2:]
		name += ", A"
	if name.startswith('An '):
		name = name[3:]
		name += ", An"
	return name

def file_rename(dirname, name):
	if name.rfind('.') == -1:
		print '"%s" needs an extension' % name
	else:
		name = name[:name.rfind('.')]

	results = ia.search_movie(name, results=1)
	if len(results) == 0:
		print 'No suggestions found for "%s"' % (name)
	else:
		result = results[0]
		title = newname_cleanup(result['title'])
		year = result['year']
		newname = "%s (%s)" % (title, year)
		if name != newname:
			print 'Rename "%s" to "%s"' % (name, newname)

def folder_rename(name):
	newname = newname_cleanup(ia.search_movie(name, results=1)[0]['title'])
	if name != newname:
		print 'Rename "%s" to "%s"' % (name, newname)
	else:
		print '"%s" ok' % name

def usage():
	print "%s file|folder" % sys.argv[0]
	sys.exit(3)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		usage()
	if os.path.isdir(argv[1]):
		folder_rename(argv[1])
	else os.path.isfile(argv[1])
		file_rename(argv[1]
	else:
		usage()
