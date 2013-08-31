#!/usr/bin/env python

import unittest
from pysnap import make_request_token, is_image, is_video, pkcs5_pad


class Snapchat(unittest.TestCase):

    def test_make_request_token(self):
        self.assertEqual(('c6a633f0c2c9e72f7cdf49f888fc64ee7179096c57fdedaad1f'
                          '4ea513dbb7b34'), make_request_token('foo', 'bar'))

    def test_is_image(self):
        self.assertFalse(is_image([]))
        self.assertFalse(is_image([None]))
        self.assertFalse(is_image([None, None]))
        self.assertTrue(is_image([chr(0xFF), chr(0xD8)]))

    def test_is_video(self):
        self.assertFalse(is_video([]))
        self.assertFalse(is_video([None]))
        self.assertFalse(is_video([None, None]))
        self.assertTrue(is_video([chr(0x00), chr(0x00)]))

    def test_pkcs5_pad(self):
        self.assertEqual('\x10' * 16, pkcs5_pad(''))
        self.assertEqual('foo\r\r\r\r\r\r\r\r\r\r\r\r\r', pkcs5_pad('foo'))


if __name__ == '__main__':
    unittest.main()
