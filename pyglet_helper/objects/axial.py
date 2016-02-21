from pyglet_helper.objects import Primitive
from math import pi
from pyglet_helper.util import Rgb, Tmatrix, Vector
from pyglet_helper.objects.material import Material


class Axial(Primitive):
    """
    A subclass for all shapes with some radial symmetry around an axis (spheres, cones, etc., ).
    """
    def __init__(self, axis=Vector(1, 0, 0), radius=1.0, color=Rgb(), pos=Vector(0, 0, 0),
                 material=Material(), other=None):
        """

        :param other: another axial object to copy properties from (optional)
        :type other: pyglet_helper.objects.Axial
        :param axis: The axis for the orientation of the object.
        :type axis: pyglet_helper.util.Vector
        :param radius: The object's radius.
        :type radius: float
        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param pos: The object's position.
        :type pos: pyglet_helper.util.Vector
        :param material: The object's material
        :type material: pyglet_helper.util.Material
        """
        super(Axial, self).__init__(color=color, pos=pos, axis=axis, material=material)
        self._radius = None
        if other is not None:
            self.radius = other.radius
        else:
            self.radius = radius

    @property
    def scale(self):
        return self.axis

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, r):
        self._radius = r

    @property
    def material_matrix(self):
        out = Tmatrix()
        out.translate(Vector(.0005, .5, .5))
        scale = self.scale(self.axis.mag(), self.radius, self.radius)
        out.scale(self.scale * (.999 / max(self.scale.x, self.scale.y * 2)))
        # Undo the rotation inside quadric::render_cylinder() and ::render_disk():]
        out_vector = Vector(0, 1, 0)
        out_vector = out_vector.rotate(angle=.5*pi)
        out = out * out_vector
        return out
