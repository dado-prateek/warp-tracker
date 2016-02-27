import unittest

from warp.core import WarpCore
from warp.config import cfg


class TestWarpCore(unittest.TestCase):
    def setUp(self):
        self.warp_core = WarpCore(cfg)
        self.torrent = object()

    def test_add_get_torrents(self):
        info_hash = b'some hash'

        self.warp_core.add_hash_torrent(info_hash, self.torrent)
        torrents = list(self.warp_core.get_torrents())

        self.assertEqual(len(torrents), 1)
        self.assertEqual(torrents[0], self.torrent)

        torrent = self.warp_core.get_torrent_by_hash(info_hash)
        self.assertEqual(torrent, self.torrent)
