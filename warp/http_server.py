import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from warp.core import WarpCore
from warp.base import Server
from warp.config import cfg

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_TPL = """<h1>Welcome to the WARP BitTorrent tracker!</h1>
<p>{torrents_list}</p>"""
URL_TPL = '<a href="{url}">{name}</a>'
NEW_LINE_TPL = '<br />'


class ServerRequest(object):
    """ Server request handlers class """
    request_url = NotImplemented

    def __init__(self, request):
        self.core = WarpCore(cfg)
        self.request = request
        super().__init__()

    def process(self):
        """ process request method """
        raise NotImplementedError


class AnnounceRequest(ServerRequest):
    """ Announce request """
    request_url = '/announce'

    def process(self):
        return bytes()


class ScrapeRequest(ServerRequest):
    """ Scrrape request """
    request_url = '/scrape'

    def process(self):
        pass


class IndexRequest(ServerRequest):
    """ Index request """
    request_url = '/'

    def process(self):
        torrents = self.core.get_torrents()
        torrents_list = format_torrent_list(torrents)

        return render_html(DEFAULT_TPL, {'torrents_list': torrents_list})


class TorrentRequest(ServerRequest):
    request_url = '/torrents'

    def process(self):
        pass


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """ BaseHTTPRequestHandler subclass """
    def __init__(self, request, client_address, server):
        self.requests = {}
        self.register_server_request(AnnounceRequest)
        self.register_server_request(ScrapeRequest)
        self.register_server_request(IndexRequest)
        super().__init__(request, client_address, server)

    def register_server_request(self, request_cls):
        """ register server request """
        self.requests[request_cls.request_url] = request_cls

    def answer(self):
        """ answer to requested path """
        request = urlparse(self.path)
        handler = self.get_request_handler(request)
        if handler:
            return handler.process()
        else:
            return bytes()

    def get_request_handler(self, request):
        """ Find suitable request handler based on path """
        try:
            return self.requests[request.path](request)
        except KeyError:
            pass

    def do_GET(self):
        """ GET query response """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(self.answer())



class WarpHTTPServer(Server):
    """ HTTP server class """
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg

    def serve(self):
        try:
            params = (self.cfg['BIND_ADDR'], self.cfg['PORT'])
            logger.info('Starting http server on %s:%s', *params)
            http_server = HTTPServer(params, HTTPRequestHandler)
            http_server.serve_forever()
        except KeyboardInterrupt:
            logger.info('Shutting down http server')
            http_server.server_close()


def render_html(template, data):
    """ render HTML from template """
    return bytes(template.format(**data), "utf-8")


def format_torrent_list(torrents):
    """ return list of HTML links generated from torrents """
    res = []
    for torr in torrents:
        res.append(
            URL_TPL.format(url='/torrents/{}'.format(torr), name=torr))
    return NEW_LINE_TPL.join(torrents)
