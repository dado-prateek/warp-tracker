#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

import lib

root = logging.getLogger()
root.addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


PORT = 1717
BIND_ADDR = '0.0.0.0'


class WarpServer(metaclass=lib.Singleton):

    def __init__(self):
        logger.debug('Initializing WarpServer')
        self.peers = []
        self.port = PORT
        self.bind_addr = BIND_ADDR
        self._http_server = HTTPServer((self.bind_addr, self.port), WarpServerHTTPRequestHandler)
        self.core = WarpCore()

    def serve(self):
        try:
            logger.info('Starting http server on {}:{}'.format(self.bind_addr, self.port))
            self._http_server.serve_forever()
        except KeyboardInterrupt:
            logger.info('Shutting down http server')
            self._http_server.socket.close()

    def process_request(self, request):
        return self.core.process_request(request)


class WarpServerHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.warp_server = WarpServer()
        super().__init__(request, client_address, server)

    def answer(self, path):
        return self.warp_server.process_request(urlparse(self.path)) or self.path

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.answer(self.path))


class WarpCore:

    def process_request(self, request):
        return bytes("<h1>Welcome to the WARP BitTorrent tracker!</h1><br /><p>{}</p>".format(request), "utf-8")


class WarpPeer:

    pass


if __name__ == '__main__':
    server = WarpServer()
    server.serve()
