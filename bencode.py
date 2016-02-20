"""Nov 25 16:07 MSK 2015
warp-tracker - bencode.py

Bencode elems map:
  <int>:<string>                : string
  i<int>e                       : int
  l<elem>...e                   : list
  d<key_elem><val_elem>...e     : dict

"""

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def decode(ben_string, start_from=0):
    position = start_from
    char = chr(ben_string[position])

    if char in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0'):
        string_len_text = char
        position += 1
        follow_char = chr(ben_string[position])
        while follow_char != ':':
            string_len_text = '{}{}'.format(string_len_text, follow_char)
            position += 1
            follow_char = chr(ben_string[position])
        position += 1
        string_start = position
        string_finish = string_start + int(string_len_text)
        return (ben_string[string_start:string_finish]), string_finish

    elif char == 'i':
        position += 1
        follow_char = chr(ben_string[position])
        int_text = ''
        while follow_char != 'e':
            int_text = '{}{}'.format(int_text, follow_char)
            position += 1
            follow_char = chr(ben_string[position])
        return int(int_text), position + 1

    elif char == 'l':
        position += 1
        follow_char = chr(ben_string[position])
        res = []
        while follow_char != 'e':
            item, position = decode(ben_string, start_from=position)
            res.append(item)
            follow_char = chr(ben_string[position])
        return res, position + 1

    elif char == 'd':
        position += 1
        follow_char = chr(ben_string[position])
        res = {}
        while follow_char != 'e':
            key, position = decode(ben_string, start_from=position)
            value, position = decode(ben_string, start_from=position)
            res.update({key: value})
            follow_char = chr(ben_string[position])
        return res, position + 1


if __name__ == '__main__':
    assert decode(b'0:')[0] == b''
    assert decode(b'5:Hello')[0] == b'Hello'
    assert decode(b'12:Hello World!')[0] == b'Hello World!'
    assert decode(b'i42e')[0] == 42
    assert decode(b'i-1e')[0] == -1
    assert decode(b'l5:helloe')[0] == [b'hello']
    assert decode(b'l5:hello5:worlde')[0] == [b'hello', b'world']
    assert decode(b'd5:hello5:world2:hil5:hello5:worldee')[0] == {b'hello': b'world', b'hi': [b'hello', b'world']}
    assert decode(b'd5:hello5:world2:hil5:hello5:worlde3:hi2l5:hello5:worldee')[0] == {b'hello': b'world', b'hi2': [b'hello', b'world'], b'hi': [b'hello', b'world']}
