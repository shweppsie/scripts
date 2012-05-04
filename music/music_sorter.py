#!/usr/bin/env python

#############################################
#            Sorting Folders                #
#############################################

# original copies of files (source dir of files to sort)
orig="/stuff/shared/music/originals/"

# hardlink the best encoding of each file here
#best="/stuff/shared/music/best/"

# hardlink mp3 encoded files here
#orig_mp3="/stuff/shared/music/originals-mp3/"

# hardlink flac encoded files here
#orig_flac="/stuff/shared/music/originals-flac/"

# hardlink mp3 encoded files here and convert non mp3 files to mp3
mp3="/stuff/shared/music/encoded-mp3/"

# Hardlink these filetypes across
link = ['.mp3','.jpg','.jpeg','.png']

# Try to re-encode these to mp3
decode = ['.flac','.ogg']

#############################################
#                 Script                    #
#############################################

import os, sys, subprocess, tempfile

VERBOSE=True

def update_path(oldpath):
	return oldpath.replace(orig, mp3)

def decode_flac(infile,outfile):
	proclist = [ "/usr/bin/flac" , "--decode" , "--totally-silent" , "--force" , "-o", outfile, infile ]
	run_command(proclist)

def decode_ogg(infile,outfile):
	proclist = [ "/usr/bin/oggdec" , "-Q" , "-o", outfile, infile ]
	run_command(proclist)

def encode_mp3(infile,outfile):
	proclist = [ "/usr/bin/lame" , "--silent" ]
	proclist.append(infile)
	proclist.append(outfile)
	run_command(proclist)

def run_command(proclist):
	return subprocess.Popen(proclist,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()
	#p = subprocess.Popen(proclist,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	#print p.stdout.read()

#TODO: deal with deleted files!

for (curdir, folders, files) in os.walk(orig):
	for oldfile in files:
		
		oldfile = os.path.join(curdir, oldfile)
		newfile = update_path(oldfile)
		name, ext = os.path.splitext(oldfile)
		
		if os.path.exists(newfile):
			print "skipping: %s" % newfile
			continue
		
		newdir = os.path.dirname(newfile)
		if not os.path.isdir(newdir):
			os.makedirs(newdir)
		
		if ext in link:
			if VERBOSE:
				print "hardlinking: %s -> %s" % (oldfile, newfile)
			try:
				os.link(oldfile, newfile)
			except:
				print "ERROR: Failed to hardlink: %s -> %s" % (oldfile, newfile)
				sys.exit(1)
		elif ext in decode:
			newfile = update_path(os.path.join(curdir,oldfile))
			newfile = os.path.splitext(newfile)[0]+'.mp3'
			(tmpfile,tmppath) = tempfile.mkstemp(suffix='.wav', prefix='tmp', dir=None, text=False)
			if VERBOSE:
				print "decoding %s file: %s" % (ext[1:], oldfile)
			try:
				if ext == ".flac":
					decode_flac(oldfile, tmppath)
				elif ext == ".ogg":
					decode_ogg(oldfile, tmppath)
				if VERBOSE:
					print "encoding file to mp3: %s" % tmppath
				encode_mp3(tmppath, newfile)
			except Exception, e:
				print "ERROR: Interrupted! Deleting incomplete mp3 file"
				if os.path.exists(newfile):
					os.unlink(newfile)
				raise
			finally:
				os.close(tmpfile)
				if os.path.exists(tmppath):
					os.unlink(tmppath)
		else:
			if VERBOSE:
				print "Not sure what to do with %s" % oldfile
