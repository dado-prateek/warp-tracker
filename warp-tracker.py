#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 1717
Peers = {}


class WarpPeer:
    params = {}

    def __init__(self, params):
        self.params = params
        return

    def addPeerToDB(self):
        return


class WarpCore:
    def __init__(self):
        return


class WarpServer:
    def __init__(self):
        return


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def answer(self, path):
        return (path)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.answer(self.path))
        return


class WarpServerHandler(MyHTTPRequestHandler):
    def answer(self, path):
        if self.path[0:9] == '/announce':
            params = parse_qs(urlparse(self.path).query)
            peer = WarpPeer(params)
            Peers += peer
            return bytes(self.path, 'utf-8')
        elif self.path[0:7] == '/scrape':
            return bytes("not implemented yet", "utf-8")
        else:
            return bytes(
                    "<h1>Welcome to the WARP BitTorrent tracker!</h1>",
                    "utf-8")

if __name__ == '__main__':
    try:
        server = HTTPServer(('', PORT), WarpServerHandler)
        print ('Started WARP tracker on port', PORT)
        server.serve_forever()

    except KeyboardInterrupt:
        print ('Shutting down the server')
        server.socket.close()
