""" Tracker config """

import os

cfg = {
    'port': 1717,
    'bind_addr': '0.0.0.0',
    'torrents_dir': os.path.join(os.getcwd(), 'torrents'),
    'announce_url': 'http://example.com/announce ',

    # Replace announce url in torrent file to given when send to client
    'patch_announce_url': True,

    # Interval in seconds that the client should wait between sending
    # regular requests to the tracker
    'check_interval': 300,
}
