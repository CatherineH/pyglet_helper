from __future__ import print_function
from pyglet.gl import glEndList, GLException, glCallList, glGenLists, \
    glNewList, GL_COMPILE


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
        self.handle = glGenLists(1)

    def gl_compile_begin(self):
        """ Generates the beginning of the list.
        """
        glNewList(self.handle, GL_COMPILE)

    def gl_compile_end(self):
        """ Generates the end of the list.
        """
        glEndList(self.handle)
        self.built = True

    def gl_render(self):
        """ Call all of the commands in the current list.
        """
        try:
            glCallList(self.handle)
        except GLException as e_msg:
            print("Got GL Exception on call list: " + str(e_msg))
        self.built = True

    @property
    def compiled(self):
        """ Returns whether the current list has beein completed.
        """
        return self.built
