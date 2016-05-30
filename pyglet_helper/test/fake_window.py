"""
The following file contains definitions of the window object when pyglet can't
be used, such as on testing on continuous integration systems.
"""


class Window(object):
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height