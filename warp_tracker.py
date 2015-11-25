#!/usr/bin/env python3

import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import lib

root = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


PORT = 1717
BIND_ADDR = '0.0.0.0'
TORRENT_PATH = os.path.join(os.getcwd(),'torrents')


class WarpException(Exception):
    pass


class NoTorrentFound(WarpException):
    pass


class WarpServer(metaclass=lib.Singleton):

    def __init__(self):
        logger.debug('Initializing WarpServer')
        self.torrents_path = TORRENT_PATH
        self.port = PORT
        self.bind_addr = BIND_ADDR
        self._core = WarpCore()
        self.read_torrents()
        self._http_server = HTTPServer((self.bind_addr, self.port), WarpServerHTTPRequestHandler)

    def read_torrents(self):
        try:
            torrents_files = os.listdir(self.torrents_path)
        except FileNotFoundError:
            logger.error('Directory does not exists {}'.format(self.torrents_path))
            exit(1)

        for path in torrents_files:
            torrent = WarpTorrent()
            torrent.read_from_file(os.path.join(self.torrents_path, path))
            self._core.add_torrent(torrent)

    def serve(self):
        try:
            logger.info('Starting http server on {}:{}'.format(self.bind_addr, self.port))
            self._http_server.serve_forever()
        except KeyboardInterrupt:
            logger.info('Shutting down http server')
            self._http_server.server_close()

    def process_request(self, request):
        return self._core.process_request(request)


class WarpServerHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.warp_server = WarpServer()
        super().__init__(request, client_address, server)

    def answer(self, path):
        return self.warp_server.process_request(urlparse(self.path)) or bytes(self.path, "utf-8")

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.answer(self.path))


class WarpCore:

    def __init__(self):
        self.torrents_peers = {}

    def add_torrent(self, torrent):
        if torrent not in self.torrents_peers:
            self.torrents_peers[torrent] = []

    def add_peer(self, torrent, peer):
        self.torrents_peers[torrent].append(peer)

    def get_peers(self, torrent):
        if torrent not in self.torrents_peers:
            raise NoTorrentFound()

        return self.torrents_peers[torrent]

    def process_request(self, request):
        if request.path == '/announce':
            pass
        elif request.path == '/scrape':
            pass
        else:
            return bytes("<h1>Welcome to the WARP BitTorrent tracker!</h1><br /><p>{}</p>".format(request), "utf-8")


class WarpTorrent:

    def __init__(self):
        self.hash = 1

    def read_from_file(self, path):
        logger.debug('Reading torrent {}'.format(path))

    def __hash__(self, *args, **kwargs):
        return self.hash


class WarpPeer:

    pass


if __name__ == '__main__':
    server = WarpServer()
    server.serve()
