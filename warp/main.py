#!/usr/bin/env python3.5

""" Main module of warp-tracker
distributing under GNU General Public License
"""

import logging

from warp.core import WarpCore
from warp.config import cfg
from warp.http_server import WarpHTTPServer


def set_logger():
    """ Setting up logger """
    try:
        import coloredlogs
        coloredlogs.install(level='DEBUG')
    except ImportError:
        root = logging.getLogger()
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s')
        log_handler.setFormatter(formatter)
        root.addHandler(log_handler)


def run_server():
    """ Init and run server """
    WarpCore(cfg)
    server = WarpHTTPServer(cfg)
    server.serve()


if __name__ == '__main__':
    set_logger()
    run_server()
