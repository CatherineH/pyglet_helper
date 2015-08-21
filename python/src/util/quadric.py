# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway

from pyglet.gl.glu import *
from pyglet.gl import *

from enum import Enum


class drawing_style(Enum):
    POINT = 1
    LINE = 2
    FILL = 3
    SILHOUETTE = 4


class normal_style(Enum):
    NONE = 1
    FLAT = 2
    SMOOTH = 3


class orientation(Enum):
    OUTSIDE = 1
    INSIDE = 2


class quadric:
    def __init__(self, q=0):
        self.q = gluNewQuadric()
        gluQuadricDrawStyle(self.q, GLU_FILL)
        gluQuadricNormals(self.q, GLU_SMOOTH)
        gluQuadricOrientation(self.q, GLU_OUTSIDE)


    def __del__(self):
        gluDeleteQuadric(self.q)
    
    
    def set_draw_style(self, style):
        if style == drawing_style.POINT:
            gluQuadricDrawStyle(self.q, GLU_POINT)
        elif style == drawing_style.LINE:
            gluQuadricDrawStyle(self.q, GLU_LINE)
        elif style == drawing_style.FILL:
            gluQuadricDrawStyle(self.q, GLU_FILL)
        elif style == drawing_style.SILHOUETTE:
            gluQuadricDrawStyle(self.q, GLU_SILHOUETTE)
    
    
    def set_normal_style(self, style):
        if style == normal_style.NONE:
            gluQuadricNormals(q, GLU_NONE)
        elif style == normal_style.FLAT:
            gluQuadricNormals(q, GLU_FLAT)
        elif style == normal_style.SMOOTH:
            gluQuadricNormals(q, GLU_SMOOTH)
    
    
    def set_orientation(self, side):
        if side == orientation.OUTSIDE:
            gluQuadricOrientation(q, GLU_OUTSIDE)
        else:
            gluQuadricOrientation(q, GLU_INSIDE)
    
    
    def render_sphere(self, radius, slices, stacks):
        gluSphere(self.q, radius, slices, stacks)
    
    
    def render_cylinder(self, base_radius, height, slices, stacks, top_radius=None):
        # GLU orients cylinders along the +z axis, and they must be
        # reoriented along the +x axis for VPython's convention of rendering along
        # the "axis" vector.
        glRotatef(90, 0, 1, 0)
        if top_radius is None:
            gluCylinder(self.q, base_radius, base_radius, height, slices, stacks)
        else:
            gluCylinder(self.q, base_radius, top_radius, height, slices, stacks)
    


    
    def render_disk(self, radius, slices, rings, rotation):
        glRotatef(90, 0, GLfloat(rotation), 0)
        gluDisk(self.q, 0.0, radius, slices, rings)
