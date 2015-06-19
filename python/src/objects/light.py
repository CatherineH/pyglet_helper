# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *

from renderable import renderable

class light(renderable):
    def __init__(self):
	    self.rgb = rgb()
        #is get_vertex an opengl thing?
        self.vertex = get_vertex(self.gcf)

    @property
    def rgb(self):
        return self.color
    @rgb.self
    def rgb(self, r):
        self.color = r

    # renderable protocol
	#def outer_render(self, view):

    @property
	def center(self):
        return vector()

    @property
    def material(self):
        raise ValueError("light object does not have a material.")
    @material.setter
    def material(self, mat):
        raise ValueError("light object does not have a material.")

    def is_light(self):
        return True

    def render_lights(self, v):
        v.light_count[0] += 1
	    p = get_vertex( v.gcf )
        for d in range(0,4):
            v.light_pos.push_back(p[d])
	    for d in range(0,3):
            v.light_color.push_back(color[d])
	    v.light_color.push_back( 1.0 )

class local_light(light):
    def __init__(self):
	    self.position = vector()

	def get_vertex(self, gcf):
        return vertex( self.position*gcf, 1.0 )

    @property
    def position(self):
        return self.position
    @position.setter
    def position(self, v):
        self.position = v

class distant_light(light) :
    def __init__(self):
        self.direction = vector()

    @property
    def vertex(self):
        return vertex( self.direction, 0.0 )

    @property
	def direction(self):
        return self.direction
    @direction.setter
    def direction(self, v):
        self.direction = v.norm()
