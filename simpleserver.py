from socketserver import TCPServer
from http.server import SimpleHTTPRequestHandler

import pandas as pd

from socket import AF_INET6
from ipaddress import ip_address
from ipaddress import IPv6Address, IPv4Address

import subprocess
import sys

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TCPServer6(TCPServer):
    address_family = AF_INET6

    def __init__(self, addr, Handler):
        super().__init__(addr, Handler)

Handler = SimpleHTTPRequestHandler

#Get and set IP config
ip_list = subprocess.getoutput("hostname -I").split(" ")
ip_list = [d for d in ip_list if d != ""]


blacklist = pd.read_csv("./blacklist.csv", comment = "#").blacklist.values.tolist()

port = 8000
ipv6 = False
try:
    if sys.argv[1] == "ipv6":
        ipv6 = True
except IndexError:
    pass

if ipv6:
    ip_list = [d for d in ip_list if isinstance(ip_address(d), IPv6Address) and not d in blacklist]
    server = TCPServer6
    logger.info("Use IPv6 address")
else:
    ip_list = [d for d in ip_list if isinstance(ip_address(d), IPv4Address) and not d in blacklist]
    server = TCPServer
    logger.info("Use IPv4 address")

if len(ip_list) == 0:
    raise Exception("Can't get any IP address")

addr = ip_list[0], port

#Start server
with server(addr, Handler) as httpd:
    try:
        if ipv6:
            logger.info("server is listening at http://[%s]:%s"%(addr[0], addr[1]))
        else:
            logger.info("server is listening at http://%s:%s"%(addr[0], addr[1]))
        httpd.serve_forever()
    except KeyboardInterrupt:
        del httpd
        logger.info("stop server")
