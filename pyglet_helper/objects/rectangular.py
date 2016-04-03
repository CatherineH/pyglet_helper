"""
pyglet_helper.rectangular contains a base class for drawing objects with
rectangular symmetry
"""

from pyglet_helper.objects import Primitive
from pyglet_helper.util import Rgb, Vector


class Rectangular(Primitive):
    """
    A base class for rectangular-like objects (such as the box or pyramid)
    """
    def __init__(self, axis=Vector([1, 0, 0]), pos=Vector([0, 0, 0]),
                 width=1.0, height=1.0, length=1.0, color=Rgb(), other=None):
        """
        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param pos: The object's position.
        :type pos: pyglet_helper.util.Vector
        :param width: The object's width.
        :type width: float
        :param height: The object's height.
        :type height: float
        :param length: The object's length.
        :type length: float
        """
        super(Rectangular, self).__init__(color=color, pos=pos, axis=axis)
        self._height = None
        self._width = None
        if other is None:
            self.width = width
            self.height = height
        else:
            self.width = other.width
            self.height = other.height
        self.length = length

    @property
    def scale(self):
        """
        Gets the rectangle's scale (defined as its length
        :return: the rectangle's scale
        :rtype: float
        """
        return self.length

    def apply_transform(self, scene):
        """ Scale the object to the correct height, width and length

        :param scene: the object's current view
        :type scene: pyglet_helper.objects.View
        """
        min_scale = max(self.axis.mag(), max(self.height, self.width)) * 1e-6
        self.size = Vector([max(min_scale, self.axis.mag()),
                            max(min_scale, self.height),
                            max(min_scale, self.width)])
        self.model_world_transform(scene.gcf, self.size).gl_mult()
