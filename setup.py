#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python setup.py file for the pyglet_helper project
"""

# IMPORTS ####################################################################

import codecs
import os
import re

from setuptools import setup, find_packages

# SETUP VALUES ###############################################################

NAME = "pyglet_helper"
PACKAGES = find_packages()
META_PATH = os.path.join("pyglet_helper", "__init__.py")
INSTALL_REQUIRES = ['enum34', 'numpy', 'pyglet']

# HELPER FUNCTONS ############################################################

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()

META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


# MAIN #######################################################################

def main():
    setup(
        name=find_meta("title"),
        version=find_meta("version"),
        url=find_meta("uri"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        packages=PACKAGES,
        description=find_meta("description"),
        install_requires=INSTALL_REQUIRES,
        package_data = {"pyglet_helper": ['common/library.txt']}
    )

if __name__ == "__main__":
    main()
