""" pyglet_helper.util.texture contains objects for describing textures to
apply to objects
"""
from pyglet.gl import glBindTexture, glDeleteTextures, GL_TEXTURE_2D


class Texture(object):
    """
    A class to assist in managing OpenGL texture resources.
    """
    def __init__(self, damaged=False, handle=0, opacity=False):
        self._have_opacity = None
        self.damaged = damaged
        self.handle = handle
        # A unique identifier for the texture, to be obtained from
        # glGenTextures().
        self._opacity = opacity

    @property
    def opacity(self):
        return self._have_opacity

    @opacity.setter
    def opacity(self, opacity):
        self._have_opacity = opacity

    def gl_activate(self):
        """
        Make this texture active.  This function constitutes use under the
            "initialize on first use" rule, and will incur a one-time speed and
            continuous graphics memory penalty.  Precondition: an OpenGL
            context must be active.
        """
        if self.damaged:
            self.damaged = False
        if not self.handle:
            return

        glBindTexture(GL_TEXTURE_2D, self.handle)

    def gl_free(self):
        """
        Returns e.g. GL_TEXTURE_2D - the thing to be enabled to make this
            texture work with the fixed function pipeline.
        """
        print("Deleting texture number " + self.handle)
        glDeleteTextures(1, self.handle)
        # Mutable subclasses must call this function whenever their texture
        # data

    # needs to be reloaded into OpenGL.
    def damage(self):
        self.damaged = True
