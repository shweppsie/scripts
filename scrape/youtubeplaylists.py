import urllib2
import xml.dom.minidom
import pprint

user='nathanoverall'
plist='90EFC99CAFC8FBE6'

url='https://gdata.youtube.com/feeds/api/users/%s/playlists?v=2' % user
url='https://gdata.youtube.com/feeds/api/playlists/%s?v=2' % plist

f = urllib2.urlopen(url)
xml = xml.dom.minidom.parseString(f.read())
print xml.toprettyxml()

