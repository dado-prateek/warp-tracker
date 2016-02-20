""" Tracker config """

import os

cfg = {
    'PORT': 1717,
    'BIND_ADDR': '0.0.0.0',
    'TORRENTS_DIR': os.path.join(os.getcwd(), 'torrents'),
}
