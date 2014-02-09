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
from zipfile import is_zipfile, ZipFile

from docopt import docopt

from pysnap import get_file_extension, Snapchat


def process_snap(s, snap, path, quiet=False):
    filename = '{0}_{1}.{2}'.format(snap['sender'], snap['id'],
                                    get_file_extension(snap['media_type']))
    abspath = os.path.abspath(os.path.join(path, filename))
    if os.path.isfile(abspath):
        return
    data = s.get_blob(snap['id'])
    if data is None:
        return
    with open(abspath, 'wb') as f:
        f.write(data)
        if not quiet:
            print('Saved: {0}'.format(abspath))

    if is_zipfile(abspath):
        zipped_snap = ZipFile(abspath)
        unzip_dir = os.path.join(path, '{0}_{1}'.format(snap['sender'],
                                                        snap['id']))
        zipped_snap.extractall(unzip_dir)
        if not quiet:
            print('Unzipped {0} to {1}'.format(filename, unzip_dir))


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

    for snap in s.get_snaps():
        process_snap(s, snap, path, quiet)


if __name__ == '__main__':
    main()
