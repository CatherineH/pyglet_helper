# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pygletHelper.util.rgba import rgb
from pygletHelper.util.vector import vector
from pygletHelper.util.displaylist import displaylist
from pygletHelper.util.tmatrix import tmatrix
from pygletHelper.objects.material import material
N_LIGHT_TYPES = 1

'''
Virtual base class for all renderable objects and composites.
'''


class renderable(object):
    def __init__(self, color = rgb(), mat = material(), opacity = 1.0, visible = False):
        # The base color of this body.  Ignored by the variable-color composites
        # (curve, faces, frame).
        self.color = color
        # Fully opaque is 1.0, fully transparent is 0.0:
        self.opacity = opacity
        #True if the object should be rendered on the screen.
        self.visible = visible
        self.mat = mat

    @property
    def material(self):
        return self.mat
    @material.setter
    def material(self, m):
        self.mat = m

    def translucent(self):

        return self.opacity != 1.0 or (self.mat and self.mat.translucent)

    def is_light(self):
        return False

    def outer_render(self, view):
        # Applies materials and other general features and calls gl_render().
        # For now, also calls refresh_cache(), but that might be moved back in
        # order to make that function compute center.
        actual_color = self.color
        if (self.v.anaglyph):
            if (self.v.coloranaglyph):
                self.color = actual_color.desaturate()
            else:
                self.color = actual_color.grayscale()
        get_material_matrix(self.v, material_matrix)
        use_mat(self.v, self.mat.get(), material_matrix )
        gl_render(self.v)

        if (self.v.anaglyph):
            self.color = actual_color

'''
    This primarily serves as a means of communicating information down to the
    various primitives that may or may not need it from the render_surface.  Most
    of the members are simply references to the real values in the owning
    render_surface.
'''
class view(object):
    def __init__(self, n_gcf = 1.0, view_width = 800, view_height = 600, anaglyph = False, coloranaglyph = False, forward_changed = False, gcf_changed = False, lod_adjust = 0, tan_hfov_x = 0, tan_hfov_y = 0, enable_shaders = True):
        # The position of the camera in world space.
        self.camera = vector()
        # The direction the camera is pointing - a unit vector.
        self.forward = vector()
        # The center of the scene in world space.
        self.center = vector()
        # The true up direction of the scene in world space.
        self.up = vector()
        # The width of the viewport in pixels.
        self.view_width = view_width
        # The height of the viewport in pixels.
        self.view_height = view_height
        # True if the forward vector changed since the last rending operation.
        self.forward_changed = forward_changed
        # The Global Scaling Factor
        self.gcf = n_gcf
        # The vector version of the Global Scaling Factor, for scene.uniform=0
        self.gcfvec = vector()
        # True if gcf changed since the last render cycle.
        self.gcf_changed = gcf_changed
        # The user adjustment to the level-of-detail.
        self.lod_adjust = lod_adjust
        # True in anaglyph stereo rendering modes.
        self.anaglyph = anaglyph
        # True in coloranaglyph stereo rendering modes.
        self.coloranaglyph = coloranaglyph
        self.tan_hfov_x = tan_hfov_x #< The tangent of half the horzontal field of view.
        self.tan_hfov_y = tan_hfov_y#< The tangent of half the vertical field of view.

        # not sure what this does...

        self.box_model = displaylist()
        self.sphere_model = [displaylist()]*6
        self.cylinder_model = [displaylist()]*6
        self.cone_model = [displaylist()]*6
        self.pyramid_model = displaylist()

        # TODO: implement gl extensions
        #self.glext = gl_extensions()
        self.camera_world = tmatrix()
        self.light_count = [0]*N_LIGHT_TYPES
        self.light_pos = vector()
        self.light_color = vector()# in eye coordinates!

        self.enable_shaders = enable_shaders

    '''
     Called on a copy of a parent view to make this a view in a child
     frame.  pft is a transform from the parent to the frame coordinate
     space.
    '''
    def apply_frame_transform(self, wft):
        self.camera = wft * self.camera
        self.forward = wft.times_v( self.forward )
        self.center = wft * self.center
        self.up = wft.times_v(self.up)
        tso = screen_objects_t( (z_comparator(self.forward)) )
        screen_objects.swap( tso )

    '''
     Compute the apparent diameter, in pixels, of a circle that is parallel
     to the screen, with a center at pos, and some radius.  If pos is behind
     the camera, it will return negative.
    '''
    def pixel_coverage(self, pos, radius):
        # The distance from the camera to this position, in the direction of the
        # camera.  This is the distance to the viewing plane that the coverage
        # circle lies in.

        pos = vector(pos)
        dist = (pos - self.camera).dot(self.forward)
        # Half of the width of the viewing plane at this distance.
        apparent_hwidth = self.tan_hfov_x * dist
        # The fraction of the apparent width covered by the coverage circle.
        if apparent_hwidth == 0:
            coverage_fraction = 1
        else:
            coverage_fraction = radius / apparent_hwidth
        # Convert from fraction to pixels.
        return coverage_fraction * self.view_width
