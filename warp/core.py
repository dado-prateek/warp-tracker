""" Core module of warp-tracker
"""
import os
import logging
import datetime
import hashlib

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
        self.hashes_torrents = {}
        self.load_torrents()
        logger.info('Loaded %i torrents', len(self.hashes_torrents))
        logger.debug(self.hashes_torrents)

    def load_torrents(self):
        """ Loading torrents from files """
        for file_path in find_files(self.cfg['TORRENTS_DIR']):
            torrent = Torrent.init_from_file(file_path)
            self.add_torrent(torrent)

    def add_torrent(self, torrent):
        """ serve torrent """
        logger.debug('Add torrent %s', torrent)
        if torrent.info_hash not in self.hashes_torrents:
            self.hashes_torrents[torrent.info_hash] = torrent

    def get_torrents(self):
        """ return serving torrent list """
        return self.hashes_torrents.values()

    def add_peer_for_hash(self, info_hash, peer):
        """ Adds peer and requested info_hash to database """
        self.hashes_torrents[info_hash].add_peer(peer)

    def get_peers_for_hash(self, info_hash):
        return self.hashes_torrents[info_hash].get_peers()

    def announce(self, params):
        peer = Peer(peer_id=params['peer_id'],
                    ip=params['host'],
                    port=params['port'])

        info_hash = params['info_hash']
        if info_hash in self.hashes_torrents:
            self.add_peer_for_hash(info_hash, peer)
            peers = self.get_peers_for_hash(info_hash)
            response = bencode.encode({
                b'interval': 60,
                b'tracker id': b'WarpTracker',
                b'complete': 0,
                b'incomplete': len(peers),
                b'peers': [p.as_bytes_dict for p in peers]
            })
            return response
        else:
            logger.warning('Unknown info_hash: %s', info_hash)


class Torrent(object):
    """ Torrent object """
    def __init__(self, metafile):
        self.metafile = metafile
        self.info_hash = self.create_info_hash()
        self.peers = set()
        logger.debug('Init %s', self)

    @property
    def info(self):
        return self.metafile.meta_info[b'info']

    def add_peer(self, peer):
        self.peers.add(peer)

    def get_peers(self):
        return self.peers

    def create_info_hash(self):
        """ Gets info_hash from torrent """
        hasher = hashlib.sha1()
        hasher.update(bencode.encode(self.info))
        return hasher.digest()

    @classmethod
    def init_from_file(cls, path):
        """ Init torrent from file path """
        return cls(TorrentMetaFile(path))

    def __repr__(self):
        return 'Torrent({})'.format(self.metafile)


class TorrentMetaFile(object):
    def __init__(self, path):
        self.path = path
        self.file_name = os.path.basename(path)
        self.meta_info = self.read_meta_info()
        logger.debug('Init %s', self)
        logger.debug("meta_info: %s", self.meta_info)

    def read_meta_info(self):
        """ read torrent info from path """
        try:
            with open(self.path, 'rb') as file:
                return bencode.decode(file.read())
        except:
            logger.warning("Not a torrent file or file does not exists")

    def __repr__(self):
        return 'TorrentMetaFile({})'.format(self.path)


class Peer(object):
    """ Peer object """
    def __init__(self, peer_id, ip, port):
        self.last_seen = datetime.datetime.now()
        self.peer_id = peer_id
        self.ip = ip
        self.port = port
        self.info_hashes = set()
        logger.debug('Init %s', self)

    @property
    def as_bytes_dict(self):
        return {
            b'peer_id': self.peer_id,
            b'ip': bytes(self.ip, 'utf-8'),
            b'port': self.port
        }

    @property
    def is_seeder(self):
        return False

    @property
    def alive(self):
        """ check alive state of peer """
        alive_time = datetime.timedelta(hours=2)
        return self.last_seen > datetime.datetime.now() + alive_time

    def __repr__(self):
        return 'Peer({}, {}, {})'.format(self.peer_id, self.ip, self.port)


def find_files(dir_path):
    """ Return list of path to torrent files """
    try:
        file_names = os.listdir(dir_path)
    except FileNotFoundError:
        logger.error('Directory does not exists %s', dir_path)
        exit(1)

    file_paths = [os.path.join(dir_path, p) for p in file_names]
    return file_paths
