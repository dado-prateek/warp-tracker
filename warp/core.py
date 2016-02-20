""" Core module of warp-tracker
"""
import os
import logging
import datetime

from warp import bencode
from warp.base import Server

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NoTorrentFound(Exception):
    """ Exception when no torrent found """
    pass


class WarpCore(Server):
    """ Core of tracker """
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.torrents = []
        self.load_torrents()

    def load_torrents(self):
        """ Loading torrents from files """
        for path in find_torrent_files(self.cfg['TORRENTS_DIR']):
            torrent = Torrent(read_torrent_info(path))
            self.add_torrent(torrent)

    def add_torrent(self, torrent):
        """ serve torrent """
        if torrent not in self.torrents:
            logger.debug('Add torrent: {}'.format(torrent.info))
            self.torrents.append(torrent)

    def get_torrents(self):
        """ return serving torrent list """
        return self.torrents

    def announce(self):
        """ Announce response """
        pass

    def scrape(self):
        """ Scrape response """
        pass


class Torrent(object):
    """ Torrent object """
    def __init__(self, torrent_info):
        self.hash = 1
        self.peers = []
        self.info = torrent_info
        self.load()

    def load(self):
        """ init object with self.info """
        pass

    def add_peer(self, peer):
        """ add peer to list of known peers """
        self.peers.append(peer)

    def __hash__(self, *args, **kwargs):
        return self.hash


class Peer(object):
    """ Peer object """
    def __init__(self, cfg, passkey):
        self.cfg = cfg
        self.last_seen = datetime.datetime.now()
        self.passkey = passkey

    def __hash__(self):
        return self.passkey

    @property
    def alive(self):
        """ check alive state of peer """
        alive_time = datetime.timedelta(hours=2)
        return self.last_seen > datetime.datetime.now() + alive_time


def read_torrent_info(fpath):
    """ read torrent info from torrent file path """
    with open(fpath, 'rb') as file:
        return bencode.decode(file.read())


def find_torrent_files(torrents_dir):
    """ Return list of path to torrent files """
    try:
        files = os.listdir(torrents_dir)
    except FileNotFoundError:
        logger.error('Directory does not exists %s', torrents_dir)
        exit(1)

    files = [os.path.join(torrents_dir, p) for p in files]
    return files
