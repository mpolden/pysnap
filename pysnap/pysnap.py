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
MEDIA_IMAGE = 0
MEDIA_VIDEO = 1


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


def get_file_extension(media_type):
    if media_type == MEDIA_VIDEO:
        return 'mp4'
    if media_type == MEDIA_IMAGE:
        return 'jpg'
    return ''


def decrypt(data):
    cipher = AES.new(BLOB_ENCRYPTION_KEY, AES.MODE_ECB)
    return cipher.decrypt(pkcs5_pad(data))


def encrypt(data):
    cipher = AES.new(BLOB_ENCRYPTION_KEY, AES.MODE_ECB)
    return cipher.encrypt(pkcs5_pad(data))


def timestamp():
    return int(round(time() * 1000))


def _map_keys(snap):
    return {
        u'id': snap.get('id', None),
        u'media_id': snap.get('c_id', None),
        u'media_type': snap.get('m', None),
        u'time': snap.get('t', None),
        u'sender': snap.get('sn', None),
        u'recipient': snap.get('rp', None),
        u'status': snap.get('st', None),
        u'screenshot_count': snap.get('c', None),
        u'sent': snap.get('sts', None),
        u'opened': snap.get('ts', None)
    }


class Snapchat(object):
    """Construct a :class:`Snapchat` object used for communicating
    with the Snapchat API.

    :param username: Snapchat username
    :param password: Snapchat password

    Usage:

        from pysnap import Snapchat
        snapchat = Snapchat('username', 'password')
        snapchat.login()
        ...

    """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def _request(self, endpoint, data=None, raise_for_status=True):
        """Wrapper method for calling Snapchat API which adds required form
        data before sending the request.

        :param endpoint: URL for API endpoint
        :param data: Dictionary containing form data
        :param raise_for_status: Raise exception for 4xx and 5xx status codes
        """
        now = timestamp()
        if data is None:
            data = {}
        data.update({
            'timestamp': now,
            'req_token': make_request_token(
                getattr(self, 'auth_token', STATIC_TOKEN), str(now))
        })
        r = requests.post(urljoin(URL, endpoint), data=data)
        if raise_for_status:
            r.raise_for_status()
        return r

    def login(self):
        """Login to Snapchat account
        Returns a dict containing user information on successful login, the
        data return is similar to get_updates.

        :param username Snapchat username
        :param password Snapchat password
        """
        r = self._request('login', {
            'username': username,
            'password': password
            })
        result = r.json()
        if 'auth_token' in result:
            self.auth_token = result['auth_token']
        return result

    def logout(self):
        """Logout of Snapchat account
        Returns true if logout was successful.
        """
        r = self._request('logout', {'username': self.username})
        return len(r.content) == 0

    def get_updates(self, update_timestamp=0):
        """Get user, friend and snap updates
        Returns a dict containing user, friends and snap information.

        :param update_timestamp: Optional timestamp (epoch in seconds) to limit
                                 updates
        """
        r = self._request('updates', {
            'username': self.username,
            'update_timestamp': update_timestamp
            })
        result = r.json()
        if 'auth_token' in result:
            self.auth_token = result['auth_token']
        return result

    def get_snaps(self, update_timestamp=0):
        """Get snaps
        Returns a dict containing metadata for snaps

        :param update_timestamp: Optional timestamp (epoch in seconds) to limit
                                 updates
        """
        updates = self.get_updates(update_timestamp)
        # Filter out snaps containing c_id as these are sent snaps
        return [_map_keys(snap) for snap in updates['snaps']
                if not 'c_id' in snap]

    def get_blob(self, snap_id):
        """Get the image or video of a given snap
        Returns the decrypted image or a video of the given snap or None if
        data is invalid.

        :param snap_id: Snap id to fetch
        """
        r = self._request('blob', {'username': self.username, 'id': snap_id},
                          raise_for_status=False)
        data = decrypt(r.content)
        return data if is_image(data) or is_video(data) else None
