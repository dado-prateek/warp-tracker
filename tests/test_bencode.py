import unittest
from warp.bencode import encode, decode


class TestBencode(unittest.TestCase):
    def test_zero_string(self):
        ben_string = b'0:'
        data = b''
        self.assertEqual(encode(data), ben_string)
        self.assertEqual(decode(ben_string), data)

    def test_string(self):
        ben_string = b'12:Hello World!'
        data = b'Hello World!'
        self.assertEqual(encode(data), ben_string)
        self.assertEqual(decode(ben_string), data)

    def test_int(self):
        ben_string = b'i42e'
        data = 42
        self.assertEqual(encode(data), ben_string)
        self.assertEqual(decode(ben_string), data)

    def test_negative_int(self):
        ben_string = b'i-1e'
        data = -1
        self.assertEqual(encode(data), ben_string)
        self.assertEqual(decode(ben_string), data)

    def test_list(self):
        ben_string = b'l5:hello5:worlde'
        data = [b'hello', b'world']
        self.assertEqual(encode(data), ben_string)
        self.assertEqual(decode(ben_string), data)

    def test_dict(self):
        ben_string = (b'd5:hello5:world2:hil5:hello5:worlde3:'
                      b'hi2l5:hello5:worldee')
        data = {
            b'hello': b'world',
            b'hi2': [b'hello', b'world'],
            b'hi': [b'hello', b'world']
        }
        self.assertEqual(encode(data), ben_string)
        self.assertEqual(decode(ben_string), data)
