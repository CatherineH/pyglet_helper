# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pygletHelper.objects.primitive import Primitive
from math import pi
from pygletHelper.util.rgba import Rgb
from pygletHelper.util.vector import Vector
from pygletHelper.util.tmatrix import Tmatrix

from pygletHelper.objects.material import Material

# A subbase class used to only export 'radius' as a property once to Python.
class Axial(Primitive):
    # The radius of whatever body inherits from this class.
    def __init__(self, other=None, axis=Vector(1, 0, 0), radius=1.0, color=Rgb(), pos=Vector(0, 0, 0), material=Material()):
        super(Axial, self).__init__(color=color, pos=pos, axis=axis, material=material)
        self._radius = None
        if other is not None:
            self.radius = other.radius
        else:
            self.radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, r):
        self._radius = r

    @property
    def material_matrix(self):
        out = tmatrix()
        out.translate(vector(.0005, .5, .5))
        scale = self.scale(self.axis.mag(), self.radius, self.radius)
        out.scale(self.scale * (.999 / max(self.scale.x, self.scale.y * 2)))
        # Undo the rotation inside quadric::render_cylinder() and ::render_disk():
        out = out * self.rotation(+.5 * pi, vector(0, 1, 0))  # xxx performance
