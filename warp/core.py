""" Core module of warp-tracker
"""
import os
import logging
import datetime
import hashlib

from warp import bencode
from warp.lib import Singleton

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NoTorrentFound(Exception):
    """ Exception when no torrent found """
    pass


class WarpCore(metaclass=Singleton):
    """ Core of tracker """
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.hashes_torrents = {}
        logger.info('Loaded %i torrents', len(self.hashes_torrents))
        logger.debug(self.hashes_torrents)

    def load_torrents(self):
        """ Loading torrents from files """
        for file_path in find_files(self.cfg['TORRENTS_DIR']):
            torrent = Torrent.init_from_file(file_path)
            self.add_hash_torrent(torrent.info_hash, torrent)

    def add_hash_torrent(self, info_hash, torrent):
        """ Serve torrent """
        logger.debug('Add torrent %s', torrent)
        if info_hash not in self.hashes_torrents:
            self.hashes_torrents[info_hash] = torrent

    def get_torrents(self):
        """ Return serving torrent iterable """
        return self.hashes_torrents.values()

    def get_torrent_by_hash(self, info_hash):
        """ Return torent by info hash """
        return self.hashes_torrents[info_hash]

    def add_peer_for_hash(self, info_hash, peer):
        """ Adds peer and requested info_hash to database """
        self.get_torrent_by_hash(info_hash).add_peer(peer)

    def get_peers_for_hash(self, info_hash):
        """ Returns list of peers for given hash """
        return self.get_torrent_by_hash(info_hash).get_peers()

    def announce(self, params):
        """ Announce response. Returns bencoded dictionary """
        peer = Peer(peer_id=params['peer_id'],
                    host=params['host'],
                    port=params['port'])

        info_hash = params['info_hash']
        if info_hash in self.hashes_torrents:
            self.add_peer_for_hash(info_hash, peer)
            peers = self.get_peers_for_hash(info_hash)
            response = {
                b'interval': 60,
                b'tracker id': b'WarpTracker',
                b'complete': 0,
                b'incomplete': len(peers),
                b'peers': [p.as_bytes_dict for p in peers]
            }
            logger.debug('Response: %s', response)
            return bencode.encode(response)
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
        """ Decoded info block from the meta file """
        return self.metafile.meta_info[b'info']

    def add_peer(self, peer):
        """ Add peer to torrent """
        self.peers.add(peer)

    def get_peers(self):
        """ Returns iterable with peers """
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
    """ Class represents torrent metafile """
    def __init__(self, path):
        self.path = path
        self.file_name = os.path.basename(path)
        self.meta_info = self.read_meta_info()
        logger.debug('Init %s', self)
        logger.debug("meta_info: %s", self.meta_info)

    def dump_to_file(self):
        """ Save meta_info to a file """
        pass

    def read_meta_info(self):
        """ Read torrent info from path """
        try:
            with open(self.path, 'rb') as file:
                return bencode.decode(file.read())
        except FileNotFoundError:
            logger.warning("File does not exists")

    def __repr__(self):
        return 'TorrentMetaFile({})'.format(self.path)


class Peer(object):
    """ Peer object """
    def __init__(self, peer_id, host, port):
        self.last_seen = datetime.datetime.now()
        self.peer_id = peer_id
        self.host = host
        self.port = port
        self.info_hashes = set()
        logger.debug('Init %s', self)

    @property
    def as_bytes_dict(self):
        """ Returns peer dictionary model for announce response """
        return {
            b'peer_id': self.peer_id,
            b'ip': self.host,
            b'port': self.port
        }

    @property
    def is_seeder(self):
        """ Check if peer is seeder """
        return False

    @property
    def alive(self):
        """ Check alive state of peer """
        alive_time = datetime.timedelta(hours=2)
        return self.last_seen > datetime.datetime.now() + alive_time

    def __repr__(self):
        return 'Peer({}, {}, {})'.format(self.peer_id, self.host, self.port)


def find_files(dir_path):
    """ Return list of paths to torrent files """
    try:
        file_names = os.listdir(dir_path)
    except FileNotFoundError:
        logger.error('Directory does not exists %s', dir_path)
        exit(1)

    file_paths = [os.path.join(dir_path, p) for p in file_names]
    return file_paths
