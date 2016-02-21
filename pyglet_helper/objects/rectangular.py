from pyglet_helper.objects import Primitive
from pyglet_helper.util import Rgb, Vector


class Rectangular(Primitive):
    """
    A base class for rectangular-like objects (such as the box or pyramid)
    """
    def __init__(self, other=None, pos=Vector(0, 0, 0), width=1.0, height=1.0, length=1.0, color=Rgb()):
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
        super(Rectangular, self).__init__(color=color, pos=pos)
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
        return self.length

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, h):
        if h < 0:
            raise RuntimeError("height cannot be negative")
        self._height = h

    @property
    def width(self):
        return self.axis.mag()

    @width.setter
    def width(self, w):
        if w < 0:
            raise RuntimeError("width cannot be negative")
        self._width = w

    @property
    def size(self):
        return Vector(self.axis.mag(), self.height, self.width)

    @size.setter
    def size(self, s):
        if s.x < 0:
            raise RuntimeError("length cannot be negative")
        if s.y < 0:
            raise RuntimeError("height cannot be negative")
        if s.z < 0:
            raise RuntimeError("width cannot be negative")
        self.axis = self.axis.norm() * s.x
        self.height = s.y
        self.width = s.z

    def apply_transform(self, scene):
        """ Scale the object to the correct height, width and length

        :param scene: the object's current view
        :type scene: pyglet_helper.objects.View
        """
        min_scale = max(self.axis.mag(), max(self.height, self.width)) * 1e-6
        self.size = Vector(max(min_scale, self.axis.mag()), max(min_scale, self.height), max(min_scale, self.width))
        self.model_world_transform(scene.gcf, self.size).gl_mult()
