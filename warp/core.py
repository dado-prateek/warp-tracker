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


class InfoHashNotFound(Exception):
    """ Exception when no torrent found for giving info_hash"""
    pass


class TorrentNotFound(Exception):
    """ Raise when torrent not found """
    pass


class WarpCore(metaclass=Singleton):
    """ Core of tracker """
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.hashes_torrents = {}
        self.torrents = set()

    def load_torrents(self):
        """ Loading torrents from files """
        logger.info('Loading torrents from %s', self.cfg['TORRENTS_DIR'])
        for file_path in find_files(self.cfg['TORRENTS_DIR']):
            torrent = Torrent.init_from_file(file_path)
            self.add_torrent(torrent)
            self.add_hash_torrent(torrent.info_hash, torrent)
        logger.info('Loaded %i torrents', len(self.hashes_torrents))

    def add_hash_torrent(self, info_hash, torrent):
        """ Serve torrent """
        logger.debug('Add torrent %s', torrent)
        if info_hash not in self.hashes_torrents:
            self.hashes_torrents[info_hash] = torrent

    def add_torrent(self, torrent):
        """ Add torrent to list """
        self.torrents.add(torrent)

    def get_torrents(self):
        """ Return serving torrents view """
        return self.hashes_torrents.values()

    def get_torrent_by_hash(self, info_hash):
        """ Return torent by info hash """
        try:
            return self.hashes_torrents[info_hash]
        except KeyError:
            msg = 'Torrent not found for info_hash {}'.format(info_hash)
            logger.info(msg)
            raise InfoHashNotFound(msg)

    def get_torrent_by_file_name(self, file_name):
        """ Return torrent by filename """
        for torr in self.torrents:
            if torr.metafile.file_name == file_name:
                torrent = torr
                break
        else:
            raise TorrentNotFound(file_name)
        return torrent

    def fix_announce_url(self, torrent):
        """ Replace announce url in torrent to current tracker url """
        if 'ANNOUNCE_URL' in self.cfg:
            url = self.cfg['ANNOUNCE_URL'].encode('utf-8')
            torrent.metafile.meta_data[b'announce'] = url
            return torrent

    def announce(self, params):
        """ Announce response. Returns bencoded dictionary """
        peer = Peer(params)

        info_hash = params['info_hash']
        try:
            torrent = self.get_torrent_by_hash(info_hash)
            torrent.add_peer(peer)
            peers = torrent.get_peers()
            response = {
                b'interval': 60,
                # b'tracker id': b'WarpTracker',
                # b'complete': len([p for p in peers if p.is_seeder]),
                # b'incomplete': len([p for p in peers if p.is_leecher]),
                b'peers': b''.join([p.as_bytes_compact for p in peers])
            }
        except InfoHashNotFound:
            response = {
                b'failure reason': b'Torrent not registered',
                b'failure code': 200
            }

        logger.debug('Response: %s', bencode.encode(response))
        return bencode.encode(response)


class Torrent(object):
    """ Torrent object """
    def __init__(self, metafile):
        self.metafile = metafile
        self.info_hash = self.create_info_hash()
        self.peers = set()
        logger.debug('Init %s', self)

    def add_peer(self, peer):
        """ Add peer to torrent """
        self.peers.discard(peer)
        self.peers.add(peer)

    def get_peers(self):
        """ Returns iterable with peers """
        return self.peers

    def create_info_hash(self):
        """ Creating info_hash from bencoded info block from metafile """
        return hash_sha1(self.metafile.bencoded_info)

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
        self.meta_data = self.read_meta_data()
        logger.debug('Init %s', self)
        logger.debug("meta_data: %s", self.meta_data)

    def dump_to_file(self):
        """ Save meta_info to a file """
        pass

    @property
    def bencoded_meta_data(self):
        return bencode.encode(self.meta_data)
    
    @property
    def bencoded_info(self):
        """ Bencoded info block """
        return bencode.encode(self.meta_data[b'info'])

    def read_meta_data(self):
        """ Read torrent info from path """
        try:
            with open(self.path, 'rb') as file:
                return bencode.decode(file.read())
        except FileNotFoundError:
            logger.error("File does not exists")

    def __repr__(self):
        return 'TorrentMetaFile({})'.format(self.path)


class Peer(object):
    """ Peer object """
    def __init__(self, params):
        self.peer_id = params['peer_id']
        self.host = params['host']
        self.port = int(params['port'])
        self.left = int(params['left'])
        self.compact = int(params['compact'])
        self.last_seen = datetime.datetime.now()
        logger.debug('Init %s', self)

    @property
    def as_bytes_dict(self):
        """ Returns peer dictionary model for announce response """
        return {
            b'peer id': self.peer_id,
            b'ip': self.host,
            b'port': self.port
        }

    @property
    def as_bytes_compact(self):
        """ Return peer in compact mode """
        ip_addr = ip4_to_4bytes(self.host)
        port = port_to_2bytes(self.port)
        return ip_addr + port

    @property
    def is_seeder(self):
        """ Check if peer is seeder """
        return self.left == 0

    def is_leecher(self):
        """ Check if peer is leecher """
        return not self.is_seeder

    @property
    def alive(self):
        """ Check alive state of peer """
        alive_time = datetime.timedelta(hours=2)
        return self.last_seen > datetime.datetime.now() + alive_time

    def __repr__(self):
        return 'Peer({}, {}, {})'.format(self.peer_id, self.host, self.port)

    def __hash__(self):
        return int.from_bytes(self.as_bytes_compact, 'big')

    def __eq__(self, other):
        return self.host == other.host and self.port == other.port


def find_files(dir_path):
    """ Return list of paths to torrent files """
    try:
        file_names = os.listdir(dir_path)
    except FileNotFoundError:
        logger.error('Directory does not exists %s', dir_path)
        exit(1)

    file_paths = [os.path.join(dir_path, p) for p in file_names]
    return file_paths


def hash_sha1(byte_str):
    """ Return sha1 hash of byte string """
    sha1 = hashlib.sha1()
    sha1.update(byte_str)
    return sha1.digest()


def ip4_to_4bytes(ip_byte_str):
    """ Convert ipv4 string to 4-byte """
    octets = ip_byte_str.split(b'.')
    return b''.join([int(x).to_bytes(1, 'big') for x in octets])


def port_to_2bytes(port_num):
    """ Convert int ro 2 bytes """
    return port_num.to_bytes(2, 'big')
