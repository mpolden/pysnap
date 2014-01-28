#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pysnap',
    version='0.1',
    description='Snapchat API client in Python',
    long_description=open('README.md').read(),
    author='Martin Polden',
    author_email='martin.polden@gmail.com',
    url='https://github.com/martinp/pysnap',
    packages=['pysnap'],
    scripts=['bin/get_snaps.py', 'bin/get_stories.py'],
    install_requires=[
        'docopt>=0.6',
        'pycrypto>=2.6',
        'requests>=2.0'
    ],
    license=open('LICENSE').read()
)
