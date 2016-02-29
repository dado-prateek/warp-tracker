import unittest

from warp.core import WarpCore, Torrent, ip4_to_4bytes, port_to_2bytes
from warp.core import Peer
from warp.config import cfg


class TestWarpCore(unittest.TestCase):
    def setUp(self):
        self.warp_core = WarpCore(cfg)
        self.torrent = object()

    def test_add_get_torrents(self):
        info_hash = b'hash'

        self.warp_core.add_hash_torrent(info_hash, self.torrent)
        torrents = list(self.warp_core.get_torrents())

        self.assertEqual(len(torrents), 1)
        self.assertEqual(torrents[0], self.torrent)

        torrent = self.warp_core.get_torrent_by_hash(info_hash)
        self.assertEqual(torrent, self.torrent)


class TestTorrent(unittest.TestCase):
    def setUp(self):
        self.torrent = Torrent(self._mock_metafile())
        self.peer = object()

    def _mock_metafile(self):
        class MockTorrentMetaFile(object):
            def __init__(self, path):
                self.path = path
                self.file_name = 'file_name'
                self.meta_data = {b'info': b'info'}
                self.bencoded_info = b'bencoded_info'

            def __repr__(self):
                return 'Metafile(path)'

        return MockTorrentMetaFile('path')

    def test_add_get_peer(self):
        self.torrent.add_peer(self.peer)
        peers = list(self.torrent.get_peers())

        self.assertEqual(len(peers), 1)
        self.assertEqual(peers[0], self.peer)

    def test_add_uniq_peers_only(self):
        self.torrent.add_peer(self.peer)
        self.torrent.add_peer(self.peer)
        peers = self.torrent.get_peers()

        self.assertEqual(len(peers), 1)

    def test_create_info_hash(self):
        bencoded_info = b'info'
        info_hash = b'Y\xbd\n?\xf4;2\x84\x9b1\x9ed]G\x98\xd8\xa5\xd1\xe8\x89'
        metafile = self._mock_metafile()
        metafile.bencoded_info = bencoded_info
        torrent = Torrent(metafile)

        self.assertEqual(torrent.create_info_hash(), info_hash)

    def test_repr(self):
        self.assertEqual(repr(self.torrent), 'Torrent(Metafile(path))')


class TestPeer(unittest.TestCase):
    def setUp(self):
        self.params = {
            'peer_id': b'peer_id',
            'info_hash': b'info_hash',
            'host': b'127.0.0.1',
            'port': b'666',
            'left': b'0',
            'compact': b'1'
        }

    def test_equality(self):
        """ Peers are equal when host and port is equal """
        peer = Peer(self.params)
        equal_peer = Peer(self.params)
        self.assertEqual(peer, equal_peer)

        params_mod = self.params
        params_mod['host'] = b'1'
        unequal_host_peer = Peer(params_mod)
        self.assertNotEqual(peer, unequal_host_peer)

        params_mod = self.params
        params_mod['port'] = b'1'
        unequal_port_peer = Peer(params_mod)
        self.assertNotEqual(peer, unequal_port_peer)

    def test_hash(self):
        peer1 = Peer(self.params)
        peer2 = Peer(self.params)
        peer_set = {peer1, peer2}
        self.assertEqual(len(peer_set), 1)


class TestFuncts(unittest.TestCase):
    def test_ip4_to_4byte(self):
        self.assertEqual(ip4_to_4bytes(b'46.163.130.47'), b'.\xa3\x82/')

    def test_port_to_2byte(self):
        self.assertEqual(port_to_2bytes(59568), b'\xe8\xb0')
