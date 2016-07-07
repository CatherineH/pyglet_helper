"""
The following file contains definitions of the window object when pyglet can't
be used, such as on testing on continuous integration systems.
"""
from __future__ import print_function, division, absolute_import

class Window(object):
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height

    def event(self, func):
        def decorator(func):
            return func
        return decorator