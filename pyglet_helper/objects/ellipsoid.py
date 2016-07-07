"""
pyglet_helper.ellipsoid contains an object for drawing an ellipsoid
"""
from __future__ import print_function, division, absolute_import

from . import Sphere
from ..util import Rgb, Vector


class Ellipsoid(Sphere):
    """
    An Ellipsoid object
    """
    def __init__(self, height=1.0, width=1.0, length=1.0, color=Rgb(),
                 pos=Vector([0, 0, 0]), axis=Vector([1.0, 0.0, 0.0]), make_trail=False,
                 trail_type='curve', interval=1, retain=-1):
        """

        :param width: The ellipsoid's width.
        :type width: float
        :param height: The ellipsoid's height.
        :type height: float
        :param length: The ellipsoid's length.
        :type length: float
        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param pos: The object's position.
        :type pos: pyglet_helper.util.Vector
        """
        super(Ellipsoid, self).__init__(color=color, pos=pos, axis=axis,
                                        make_trail=make_trail, trail_type=trail_type,
                                        interval=interval, retain=retain)
        self._height = None
        self._width = None
        self.height = height
        self.width = width
        self.length = length


    @property
    def scale(self):
        """
        Gets the scaling factor of the ellipsoid (1/2 of the size)
        :return: the scaling factors
        :rtype: pyglet_helper.util.Vector
        """
        return Vector([self.axis.mag(), self.height, self.width]) * 0.5

    @property
    def degenerate(self):
        """
        True if the scale in any dimension is zero, or if the object is not
        visible.
        :return: whether the object is degenerate
        :rtype: bool
        """
        return not self.visible or self.height == 0.0 or self.width == 0.0 or \
               self.axis.mag() == 0.0
