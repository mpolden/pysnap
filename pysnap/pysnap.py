#!/usr/bin/env python

import requests
from Crypto.Cipher import AES
from hashlib import sha256
from time import time
from urlparse import urljoin

URL = 'https://feelinsonice-hrd.appspot.com/bq/'
SECRET = 'iEk21fuwZApXlz93750dmW22pw389dPwOk'
STATIC_TOKEN = 'm198sOkJEn37DjqZ32lpRu76xmw288xSQ9'
BLOB_ENCRYPTION_KEY = 'M02cnQ51Ji97vwT4'
HASH_PATTERN = ('00011101111011100011110101011110'
                '11010001001110011000110001000110')


def make_request_token(a, b):
    hash_a = sha256(SECRET + a).hexdigest()
    hash_b = sha256(b + SECRET).hexdigest()
    return ''.join((hash_b[i] if c == '1' else hash_a[i]
                    for i, c in enumerate(HASH_PATTERN)))


def pkcs5_pad(data, blocksize=16):
    pad_count = blocksize - len(data) % blocksize
    return data + (chr(pad_count) * pad_count)


def is_video(data):
    return len(data) > 1 and data[0] == chr(0x00) and data[1] == chr(0x00)


def is_image(data):
    return len(data) > 1 and data[0] == chr(0xFF) and data[1] == chr(0xD8)


def decrypt(data):
    cipher = AES.new(BLOB_ENCRYPTION_KEY, AES.MODE_ECB)
    return cipher.decrypt(pkcs5_pad(data))


def encrypt(data):
    cipher = AES.new(BLOB_ENCRYPTION_KEY, AES.MODE_ECB)
    return cipher.encrypt(pkcs5_pad(data))


def timestamp():
    return int(round(time() * 1000))


class Snapchat(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def _request(self, endpoint, data=None):
        now = timestamp()
        if data is None:
            data = {}
        data.update({
            'username': self.username,
            'timestamp': now,
            'req_token': make_request_token(
                getattr(self, 'auth_token', STATIC_TOKEN), str(now))
        })
        return requests.post(urljoin(URL, endpoint), data=data)

    def login(self):
        r = self._request('login', {'password': self.password})
        result = r.json()
        if 'auth_token' in result:
            self.auth_token = result['auth_token']
        return result

    def logout(self):
        r = self._request('logout')
        return r.status_code == 200

    def get_updates(self, update_timestamp=0):
        r = self._request('updates', {'update_timestamp': update_timestamp})
        result = r.json()
        if 'auth_token' in result:
            self.auth_token = result['auth_token']
        return result

    def get_blob(self, snap_id):
        r = self._request('blob', {'id': snap_id})
        data = decrypt(r.content)
        return data if is_image(data) or is_video(data) else None
