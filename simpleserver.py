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

class HTTPServersHandle():
    def __init__(self, auto= True, ipv4=True, ipv6=False, port=8000):
        self.blacklist = pd.read_csv("./blacklist.csv", comment = "#").blacklist.values.tolist()
        self.port = port
        self.auto = auto
        self.ipv6 = ipv6
        self.ipv4 = ipv4
        self.Handler = SimpleHTTPRequestHandler

        if self.auto:
            if not ipv6 and not ipv4:
                raise Exception("If you set auto mode you mast set True in ipv6 or ipv4")
            ip_list = subprocess.getoutput("hostname -I").split(" ")
            ip_list = [d for d in ip_list if d != ""]
            if ipv6:
                self.ip_list6 = [d for d in ip_list if isinstance(ip_address(d), IPv6Address) and not d in self.blacklist]
                if len(self.ip_list6) == 0:
                    raise Exception("Can't get any IPv6 address")
                else:
                    logger.info("Detect IPv6 address list %s".format(self.ip_list6))

            if ipv4:
                self.ip_list4 = [d for d in ip_list if isinstance(ip_address(d), IPv4Address) and not d in self.blacklist]
                if len(self.ip_list4) == 0:
                     raise Exception("Can't get any IPv6 address")
                else:
                    logger.info("Detect IPv4 address list %s".format(self.ip_list4))

    def start_server(self, ipv6 = False, addr=None):
        if addr is None:
            if self.auto:
                if ipv6:
                    if self.ipv6:
                        addr = self.ip_list6[0], self.port
                    else:
                        raise Exception("Cant't set IPv6.")
                else:
                    if self.ipv4:
                        addr = self.ip_list4[0], self.port
                    else:
                        raise Exception("Cant't set IPv4.")
            else:
                raise Exception("Must set addr.")

        server = TCPServer6 if ipv6 else TCPServer
        with server(addr, self.Handler) as httpd:
            try:
                if ipv6:
                    logger.info("server is listening at http://[%s]:%s"%(addr[0], addr[1]))
                else:
                    logger.info("server is listening at http://%s:%s"%(addr[0], addr[1]))
                httpd.serve_forever()
            except KeyboardInterrupt:
                del httpd
                logger.info("stop server")

    def start_servers():
        pass

if __name__ == "__main__":
    ipv6 = False
    try:
        if sys.argv[1] == "ipv6":
            ipv6 = True
    except IndexError:
        pass

    if ipv6:
        sv_handle = HTTPServersHandle(ipv4=False, ipv6=True)
        sv_handle.start_server(ipv6=True)
    else:
        sv_handle = HTTPServersHandle(ipv4=True, ipv6=False)
        sv_handle.start_server()
