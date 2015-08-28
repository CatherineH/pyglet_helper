# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pygletHelper.objects.primitive import primitive
from pygletHelper.util.rgba import rgb
from pygletHelper.util.vector import vector

class rectangular(primitive):
    def __init__(self, other=None, pos= vector(0,0,0),width = 1.0, height = 1.0, length = 1.0, color = rgb()):
        super(rectangular, self).__init__(color = color, pos = pos)
        if other==None:
            self.width = width
            self.height = height
        else:
            self.width = other.width
            self.height = other.height
        self.length = length

    @property
    def length(self):
        return self.axis.mag()
    @length.setter
    def length(self, l):
        if (l < 0):
            raise RuntimeError( "length cannot be negative")
        self.axis = self.axis.norm() * l

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, h):
        if (h < 0):
            raise RuntimeError( "height cannot be negative")
        #self.axis = self.axis.norm() * h
        self._height = h

    @property
    def width(self):
        return self.axis.mag()
    @width.setter
    def width(self, w):
        if (w < 0):
            raise RuntimeError( "width cannot be negative")
        #self.axis = self.axis.norm() * w
        self._width = w

    @property
    def size(self):
        return vector(self.axis.mag(), self.height, self.width)
    @size.setter
    def size(self, s):
        if (s.x < 0):
            raise RuntimeError( "length cannot be negative")
        if (s.y < 0):
            raise RuntimeError( "height cannot be negative")
        if (s.z < 0):
            raise RuntimeError( "width cannot be negative")
        self.axis = self.axis.norm() * s.x
        self.height = s.y
        self.width = s.z

    def apply_transform( self, scene ):
    	# OpenGL needs to invert the modelview matrix to generate the normal matrix,
    	#   so try not to make it singular:
    	min_scale = max( self.axis.mag(), max(self.height,self.width) ) * 1e-6
    	size = vector( max(min_scale,self.axis.mag()), max(min_scale,self.height),\
    			     max(min_scale,self.width) )
    	self.model_world_transform( scene.gcf, self.size ).gl_mult()
