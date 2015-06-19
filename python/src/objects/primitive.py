# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *

class primitive(renderable):
	# Generate a displayobject at the origin, with up pointing along +y and
	# an axis = vector(1, 0, 0).
	def __init__(self, axis = vector(1,0,0), up = vector(0,1,0), pos = vector(0,0,0), make_trail = False, trail_initialized = False, obj_initialized = False, other = None):
		# The position and orientation of the body in World space.
		if other == None:
			self.axis = axis
			self.up = up
			self.pos = pos
		else:
			self.axis = other.axis
			self.up = other.up
			self.pos = other.pos

		self.make_trail = make_trail
		self.trail_initialized = trail_initialized
		self.obj_initialized = obj_initialized
		self.primitive_object = other
		self.obj_initialized = False

	# Returns a tmatrix that performs reorientation of the object from model
	# orientation to world (and view) orientation.
	def model_world_transform(self, world_scale = 0.0, object_scale = vector(1,1,1) ):
		'''
		 Performs scale, rotation, translation, and world scale (gcf) transforms in that order.
		 ret = world_scale o translation o rotation o scale
		 Note that with the default parameters, only the rotation transformation is returned!  Typical
		   usage should be model_world_transform( scene.gcf, my_size );
		'''
		tmatrix ret;
		# A unit vector along the z_axis.
		z_axis = vector(0,0,1);
		if (fabs(self.axis.dot(up) / sqrt( self.up.mag2() * self.axis.mag2())) > 0.98):
			# Then axis and up are in (nearly) the same direction: therefore,
			# try two other possible directions for the up vector.
			if (fabs(self.axis.norm().dot( vector(-1,0,0))) > 0.98):
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

		ret.scale( self.object_scale * world_scale )

		return ret

	# See above for PRIMITIVE_TYPEINFO_DECL/IMPL.
	virtual const std::type_info& get_typeid() const

	# Used when obtaining the center of the body.
	virtual vector get_center() const


	# Manually overload this member since the default arguments are variables.
    def rotate(self, angle, _axis, origin):
		R = rotation( angle, _axis, origin)
		fake_up = self.up
		if (!self.axis.cross( fake_up)):
			fake_up = vector( 1,0,0)
			if (!self.axis.cross( fake_up)):
				fake_up = vector( 0,1,0)
	    self.pos = R * self.pos
	    self.axis = R.times_v(self.axis)
	    self.up = R.times_v(fake_up)

	@property
	def pos(self):
		return self.pos
	@pos.setter
	def pos(self, n_pos):
		self.pos = n_pos;
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
		return self.axis
	@axis.setter
	def axis(self, n_axis):
		a = self.axis.cross(n_axis)
		if (a.mag() == 0.0):
			self.axis = n_axis;
		else:
			angle = n_axis.diff_angle(self.axis)
			self.axis = n_axis.mag()*self.axis.norm()
			rotate(angle, a, pos)

	@property
	def up(self):
		return self.up
	@up.setter
	def up(self, n_up):
		self.up = n_up

	@property
	def color(self):
		return self.color
	@color.setter
	def color(self, n_color):
		self.color = n_color

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
	def opacity(self):
		return self.opacity
	@opacity.setter
	def opacity(self, x):
		self.opacity = x

	@property
	def make_trail(self):
		return self.make_trail
	@make_trail.setter
	def make_trail(self, x):
		if (x and not self.obj_initialized):
			raise RuntimeError("Can't set make_trail=True unless object was created with make_trail specified")
		if (self.startup):
			import visual_common.primitives.trail_update as trail_update
			self.startup = False
		self.make_trail = x
		self.trail_initialized = False

	@property
	def primitive_object(self):
		return self.primitive_object
	@primitive_object.setter
	def primitive_object(self, x):
		self.primitive_object = x
		self.obj_initialized = True
