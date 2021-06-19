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

        self.ip_list6 = []
        self.ip_list4 = []

        if self.auto:
            if not ipv6 and not ipv4:
                raise Exception("If you set auto mode you mast set True in ipv6 or ipv4")
            ip_list = subprocess.getoutput("hostname -I").split(" ")
            ip_list = [d for d in ip_list if d != ""]
            if ipv6:
                for d in ip_list:
                    if isinstance(ip_address(d), IPv6Address) and not d in self.blacklist:
                        self.ip_list6.append(d)
                if len(self.ip_list6) == 0:
                    raise Exception("Can't get any IPv6 address")
                else:
                    logger.info("Detect IPv6 address list %s"%(self.ip_list6))

            if ipv4:
                for d in ip_list:
                    if isinstance(ip_address(d), IPv4Address) and not d in self.blacklist:
                        self.ip_list4.append(d)
                if len(self.ip_list4) == 0:
                     raise Exception("Can't get any IPv6 address")
                else:
                    logger.info("Detect IPv4 address list %s"%(self.ip_list4))
        else:
            logger.info("You must set IP address manually")

    def start_server(self, ipv6 = False, addr=None):
        if addr is None:
            if ipv6:
                if len(self.ip_list6) != 0:
                    addr = self.ip_list6[0], self.port
                else:
                    raise Exception("Cant't set IPv6.")
            else:
                if len(self.ip_list4) != 0:
                    addr = self.ip_list4[0], self.port
                else:
                    raise Exception("Cant't set IPv4.")

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

    def add_ip_addresses(self, ip):
        if ip in self.ip_list4 or ip in self.ip_list6:
            raise Exception("Already added")
        try:
            if isinstance(ip_address(ip), IPv6Address):
                self.ip_list6.append(ip)
                logger.info("Set IPv6 address")
            elif isinstance(ip_address(ip), IPv4Address):
                self.ip_list4.append(ip)
                logger.info("Set IPv4 Address")
            else:
                raise Exception("IP address format what you set is incorrect.")
        except ValueError:
            raise Exception("IP address format what you set is incorrect.")

    def get_ip_lists(self):
        return {"IPv4": self.ip_list4, "IPv6": self.ip_list6}

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
