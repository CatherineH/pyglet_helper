# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from math import pi

'''
 A class that manages all OpenGL aspects of a given scene.  This class
 requires platform-specific support from render_surface to manage an OpenGL
 rendering context and mouse and keyboard interaction.
'''

class display_kernel:
	def __init__(self, exit = True, visible = False, explicitly_invisible = False, \
	 fullscreen = False, title =  "Python", window_x = 0, window_y = 0, window_width = 430,\
	 window_height = 450, view_width = -1, view_height = -1, center = [0, 0, 0],\
	 forward = [0, 0, -1], internal_forward = [0, 0, -1], up = [0, 1, 0], forward_changed = True, \
	 fov =  60 * pi / 180.0, autoscale = True, autocenter = False, uniform = True, \
	 camera = [0,0,0], user_scale = 1.0, gcf = 1.0, gcfvec = [1.0,1.0,1.0], \
	 gcf_changed = False, ambient = [ 0.2, 0.2, 0.2], show_toolbar = False, last_time = 0, \
	 background = [0, 0, 0], spin_allowed = True, zoom_allowed = True, mouse_mode = ZOOM_ROTATE, \
	 stereo_mode = NO_STEREO, stereodepth = 0.0, lod_adjust = 0, realized = False, \
	 mouse = self, range_auto = 0.0, range = [0,0,0], world_extent = 0.0)
 		self.extensions = ''
 		self.renderer = ''
 		self.version = ''
 		self.vendor = ''
 		self.last_time = last_time
 		self.render_time = 0
 		self.realized = realized
		self.selected = ''

		self.center = center # The observed center of the display, in world space.
		self.forward = forward #/< The direction of the camera, in world space.
		self.up  = up #/< The vertical orientation of the scene, in world space.
		self.internal_forward = internal_forward #/< Do not permit internal_forward to be +up or -up
		self.range  = range #/< Explicitly specified scene.range, or (0,0,0)
		self.camera = camera #< World coordinates of camera location
		self.range_auto = range_auto	#< Automatically determined camera z from autoscale

		# True initally and whenever the camera direction changes.  Set to false
		# after every render cycle.
		self.forward_changed = forward_changed

		self.world_extent = world_extent #/< The extent of the current world.

		self.fov = fov #/< The field of view, in radians
		self.stereodepth = stereodepth #< How far in or out of the screen the scene seems to be
		self.autoscale = autoscale #/< True if Visual should scale the camera's position automatically.
		# True if Visual should automatically reposition the center of the scene.
	 	self.autocenter = autocenter
		# True if the autoscaler should compute uniform axes.
		self.uniform = uniform
	 	# A scaling factor determined by middle mouse button scrolling.
		self.user_scale = user_scale
	 	# The global scaling factor. It is used to ensure that objects with
		# large dimensions are rendered properly. See the .cpp file for details.
	    self.gcf = gcf
		# Vector version of the global scaling factor used when scene.uniform=0.
	 	# Affects just curve, points, faces, label, frame, and conversion of mouse coordinates.
		self.gcfvec = gcfvec

	 	# True if the gcf has changed since the last render cycle.  Set to false
	  	# after every rendering cycle.
		self.gcf_changed = gcf_changed

		self.ambient = ambient #/< The ambient light color.

		self.background = background #/< The background color of the scene.
		self.foreground = foreground #/< The default color for objects to be rendered into the scene.

		# Whether or not the user is allowed to spin or zoom the display
		self.spin_allowed = spin_allowed
		self.zoom_allowed = zoom_allowed

		# Opaque objects to be rendered into world space.
		self.world_iterator = indirect_iterator()

		# objects with a nonzero level of transparency that need to be depth sorted
		#	prior to rendering.
		self.layer_world_transparent = Vector()
		self.world_trans_iterator = indirect_iterator()
		# Mouse and keyboard objects
		self.mouse = mouse
		self.mouse_mode = mouse_mode
		self.stereo_mode = stereo_mode

		# The bounding rectangle of the window on the screen (or equivalent super-window
		# coordinate system), including all decorations.
		# If the window is invisible, window_x and/or window_y may be -1, meaning
		# that the window will be positioned automatically by the window system.
		self.window_x = window_x
		self.window_y = window_y
		self.window_width = window_width
		self.window_height = window_height

		# The rectangle on the screen into which we can actually draw.
		# At present, these are undefined until the display is realized, and
		# they are not used in constructing the display (they are outputs of
		# that process)
		# This includes both viewports in a side-by-side stereo mode, whereas
		#   view::view_width does not.
		self.view_width = view_width
		self.view_height = view_height

		self.exit = exit #/< True when Visual should shutdown on window close.
		self.visible = visible #/< scene.visible
		self.explicitly_invisible = explicitly_invisible #/< true iff scene.visible has ever been set to 0 by the program, or by the user closing a window
		self.fullscreen = fullscreen #/< True when the display is in fullscreen mode.
		self.show_toolbar #/< True when toolbar is displayed (pan, etc).
		self.title = title

		#Older machines should set this to some number between -6 and 0.  All of
		# the tesselated models choose a lower level of detail based on this value
		# when it is less than 0.
		self.lod_adjust = lod_adjust
		self.realized = realized

		self.glext = gl_extensions()
		self.mouse_mode_t = enumerate( ZOOM_ROTATE, ZOOM_ROLL, PAN, FIXED )
		self.mouse_button = enumerate( NONE, LEFT, RIGHT, MIDDLE )
		self.stereo_mode_t = enumerate( NO_STEREO, PASSIVE_STEREO, ACTIVE_STEREO, CROSSEYED_STEREO, \
			REDBLUE_STEREO, REDCYAN_STEREO, YELLOWBLUE_STEREO, GREENMAGENTA_STEREO)


	def enable_lights(self, scene):
		'''
		Called at the beginning of a render cycle to establish lighting.
		'''
		scene.light_count[0] = 0
		scene.light_pos.clear()
		scene.light_color.clear()
		i = self.layer_world.begin()
		i_end = self.layer_world.end()
		while i != i_end:
			i.render_lights( scene )
			i += 1
		j = self.layer_world_transparent.begin()
		j_end = self.layer_world_transparent.end()
		while j != j_end:
			j.render_lights( scene )

		world_camera.gl_modelview_get()
		p = vertex()

		# Clear modelview matrix since we are multiplying the light positions ourselves
		guard = gl_matrix_stackguard()
		glLoadIdentity()
		limit = min([scene.light_count[0],8])
		for i in range(0,limit):
			li = i*4

			# Transform the light into eye space
			for d in range(0,4):
				p[d] = scene.light_pos[li+d]
				p = world_camera * p
			for d in range(0,4):
				scene.light_pos[li+d] = p[d]

			# Enable the light for fixed function lighting.  This is unnecessary if everything in the scene
			# uses materials and the card supports our shaders, but for now...
			id = GL_LIGHT0 + i
			glLightfv( id, GL_DIFFUSE, scene.light_color[li])
			glLightfv( id, GL_SPECULAR, scene.light_color[li])
			glLightfv( id, GL_POSITION, scene.light_pos[li])
			glEnable(id)

		for i in range(scene.light_count[0], 8):
			glDisable( GL_LIGHT0 + i )

		glEnable( GL_LIGHTING)
		glLightModelfv( GL_LIGHT_MODEL_AMBIENT, self.ambient.red)

		check_gl_error()

	def disable_lights(self):
		'''
		Called at the end of a render cycle to complete lighting.
		'''
		glDisable( GL_LIGHTING)

	def world_to_view_transform(self, view, whicheye = 0, forpick = False):
		'''
		Set up matrices for transforms from world coordinates to view coordinates
 		Precondition: the OpenGL Modelview and Projection matrix stacks should be
		at the bottom.
		Postcondition: active matrix stack is GL_MODELVIEW, matrix stacks are at
		the bottom.  Viewing transformations have been applied.  geometry.camera
		is initialized.
		whicheye: -1 for left, 0 for center, 1 for right.
		'''
		# See http://www.stereographics.com/support/developers/pcsdk.htm for a
		# discussion regarding the design basis for the frustum offset code.

		# gcf scales the region encompassed by scene.range_* into a ROUGHLY 2x2x2 cube.
		# Note that this is NOT necessarily the entire world, since scene.range
		#   can be changed.
		# This coordinate system is used for most of the calculations below.

		scene_center = self.center.scale(self.gcfvec)
		scene_up = self.up.norm()
    	scene_forward = self.internal_forward.norm()

		# the horizontal and vertical tangents of half the field of view.
		[tan_hfov_x, tan_hfov_y] = self.tan_hfov()

		# The cotangent of half of the wider field of view.
		if not self.uniform: # We force width to be 2.0 (range.x 1.0)
			cot_hfov = 1.0 / tan_hfov_x
		else:
			cot_hfov = 1.0 / max([tan_hfov_x, tan_hfov_y])

		# The camera position is chosen by the tightest of the enabled range_* modes.
		cam_to_center_without_zoom = 1e150

		if self.range_auto:
			cam_to_center_without_zoom = min([cam_to_center_without_zoom,
				range_auto])
		if self.range.nonzero():
			cam_to_center_without_zoom = std::min(cam_to_center_without_zoom,
				range.x * cot_hfov / 1.02)
		if (cam_to_center_without_zoom >= 1e150):
			cam_to_center_without_zoom = 10.0 / sin( self.fov * 0.5 )
		cam_to_center_without_zoom *= self.gcf * 1.02

		# Position camera so that a sphere containing the box range will fit on the screen
		#   OR a 2*user_scale cube will fit.  The former is tighter for "non cubical" ranges
		#   and the latter is tighter for cubical ones.
		scene_camera = scene_center - cam_to_center_without_zoom*self.user_scale*self.scene_forward

		[nearest, farthest] = world_extent.get_near_and_far(internal_forward, nearest, farthest) # nearest and farthest points relative to scene.center when projected onto forward
		nearest = nearest*self.gcf
		farthest = farthest*self.gcf

		cam_to_center = (scene_center - scene_camera).mag()
		'''
		 Z buffer resolution is highly sensitive to nearclip - a "small" camera will have terrible z buffer
		   precision for distant objects.  PLEASE don't fiddle with this unless you know what kind of
		   test cases you need to see the results, including at nonstandard fields of view and 24 bit
		   z buffers!
		 The equation for nearclip below is designed to give similar z buffer resolution at all fields of
		   view.  It's a little weird, but seems to give acceptable results in all the cases I've been able
		   to test.
		 The other big design question here is the effect of "zoom" (user_scale) on the near clipping plane.
		   Most users will have the mental model that this moves the camera closer to the scene, rather than
		   scaling the scene up.  There is actually a difference since the camera has a finite "size".
		   Unfortunately, following this model leads to a problem with zooming in a lot!  The problem is
		   especially pronounced at tiny fields of view, which typically have an enormous camera very far away
		   when you try to zoom in the big camera "crashes" into the tiny scene!  So instead we use the
		   slightly odd model of scaling the scene, or equivalently making the camera smaller as you zoom in.
		'''
		fwz = cam_to_center_without_zoom + 1.0
		nearclip = fwz * fwz / (100 + fwz) * self.user_scale
		# TODO: nearclip = std::max( nearclip, (cam_to_center + nearest) * 0.95 )  #< ?? boost z buffer resolution if there's nothing close to camera?
		farclip = (farthest + cam_to_center) * 1.05 #< actual maximum z in scene plus a little
		farclip = max( [farclip, nearclip * 1.001] ) #< just in def set_everything is behind the camera!

		# Here is the stereodepth and eye offset machinery from Visual 3, where the docs claimed that
		# stereodepth=0 was the default (zero-parallax plane at screen surface
		# stereodepth=1 moves the center of the scene to the screen surface
		# stereodepth=2 moves the back of the scene to the screen surface:

		# A multiple of the number of cam_to_center's away from the camera to place
		# the zero-parallax plane.
		# The distance from the camera to the zero-parallax plane.
		focallength = cam_to_center+0.5*self.stereodepth
		# Translate camera left/right 2% of the viewable width of the scene at
		# the distance of its center.
		camera_stereo_offset = tan_hfov_x * focallength * 0.02
		camera_stereo_delta = camera_stereo_offset \
			* self.up.cross( scene_camera).norm() * whicheye
		scene_camera += camera_stereo_delta
		scene_center += camera_stereo_delta
		# The amount to translate the frustum to the left and right.
		frustum_stereo_offset = camera_stereo_offset * nearclip \
			/ focallength * whicheye

		# Finally, the OpenGL transforms based on the geometry just calculated.
		clear_gl_error()
		# Position the camera.
		glMatrixMode( GL_MODELVIEW)
		glLoadIdentity()

		#if 0	# Enable this to peek at the actual scene geometry.
		max_proj_stack_depth = glGetIntegerv( GL_MAX_PROJECTION_STACK_DEPTH)
		max_mv_stack_depth = glGetIntegerv( GL_MAX_MODELVIEW_STACK_DEPTH )
		proj_stack_depth = glGetIntegerv( GL_PROJECTION_STACK_DEPTH )
		mv_stack_depth = glGetIntegerv( GL_MODELVIEW_STACK_DEPTH )
		print "scene_geometry: camera:" + str(scene_camera) \
	        + " true camera:" + str(self.camera)}"\n"  \
			+ " center:" + str(scene_center) + " true center:" + str(self.center) + "\n" \
			+ " forward:" + str(scene_forward) + " true forward:" + str(self.forward) + "\n" \
			+ " up:" + str(scene_up) + " range:" + str(self.range) + " gcf:" + str(self.gcf) + "\n" \
			+ " nearclip:" + str(nearclip) + " nearest:" + str(self.nearest) + "\n" \
			+ " farclip:" + str(farclip) + " farthest:" + str(self.farthest) + "\n" \
			+ " user_scale:" + str(user_scale) + "\n" \
	        + " cot_hfov:" + str(cot_hfov) + " tan_hfov_x:" + str(tan_hfov_x) + "\n" \
	        + " tan_hfov_y: " + str(tan_hfov_y) + "\n" \
	        + " window_width:" + str(window_width) + " window_height:" + str(window_height) + "\n" \
	        + " max_proj_depth:" + str(max_proj_stack_depth) + " current_proj_depth:" + str(proj_stack_depth) + "\n" \
	        + " max_mv_depth:" + str(max_mv_stack_depth) + " current_mv_depth:" + str(mv_stack_depth) + "\n"
		self.world_extent.dump_extent()

		gluLookAt( \
			scene_camera.x, scene_camera.y, scene_camera.z, \
			scene_center.x, scene_center.y, scene_center.z, \
			scene_up.x, scene_up.y, scene_up.z)

		world_camera = gl_modelview_get()
		inverse( geometry.camera_world, world_camera )

		# Establish a parallel-axis asymmetric stereo projection frustum.
		glMatrixMode( GL_PROJECTION)
		if not forpick :
			glLoadIdentity()
		if whicheye == 1:
			frustum_stereo_offset = -frustum_stereo_offset
		elif whicheye == 0:
			frustum_stereo_offset = 0

		if self.nearclip<=0 or self.farclip<=self.nearclip or tan_hfov_x<=0 or tan_hfov_y<=0:
			except RunTimeEror("degenerate projection: " + str(self.nearclip) + " " + str(self.farclip) + " " + str(tan_hfov_x) + " " + str(tan_hfov_y))

		glFrustum( \
			-self.nearclip * tan_hfov_x + frustum_stereo_offset, \
			self.nearclip * tan_hfov_x + frustum_stereo_offset, \
			-self.nearclip * tan_hfov_y, \
			self.nearclip * tan_hfov_y, \
			self.nearclip, \
			self.farclip )

		glMatrixMode( GL_MODELVIEW)
		check_gl_error()

		# The true camera position, in world space.
		self.camera = scene_camera/gcf

		# Finish initializing the view object.
		geometry.camera = self.camera
		geometry.tan_hfov_x = tan_hfov_x
		geometry.tan_hfov_y = tan_hfov_y
		# The true viewing vertical direction is not the same as what is needed for
		geometry.up = internal_forward.cross_b_cross_c(up, internal_forward).norm()


	def draw(self, scene_geometry, whicheye=0):
		'''
		 Renders the scene for one eye.
			@param scene The dimensions of the scene, to be propogated to this
				display_kernel's children.
			@param eye Which eye is being rendered.  -1 for the left, 0 for the
				center, and 1 for the right.
			@param scene_geometry.anaglyph  True if using anaglyph stereo requiring color
				desaturation or grayscaling.
			@param scene_geometry.coloranaglyph  True if colors must be grayscaled, false if colors
				must be desaturated.
		'''
		# Set up the base modelview and projection matrices
		self.world_to_view_transform( scene_geometry, whicheye)
		# Render all opaque objects in the world space layer
		enable_lights(scene_geometry)
		i = world_iterator ( layer_world.begin())
		i_end = world_iterator ( layer_world.end())
		while (i != i_end) :
			if (i.translucent()):
				# The color of the object has become transparent when it was not
				# initially.  Move it to the transparent layer.  The penalty for
				# being rendered in the transparent layer when it is opaque is only
				# a small speed hit when it has to be sorted.  Therefore, that case
				# is not tested at all.  (TODO Untrue-- rendering opaque objects in transparent
				# layer makes it possible to have opacity artifacts with a single convex
				# opaque objects, provided other objects in the scene were ONCE transparent)
				self.layer_world_transparent.push_back( i.base())
				i = layer_world.erase(i.base())
				continue
			check_gl_error()
			i.outer_render( scene_geometry)
			check_gl_error()
			i += 1


		# Perform a depth sort of the transparent world from back to front.
		if (self.layer_world_transparent.size() > 1):
			stable_sort( \
				self.layer_world_transparent.begin(), self.layer_world_transparent.end(), \
				z_comparator( self.internal_forward.norm()))

		# Render translucent objects in world space.
		j = world_trans_iterator( layer_world_transparent.begin())
		j_end = world_trans_iterator( layer_world_transparent.end())
		while (j != j_end) :
			j.outer_render( scene_geometry )
			j+=1

		# Render all objects in screen space.
		disable_lights()
		gl_disable depth_test( GL_DEPTH_TEST)
		k = screen_iterator ( scene_geometry.screen_objects.begin())
		k_end = screen_iterator ( scene_geometry.screen_objects.end())
		while ( k != k_end) :
			k.second.gl_render()
			k +=1

		scene_geometry.screen_objects.clear()

		return True

	# Computes the extent of the scene and takes action for autozoom and
	# autoscaling.
	def recalc_extent(self):

		[tan_hfov_x,tan_hfov_y]  = self.tan_hfov( tan_hfov_x, tan_hfov_y )
		tan_hfov = max([tan_hfov_x, tan_hfov_y])

		while (1) :  #< Might have to do this twice for autocenter
			world_extent = self.extent_data( tan_hfov )
			l_cw.translate( -center )
			ext = extent( world_extent, l_cw )
			i = world_iterator( layer_world.begin())
			end = world_iterator( layer_world.end())
			while (i != end) :
				i.grow_extent( ext)
				i+=1

			j = world_trans_iterator ( layer_world_transparent.begin())
			j_end = world_trans_iterator ( layer_world_transparent.end())
			while (j != j_end) :
				j.grow_extent( ext)
				j+=1

			if (self.autocenter) :
				c = world_extent.get_center() + self.center
				if ( (self.center-c).mag2() > (self.center.mag2() + c.mag2()) * 1e-6 ) :
					# Change center and recalculate extent (since camera_z depends on center)
					self.center = c
					continue
			break

		if (self.autoscale and self.uniform) :
			r = world_extent.get_camera_z()
			if (r > range_auto):
				range_auto = r
			elif ( 3.0*r < range_auto ):
				range_auto = 3.0*r

		# Rough scale calculation for gcf.  Doesn't need to be exact.
		# TODO: If extent and range are very different in scale, we are using extent to drive
		#   gcf.  Both options have pros and cons.
		mr = world_extent.get_range(vector(0,0,0)).mag()
		if mr != None or mr != 0.0:
			scale = 1.0/mr
		else:
			scale = 1.0

		if not uniform and self.range.nonzero()) :
			self.gcf_changed = True
			self.gcf = 1.0/self.range.x
			if self.stereo_mode == PASSIVE_STEREO or self.stereo_mode == CROSSEYED_STEREO:
				width = self.view_width*0.5
			else:
				width = self.view_width
			self.gcfvec = vector(1.0/self.range.x, (self.view_height/width)/self.range.y, 0.1/self.range.z)
		 else :
			# TODO: Instead of changing gcf so much, we could change it only when it is 2x
			# off, to aid primitives whose caching may depend on gcf (but are there any?)
			if (self.gcf != scale) :
				self.gcf = scale
				self.gcf_changed = True
			self.gcfvec = vector(self.gcf,self.gcf,self.gcf)


	# Compute the tangents of half the vertical and half the horizontal
	# true fields-of-view.
	def tan_hfov(self):
		# tangent of half the field of view.
		tan_hfov = tan( self.fov*0.5)
		aspect_ratio = self.view_height / self.view_width
		if (self.stereo_mode == PASSIVE_STEREO or self.stereo_mode == CROSSEYED_STEREO):
			aspect_ratio *= 2.0
		if (aspect_ratio > 1.0) :
			# Tall window
			x = tan_hfov / aspect_ratio
			y = tan_hfov
		else :
			# Wide window
			x = tan_hfov
			y = tan_hfov * aspect_ratio
		return[x,y]

	def realize(self):
		clear_gl_error()
		if not self.extensions :
			self.extensions.reset( '')
			strm = glGetString( GL_EXTENSIONS)
			copy( strm, '', inserter( self.extensions, self.extensions.begin()))

			vendor = glGetString(GL_VENDOR)
			version = glGetString(GL_VERSION)
			renderer = glGetString(GL_RENDERER)

			# The test is a hack so that subclasses not bothering to implement getProcAddress just
			#   don't get any extensions.
			#if (getProcAddress("display_kernel::getProcAddress") != notImplemented)
			#	glext.init( *self )


		# Those features of OpenGL that are always used are set up here.
		# Depth buffer properties
		glClearDepth( 1.0)
		glEnable( GL_DEPTH_TEST)
		glDepthFunc( GL_LEQUAL)

		# Lighting model properties
		glShadeModel( GL_SMOOTH)
		# TODO: Figure out what the concrete costs/benefits of these commands are.
		# glHint( GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
		glHint( GL_POLYGON_SMOOTH_HINT, GL_NICEST)
		glHint( GL_LINE_SMOOTH_HINT, GL_NICEST)
		glHint( GL_POINT_SMOOTH_HINT, GL_NICEST)
		glEnable( GL_NORMALIZE)
		glColorMaterial( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
		glEnable( GL_COLOR_MATERIAL)
		glEnable( GL_BLEND )
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		# Ensures that fully transparent pixels don't write into the depth buffer,
		# ever.
		glEnable( GL_ALPHA_TEST)
		glAlphaFunc( GL_GREATER, 0.0)

		# FSAA.  Doesn't seem to have much of an effect on my TNT2 card.  Grrr.
		if (hasExtension( "GL_ARB_multisample" ) ) :
			glEnable( GL_MULTISAMPLE_ARB)
			n_samples = glGetIntegerv( GL_SAMPLES_ARB)
			n_buffers = glGetIntegerv( GL_SAMPLE_BUFFERS_ARB)
		check_gl_error()

	def implicit_activate(self):
		if not self.visible and not self.explicitly_invisible:
			self.visible = True

	def add_renderable(self, obj):
		'''
	    Add a normal renderable object to the list of objects to be rendered into
	    world space.
	    '''
		if not obj.translucent():
			self.layer_world.push_back( obj)
		else:
		    self.layer_world_transparent.push_back( obj)
		if not obj.is_light():
			self.implicit_activate()

	def remove_renderable(self, obj):
		'''
		  Remove a renderable object from this display, regardless of which layer
	       it resides in.
		'''
		if not obj.translucent()):
			remove( self.layer_world.begin(), self.layer_world.end(), obj)
			self.layer_world.pop_back()
		else:
			remove( self.layer_world_transparent.begin(), self.layer_world_transparent.end(), obj)
			self.layer_world_transparent.pop_back()

	# Compute the location of the camera based on the current geometry.
	def calc_camera(self):
		return self.camera

	def render_scene(self):
		'''
		 Renders the scene once.  The enveloping widget is resposible for calling
	     this function appropriately.
	 	 @return If false, something catastrophic has happened and the
	 	 application should probably exit.
		'''
		# TODO: Exception handling?
		if not self.realized :
			self.realize()

		try :
			self.recalc_extent()
			scene_geometry  = view( self.internal_forward.norm(), self.center, self.view_width, \
				self.view_height, self.forward_changed, self.gcf, self.gcfvec, self.gcf_changed, self.glext)
			scene_geometry.lod_adjust = self.lod_adjust
			scene_geometry.enable_shaders = self.enable_shaders
			clear_gl_error()

			on_gl_free.frame()

			glClearColor( self.background.red, self.background.green, self.background.blue, 0)
			modes = {NO_STEREO:self.set_NO_STEREO, ACTIVE_STEREO:self.set_ACTIVE_STEREO, \
			     REDBLUE_STEREO: self.set_REDBLUE_STEREO, REDCYAN_STEREO: self.set_REDCYAN_STEREO,\
				 YELLOWBLUE_STEREO: self.set_YELLOWBLUE_STEREO, GREENMAGENTA_STEREO: self.set_GREENMAGENTA_STEREO,\
				 PASSIVE_STEREO: self.set_PASSIVE_STEREO, CROSSEYED_STEREO: self.set_CROSSEYED_STEREO
			}
			modes[self.stereo_mode]()
			# Cleanup
			check_gl_error()
			self.gcf_changed = False
			self.forward_changed = False

		catch (gl_error e) :
			except RunTimeError("render_scene OpenGL error: " + e.what() + ", aborting.\n")


		# TODO: Can we delay picking until the Python program actually wants one of these attributes?
		mouse.get_mouse().cam = camera
		#not exactly sure what this is doing...
		#boost::tie( mouse.get_mouse().pick, mouse.get_mouse().pickpos, mouse.get_mouse().position) =
		#	pick( mouse.get_x(), mouse.get_y() )

		on_gl_free.frame()

		return True

	def set_NO_STEREO(self, scene_geometry):
		scene_geometry.anaglyph = False
		scene_geometry.coloranaglyph = False
		glViewport( 0, 0, self.view_width, self.view_height)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		self.draw(scene_geometry, 0)
	def set_ACTIVE_STEREO(self, scene_geometry):
		scene_geometry.anaglyph = False
		scene_geometry.coloranaglyph = False
		glViewport( 0, 0, self.view_width, self.view_height)
		glDrawBuffer( GL_BACK_LEFT)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		self.draw( scene_geometry, -1)
		glDrawBuffer( GL_BACK_RIGHT)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		self.draw( scene_geometry, 1)
	def set_REDBLUE_STEREO(self, scene_geometry):
		# Red channel
		scene_geometry.anaglyph = True
		scene_geometry.coloranaglyph = False
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		glViewport( 0, 0, self.view_width, self.view_height)
		glColorMask( GL_TRUE, GL_FALSE, GL_FALSE, GL_TRUE)
		self.draw( scene_geometry, -1)
		# Blue channel
		glColorMask( GL_FALSE, GL_FALSE, GL_TRUE, GL_TRUE)
		glClear( GL_DEPTH_BUFFER_BIT)
		self.draw( scene_geometry, 1)
		# Put everything back
		glColorMask( GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
	def set_REDCYAN_STEREO(self, scene_geometry):
		# Red channel
		scene_geometry.anaglyph = True
		scene_geometry.coloranaglyph = True
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		glViewport( 0, 0, self.view_width, self.view_height)
		glColorMask( GL_TRUE, GL_FALSE, GL_FALSE, GL_TRUE)
		self.draw( scene_geometry, -1)
		# Green and Blue channels
		glColorMask( GL_FALSE, GL_TRUE, GL_TRUE, GL_TRUE)
		glClear( GL_DEPTH_BUFFER_BIT)
		self.draw( scene_geometry, 1)
		# Put everything back
		glColorMask( GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
	def set_YELLOWBLUE_STEREO(self, scene_geometry):
		# Red and green channels
		scene_geometry.anaglyph = True
		scene_geometry.coloranaglyph = True
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		glViewport( 0, 0, self.view_width, self.view_height)
		glColorMask( GL_TRUE, GL_TRUE, GL_FALSE, GL_TRUE)
		self.draw( scene_geometry, -1)
		# Blue channel
		glColorMask( GL_FALSE, GL_FALSE, GL_TRUE, GL_TRUE)
		glClear( GL_DEPTH_BUFFER_BIT)
		self.draw( scene_geometry, 1)
		# Put everything back
		glColorMask( GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
	def set_GREENMAGENTA_STEREO(self, scene_geometry):
		# Green channel
		scene_geometry.anaglyph = True
		scene_geometry.coloranaglyph = True
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		glViewport( 0, 0, self.view_width, self.view_height)
		glColorMask( GL_FALSE, GL_TRUE, GL_FALSE, GL_TRUE)
		self.draw( scene_geometry, -1)
		# Red and blue channels
		glColorMask( GL_TRUE, GL_FALSE, GL_TRUE, GL_TRUE)
		glClear( GL_DEPTH_BUFFER_BIT)
		self.draw( scene_geometry, 1)
		# Put everything back
		glColorMask( GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
	def set_PASSIVE_STEREO(self, scene_geometry):
		# Also handle viewport modifications.
		scene_geometry.view_width =  self.view_width/2
		scene_geometry.anaglyph = False
		scene_geometry.coloranaglyph = False
		stereo_width = int(scene_geometry.view_width)
		# Left eye
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		glViewport( 0, 0, self.stereo_width, self.view_height )
		draw( scene_geometry, -1)
		# Right eye
		glViewport( stereo_width+1, 0, self.stereo_width, self.view_height)
		self.draw( scene_geometry, 1)

	def set_CROSSEYED_STEREO(self, scene_geometry):
		# Also handle viewport modifications.
		scene_geometry.view_width =  view_width/2
		scene_geometry.anaglyph = False
		scene_geometry.coloranaglyph = False
		stereo_width = int(scene_geometry.view_width)
		# Left eye
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )
		glViewport( 0, 0, self.stereo_width, self.view_height)
		self.draw( self.scene_geometry, 1);
		# Right eye
		glViewport( self.stereo_width+1, 0, self.stereo_width, self.view_height )
		self.draw( scene_geometry, -1)

	def report_closed(self):
		'''
		 Inform this object that the window has been closed (is no longer physically
		 visible)
		'''
		if self.visible:
			self.set_display_visible( self, False )
		self.realized = False
		self.visible = False
		self.explicitly_invisible = True


	def report_camera_motion(self, dx, dy, button ):
		'''
	    Called by mouse_manager to report mouse movement that should affect the camera.
		Report that the mouse moved with one mouse button down.
 		@param dx horizontal change in mouse position in pixels.
 		@param dy vertical change in mouse position in pixels.
		'''

		# This stuff handles automatic movement of the camera in response to user
		# input. See also view_to_world_transform for how the affected variables
		# are used to actually position the camera.

		# Scaling conventions:
		# the full width of the widget rotates the scene horizontally by 120 degrees.
		# the full height of the widget rotates the scene vertically by 120 degrees.
		# the full height of the widget zooms the scene by a factor of 10

		# Panning conventions:
		# The full height or width of the widget pans the scene by the eye distance.

		# Locking:
		# center and forward are already synchronized. The only variable that
		# remains to be synchronized is user_scale.

		# The vertical and horizontal fractions of the window's height that the
		# mouse has traveled for this event.
		# TODO: Implement ZOOM_ROLL modes.
		vfrac = float(dy / self.view_height)
		if self.stereo_mode == PASSIVE_STEREO or stereo_mode == CROSSEYED_STEREO:
			hfrac = float(dx/(self.view_width*0.5))
		else:
			hfrac = float(dx/(self.view_width))

		# The amount by which the scene should be shifted in response to panning
		# motion.
		# TODO: Keep this synchronized with the eye_dist calc in
		# world_view_transform
		[tan_hfov_x, tan_hfov_y] = self.tan_hfov()
		pan_rate = (self.center - self.calc_camera()).mag()*min([tan_hfov_x, tan_hfov_y])

		if button == MIDDLE:
			if self.mouse_mode== PAN :
				# Pan front/back.
				if self.spin_allowed:
					self.center += pan_rate * vfrac * self.internal_forward.norm()
			if self.mouse_mode == ZOOM_ROLL or self.mouse_mode == ZOOM_ROTATE:
				# Zoom in/out.
				if (self.zoom_allowed):
					self.user_scale *= pow( 10.0, vfrac)
		if button == RIGHT:
			if self.mouse_mode == PAN :
				# Pan up/down and left/right.
				# A vector pointing along the camera's horizontal axis.
				horiz_dir = self.internal_forward.cross(self.up).norm();
				# A vector pointing along the camera's vertical axis.
				vert_dir = self.horiz_dir.cross(self.internal_forward).norm();
				if (self.spin_allowed) :
					self.center += -horiz_dir * pan_rate * hfrac;
					self.center += vert_dir * pan_rate * vfrac;
			if self.mouse_mode == ZOOM_ROTATE:
				if self.spin_allowed:
					# Rotate
					# First perform the rotation about the up vector.
					R = rotation( -hfrac * 2.0, self.up.norm())
					self.internal_forward = R * self.internal_forward

					# Then perform rotation about an axis orthogonal to up and forward.
					vertical_angle = vfrac * 2.0
					max_vertical_angle = self.up.diff_angle(-self.internal_forward.norm())

					# Over the top (or under the bottom) rotation
					if not (vertical_angle >= max_vertical_angle or
						vertical_angle <= max_vertical_angle - pi)):
						# Over the top (or under the bottom) rotation
						R = rotation( -vertical_angle, self.internal_forward.cross(self.up).norm());
						self.forward = self.internal_forward = R*self.internal_forward
						self.forward_changed = True



	/** Report that the position and/or size of the window or drawing area widget has changed.
		Some platforms might not know about position changes they can pass (x,y,new_width,new_height)
 		win_* give the window rectangle (see this.window_*)
 		v_* give the view rectangle (see this.view_*)
 		*/
	void report_window_resize( int win_x, int win_y, int win_w, int win_h )
	void report_view_resize( int v_w, int v_h )

	/** Determine which object (if any) was picked by the cursor.
 	    @param x the x-position of the mouse cursor, in pixels.
		@param y the y-position of the mouse cursor, in pixels.
		@param d_pixels the allowable variation in pixels to successfully score
			a hit.
		@return  the nearest selected object, the position that it was hit, and
			the position of the mouse cursor on the near clipping plane.
           retval.get<0>() may be NULL if nothing was hit, in which def set_the
           positions are undefined.
	*/
	boost::tuple<shared_ptr<renderable>, vector, vector>
	pick( int x, int y, float d_pixels = 2.0)

	/** Recenters the scene.  Call this function exactly once to move the visual
	 * center of the scene to the true center of the scene.  This will work
	 * regardless of the value of this->autocenter.
	 */
	void recenter()

	/** Rescales the scene.  Call this function exactly once to scale the scene
	 * such that it fits within the entire window.  This will work
	 * regardless of the value of this->autoscale.
	 */
	void rescale()

	/** Release GL resources.  Call this as many times as you like during the
	 * shutdown.  However, neither pick() nor render_scene() may be called on
	 * any display_kernel after gl_free() has been invoked.
	 */
	void gl_free()

	void allow_spin(bool)
	bool spin_is_allowed(void) const

	void allow_zoom(bool)
	bool zoom_is_allowed(void) const


	# Python properties
	void set_up( const vector& n_up)
	shared_vector& get_up()

	void set_forward( const vector& n_forward)
	shared_vector& get_forward()

	void set_scale( const vector& n_scale)
	vector get_scale()

	void set_center( const vector& n_center)
	shared_vector& get_center()

	void set_fov( double)
	double get_fov()
	void set_lod(int)
	int get_lod()

	void set_uniform( bool)
	bool is_uniform()

	void set_background( const rgb&)
	rgb get_background()

	void set_foreground( const rgb&)
	rgb get_foreground()

	void set_autoscale( bool)
	bool get_autoscale()

	void set_autocenter( bool)
	bool get_autocenter()

	void set_range_d( double)
	void set_range( const vector&)
	vector get_range()

	void set_ambient_f( float)
	void set_ambient( const rgb&)
	rgb get_ambient()

	void set_stereodepth( float)
	float get_stereodepth()

	# The only mode that cannot be changed after initialization is active,
	# which will result in a gl_error exception when rendered.  The completing
	# display class will have to perform some filtering on this parameter.  This
	# properties setter will not change the mode if the new one is invalid.
	void set_stereomode( std::string mode)
	std::string get_stereomode()

	# A list of all objects rendered into this display_kernel.  Modifying it
	# does not propogate to the owning display_kernel.
	std::vector<shared_ptr<renderable> > get_objects() const

	std::string info( void)

	void set_x( float x)
	float get_x()

	void set_y( float y)
	float get_y()

	void set_width( float w)
	float get_width()

	void set_height( float h)
	float get_height()

	void set_visible( bool v)
	bool get_visible()

	void set_title( std::string n_title)
	std::string get_title()

	bool is_fullscreen()
	void set_fullscreen( bool)

	bool get_exit()
	void set_exit(bool)

	bool is_showing_toolbar()
	void set_show_toolbar( bool)

	static bool enable_shaders

	mouse_t* get_mouse()

	static void set_selected( shared_ptr<display_kernel> )
	static shared_ptr<display_kernel> get_selected()

	bool hasExtension( const std::string& ext )

	void pushkey(std::string k)

	typedef void (APIENTRYP EXTENSION_FUNCTION)()
	#virtual EXTENSION_FUNCTION getProcAddress( const char* )

	EXTENSION_FUNCTION getProcAddress( const char* )

	virtual void activate( bool active ) = 0
}

} # !namespace cvisual

#endif # !defined VPYTHON_DISPLAY_KERNEL_HPP
