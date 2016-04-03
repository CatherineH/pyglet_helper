""" pyglet_helper.display_list contains a class for generating lists of
objects to render to the screen
"""
from __future__ import print_function
try:
    import pyglet.gl
except Exception as error_msg:
    print("Pyglet import error: "+str(error_msg))


class DisplayList(object):
    """
    A class for storing the OpenGl commands for rendering an object.
    """
    def __init__(self, built=False):
        """
        :param built: If True, the commands have been executed
        :type built: bool
        """
        self.built = built
        self.handle = pyglet.gl.glGenLists(1)

    def gl_compile_begin(self):
        """ Generates the beginning of the list.
        """
        pyglet.gl.glNewList(self.handle, pyglet.gl.GL_COMPILE)

    def gl_compile_end(self):
        """ Generates the end of the list.
        """
        pyglet.gl.glEndList(self.handle)
        self.built = True

    def gl_render(self):
        """ Call all of the commands in the current list.
        """
        try:
            pyglet.gl.glCallList(self.handle)
        except pyglet.gl.GLException as e_msg:
            print("Got GL Exception on call list: " + str(e_msg))
        self.built = True

    @property
    def compiled(self):
        """ Returns whether the current list has beein completed.
        """
        return self.built
