# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from objects.sphere import sphere
class ellipsoid(sphere):
    def __init__(self, height = 1.0, width = 1.0):
        self.height = height
        self.width = width

    @property
    def length(self):
        return self.axis.mag()
    @length.setter
    def length(self, l):
        if (l < 0):
            raise ValueError( "length cannot be negative")
        self.axis = self.axis.norm() * l

    @property
    def height(self):
        return self.height
    @height.setter
    def height(self, h):
        if (h < 0):
            raise ValueError( "height cannot be negative")
        self.height = h

    @property
    def width(self):
        return self.width
    @width.setter
    def width(self, w):
        if (w < 0):
            raise ValueError( "width cannot be negative")
        self.width = w

    @property
    def size(self):
        return vector(self.axis.mag(), self.height, self.width)
    @size.setter
    def size( self, s):
        if (s.x < 0):
            raise ValueError( "length cannot be negative")
        if (s.y < 0):
            raise ValueError( "height cannot be negative")
        if (s.z < 0):
            raise ValueError( "width cannot be negative")
        self.axis = self.axis.norm() * s.x
        self.height = s.y
        self.width = s.z

    @property
    def scale(self):
        return vector( self.axis.mag(), self.height, self.width)*0.5

    def degenerate(self):
        return not self.visible or self.height == 0.0 or self.width == 0.0 or self.axis.mag() == 0.0

    def grow_extent(self, world):
        if self.degenerate():
            return
        # TODO: not accurate (overestimates extent)
        s = vector(self.axis.mag(),self.height,self.width)*0.5
        world.add_box( self.model_world_transform(1.0), -s, s )
        world.add_body()
