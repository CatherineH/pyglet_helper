# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *

'''
Operations on frame objects include:
get_center() : Use the average of all its children.
update_z_sort() : Never called.  Always re-sort this body's translucent children
	in gl_render().
gl_render() : Calls gl_render() on all its children.
grow_extent() : Calls grow_extent() for each of its children, then transforms
	the vertexes of the bounding box and uses those as its bounds.
gl_pick_render() : PushName() on to the Name Stack, and renders its children.
	When looking up names later, the render_core calls lookup_name() with a
	vector<uint>, which the frame uses to recursively look through frames to
	find the right object.
oolie case: When the frame is scaled up to a superhuge universe and the
	child is very small, the frame_world_transform may overflow OpenGL.  The
	problem lies in the scale variable.
another oolie: A transparent object that intersects a frame containing other
	transparent object's will not be rendered in the right order.
'''

class frame(renderable) :
	def __init__(self, axis = vector(1,0,0), up = vector(0,1,0), pos = vector(0,0,0), other = None):
		# The position and orientation of the body in World space.
		if other == None:
			self.axis = axis
			self.up = up
			self.pos = pos
		else:
			self.axis = other.axis
			self.up = other.up
			self.pos = other.pos
		#children is an iterator? I guess I need to learn python iterators...
		self.children = iterator()
		self.trans_children = iterator()
		self.child_iterator = []
		self.const_child_iterator = []
		self.trans_child_iterator = []
		self.const_trans_child_iterator = []

	def world_zaxis(self):
		if (fabs(self.axis.dot(self.up) / sqrt( self.up.mag2() * self.axis.mag2())) > 0.98):
			if (fabs(self.axis.norm().dot( vector(-1,0,0))) > 0.98):
				z_axis = self.axis.cross( vector(0,0,1)).norm()
			else:
				z_axis = self.axis.cross( vector(-1,0,0)).norm()
		else:
			z_axis = self.axis.cross(self.up).norm()
		return z_axis

	def frame_to_world(self, p):
		z_axis = self.world_zaxis()
		y_axis = z_axis.cross(self.axis).norm()
		x_axis = self.axis.norm()
		inworld = self.pos + p.x*x_axis + p.y*y_axis + p.z*z_axis
		return inworld

	def world_to_frame( self, p):
		z_axis = self.world_zaxis()
		y_axis = z_axis.cross(self.axis).norm()
		x_axis = self.axis.norm()
		v = p - self.pos
		inframe = vector(v.dot(x_axis), v.dot(y_axis), v.dot(z_axis))
		return inframe

	def frame_world_transform(self, gcf):
		'''
		 Performs a reorientation transform.
	 	ret = translation o reorientation
		'''
		z_axis = world_zaxis()
		y_axis = z_axis.cross(self.axis).norm()
		x_axis = self.axis.norm()
		ret.x_column( x_axis)
		ret.y_column( y_axis)
		ret.z_column( z_axis)
		ret.w_column( self.pos * gcf)
		ret.w_row()
		return ret

	def world_frame_transform(self):
		'''
	     Performs a reorientation transform.
	     ret = translation o reorientation
	     ret = ireorientation o itranslation.
	     Robert Xiao pointed out that this was incorrect, and he proposed
	     replacing it with inverse(ret, frame_world_transform(1.0)).
	     However, comparison with Visual 3 showed that there were
	     simply minor errors to be fixed.
		'''
	 	z_axis = world_zaxis();
		y_axis = z_axis.cross(self.axis).norm()
	    x_axis = axis.norm()
		ret(0,0) = x_axis.x
		ret(0,1) = x_axis.y
		ret(0,2) = x_axis.z
		ret(0,3) = -(self.pos * x_axis).sum()
		ret(1,0) = y_axis.x
		ret(1,1) = y_axis.y
		ret(1,2) = y_axis.z
		ret(1,3) = -(self.pos * y_axis).sum()
		ret(2,0) = z_axis.x
		ret(2,1) = z_axis.y
		ret(2,2) = z_axis.z
		ret(2,3) = -(self.pos * z_axis).sum()
		ret.w_row()
		return ret

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

	def add_renderable(self, obj):
		# Driven from visual/primitives.py set_visible
		if not obj.translucent():
			self.children.push_back( obj)
		else:
			self.trans_children.push_back( obj)

	def remove_renderable(self, obj):
		# Driven from visual/primitives.py set_visible
		if not obj.translucent():
			remove( self.children.begin(), self.children.end(), obj)
			self.children.pop_back()
		else:
			remove( self.trans_children.begin(), self.trans_children.end(), obj)
			self.trans_children.pop_back()

	def get_objects(self):
		ret = self.get_children()
		return ret

	def lookup_name(self, name_top, name_end):
		assert( name_top < name_end)
		assert( name_top < self.children.size() + self.trans_children.size())
		size = 0
		i =  iterator( self.children.begin())
		i_end = iterator( self.children.end())
		while i != i_end:
			if (name_top == size):
				ret = i.base()
				break
			size+=1
			i+=1
		if ret == None:
			ret = self.trans_children[name_top - size]
		if (name_end - name_top > 1):
			ref_frame = ret.get()
			assert( ref_frame != None)
			return ref_frame.lookup_name(name_top + 1, name_end)
		else:
			return ret

	def get_center(self):
		return self.pos

	def gl_render(self, v):
		local = v
		local.apply_frame_transform(self.world_frame_transform())
    	fwt = frame_world_transform(v.gcf)
		guard = gl_matrix_stackguard(fwt)
		i = child_iterator (children.begin())
		i_end = child_iterator(children.end())

		while (i != i_end):
			if i.translucent():
				# See display_kernel::draw().
				self.trans_children.push_back( i.base())
				i = self.children.erase(i.base())
				continue
			i.outer_render(local)
			i+=1

		# Perform a depth sort of the transparent children from forward to backward.
		if not self.trans_children.empty()):
			opacity = 0.5  #< TODO: BAD HACK

		if (self.trans_children.size() > 1):
			stable_sort( self.trans_children.begin(), self.trans_children.end(),
				z_comparator( (self.pos*v.gcf - v.camera).norm()))

		for i in range(self.trans_children.begin(), self.trans_child_iterator(self.trans_children.end()):
			i.outer_render(local)

		screen_iterator = iterator();
		i = iterator( local.screen_objects.begin()))
		i_end = iterator( local.screen_objects.end())
  		#  v.screen_objects.clear();
		while (i != i_end):
			v.screen_objects.insert( make_pair(i.first, i.second))
			i+=1
		#check_gl_error();

	def gl_pick_render(self, scene):
		# TODO: This needs to construct a valid local view!
		# Push name
		glPushName(0)
		guard = gl_matrix_stackguard( self.frame_world_transform(scene.gcf))
		#gl_matrix_stackguard guard( self.frame_world_transform(1.0))
		i = child_iterator(children.begin())
		i_end = child_iterator( children.end())
		# The unique integer to pass to OpenGL.
		name = 0
		while (i != i_end):
			glLoadName(name)
			i.gl_pick_render( scene)
			i+=1
			name+=1

		j = trans_child_iterator( self.trans_children.begin())
		j_end = trans_child_iterator( self.trans_children.end())
		while (j != j_end):
			glLoadName(name)
			j.gl_pick_render(scene)
			j+=1
			name+=1
		# Pop name
		glPopName()
		#check_gl_error();

	def = grow_extent(self, world):
		local = extent( world, self.frame_world_transform(1.0) )
		i = child_iterator(children.begin())
		i_end = child_iterator(children.end())
		while i != i_end:
			i.grow_extent( local)
			local.add_body()
			i++
	    j = trans_child_iterator( trans_children.begin())
	    j_end = trans_child_iterator( trans_children.end())
	    while j != j_end:
			j.grow_extent( local)
			local.add_body()

    def render_lights( self, world ):
		# TODO: this is expensive, especially if there are no lights at all in the frame!
	    local = view( world )
		local.apply_frame_transform(self.world_frame_transform())
 		i = child_iterator( self.children.begin())
	    i_end = child_iterator( self.children.end())
		while i != i_end:
			i.render_lights( local )
			j = trans_child_iterator ( self.trans_children.begin())
			j_end = trans_child_iterator ( self.trans_children.end())
		while j != j_end:
			j.render_lights( local )

		# Transform lights back into scene
		if ( world.light_count[0] != local.light_count[0] ):
			fwt = self.frame_world_transform(world.gcf)
			world.light_pos.resize( local.light_pos.size() )
			world.light_color.resize( local.light_color.size() )
			for l in range(world.light_count[0], local.light_count[0]):
				li = l*4
				v = vertex( local.light_pos[li], local.light_pos[li+1], local.light_pos[li+2], local.light_pos[li+3] )
				v = fwt * v
				for d in range(0,4):
					world.light_pos[li+d] = v[d]
					world.light_color[li+d] = local.light_color[li+d]
			world.light_count[0] = local.light_count[0]

	def get_children(self, all ):
		all.insert( all.end(), self.children.begin(), self.children.end() )
		all.insert( all.end(), self.trans_children.begin(), self.trans_children.end() )
		return all

	def outer_render(self, v):
  		gl_render(v)

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
	def z(self, z):
	  self.pos.z = z
	  if (self.trail_initialized and self.make_trail):
	    if (self.obj_initialized):
	      trail_update(self.primitive_object)
	@z.setter
	def z(self):
	  return self.pos.z

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
