import unittest

from warp.core import WarpCore, Torrent
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
