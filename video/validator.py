#!/usr/bin/env python

import sys,os,re

#TODO: add different modes: movie and tv
#TODO: detect empty folders
#TODO: detect missing episodes from a Season

season = re.compile(r'^(Specials|Season (0[1-9]|[1-9][0-9]|(20|19)[0-9][0-9]))$')
tv = re.compile(r'^(.*) - ([0-9]{1,4})(x([0-9]{2,3}))+( - .*)?\.[^.]+$')

def size(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def failed(path, reason):
    print "Failed (%s): %s" % (reason,path)
    return 1

def processTV(path):
    fullpath = path
    path, filename = os.path.split(path)
    path, folder_season = os.path.split(path)
    path, folder_seriesname = os.path.split(path)

    # check for leader 'The'
    if folder_seriesname.startswith('The '):
        return failed(fullpath,
                "The should be moved to the end of names")

    if folder_seriesname.endswith(', The'):
        folder_seriesname = "The %s" % folder_seriesname[:-5]

    # check name on season folder
    res = season.match(folder_season)
    if not res:
        return failed(fullpath,
                "Season Folder Name does not meet spec")
    else:
        folder_seasonnum = res.group(2)

    # check filename
    res = tv.match(filename)
    if not res:
        return failed(fullpath,"Filename does not meet spec")

    file_seriesname = res.group(1)
    file_seasonnum = int(res.group(2))

    # compare file series name and dir series name
    if folder_seriesname != file_seriesname:
        return failed(fullpath, "Series Names do not match")

    # compare file season number and dir season number
    if folder_season != 'Specials' \
        and int(file_seasonnum) != int(folder_seasonnum):
            return failed(fullpath,"File (%s) and folder " \
                    "Season (%s) Number do not match" %
                    (file_seasonnum,folder_seasonnum) )

    # Detect duplicate episodes
    file, ext = os.path.splitext(filename)
    path = os.path.dirname(fullpath)
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path,f)):
            f, e = os.path.splitext(f)
            ignore = ['.sfv','.srt','.nfo']
            if f == file and e != ext and \
                    e not in ignore and ext not in ignore:
                filea = os.path.join(path,file+ext)
                fileb = os.path.join(path,file+e)
                filea = (filea, ext, \
                        os.path.getsize(filea))
                fileb = (fileb, e, \
                        os.path.getsize(fileb))
                if filea[2] > fileb[2]:
                    file = filea
                    filea = fileb
                    fileb = file
                print "Duplicate file, Remove: %s (%s, %s)" % \
                            (filea[0], size(filea[2]), size(fileb[2]))

    return 0

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
                    description='Process command line arguments.')

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
            processTV("%s/%s" % (d,i))

