""" Web server related module """

import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, _coerce_args, unquote_to_bytes

import warp.config
from warp.core import WarpCore
from warp.base import Server

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ServerRequest(object):
    """ Server request handlers class """
    request_url = NotImplemented

    def __init__(self, request, host):
        self.core = WarpCore(warp.config.cfg)
        self.request = request
        self.host = host
        self.query = parse_qs_to_bytes(self.request.query)
        super().__init__()
        logger.debug('Query %s', self.query)

    def process(self):
        """ Process request method """
        raise NotImplementedError


class UnknownRequest(ServerRequest):
    """ Process unknown requests. Generally return 404 """
    def process(self):
        return 'text/plain', bytes('Unknown request', 'utf-8')


class AnnounceRequest(ServerRequest):
    """ Announce request """
    request_url = '/announce'

    def process(self):
        params = {
            'peer_id': self.query[b'peer_id'][0],
            'info_hash': self.query[b'info_hash'][0],
            'host': self.host.decode('utf-8'),
            'port': self.query[b'port'][0]
        }
        content_type = 'text/plain'
        return content_type, self.core.announce(params)


class HTTPRequestHandler(BaseHTTPRequestHandler):
    """ BaseHTTPRequestHandler subclass """
    def __init__(self, request, client_address, server):
        self.requests = {}
        self.register_server_request(AnnounceRequest)
        super().__init__(request, client_address, server)

    def register_server_request(self, request_cls):
        """ Register server request """
        self.requests[request_cls.request_url] = request_cls

    def answer(self):
        """ Answer to requested path """
        request = urlparse(self.path)
        host, _ = self.client_address
        handler = self.get_request_handler(request)
        return handler(request, host).process()

    def get_request_handler(self, request):
        """ Find suitable request handler based on path """
        try:
            return self.requests[request.path]
        except KeyError:
            return UnknownRequest

    def do_GET(self):
        """ GET query response """
        content_type, response = self.answer()
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(response_to_bytes(response))


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


def parse_qs_to_bytes(query_string, keep_blank_values=False,
                      strict_parsing=False):
    """Parse a query given as a string argument.

        Arguments:

        qs: percent-encoded query string to be parsed

        keep_blank_values: flag indicating whether blank values in
            percent-encoded queries should be treated as blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored and treated as if they were
            not included.

        strict_parsing: flag indicating what to do with parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors raise a ValueError exception.

        encoding and errors: specify how to decode percent-encoded sequences
            into Unicode characters, as accepted by the bytes.decode() method.
    """
    parsed_result = {}
    pairs = parse_qsl_to_bytes(query_string, keep_blank_values, strict_parsing)
    for name, value in pairs:
        if name in parsed_result:
            parsed_result[name].append(value)
        else:
            parsed_result[name] = [value]
    return parsed_result


def parse_qsl_to_bytes(query_string, keep_blank_values=False,
                       strict_parsing=False):
    """Parse a query given as a string argument.

    Arguments:

    qs: percent-encoded query string to be parsed

    keep_blank_values: flag indicating whether blank values in
        percent-encoded queries should be treated as blank strings.  A
        true value indicates that blanks should be retained as blank
        strings.  The default false value indicates that blank values
        are to be ignored and treated as if they were  not included.

    strict_parsing: flag indicating what to do with parsing errors. If
        false (the default), errors are silently ignored. If true,
        errors raise a ValueError exception.

    encoding and errors: specify how to decode percent-encoded sequences
        into Unicode characters, as accepted by the bytes.decode() method.

    Returns a list, as G-d intended.
    """
    query_string, _coerce_result = _coerce_args(query_string)
    pairs = [s2 for s1 in query_string.split('&') for s2 in s1.split(';')]
    res = []
    for name_value in pairs:
        if not name_value and not strict_parsing:
            continue
        nval = name_value.split('=', 1)
        if len(nval) != 2:
            if strict_parsing:
                raise ValueError("bad query field: %r" % (name_value,))
            # Handle case of a control-name with no equal sign
            if keep_blank_values:
                nval.append('')
            else:
                continue
        if len(nval[1]) or keep_blank_values:
            name = nval[0].replace('+', ' ')
            name = unquote_to_bytes(name)
            name = _coerce_result(name)
            value = nval[1].replace('+', ' ')
            value = unquote_to_bytes(value)
            value = _coerce_result(value)
            res.append((name, value))
    return res


def response_to_bytes(string):
    """ Convert response string to bytes if needed """
    if string is not None:
        if not isinstance(string, bytes):
            return bytes(string, 'utf-8')
        else:
            return string
    else:
        return bytes()
