import socket
import os

s = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW)
s.bind((os.getpid(),0))
