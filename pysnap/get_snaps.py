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
from docopt import docopt
from getpass import getpass
from pysnap import Snapchat

if __name__ == '__main__':
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

    s = Snapchat(username, password)
    if not s.login().get('logged'):
        print('Invalid username or password')
        sys.exit(1)

    for snap in s.get_updates()['snaps']:
        data = s.get_blob(snap['id'])
        if data is None:
            continue
        filename = '{user}_{id}.jpg'.format(user=snap['sn'], id=snap['id'])
        abspath = os.path.abspath(os.path.join(path, filename))
        with open(abspath, 'w') as f:
            f.write(data)
            if not quiet:
                print('Saved: {0}'.format(abspath))
