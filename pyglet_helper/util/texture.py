# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway

def next_power_of_two(arg):
    ret = 2
    # upper bound of 28 chosen to limit memory growth to about 256MB, which is
    # _much_ larger than most supported textures
    while ret < arg and ret < (1 << 28):
        ret <<= 1
    return ret


'''
A class to assist in managing OpenGL texture resources.
'''


class Texture(object):
    def __init__(self, damaged=False, handle=0, have_opacity=False):
        self._have_opacity = None
        self.damaged = damaged
        self.handle = handle
        # A unique identifier for the texture, to be obtained from glGenTextures().
        self.have_opacity = have_opacity

    @property
    def have_opacity(self):
        return self._have_opacity

    @have_opacity.setter
    def have_opacity(self, opacity):
        self._have_opacity = opacity

    def gl_activate(self, v):
        """
        Make this texture active.  This function constitutes use under the
            "initialize on first use" rule, and will incur a one-time speed and
            continuous graphics memory penalty.  Precondition: an OpenGL context
            must be active.
        """
        self.damage_check()
        if self.damaged:
            gl_init(v)
            self.damaged = False
            check_gl_error()
        if not self.handle:
            return

        glBindTexture(self.enable_type(), self.handle)
        self.gl_transform()
        check_gl_error()

    def gl_free(self, _handle):
        """
        Returns e.g. GL_TEXTURE_2D - the thing to be enabled to make this texture
            work with the fixed function pipeline.
        """
        print("Deleting texture number " + _handle)
        glDeleteTextures(1, _handle)
        # Mutable subclasses must call this function whenever their texture data

    # needs to be reloaded into OpenGL.
    def damage(self):
        self.damaged = True
