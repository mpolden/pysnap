#!/usr/bin/env python

"""Basic Snapchat client

Usage:
  get_snaps.py -u <username> [-p <password> -q] <path>

Options:
  -h --help                 Show usage
  -q --quiet                Suppress output
  -u --username=<username>  Username
  -p --password=<password>  Password (optional, will prompt if omitted)

"""
from __future__ import print_function

import os.path
import sys
from getpass import getpass
import base64

from docopt import docopt

from pysnap import get_file_extension, Snapchat


def main():
    arguments = docopt(__doc__)
    quiet = arguments['--quiet']
    username = arguments['--username']
    if arguments['--password'] is None:
        password = getpass('Password:')
    else:
        password = arguments['--password']
    path = arguments['<path>']

    if not os.path.isdir(path):
        print('No such directory: {0}'.format(arguments['<path>']))
        sys.exit(1)

    s = Snapchat()
    if not s.login(username, password).get('logged'):
        print('Invalid username or password')
        sys.exit(1)

    for snap in s.get_friend_stories():
        filename = '{0}_{1}.{2}'.format(snap['sender'], snap['id'],
                                        get_file_extension(snap['media_type']))
        abspath = os.path.abspath(os.path.join(path, filename))
        if os.path.isfile(abspath):
            continue
        data = s.get_story_blob(snap['media_id'],
                                base64.b64decode(snap['media_key']),
                                base64.b64decode(snap['media_iv']))
        if data is None:
            continue
        with open(abspath, 'wb') as f:
            f.write(data)
            if not quiet:
                print('Saved: {0}'.format(abspath))


if __name__ == '__main__':
    main()
