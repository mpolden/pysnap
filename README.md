pysnap
======
Implementation of Snapchat API in Python. Partially based on
https://github.com/dstelljes/php-snapchat

Dependencies
------------

    pip install -r requirements.txt

Usage
-----

    $ python pysnap/get_snaps.py -h
    Basic Snapchat client

    Usage:
      get_snaps.py [-q] -u <username> [-p <password>] <path>

    Options:
      -h --help                 Show usage
      -q --quiet                Suppress output
      -u --username=<username>  Username
      -p --password=<password>  Password (optional, will prompt if omitted)
