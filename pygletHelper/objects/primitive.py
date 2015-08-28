# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pygletHelper.objects.renderable import renderable
from pygletHelper.util.vector import vector
from pygletHelper.util.rgba import rgb
from pygletHelper.util.tmatrix import tmatrix, rotation
from traceback import print_stack
from math import sqrt

def trail_update(obj):
    # trail_update does not detect changes such as ball.pos.x += 1
    # which are detected in create_display/_Interact which looks at trail_list
    if obj.interval == 0: return
    obj.updated = True
    obj.interval_count += 1
    if len(obj.trail_object.pos) == 0:
        obj.trail_object.append(pos=obj.pos)
        obj.interval_count -= 1
    if obj.interval_count == obj.interval:
        if obj.pos != obj.trail_object.pos[-1]:
            obj.trail_object.append(pos=obj.pos, retain=obj.retain)
        obj.interval_count = 0

class primitive(renderable):
    # Generate a displayobject at the origin, with up pointing along +y and
    # an axis = vector(1, 0, 0).
    def __init__(self, axis = vector(1,0,0), up = vector(0,1,0), pos = vector(0,0,0), make_trail = False, trail_initialized = False, obj_initialized = False, other = None, color = rgb()):
        super(primitive, self).__init__(color = color)
        self.startup = True
        self.make_trail = make_trail
        self.trail_initialized = trail_initialized
        self.obj_initialized = obj_initialized
        self.primitive_object = other
        self.obj_initialized = False

        # The position and orientation of the body in World space.
        if other == None:
            # position must be defined first, before the axis
            self.up = vector(up)
            self.pos = vector(pos)
            self.axis = vector(axis)

        else:
            self.up = other.up
            self.pos = other.pos
            self.axis = other.axis


    # Returns a tmatrix that performs reorientation of the object from model
    # orientation to world (and view) orientation.
    def model_world_transform(self, world_scale = 0.0, object_scale = vector(1,1,1) ):
        '''
         Performs scale, rotation, translation, and world scale (gcf) transforms in that order.
         ret = world_scale o translation o rotation o scale
         Note that with the default parameters, only the rotation transformation is returned!  Typical
           usage should be model_world_transform( scene.gcf, my_size );
        '''
        ret = tmatrix()
        # A unit vector along the z_axis.
        z_axis = vector(0,0,1);
        if (abs(self.axis.dot(self.up) / sqrt( self.up.mag2() * self.axis.mag2())) > 0.98):
            # Then axis and up are in (nearly) the same direction: therefore,
            # try two other possible directions for the up vector.
            if (abs(self.axis.norm().dot( vector(-1,0,0))) > 0.98):
                z_axis = self.axis.cross( vector(0,0,1)).norm()
            else:
                z_axis = self.axis.cross( vector(-1,0,0)).norm()
        else:
            z_axis = self.axis.cross( self.up).norm()

        y_axis = z_axis.cross(self.axis).norm()
        x_axis = self.axis.norm()
        ret.x_column( x_axis )
        ret.y_column( y_axis )
        ret.z_column( z_axis )
        ret.w_column( self.pos * world_scale )
        ret.w_row()

        ret.scale( object_scale * world_scale, 1 )

        return ret

    @property
    def typeid(self):
        # See above for PRIMITIVE_TYPEINFO_DECL/IMPL.
        return type(self)

    # Manually overload this member since the default arguments are variables.
    def rotate(self, angle, _axis, origin):
        R = rotation( angle, _axis, origin)
        fake_up = self.up
        if not self.axis.cross( fake_up):
            fake_up = vector( 1,0,0)
            if not self.axis.cross( fake_up):
                fake_up = vector( 0,1,0)
        self.pos = R * self._pos
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
        self._pos = vector(n_pos)
        if (self.trail_initialized and self.make_trail):
            if (self.obj_initialized) :
                trail_update(self.primitive_object)

    @property
    def x(self):
        return self.pos.x
    @x.setter
    def x(self, x):
        self.pos.x = x
        if (self.trail_initialized and self.make_trail):
            if (self.obj_initialized):
                trail_update(self.primitive_object)

    @property
    def y(self):
      return self.pos.y
    @y.setter
    def y(self, y):
      self.pos.y = y
      if (self.trail_initialized and self.make_trail):
        if (self.obj_initialized):
          trail_update(self.primitive_object)

    @property
    def z(self):
      return self.pos.z
    @z.setter
    def z(self, z):
      self.pos.z = z
      if (self.trail_initialized and self.make_trail):
        if (self.obj_initialized):
          trail_update(self.primitive_object)

    @property
    def axis(self):
        try:
            return self._axis
        except:
            return None
    @axis.setter
    def axis(self, n_axis):
        if self.axis is None:
            self._axis = vector(1,0,0)
        if type(n_axis) is not vector:
            n_axis = vector(n_axis)
        a = self.axis.cross(n_axis)
        if (a.mag() == 0.0):
            self._axis = n_axis
        else:
            angle = n_axis.diff_angle(self._axis)
            self._axis = n_axis.mag()*self._axis.norm()
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
        if (x and not self.obj_initialized):
            raise RuntimeError("Can't set make_trail=True unless object was created with make_trail specified")
        if (self.startup):
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
