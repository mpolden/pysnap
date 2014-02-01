#!/usr/bin/env python

import unittest

import responses

from requests.exceptions import HTTPError

from pysnap import is_image, is_video, Snapchat
from pysnap.utils import make_request_token, pkcs5_pad, URL


class ModuleTestCase(unittest.TestCase):

    def test_is_image(self):
        self.assertFalse(is_image(b''))
        self.assertFalse(is_image(b'\x00'))
        self.assertFalse(is_image(b'\x00\x00'))
        self.assertTrue(is_image(b'\xFF\xD8'))

    def test_is_video(self):
        self.assertFalse(is_video(b''))
        self.assertFalse(is_video(b'\xFF'))
        self.assertFalse(is_video(b'\xFF\xFF'))
        self.assertTrue(is_video(b'\x00\x00'))


class UtilsTestCase(unittest.TestCase):

    def test_make_request_token(self):
        self.assertEqual(('c6a633f0c2c9e72f7cdf49f888fc64ee7179096c57fdedaad1f'
                          '4ea513dbb7b34'), make_request_token('foo', 'bar'))

    def test_pkcs5_pad(self):
        self.assertEqual(b'\x10' * 16, pkcs5_pad(b''))
        self.assertEqual(b'foo\r\r\r\r\r\r\r\r\r\r\r\r\r', pkcs5_pad(b'foo'))


class SnapchatTestCase(unittest.TestCase):

    def setUp(self):
        responses.reset()
        self.snapchat = Snapchat()

    @responses.activate
    def test_login(self):
        responses.add(responses.POST, URL + 'login',
                      body='{}', status=200,
                      content_type='application/json')
        self.assertEqual({}, self.snapchat.login('eggs', 'spam'))

        responses.reset()
        responses.add(responses.POST, URL + 'login',
                      body='{}', status=404,
                      content_type='application/json')
        self.assertRaises(HTTPError, self.snapchat.login, 'eggs', 'spam')

        responses.reset()
        responses.add(responses.POST, URL + 'login',
                      body='', status=200,
                      content_type='application/json')
        self.assertRaises(ValueError, self.snapchat.login, 'eggs', 'spam')

    @responses.activate
    def test_logout(self):
        responses.add(responses.POST, URL + 'logout',
                      body='', status=200,
                      content_type='application/json')
        self.assertTrue(self.snapchat.logout())

        responses.reset()
        responses.add(responses.POST, URL + 'logout',
                      body='{}', status=404,
                      content_type='application/json')
        self.assertRaises(HTTPError, self.snapchat.logout)

        responses.reset()
        responses.add(responses.POST, URL + 'logout',
                      body='{}', status=200,
                      content_type='application/json')
        self.assertFalse(self.snapchat.logout())


if __name__ == '__main__':
    unittest.main()
