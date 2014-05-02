#!/usr/bin/env python

import json
import os.path
from time import time

from pysnap.utils import (encrypt, decrypt, decrypt_story,
                          make_media_id, request)

MEDIA_IMAGE = 0
MEDIA_VIDEO = 1
MEDIA_VIDEO_NOAUDIO = 2

FRIEND_CONFIRMED = 0
FRIEND_UNCONFIRMED = 1
FRIEND_BLOCKED = 2
PRIVACY_EVERYONE = 0
PRIVACY_FRIENDS = 1


def is_video(data):
    return len(data) > 1 and data[0:2] == b'\x00\x00'


def is_image(data):
    return len(data) > 1 and data[0:2] == b'\xFF\xD8'


def is_zip(data):
    return len(data) > 1 and data[0:2] == 'PK'


def get_file_extension(media_type):
    if media_type in (MEDIA_VIDEO, MEDIA_VIDEO_NOAUDIO):
        return 'mp4'
    if media_type == MEDIA_IMAGE:
        return 'jpg'
    return ''


def get_media_type(data):
    if is_video(data):
        return MEDIA_VIDEO
    if is_image(data):
        return MEDIA_IMAGE
    return None


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

    Usage:

        from pysnap import Snapchat
        snapchat = Snapchat()
        snapchat.login('username', 'password')
        ...

    """
    def __init__(self):
        self.username = None
        self.auth_token = None

    def _request(self, endpoint, data=None, files=None,
                 raise_for_status=True, req_type='post'):
        return request(endpoint, self.auth_token, data, files,
                       raise_for_status, req_type)

    def _unset_auth(self):
        self.username = None
        self.auth_token = None

    def login(self, username, password):
        """Login to Snapchat account
        Returns a dict containing user information on successful login, the
        data returned is similar to get_updates.

        :param username Snapchat username
        :param password Snapchat password
        """
        self._unset_auth()
        r = self._request('login', {
            'username': username,
            'password': password
        })
        result = r.json()
        if 'auth_token' in result:
            self.auth_token = result['auth_token']
        if 'username' in result:
            self.username = username
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
                if 'c_id' not in snap]

    def get_friend_stories(self, update_timestamp=0):
        """Get stories
        Returns a dict containing metadata for stories

        :param update_timestamp: Optional timestamp (epoch in seconds) to limit
                                 updates
        """
        r = self._request("all_updates", {
            'username': self.username,
            'update_timestamp': update_timestamp
        })
        result = r.json()
        if 'auth_token' in result:
            self.auth_token = result['auth_token']
        stories = []
        story_groups = result['stories_response']['friend_stories']
        for group in story_groups:
            sender = group['username']
            for story in group['stories']:
                obj = story['story']
                obj['sender'] = sender
                stories.append(obj)
        return stories

    def get_story_blob(self, story_id, story_key, story_iv):
        """Get the image or video of a given snap
        Returns the decrypted image or a video of the given snap or None if
        data is invalid.

        :param story_id: Media id to fetch
        :param story_key: Encryption key of the story
        :param story_iv: Enctyprion IV of the story
        """
        r = self._request('story_blob', {'story_id': story_id},
                          raise_for_status=False, req_type='get')
        data = decrypt_story(r.content, story_key, story_iv)
        if any((is_image(data), is_video(data), is_zip(data))):
            return data
        return None

    def get_blob(self, snap_id):
        """Get the image or video of a given snap
        Returns the decrypted image or a video of the given snap or None if
        data is invalid.

        :param snap_id: Snap id to fetch
        """
        r = self._request('blob', {'username': self.username, 'id': snap_id},
                          raise_for_status=False)
        data = decrypt(r.content)
        if any((is_image(data), is_video(data), is_zip(data))):
            return data
        return None

    def send_events(self, events, data=None):
        """Send event data
        Returns true on success.

        :param events: List of events to send
        :param data: Additional data to send
        """
        if data is None:
            data = {}
        r = self._request('update_snaps', {
            'username': self.username,
            'events': json.dumps(events),
            'json': json.dumps(data)
        })
        return len(r.content) == 0

    def mark_viewed(self, snap_id, view_duration=1):
        """Mark a snap as viewed
        Returns true on success.

        :param snap_id: Snap id to mark as viewed
        :param view_duration: Number of seconds snap was viewed
        """
        now = time()
        data = {snap_id: {u't': now, u'sv': view_duration}}
        events = [
            {
                u'eventName': u'SNAP_VIEW', u'params': {u'id': snap_id},
                u'ts': int(round(now)) - view_duration
            },
            {
                u'eventName': u'SNAP_EXPIRED', u'params': {u'id': snap_id},
                u'ts': int(round(now))
            }
        ]
        return self.send_events(events, data)

    def update_privacy(self, friends_only):
        """Set privacy settings
        Returns true on success.

        :param friends_only: True to allow snaps from friends only
        """
        setting = lambda f: PRIVACY_FRIENDS if f else PRIVACY_EVERYONE
        r = self._request('settings', {
            'username': self.username,
            'action': 'updatePrivacy',
            'privacySetting': setting(friends_only)
        })
        return r.json().get('param') == str(setting(friends_only))

    def get_friends(self):
        """Get friends
        Returns a list of friends.
        """
        return self.get_updates().get('friends', [])

    def get_best_friends(self):
        """Get best friends
        Returns a list of best friends.
        """
        return self.get_updates().get('bests', [])

    def add_friend(self, username):
        """Add user as friend
        Returns JSON response.
        Expected messages:
            Success: '{username} is now your friend!'
            Pending: '{username} is private. Friend request sent.'
            Failure: 'Sorry! Couldn't find {username}'

        :param username: Username to add as a friend
        """
        r = self._request('friend', {
            'action': 'add',
            'friend': username,
            'username': self.username
        })
        return r.json()

    def delete_friend(self, username):
        """Remove user from friends
        Returns true on success.

        :param username: Username to remove from friends
        """
        r = self._request('friend', {
            'action': 'delete',
            'friend': username,
            'username': self.username
        })
        return r.json().get('logged')

    def block(self, username):
        """Block a user
        Returns true on success.

        :param username: Username to block
        """
        r = self._request('friend', {
            'action': 'block',
            'friend': username,
            'username': self.username
        })
        return r.json().get('message') == '{0} was blocked'.format(username)

    def unblock(self, username):
        """Unblock a user
        Returns true on success.

        :param username: Username to unblock
        """
        r = self._request('friend', {
            'action': 'unblock',
            'friend': username,
            'username': self.username
        })
        return r.json().get('message') == '{0} was unblocked'.format(username)

    def get_blocked(self):
        """Find blocked users
        Returns a list of currently blocked users.
        """
        return [f for f in self.get_friends() if f['type'] == FRIEND_BLOCKED]

    def upload(self, path):
        """Upload media
        Returns the media ID on success. The media ID is used when sending
        the snap.
        """
        if not os.path.exists(path):
            raise ValueError('No such file: {0}'.format(path))

        with open(path, 'rb') as f:
            data = f.read()

        media_type = get_media_type(data)
        if media_type is None:
            raise ValueError('Could not determine media type for given data')

        media_id = make_media_id(self.username)
        r = self._request('upload', {
            'username': self.username,
            'media_id': media_id,
            'type': media_type
            }, files={'data': encrypt(data)})

        return media_id if len(r.content) == 0 else None

    def send(self, media_id, recipients, time=5):
        """Send a snap. Requires a media_id returned by the upload method
        Returns true if the snap was sent successfully
        """
        r = self._request('send', {
            'username': self.username,
            'media_id': media_id,
            'recipient': recipients,
            'time': time,
            'zipped': '0'
            })
        return len(r.content) == 0
