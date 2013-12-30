#!/usr/bin/env python

import sys, socket

if len(sys.argv) != 2:
    print "Usage: %s IP" % sys.argv[0]
    sys.exit(1)

#json='{ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "params": { "filter": { "id": "VideoLibrary.Scan", "type": "method" } }, "id": 1 }'

json = '{ "jsonrpc": "2.0", "method": "VideoLibrary.Scan" }'

ip = socket.gethostbyname(sys.argv[1])
s = socket.create_connection((ip, 9090))
s.send(json)

data = s.recv(1024)
print data

