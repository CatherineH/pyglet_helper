# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *

from pyglet_helper.objects.renderable import Renderable
from pyglet_helper.util.rgba import Rgb
from pyglet_helper.util.vector import Vector
import abc


class Light(Renderable):
    def __init__(self, color=Rgb(), specular=(.5, .5, 1, 0.5), diffuse=(1, 1, 1, 1), position=(1, 0.5, 1, 0)):
        super(Light, self).__init__(color=color)
        self.color = None
        self.rgb = color
        self.specular = (GLfloat * 4)(*specular)
        self.diffuse = (GLfloat * 4)(*diffuse)
        self.position = (GLfloat * 4)(*position)

    @property
    def rgb(self):
        return self.color

    @rgb.setter
    def rgb(self, r):
        self.color = r

    @property
    def center(self):
        return Vector()

    @property
    def material(self):
        raise ValueError("light object does not have a material.")

    @material.setter
    def material(self, mat):
        raise ValueError("light object does not have a material.")

    def is_light(self):
        return True

    def render(self, v):
        v.lights.append(self)
        v.draw_lights()

    @abc.abstractmethod
    def get_vertex(self, gcf):
        return 0


class LocalLight(Light):
    def __init__(self, position=Vector(), color=Rgb()):
        super(LocalLight, self).__init__(color=color)
        self.position = position

    def get_vertex(self, gcf):
        return vertex(self.position * gcf, 1.0)

    @property
    def position(self):
        return self.position

    @position.setter
    def position(self, v):
        self.position = v


class DistantLight(Light):
    def __init__(self, direction=Vector(), color=Rgb()):
        super(DistantLight, self).__init__(color=color)
        self.direction = direction

    @property
    def vertex(self):
        return Vertex(self.direction, 0.0)

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, v):
        v = Vector(v)
        self._direction = v.norm()

    def get_vertex(self, gcf):
        return Vertex(direction, 0.0)
