#!/usr/bin/env python

import unittest

from pysnap import is_image, is_video
from pysnap.utils import make_request_token, pkcs5_pad


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


if __name__ == '__main__':
    unittest.main()
