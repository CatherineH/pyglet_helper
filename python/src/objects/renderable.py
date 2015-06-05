# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *

#include "util/rgba.hpp"
#include "util/extent.hpp"
#include "util/displaylist.hpp"
#include "util/texture.hpp"
#include "util/gl_extensions.hpp"
#include <boost/shared_ptr.hpp>

#include <map>
int N_LIGHT_TYPES = 1
'''
not sure what z_comparator does...
'''
'''
    This primarily serves as a means of communicating information down to the
	various primitives that may or may not need it from the render_surface.  Most
	of the members are simply references to the real values in the owning
	render_surface.
'''
class view:
    def __init__(self, gcf = gcf(), anaglyph = False, coloranaglyph = False, lod_adjust = 0, tan_hfov_x = 0, tan_hfov_y = 0, enable_shaders = True):
        # The position of the camera in world space.
        self.camera = vector()
        # The direction the camera is pointing - a unit vector.
        self.forward = vector()
        # The center of the scene in world space.
        self.center = vector()
        # The true up direction of the scene in world space.
        self.up = vector()
        # The width of the viewport in pixels.
        self.view_width
        # The height of the viewport in pixels.
        self.view_height
        # True if the forward vector changed since the last rending operation.
        self.forward_changed
        # The Global Scaling Factor
        self.gcf = gcf
        # The vector version of the Global Scaling Factor, for scene.uniform=0
        self.gcfvec = vector()
        # True if gcf changed since the last render cycle.
        self.gcf_changed
        # The user adjustment to the level-of-detail.
        self.lod_adjust = lod_adjust
        # True in anaglyph stereo rendering modes.
        self.anaglyph = anaglyph
        # True in coloranaglyph stereo rendering modes.
        self.coloranaglyph = coloranaglyph
        self.tan_hfov_x = tan_hfov_x #< The tangent of half the horzontal field of view.
        self.tan_hfov_y = tan_hfov_y#< The tangent of half the vertical field of view.

        self.box_model = displaylist()
        self.sphere_model = [displaylist()]*6
        self.cylinder_model = [displaylist()]*6
        self.cone_model = [displaylist()]*6
        self.pyramid_model = displaylist()
        self.glext = gl_extensions()
        self.camera_world = tmatrix()
        self.light_count = [0]*N_LIGHT_TYPES
        self.light_pos = vector()
        self.light_color = vector()# in eye coordinates!

        self.enable_shaders = enable_shaders

    def view(self, n_forward = forward(), n_center = vector(), n_width = view_width(),\
      n_height = view_height(), n_forward_changed = forward_changed(), n_gcf = gcf(),\
      n_gcfvec = gcfvec(), n_gcf_changed = gcf_changed(), glext = glext()):
        for i in range(0, N_LIGHT_TYPES):
            self.light_count[i] = 0
    '''
     Called on a copy of a parent view to make this a view in a child
     frame.  pft is a transform from the parent to the frame coordinate
     space.
    '''
    def apply_frame_transform(self, pft):

    '''
     Compute the apparent diameter, in pixels, of a circle that is parallel
     to the screen, with a center at pos, and some radius.  If pos is behind
     the camera, it will return negative.
    '''
    def pixel_coverage(self, pos, radius):

'''
Virtual base class for all renderable objects and composites.
'''
class renderable:
    def __init__(self, color = rgb(), mat = material(), opacity = 1.0, visible = False):
        '''
    	The base color of this body.  Ignored by the variable-color composites
    	(curve, faces, frame).
    	'''
    	self.color = color
        # Fully opaque is 1.0, fully transparent is 0.0:
        self.opacity = opacity
        #True if the object should be rendered on the screen.
    	self.visible = visible
        self.mat = mat


	'''
     Applies materials and other general features and calls gl_render().
	 For now, also calls refresh_cache(), but that might be moved back in
	 order to make that function compute center.
     '''
	def outer_render(self, view):

    '''
    Called when rendering for mouse hit testing.  Since the result is not
	 visible, subclasses should not perform texture mapping or blending,
	 and should use the lowest-quality level of detail that covers the
	 geometry.
	'''
	def gl_pick_render(self, view):

	'''
    Report the total extent of the object.
    '''
	def grow_extent(self, extent):


	'''
    Report the approximate center of the object.  This is used for depth
	 sorting of the transparent models.
    '''
    def get_center(self):

    @property
    def material(self):
    @mat.setter
	def material(self, m):

    def get_material_matrix(self, view):

	def translucent(self):

	def render_lights(self, view):

	def is_light(self):
        return False

	def get_children(self):

    '''
     Called by outer_render when drawing to the screen.  The default
     is to do nothing.
    '''
    def gl_render(self, view):
