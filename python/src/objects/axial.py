# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from primitive import primitive
from math import pi

# A subbase class used to only export 'radius' as a property once to Python.
class axial(primitive):
    # The radius of whatever body inherits from this class.
    def __init__(self, other = None, radius = 1.0):
        if not other == None:
            self.radius = other.radius
        else:
            self.radius = radius

    @property
    def radius(self):
        return self.radius
    @radius.setter
    def radius(self, r):
        self.radius = r

    @property
    def material_matrix(self):
        out = tmatrix()
        out.translate( vector(.0005,.5,.5) )
        scale = self.scale( self.axis.mag(), self.radius, self.radius )
        out.scale( self.scale * (.999 / max(self.scale.x, self.scale.y*2)) )
        # Undo the rotation inside quadric::render_cylinder() and ::render_disk():
        out = out * self.rotation( +.5*pi, vector(0,1,0) ) # xxx performance
