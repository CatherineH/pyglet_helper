"""
pyglet_helper.primitive contains objects and methods related to drawing all
geometric shapes
"""
from pyglet_helper.objects import Material, Renderable
from pyglet_helper.util import Rgb, rotation, Tmatrix, Vector



class Primitive(Renderable):
    """
     A base class for all geometric shapes.
    """
    def __init__(self, axis=Vector([1, 0, 0]), up_vector=Vector([0, 1, 0]),
                 pos=Vector([0, 0, 0]), obj_initialized=False, color=Rgb(),
                 material=Material()):
        """

        :param axis: The orientation to use when drawing.
        :type axis: pyglet_helper.util.Vector
        :param up_vector: A vector that points to the current up direction in
        the view.
        :type up_vector: pyglet_helper.util.Vector
        :param pos: The object's position.
        :type pos: pyglet_helper.util.Vector
        :param obj_initialized: If True, the object has been initialized
        :type obj_initialized: bool
        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param material: The object's material
        :type material: pyglet_helper.util.Material
        """
        super(Primitive, self).__init__(color=color, mat=material)
        self._axis = None
        self._pos = None
        self._up = None
        self._width = None
        self._height = None

        self.startup = True
        self.obj_initialized = obj_initialized

        # position must be defined first, before the axis
        self.up_vector = Vector(up_vector)
        self.pos = Vector(pos)
        self.axis = Vector(axis)

    def model_world_transform(self, world_scale=0.0,
                              object_scale=Vector([1, 1, 1])):
        """Performs scale, rotation, translation, and world scale (gcf)
        transforms in that order.

        :param world_scale: The global scaling factor.
        :type world_scale: float
        :param object_scale: The scaling to applied to this specific object
        :type object_scale: pyglet_helper.util.Vector
        :rtype: pyglet_helper.util.Tmatrix
        :returns:  Returns a tmatrix that performs reorientation of the object
        from model orientation to world
         (and view) orientation.
        """
        ret = Tmatrix()
        # A unit vector along the z_axis.
        z_axis = Vector([0, 0, 1])
        if abs(self.axis.dot(self.up_vector) / self.up_vector.mag()**2.0) \
                > 0.98:
            # Then axis and up are in (nearly) the same direction: therefore,
            # try two other possible directions for the up vector.
            if abs(self.axis.norm().dot(Vector([-1, 0, 0]))) > 0.98:
                z_axis = self.axis.cross(Vector([0, 0, 1])).norm()
            else:
                z_axis = self.axis.cross(Vector([-1, 0, 0])).norm()
        else:
            z_axis = self.axis.cross(self.up_vector).norm()

        y_axis = z_axis.cross(self.axis).norm()
        x_axis = self.axis.norm()
        ret.x_column(x_axis)
        ret.y_column(y_axis)
        ret.z_column(z_axis)
        w_column = world_scale*self.pos
        ret.w_column(w_column)
        ret.w_row()

        ret.scale(object_scale * world_scale, 1)

        return ret

    def rotate(self, angle, axis, origin):
        """Rotate the primitive's axis by angle about a specified axis at a
        specified origin.

        :param angle: the angle to rotate by, in radians
        :type angle: float
        :param axis: The axis to rotate around.
        :type axis: pyglet_helper.util.Vector
        :param origin: The center of the axis of rotation.
        :type origin: pyglet_helper.util.Vector
        """
        rotation_matrix = rotation(angle, axis, origin)
        fake_up = self.up_vector
        if not self.axis.cross(fake_up):
            fake_up = Vector([1, 0, 0])
            if not self.axis.cross(fake_up):
                fake_up = Vector([0, 1, 0])
        # is this rotation needed at present? Is it already included in the
        # transformation matrix?
        #self.pos = R * self._pos
        self.up_vector = rotation_matrix.times_v(fake_up)
        self._axis = rotation_matrix.times_v(self._axis)

    @property
    def center(self):
        """
        Gets the object's center
        :return: the object's center, as a vector
        :rtype: pyglet_helper.util.Vector
        """
        return self.pos

    @property
    def pos(self):
        """
        Get the object's current position
        :return: the object's position
        :rtype: pyglet_helper.util.Vector
        """
        return self._pos

    @pos.setter
    def pos(self, n_pos):
        """
        Set the object's position with a Vector
        :param n_pos: a vector with the object's new position
        :type n_pos: pyglet_helper.util.Vector
        :return:
        """
        self._pos = Vector(n_pos)

    @property
    def length(self):
        """
        Get the object's length (for most objects, this is the magnitude of
        its axis)
        :return: the object's length
        :rtype: float
        """
        return self.axis.mag()

    @length.setter
    def length(self, new_length):
        """
        Set the object's length
        :param new_length: the new length of the object
        :type new_length: float
        :return:
        """
        if new_length < 0:
            raise ValueError("length cannot be negative")
        self.axis = self.axis.norm() * new_length

    @property
    def height(self):
        """
        Gets the scale of the object along the y axis
        :return: the object's scale along the y axis
        :rtype: float
        """
        return self._height

    @height.setter
    def height(self, new_height):
        """
        Sets the scale of the object along the y axis
        :param new_height: the object's scale along the y axis
        :type new_height: float
        """
        if new_height < 0:
            raise ValueError("height cannot be negative")
        self._height = new_height

    @property
    def width(self):
        """
        Gets the scale of the object along the z axis
        :return: the object's scale along the z axis
        :rtype: float
        """
        return self._width

    @width.setter
    def width(self, new_width):
        """
        Sets the scale of the object along the z axis
        :param new_width: the object's scale along the y axis
        :type new_width: float
        """
        if new_width < 0:
            raise ValueError("width cannot be negative")
        self._width = new_width

    @property
    def size(self):
        """
        Gets a vector with the object's scale along the x, y, and z axes
        :return: a vector with the scales
        :rtype: pyglet_helper.util.Vector
        """
        return Vector([self.axis.mag(), self.height, self.width])

    @size.setter
    def size(self, new_size):
        """
        Sets the object's scale along the x, y, and z axes
        :param new_size: the new scales, in a vector
        :type new_size: pyglet_helper.util.Vector
        """
        if new_size.x_component < 0:
            raise ValueError("length cannot be negative")
        if new_size.y_component < 0:
            raise ValueError("height cannot be negative")
        if new_size.z_component < 0:
            raise ValueError("width cannot be negative")
        self.axis = self.axis.norm() * new_size.x_component
        self.height = new_size.y_component
        self.width = new_size.z_component

    @property
    def axis(self):
        """
        Get the object's axis, which defines the orientation and size of the
        object
        :return: the object's axis
        :rtype; pyglet_helper.util.Vector
        """
        return self._axis

    @axis.setter
    def axis(self, n_axis):
        """
        Set the object's axis, as a vector
        :param n_axis: the new axis
        :type n_axis: pyglet_helper.util.Vector
        """
        if self.axis is None:
            self._axis = Vector([1, 0, 0])
        _axis = self.axis.cross(n_axis)
        if _axis.mag() == 0.0:
            self._axis = n_axis
        else:
            angle = n_axis.diff_angle(self._axis)
            self._axis = n_axis.mag() * self._axis.norm()
            self.rotate(angle, _axis, self.pos)

    @property
    def up_vector(self):
        """
        Get the object's up axis
        :return: the object's up axis
        :rtype: pyglet_helper.util.Vector
        """
        return self._up

    @up_vector.setter
    def up_vector(self, n_up):
        """
        Set the object's up axis
        :param n_up: the object's up axis
        :type n_up: pyglet_helper.util.Vector
        """
        self._up = n_up

    @property
    def is_light(self):
        """
        Returns false if the object is not a light. By default,
        all primitives are not lights
        :return: whether the object is a light
        :rtype: bool
        """
        return False
