#!/usr/bin/python

import urllib2

url = "http://www.imdb.com/find?s=all&q=The+god+father"

u = urllib2.Request(url)
u.add_header('User-Agent','Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.375.70 Safari/533.4')
u.add_header("Accept","text/html")
n = urllib2.urlopen(u)

p = n.read()

p = p[p.find('<a href="/title/tt'):]
p = p[:p.find('</a>')]

print p
