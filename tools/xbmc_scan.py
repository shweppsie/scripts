import socket

#json='{ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "params": { "filter": { "id": "VideoLibrary.Scan", "type": "method" } }, "id": 1 }'

json = '{ "jsonrpc": "2.0", "method": "VideoLibrary.Scan" }'

s = socket.create_connection(('127.0.0.1', 9090))
s.send(json)

#data = s.recv(1024)
#print data

