from pyglet.gl import *
from pyglet_helper.objects import Material, Renderable
from pyglet_helper.util import Rgb, rotation, Tmatrix, Vector
from math import sqrt


def trail_update(obj):
    # trail_update does not detect changes such as ball.pos.x += 1
    # which are detected in create_display/_Interact which looks at trail_list
    if obj.interval == 0:
        return
    obj.updated = True
    obj.interval_count += 1
    if len(obj.trail_object.pos) == 0:
        obj.trail_object.append(pos=obj.pos)
        obj.interval_count -= 1
    if obj.interval_count == obj.interval:
        if obj.pos != obj.trail_object.pos[-1]:
            obj.trail_object.append(pos=obj.pos, retain=obj.retain)
        obj.interval_count = 0


class Primitive(Renderable):
    # Generate a displayobject at the origin, with up pointing along +y and
    # an axis = vector(1, 0, 0).
    def __init__(self, axis=Vector(1, 0, 0), up=Vector(0, 1, 0), pos=Vector(0, 0, 0), make_trail=False,
                 trail_initialized=False, obj_initialized=False, other=None, color=Rgb(), material=Material()):
        super(Primitive, self).__init__(color=color, mat=material)
        self._axis = None
        self._pos = None
        self._up = None
        self._make_trail = None
        self._primitive_object = None

        self.startup = True
        self.make_trail = make_trail
        self.trail_initialized = trail_initialized
        self.obj_initialized = obj_initialized
        self.primitive_object = other
        self.obj_initialized = False

        # The position and orientation of the body in World space.
        if other is None:
            # position must be defined first, before the axis
            self.up = Vector(up)
            self.pos = Vector(pos)
            self.axis = Vector(axis)

        else:
            self.up = other.up
            self.pos = other.pos
            self.axis = other.axis

    # Returns a tmatrix that performs reorientation of the object from model
    # orientation to world (and view) orientation.
    def model_world_transform(self, world_scale=0.0, object_scale=Vector(1, 1, 1)):
        """
         Performs scale, rotation, translation, and world scale (gcf) transforms in that order.
         ret = world_scale o translation o rotation o scale
         Note that with the default parameters, only the rotation transformation is returned!  Typical
           usage should be model_world_transform( scene.gcf, my_size );
        """
        ret = Tmatrix()
        # A unit vector along the z_axis.
        z_axis = Vector(0, 0, 1)
        if abs(self.axis.dot(self.up) / self.up.mag()**2.0) > 0.98:
            # Then axis and up are in (nearly) the same direction: therefore,
            # try two other possible directions for the up vector.
            if abs(self.axis.norm().dot(Vector(-1, 0, 0))) > 0.98:
                z_axis = self.axis.cross(Vector(0, 0, 1)).norm()
            else:
                z_axis = self.axis.cross(Vector(-1, 0, 0)).norm()
        else:
            z_axis = self.axis.cross(self.up).norm()

        y_axis = z_axis.cross(self.axis).norm()
        x_axis = self.axis.norm()
        ret.x_column(x_axis)
        ret.y_column(y_axis)
        ret.z_column(z_axis)
        ret.w_column(self.pos * world_scale)
        ret.w_row()

        ret.scale(object_scale * world_scale, 1)

        return ret

    @property
    def typeid(self):
        # See above for PRIMITIVE_TYPEINFO_DECL/IMPL.
        return type(self)

    # Manually overload this member since the default arguments are variables.
    def rotate(self, angle, _axis, origin):
        R = rotation(angle, _axis, origin)
        fake_up = self.up
        if not self.axis.cross(fake_up):
            fake_up = Vector(1, 0, 0)
            if not self.axis.cross(fake_up):
                fake_up = Vector(0, 1, 0)
        # is this rotation needed at present? Is it already included in the transformation matrix?
        #self.pos = R * self._pos
        self.up = R.times_v(fake_up)
        self._axis = R.times_v(self._axis)

    @property
    def center(self):
        # Used when obtaining the center of the body.
        return self.pos

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, n_pos):
        self._pos = Vector(n_pos)
        if self.trail_initialized and self.make_trail:
            if self.obj_initialized:
                trail_update(self.primitive_object)

    @property
    def x(self):
        return self.pos.x

    @x.setter
    def x(self, x):
        self.pos.x = x
        if self.trail_initialized and self.make_trail:
            if self.obj_initialized:
                trail_update(self.primitive_object)

    @property
    def y(self):
        return self.pos.y

    @y.setter
    def y(self, y):
        self.pos.y = y
        if self.trail_initialized and self.make_trail:
            if self.obj_initialized:
                trail_update(self.primitive_object)

    @property
    def z(self):
        return self.pos.z

    @z.setter
    def z(self, z):
        self.pos.z = z
        if self.trail_initialized and self.make_trail:
            if self.obj_initialized:
                trail_update(self.primitive_object)

    @property
    def axis(self):
        try:
            return self._axis
        except Exception as e:
            print "caught exception: "+str(e)
            return None

    @axis.setter
    def axis(self, n_axis):
        if self.axis is None:
            self._axis = Vector(1, 0, 0)
        if type(n_axis) is not Vector:
            n_axis = Vector(n_axis)
        a = self.axis.cross(n_axis)
        if a.mag() == 0.0:
            self._axis = n_axis
        else:
            angle = n_axis.diff_angle(self._axis)
            self._axis = n_axis.mag() * self._axis.norm()
            self.rotate(angle, a, self.pos)

    @property
    def up(self):
        return self._up

    @up.setter
    def up(self, n_up):
        self._up = n_up

    @property
    def red(self):
        return self.color.red

    @red.setter
    def red(self, x):
        self.color.red = x

    @property
    def green(self):
        return self.color.green

    @green.setter
    def green(self, x):
        self.color.green = x

    @property
    def blue(self):
        return self.color.blue

    @blue.setter
    def blue(self, x):
        self.color.blue = x

    @property
    def make_trail(self):
        return self._make_trail

    @make_trail.setter
    def make_trail(self, x):
        if x and not self.obj_initialized:
            raise RuntimeError("Can't set make_trail=True unless object was created with make_trail specified")
        if self.startup:
            self.startup = False
        self._make_trail = x
        self.trail_initialized = False

    @property
    def primitive_object(self):
        return self._primitive_object

    @primitive_object.setter
    def primitive_object(self, x):
        self._primitive_object = x
        self.obj_initialized = True
