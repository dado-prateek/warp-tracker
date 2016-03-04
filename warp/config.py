""" Tracker config """

import os

cfg = {
    'port': 1717,
    'bind_addr': '127.0.0.1',
    'torrents_dir': os.path.join(os.getcwd(), 'torrents'),
    'announce_url': 'http://127.0.0.1:1717/announce',

    # Replace announce url in torrent file to given when send to client
    'patch_announce_url': True,

    # Interval in seconds that the client should wait between sending
    # regular requests to the tracker
    'check_interval': 300,
}
