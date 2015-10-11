# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from math import pi

from enum import Enum

from pygletHelper.objects.mouseobject import MouseBase
from pygletHelper.objects.mouse_manager import MouseButton
from pygletHelper.util import color
from pygletHelper.util.vector import Vector


class MouseModeT(Enum):
    ZOOM_ROTATE = 1
    ZOOM_ROLL = 2
    PAN = 3
    FIXED = 4


class StereoModeT(Enum):
    NO_STEREO = 1
    PASSIVE_STEREO = 2
    ACTIVE_STEREO = 3
    CROSS_EYED_STEREO = 4
    RED_BLUE_STEREO = 5
    RED_CYAN_STEREO = 6
    YELLOW_BLUE_STEREO = 7
    GREEN_MAGENTA_STEREO = 8


displays_visible = 0
enable_shaders = True


def set_display_visible(display_kernel, visible):
    if visible:
        displays_visible += 1
    else:
        displays_visible -= 1


'''
 A class that manages all OpenGL aspects of a given scene.  This class
 requires platform-specific support from render_surface to manage an OpenGL
 rendering context and mouse and keyboard interaction.
'''

class DisplayKernel(object):
    def __init__(self, exit=True, visible=False, explicitly_invisible=False,
                 fullscreen=False, title="Python", window_x=0, window_y=0, window_width=430,
                 window_height=450, view_width=-1, view_height=-1, center=[0, 0, 0],
                 forward=[0, 0, -1], internal_forward=[0, 0, -1], up=[0, 1, 0], forward_changed=True,
                 fov=60 * pi / 180.0, auto_scale=True, auto_center=False, uniform=True,
                 camera=[0, 0, 0], user_scale=1.0, gcf=1.0, gcfvec=[1.0, 1.0, 1.0],
                 gcf_changed=False, ambient=[0.2, 0.2, 0.2], show_toolbar=False, last_time=0,
                 background=[0, 0, 0], spin_allowed=True, zoom_allowed=True, mouse_mode=MouseModeT.ZOOM_ROTATE,
                 stereo_mode=StereoModeT.NO_STEREO, stereo_depth=0.0, lod_adjust=0, realized=False,
                 mouse=MouseBase(), range_auto=0.0, range=[0, 0, 0], world_extent=0.0, foreground=color.white):
        self._show_toolbar = None
        self.extensions = ''
        self.renderer = ''
        self.version = ''
        self.vendor = ''
        self.last_time = last_time
        self.render_time = 0
        self.realized = realized
        self.selected = ''

        self.center = center  # The observed center of the display, in world space.
        self.forward = forward  # The direction of the camera, in world space.
        self.up = up  # The vertical orientation of the scene, in world space.
        self.internal_forward = internal_forward  # /< Do not permit internal_forward to be +up or -up
        self.range = range  # /< Explicitly specified scene.range, or (0,0,0)
        self.camera = camera  # < World coordinates of camera location
        self.range_auto = range_auto  # < Automatically determined camera z from autoscale

        # True initally and whenever the camera direction changes.  Set to false
        # after every render cycle.
        self.forward_changed = forward_changed

        self.world_extent = world_extent  # /< The extent of the current world.

        self.fov = fov  # /< The field of view, in radians
        self.stereo_depth = stereo_depth  # < How far in or out of the screen the scene seems to be
        self.auto_scale = auto_scale  # /< True if Visual should scale the camera's position automatically.
        # True if Visual should automatically reposition the center of the scene.
        self.auto_center = auto_center
        # True if the autoscaler should compute uniform axes.
        self.uniform = uniform
        # A scaling factor determined by middle mouse button scrolling.
        self.user_scale = user_scale
        # The global scaling factor. It is used to ensure that objects with
        # large dimensions are rendered properly. See the .cpp file for details.
        self.gcf = gcf
        # Vector version of the global scaling factor used when scene.uniform=0.
        # Affects just curve, points, faces, label, frame, and conversion of mouse coordinates.
        self.gcf_vec = gcf_vec

        # True if the gcf has changed since the last render cycle.  Set to false
        # after every rendering cycle.
        self.gcf_changed = gcf_changed

        self.ambient = ambient  # /< The ambient light color.

        self.background = background  # /< The background color of the scene.
        self.foreground = foreground  # /< The default color for objects to be rendered into the scene.

        # Whether or not the user is allowed to spin or zoom the display
        self.spin_allowed = spin_allowed
        self.zoom_allowed = zoom_allowed

        # Opaque objects to be rendered into world space.
        # self.world_iterator = indirect_iterator()

        # objects with a nonzero level of transparency that need to be depth sorted
        # prior to rendering.
        self.layer_world_transparent = Vector()
        # self.world_trans_iterator = indirect_iterator()
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

        self.exit = exit  # /< True when Visual should shutdown on window close.
        self.visible = visible  # /< scene.visible
        self.explicitly_invisible = explicitly_invisible  # /< true iff scene.visible has ever been set to 0 by the program, or by the user closing a window
        self.fullscreen = fullscreen  # /< True when the display is in fullscreen mode.
        self.show_toolbar = show_toolbar  # /< True when toolbar is displayed (pan, etc).
        self.title = title

        # Older machines should set this to some number between -6 and 0.  All of
        # the tesselated models choose a lower level of detail based on this value
        # when it is less than 0.
        self.lod_adjust = lod_adjust
        self.realized = realized

        # self.glext = gl_extensions()
        self.mouse_mode_t = MouseModeT
        self.mouse_button = mouse_button
        self.stereo_mode_t = StereoModeT

    def enable_lights(self, scene):
        """
        Called at the beginning of a render cycle to establish lighting.
        """
        scene.light_count[0] = 0
        scene.light_pos.clear()
        scene.light_color.clear()
        i = self.layer_world.begin()
        i_end = self.layer_world.end()
        while i != i_end:
            i.render_lights(scene)
            i += 1
        j = self.layer_world_transparent.begin()
        j_end = self.layer_world_transparent.end()
        while j != j_end:
            j.render_lights(scene)

        world_camera.gl_modelview_get()
        p = vertex()

        # Clear modelview matrix since we are multiplying the light positions ourselves
        glLoadIdentity()
        limit = min([scene.light_count[0], 8])
        for i in range(0, limit):
            li = i * 4

            # Transform the light into eye space
            for d in range(0, 4):
                p[d] = scene.light_pos[li + d]
                p = world_camera * p
            for d in range(0, 4):
                scene.light_pos[li + d] = p[d]

            # Enable the light for fixed function lighting.  This is unnecessary if everything in the scene
            # uses materials and the card supports our shaders, but for now...
            id = GL_LIGHT0 + i
            glLightfv(id, GL_DIFFUSE, scene.light_color[li])
            glLightfv(id, GL_SPECULAR, scene.light_color[li])
            glLightfv(id, GL_POSITION, scene.light_pos[li])
            glEnable(id)

        for i in range(scene.light_count[0], 8):
            glDisable(GL_LIGHT0 + i)

        glEnable(GL_LIGHTING)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self.ambient.red)

    def disable_lights(self):
        """
        Called at the end of a render cycle to complete lighting.
        """
        glDisable(GL_LIGHTING)

    def world_to_view_transform(self, view, whicheye=0, forpick=False):
        """
        Set up matrices for transforms from world coordinates to view coordinates
        Precondition: the OpenGL Modelview and Projection matrix stacks should be
        at the bottom.
        Postcondition: active matrix stack is GL_MODELVIEW, matrix stacks are at
        the bottom.  Viewing transformations have been applied.  geometry.camera
        is initialized.
        whicheye: -1 for left, 0 for center, 1 for right.
        """
        # See http://www.stereographics.com/support/developers/pcsdk.htm for a
        # discussion regarding the design basis for the frustum offset code.

        # gcf scales the region encompassed by scene.range_* into a ROUGHLY 2x2x2 cube.
        # Note that this is NOT necessarily the entire world, since scene.range
        # can be changed.
        # This coordinate system is used for most of the calculations below.

        scene_center = self.center.scale(self.gcfvec)
        scene_up = self.up.norm()
        scene_forward = self.internal_forward.norm()

        # the horizontal and vertical tangents of half the field of view.
        [tan_hfov_x, tan_hfov_y] = self.tan_hfov()

        # The cotangent of half of the wider field of view.
        if not self.uniform:  # We force width to be 2.0 (range.x 1.0)
            cot_hfov = 1.0 / tan_hfov_x
        else:
            cot_hfov = 1.0 / max([tan_hfov_x, tan_hfov_y])

        # The camera position is chosen by the tightest of the enabled range_* modes.
        cam_to_center_without_zoom = 1e150

        if self.range_auto:
            cam_to_center_without_zoom = min([cam_to_center_without_zoom, range_auto])
        if self.range.nonzero():
            cam_to_center_without_zoom = min(cam_to_center_without_zoom, range.x * cot_hfov / 1.02)
        if cam_to_center_without_zoom >= 1e150:
            cam_to_center_without_zoom = 10.0 / sin(self.fov * 0.5)
        cam_to_center_without_zoom *= self.gcf * 1.02

        # Position camera so that a sphere containing the box range will fit on the screen
        #   OR a 2*user_scale cube will fit.  The former is tighter for "non cubical" ranges
        #   and the latter is tighter for cubical ones.
        scene_camera = scene_center - cam_to_center_without_zoom * self.user_scale * self.scene_forward
        # nearest and farthest points relative to scene.center when projected onto forward

        [nearest, farthest] = world_extent.get_near_and_far(internal_forward, nearest, farthest)
        nearest = nearest * self.gcf
        farthest = farthest * self.gcf

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
        # TODO: nearclip = max( nearclip, (cam_to_center + nearest) * 0.95 )
        #  ?? boost z buffer resolution if there's nothing close to camera?
        farclip = (farthest + cam_to_center) * 1.05  # < actual maximum z in scene plus a little
        farclip = max([farclip, nearclip * 1.001])  # < just in def set_everything is behind the camera!

        # Here is the stereodepth and eye offset machinery from Visual 3, where the docs claimed that
        # stereodepth=0 was the default (zero-parallax plane at screen surface
        # stereodepth=1 moves the center of the scene to the screen surface
        # stereodepth=2 moves the back of the scene to the screen surface:

        # A multiple of the number of cam_to_center's away from the camera to place
        # the zero-parallax plane.
        # The distance from the camera to the zero-parallax plane.
        focallength = cam_to_center + 0.5 * self.stereodepth
        # Translate camera left/right 2% of the viewable width of the scene at
        # the distance of its center.
        camera_stereo_offset = tan_hfov_x * focallength * 0.02
        camera_stereo_delta = camera_stereo_offset * self.up.cross(scene_camera).norm() * whicheye
        scene_camera += camera_stereo_delta
        scene_center += camera_stereo_delta
        # The amount to translate the frustum to the left and right.
        frustum_stereo_offset = camera_stereo_offset * nearclip / focallength * whicheye

        # Finally, the OpenGL transforms based on the geometry just calculated.
        clear_gl_error()
        # Position the camera.
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # if 0	# Enable this to peek at the actual scene geometry.
        max_proj_stack_depth = glGetIntegerv(GL_MAX_PROJECTION_STACK_DEPTH)
        max_mv_stack_depth = glGetIntegerv(GL_MAX_MODELVIEW_STACK_DEPTH)
        proj_stack_depth = glGetIntegerv(GL_PROJECTION_STACK_DEPTH)
        mv_stack_depth = glGetIntegerv(GL_MODELVIEW_STACK_DEPTH)
        print "scene_geometry: camera:" + str(scene_camera) \
              + " true camera:" + str(self.camera) + "\n" \
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

        gluLookAt(scene_camera.x, scene_camera.y, scene_camera.z,
                  scene_center.x, scene_center.y, scene_center.z,
                  scene_up.x, scene_up.y, scene_up.z)

        world_camera = gl_modelview_get()
        inverse(geometry.camera_world, world_camera)

        # Establish a parallel-axis asymmetric stereo projection frustum.
        glMatrixMode(GL_PROJECTION)
        if not forpick:
            glLoadIdentity()
        if whicheye == 1:
            frustum_stereo_offset = -frustum_stereo_offset
        elif whicheye == 0:
            frustum_stereo_offset = 0

        if self.nearclip <= 0 or self.farclip <= self.nearclip or tan_hfov_x <= 0 or tan_hfov_y <= 0:
            raise RunTimeEror("degenerate projection: " + str(self.nearclip) + " " + str(self.farclip) + " " + str(
                tan_hfov_x) + " " + str(tan_hfov_y))

        glFrustum(-self.nearclip * tan_hfov_x + frustum_stereo_offset,
                  self.nearclip * tan_hfov_x + frustum_stereo_offset,
                  -self.nearclip * tan_hfov_y,
                  self.nearclip * tan_hfov_y,
                  self.nearclip,
                  self.farclip)

        glMatrixMode(GL_MODELVIEW)

        # The true camera position, in world space.
        self.camera = scene_camera / gcf

        # Finish initializing the view object.
        geometry.camera = self.camera
        geometry.tan_hfov_x = tan_hfov_x
        geometry.tan_hfov_y = tan_hfov_y
        # The true viewing vertical direction is not the same as what is needed for
        geometry.up = internal_forward.cross_b_cross_c(up, internal_forward).norm()

    def draw(self, scene_geometry, whicheye=0):
        """
         Renders the scene for one eye.
            @param scene The dimensions of the scene, to be propogated to this
                display_kernel's children.
            @param eye Which eye is being rendered.  -1 for the left, 0 for the
                center, and 1 for the right.
            @param scene_geometry.anaglyph  True if using anaglyph stereo requiring color
                desaturation or grayscaling.
            @param scene_geometry.coloranaglyph  True if colors must be grayscaled, false if colors
                must be desaturated.
        """
        # Set up the base modelview and projection matrices
        self.world_to_view_transform(scene_geometry, whicheye)
        # Render all opaque objects in the world space layer
        enable_lights(scene_geometry)
        i = world_iterator(layer_world.begin())
        i_end = world_iterator(layer_world.end())
        while i != i_end:
            if i.translucent():
                # The color of the object has become transparent when it was not
                # initially.  Move it to the transparent layer.  The penalty for
                # being rendered in the transparent layer when it is opaque is only
                # a small speed hit when it has to be sorted.  Therefore, that case
                # is not tested at all.  (TODO Untrue-- rendering opaque objects in transparent
                # layer makes it possible to have opacity artifacts with a single convex
                # opaque objects, provided other objects in the scene were ONCE transparent)
                self.layer_world_transparent.push_back(i.base())
                i = layer_world.erase(i.base())
                continue
            i.outer_render(scene_geometry)
            i += 1

        # Perform a depth sort of the transparent world from back to front.
        if self.layer_world_transparent.size() > 1:
            stable_sort(self.layer_world_transparent.begin(), self.layer_world_transparent.end(),
                        z_comparator(self.internal_forward.norm()))

        # Render translucent objects in world space.
        j = world_trans_iterator(layer_world_transparent.begin())
        j_end = world_trans_iterator(layer_world_transparent.end())
        while j != j_end:
            j.outer_render(scene_geometry)
            j += 1

        # Render all objects in screen space.
        disable_lights()
        gl_disable(GL_DEPTH_TEST)
        k = screen_iterator(scene_geometry.screen_objects.begin())
        k_end = screen_iterator(scene_geometry.screen_objects.end())
        while k != k_end:
            k.second.gl_render()
            k += 1

        scene_geometry.screen_objects.clear()

        return True

    # Computes the extent of the scene and takes action for autozoom and
    # autoscaling.
    def recalc_extent(self):

        [tan_hfov_x, tan_hfov_y] = self.tan_hfov(tan_hfov_x, tan_hfov_y)
        tan_hfov = max([tan_hfov_x, tan_hfov_y])

        while True:  # < Might have to do this twice for autocenter
            world_extent = self.extent_data(tan_hfov)
            l_cw.translate(-center)
            ext = extent(world_extent, l_cw)
            i = world_iterator(layer_world.begin())
            end = world_iterator(layer_world.end())
            while i != end:
                i.grow_extent(ext)
                i += 1

            j = world_trans_iterator(layer_world_transparent.begin())
            j_end = world_trans_iterator(layer_world_transparent.end())
            while j != j_end:
                j.grow_extent(ext)
                j += 1

            if self.autocenter:
                c = world_extent.get_center() + self.center
                if (self.center - c).mag2() > (self.center.mag2() + c.mag2()) * 1e-6:
                    # Change center and recalculate extent (since camera_z depends on center)
                    self.center = c
                    continue
            break

        if self.autoscale and self.uniform:
            r = world_extent.get_camera_z()
            if r > range_auto:
                range_auto = r
            elif 3.0 * r < range_auto:
                range_auto = 3.0 * r

        # Rough scale calculation for gcf.  Doesn't need to be exact.
        # TODO: If extent and range are very different in scale, we are using extent to drive
        # gcf.  Both options have pros and cons.
        mr = world_extent.get_range(vector(0, 0, 0)).mag()
        if mr is not None or mr != 0.0:
            scale = 1.0 / mr
        else:
            scale = 1.0

        if not uniform and self.range.nonzero():
            self.gcf_changed = True
            self.gcf = 1.0 / self.range.x
            if self.stereo_mode == PASSIVE_STEREO or self.stereo_mode == CROSSEYED_STEREO:
                width = self.view_width * 0.5
            else:
                width = self.view_width
            self.gcfvec = vector(1.0 / self.range.x, (self.view_height / width) / self.range.y, 0.1 / self.range.z)
        else:
            # TODO: Instead of changing gcf so much, we could change it only when it is 2x
            # off, to aid primitives whose caching may depend on gcf (but are there any?)
            if self.gcf is not scale:
                self.gcf = scale
                self.gcf_changed = True
            self.gcfvec = vector(self.gcf, self.gcf, self.gcf)

    # Compute the tangents of half the vertical and half the horizontal
    # true fields-of-view.
    def tan_hfov(self):
        # tangent of half the field of view.
        tan_hfov = tan(self.fov * 0.5)
        aspect_ratio = self.view_height / self.view_width
        if self.stereo_mode == PASSIVE_STEREO or self.stereo_mode == CROSSEYED_STEREO:
            aspect_ratio *= 2.0
        if aspect_ratio > 1.0:
            # Tall window
            x = tan_hfov / aspect_ratio
            y = tan_hfov
        else:
            # Wide window
            x = tan_hfov
            y = tan_hfov * aspect_ratio
        return [x, y]

    def realize(self):
        clear_gl_error()
        if not self.extensions:
            self.extensions.reset('')
            strm = glGetString(GL_EXTENSIONS)
            copy(strm, '', inserter(self.extensions, self.extensions.begin()))

            vendor = glGetString(GL_VENDOR)
            version = glGetString(GL_VERSION)
            renderer = glGetString(GL_RENDERER)

        # The test is a hack so that subclasses not bothering to implement getProcAddress just
        # don't get any extensions.


        # Those features of OpenGL that are always used are set up here.
        # Depth buffer properties
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # Lighting model properties
        glShadeModel(GL_SMOOTH)
        # TODO: Figure out what the concrete costs/benefits of these commands are.
        # glHint( GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_NORMALIZE)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Ensures that fully transparent pixels don't write into the depth buffer,
        # ever.
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0.0)

        # FSAA.  Doesn't seem to have much of an effect on my TNT2 card.  Grrr.
        if has_extension("GL_ARB_multisample"):
            glEnable(GL_MULTISAMPLE_ARB)
            n_samples = glGetIntegerv(GL_SAMPLES_ARB)
            n_buffers = glGetIntegerv(GL_SAMPLE_BUFFERS_ARB)
        check_gl_error()

    def implicit_activate(self):
        if not self.visible and not self.explicitly_invisible:
            self.visible = True

    def add_renderable(self, obj):
        """
        Add a normal renderable object to the list of objects to be rendered into
        world space.
        """
        if not obj.translucent():
            self.layer_world.push_back(obj)
        else:
            self.layer_world_transparent.push_back(obj)
        if not obj.is_light():
            self.implicit_activate()

    def remove_renderable(self, obj):
        """
          Remove a renderable object from this display, regardless of which layer
           it resides in.
        """
        if not obj.translucent():
            remove(self.layer_world.begin(), self.layer_world.end(), obj)
            self.layer_world.pop_back()
        else:
            remove(self.layer_world_transparent.begin(), self.layer_world_transparent.end(), obj)
            self.layer_world_transparent.pop_back()

    # Compute the location of the camera based on the current geometry.
    def calc_camera(self):
        return self.camera

    def render_scene(self):
        """
         Renders the scene once.  The enveloping widget is resposible for calling
         this function appropriately.
          @return If false, something catastrophic has happened and the
          application should probably exit.
        """
        print("starting render")
        # TODO: Exception handling?
        if not self.realized:
            self.realize()

        try:
            self.recalc_extent()

            scene_geometry = view(self.internal_forward.norm(), self.center, self.view_width,
                                  self.view_height, self.forward_changed, self.gcf, self.gcfvec, self.gcf_changed,
                                  self.glext)
            scene_geometry.lod_adjust = self.lod_adjust
            scene_geometry.enable_shaders = enable_shaders
            clear_gl_error()

            on_gl_free.frame()

            glClearColor(self.background.red, self.background.green, self.background.blue, 0)
            modes = {NO_STEREO: self.set_no_stere, ACTIVE_STEREO: self.set_active_stereo,
                     RED_BLUE_STEREO: self.set_red_blue_stereo, RED_CYAN_STEREO: self.set_red_cyan_stereo,
                     YELLOW_BLUE_STEREO: self.set_yellow_blue_stereo,
                     GREEN_MAGENTA_STEREO: self.set_green_magenta_stereo, PASSIVE_STEREO: self.set_passive_stereo,
                     CROSS_EYED_STEREO: self.set_cross_eyed_stereo}
            modes[self.stereo_mode]()
            print("stereo mode: " + str(self.stereo_mode))
            # Cleanup
            check_gl_error()
            self.gcf_changed = False
            self.forward_changed = False

        except gl_error as e:
            raise RunTimeError("render_scene OpenGL error: " + e.what() + ", aborting.\n")
        except Exception as e:
            print "something went wrong: " + str(e)

        # TODO: Can we delay picking until the Python program actually wants one of these attributes?
        mouse.get_mouse().cam = camera

        on_gl_free.frame()

        return True

    def set_no_stereo(self, scene_geometry):
        scene_geometry.anaglyph = False
        scene_geometry.coloranaglyph = False
        glViewport(0, 0, self.view_width, self.view_height)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw(scene_geometry, 0)

    def set_active_stereo(self, scene_geometry):
        scene_geometry.anaglyph = False
        scene_geometry.coloranaglyph = False
        glViewport(0, 0, self.view_width, self.view_height)
        glDrawBuffer(GL_BACK_LEFT)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw(scene_geometry, -1)
        glDrawBuffer(GL_BACK_RIGHT)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw(scene_geometry, 1)

    def set_red_blue_stereo(self, scene_geometry):
        # Red channel
        scene_geometry.anaglyph = True
        scene_geometry.coloranaglyph = False
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.view_width, self.view_height)
        glColorMask(GL_TRUE, GL_FALSE, GL_FALSE, GL_TRUE)
        self.draw(scene_geometry, -1)
        # Blue channel
        glColorMask(GL_FALSE, GL_FALSE, GL_TRUE, GL_TRUE)
        glClear(GL_DEPTH_BUFFER_BIT)
        self.draw(scene_geometry, 1)
        # Put everything back
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

    def set_red_cyan_stereo(self, scene_geometry):
        # Red channel
        scene_geometry.anaglyph = True
        scene_geometry.coloranaglyph = True
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.view_width, self.view_height)
        glColorMask(GL_TRUE, GL_FALSE, GL_FALSE, GL_TRUE)
        self.draw(scene_geometry, -1)
        # Green and Blue channels
        glColorMask(GL_FALSE, GL_TRUE, GL_TRUE, GL_TRUE)
        glClear(GL_DEPTH_BUFFER_BIT)
        self.draw(scene_geometry, 1)
        # Put everything back
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

    def set_yellow_blue_stereo(self, scene_geometry):
        # Red and green channels
        scene_geometry.anaglyph = True
        scene_geometry.coloranaglyph = True
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.view_width, self.view_height)
        glColorMask(GL_TRUE, GL_TRUE, GL_FALSE, GL_TRUE)
        self.draw(scene_geometry, -1)
        # Blue channel
        glColorMask(GL_FALSE, GL_FALSE, GL_TRUE, GL_TRUE)
        glClear(GL_DEPTH_BUFFER_BIT)
        self.draw(scene_geometry, 1)
        # Put everything back
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

    def set_green_majenta_stereo(self, scene_geometry):
        # Green channel
        scene_geometry.anaglyph = True
        scene_geometry.coloranaglyph = True
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.view_width, self.view_height)
        glColorMask(GL_FALSE, GL_TRUE, GL_FALSE, GL_TRUE)
        self.draw(scene_geometry, -1)
        # Red and blue channels
        glColorMask(GL_TRUE, GL_FALSE, GL_TRUE, GL_TRUE)
        glClear(GL_DEPTH_BUFFER_BIT)
        self.draw(scene_geometry, 1)
        # Put everything back
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

    def set_passive_stereo(self, scene_geometry):
        # Also handle viewport modifications.
        scene_geometry.view_width = self.view_width / 2
        scene_geometry.anaglyph = False
        scene_geometry.coloranaglyph = False
        stereo_width = int(scene_geometry.view_width)
        # Left eye
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.stereo_width, self.view_height)
        draw(scene_geometry, -1)
        # Right eye
        glViewport(stereo_width + 1, 0, self.stereo_width, self.view_height)
        self.draw(scene_geometry, 1)

    def set_cross_eyed_stereo(self, scene_geometry):
        # Also handle viewport modifications.
        scene_geometry.view_width = view_width / 2
        scene_geometry.anaglyph = False
        scene_geometry.coloranaglyph = False
        stereo_width = int(scene_geometry.view_width)
        # Left eye
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.stereo_width, self.view_height)
        self.draw(self.scene_geometry, 1)
        # Right eye
        glViewport(self.stereo_width + 1, 0, self.stereo_width, self.view_height)
        self.draw(scene_geometry, -1)

    def report_closed(self):
        """
         Inform this object that the window has been closed (is no longer physically
         visible)
        """
        if self.visible:
            self.set_display_visible(self, False)
        self.realized = False
        self.visible = False
        self.explicitly_invisible = True

    def report_camera_motion(self, dx, dy, button):
        """
        Called by mouse_manager to report mouse movement that should affect the camera.
        Report that the mouse moved with one mouse button down.
            @param dx horizontal change in mouse position in pixels.
            @param dy vertical change in mouse position in pixels.
        """

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
        if self.stereo_mode == PASSIVE_STEREO or stereo_mode == CROSS_EYED_STEREO:
            hfrac = float(dx / (self.view_width * 0.5))
        else:
            hfrac = float(dx / self.view_width)

        # The amount by which the scene should be shifted in response to panning
        # motion.
        # TODO: Keep this synchronized with the eye_dist calc in
        # world_view_transform
        [tan_hfov_x, tan_hfov_y] = self.tan_hfov()
        pan_rate = (self.center - self.calc_camera()).mag() * min([tan_hfov_x, tan_hfov_y])

        if button == MIDDLE:
            if self.mouse_mode == PAN:
                # Pan front/back.
                if self.spin_allowed:
                    self.center += pan_rate * vfrac * self.internal_forward.norm()
            if self.mouse_mode == ZOOM_ROLL or self.mouse_mode == ZOOM_ROTATE:
                # Zoom in/out.
                if self.zoom_allowed:
                    self.user_scale *= pow(10.0, vfrac)
        if button == RIGHT:
            if self.mouse_mode == PAN:
                # Pan up/down and left/right.
                # A vector pointing along the camera's horizontal axis.
                horiz_dir = self.internal_forward.cross(self.up).norm()
                # A vector pointing along the camera's vertical axis.
                vert_dir = self.horiz_dir.cross(self.internal_forward).norm()
                if self.spin_allowed:
                    self.center += -horiz_dir * pan_rate * hfrac
                    self.center += vert_dir * pan_rate * vfrac
            if self.mouse_mode == ZOOM_ROTATE:
                if self.spin_allowed:
                    # Rotate
                    # First perform the rotation about the up vector.
                    r = rotation(-hfrac * 2.0, self.up.norm())
                    self.internal_forward = r * self.internal_forward

                    # Then perform rotation about an axis orthogonal to up and forward.
                    vertical_angle = vfrac * 2.0
                    max_vertical_angle = self.up.diff_angle(-self.internal_forward.norm())

                    # Over the top (or under the bottom) rotation
                    if not (vertical_angle >= max_vertical_angle or vertical_angle <= max_vertical_angle - pi):
                        # Over the top (or under the bottom) rotation
                        r = rotation(-vertical_angle, self.internal_forward.cross(self.up).norm())
                        self.forward = self.internal_forward = r * self.internal_forward
                        self.forward_changed = True

    def report_window_resize(self, win_x, win_y, win_w, win_h):
        """
        Report that the position and/or size of the window or drawing area widget has changed.
        Some platforms might not know about position changes they can pass (x,y,new_width,new_height)
        win_* give the window rectangle (see self.window_*)
        v_* give the view rectangle (see self.view_*)
        """
        self.window_x = win_x
        self.window_y = win_y
        self.window_width = win_w
        self.window_height = win_h

    def report_view_resize(self, v_w, v_h):
        self.view_width = max(v_w, 1)
        self.view_height = max(v_h, 1)

    def pick(self, x, y, d_pixels=2.0):
        """
        Determine which object (if any) was picked by the cursor.
        @param x the x-position of the mouse cursor, in pixels.
        @param y the y-position of the mouse cursor, in pixels.
        @param d_pixels the allowable variation in pixels to successfully score
        a hit.
        @return  the nearest selected object, the position that it was hit, and
        the position of the mouse cursor on the near clipping plane.
        retval.get<0>() may be NULL if nothing was hit, in which def set_the
        positions are undefined.
        """
        best_pick = vector()
        pickpos = vector()
        mousepos = vector()
        try:
            clear_gl_error()
            # Notes:
            # culled polygons don't count.  glRasterPos() does count.

            # Allocate a selection buffer of uints.  Format for returned hits is:
            # :uint32: n_names:uint32: minimunm depth:uint32: maximum depth
            # :unit32[n_names]: name_stack
            # n_names is the depth of the name stack at the time of the hit.
            # minimum and maximum depth are the minimum and maximum values in the
            # depth buffer scaled between 0 and 2^32-1. (source is [0,1])
            # name_stack is the full contents of the name stack at the time of the
            # hit.

            hit_buffer_size = max(
                (self.layer_world.size() + self.layer_world_transparent.size()) * 4,
                self.world_extent.get_select_buffer_depth())
            # Allocate an exception-safe buffer for the GL to talk back to us.
            hit_buffer = scoped_array(int(hit_buffer_size))
            # unsigned int hit_buffer[hit_buffer_size]

            # Allocate a vector<shared_ptr<renderable> > to lookup names
            # as they are rendered.
            name_table = Vector()
            # Pass the name stack to OpenGL with glSelectBuffer.
            glSelectBuffer(hit_buffer_size, hit_buffer.get())
            # Enter selection mode with glRenderMode
            glRenderMode(GL_SELECT)
            glClear(GL_DEPTH_BUFFER_BIT)
            # Clear the name stack with glInitNames(), raise the height of the name
            # stack with glPushName() exactly once.
            glInitNames()
            glPushName(0)

            # Initialize the picking matrix.
            viewport_bounds = GLint(0, 0, self.view_width, self.view_height)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPickMatrix(x, (self.view_height - y), d_pixels, d_pixels, self.viewport_bounds)
            scene_geometry = view(self.internal_forward.norm(), self.center, self.view_width, self.view_height,
                                  self.forward_changed, self.gcf, self.gcfvec, self.gcf_changed, self.glext)
            scene_geometry.lod_adjust = self.lod_adjust
            world_to_view_transform(scene_geometry, 0, True)

            # Iterate across the world, rendering each body for picking.
            i = layer_world.begin()
            i_end = layer_world.end()
            while i != i_end:
                glLoadName(name_table.size())
                name_table.push_back(i)
                i.gl_pick_render(scene_geometry)
                i += 1

            j = self.layer_world_transparent.begin()
            j_end = self.layer_world_transparent.end()
            while j != j_end:
                glLoadName(name_table.size())
                name_table.push_back(j)
                j.gl_pick_render(scene_geometry)
                j += 1

            # Return the name stack to the bottom with glPopName() exactly once.
            glPopName()

            # Exit selection mode, return to normal rendering rendering. (collects
            # the number of hits at this time).
            n_hits = glRenderMode(GL_RENDER)
            check_gl_error()

            # Lookup the name to get the shared_ptr<renderable> associated with it.
            # The farthest point away in the depth buffer.
            best_pick_depth = 1.0
            hit_record = hit_buffer.get()
            hit_buffer_end = hit_buffer.get() + hit_buffer_size
            while n_hits > 0 and hit_record < hit_buffer_end:
                n_names = hit_record[0]
                if hit_record + 3 + n_names > hit_buffer_end:
                    break
                min_hit_depth = hit_record[1] / 268435455
                if min_hit_depth < best_pick_depth:
                    best_pick_depth = min_hit_depth
                    best_pick = name_table[hit_record + 3]
                if n_names > 1:
                    # Then the picked object is the child of a frame.
                    ref_frame = best_pick.get()
                    assert (ref_frame is not None)
                    best_pick = ref_frame.lookup_name(hit_record + 4, hit_record + 3 + n_names)

                hit_record += 3 + n_names
                n_hits -= 1

            if hit_record > hit_buffer_end:
                raise ("More objects were picked than could be reported by the GL."
                       "  The hit buffer size was too small.")

            modelview.gl_modelview_get()
            projection = tmatrix()
            projection.gl_projection_get()
            pickpos.x, pickpos.y, pickpos.z = gluUnProject(x, self.view_height - y, self.best_pick_depth,
                                                           modelview.matrix_addr(), projection.matrix_addr(),
                                                           viewport_bounds)
            # TODO: Replace the calls to gluUnProject() with own tmatrix inverse
            # and such for optimization
            tcenter.x, tcenter.y, tcenter.z = gluProject(self.center.x * self.gcf, self.center.y * self.gcf,
                                                         self.center.z * sel.fgcf, modelview.matrix_addr(),
                                                         projection.matrix_addr(), viewport_bounds)
            mousepos.x, mousepos.y, mousepos.z = gluUnProject(x, self.view_height - y, tcenter.z,
                                                              modelview.matrix_addr(), projection.matrix_addr(),
                                                              viewport_bounds)
        except gl_error as e:
            raise "pick OpenGL error: " + e + ", aborting.\n"

        pickpos.x /= self.gcfvec.x
        pickpos.y /= self.gcfvec.y
        pickpos.z /= self.gcfvec.z
        mousepos.x /= self.gcfvec.x
        mousepos.y /= self.gcfvec.y
        mousepos.z /= self.gcfvec.z
        return [best_pick, pickpos, mousepos]

    def gl_free(self):
        """
        Release GL resources.  Call this as many times as you like during the
        shutdown.  However, neither pick() nor render_scene() may be called on
        any display_kernel after gl_free() has been invoked.
        """
        try:
            clear_gl_error()
            on_gl_free.shutdown()
            check_gl_error()
        except Exception as error:
            raise ("Caught OpenGL error during shutdown: " + error + " Continuing with the shutdown.")

    def allow_spin(self, b):
        self.spin_allowed = b

    def spin_is_allowed(self):
        return self.spin_allowed

    def allow_zoom(self, b):
        self.zoom_allowed = b

    def zoom_is_allowed(self):
        return self.zoom_allowed

    # Python properties
    @property
    def up(self):
        return self.up

    @up.setter
    def up(self, n_up):
        if n_up == vector():
            raise ValueError("Up cannot be zero.")
        v = n_up.norm()
        # if internal_forward parallel to new up, move it away from new up
        if v.cross(self.internal_forward) == vector():
            # old internal_forward was not parallel to old up
            if v.cross(self.forward) == vector():
                self.internal_forward = (self.forward - 0.0001 * self.up).norm()
            else:
                self.internal_forward = self.forward
        self.up = v

    @property
    def forward(self):
        return self.forward

    @forward.setter
    def forward(self, n_forward):
        if n_forward == vector():
            raise ValueError("Forward cannot be zero.")
        v = n_forward.norm()
        if v.cross(self.up) == vector():
            # if new forward parallel to up, move internal_forward away from up
            # old internal_forward was not parallel to up
            self.internal_forward = (v.dot(self.up) * self.up +
                                     0.0001 * self.up.cross(self.internal_forward.cross(self.up))).norm()
        else:
            # since new forward not parallel to up, new forward is okay
            self.internal_forward = v
            self.forward = v
        self.forward_changed = True

    @property
    def scale(self):
        if self.autoscale or not self.range.nonzero():
            raise Exception("Reading .scale and .range is not supported when autoscale is enabled.")
        return vector(1.0 / self.range.x, 1.0 / self.range.y, 1.0 / self.range.z)

    @scale.setter
    def scale(self, n_scale):
        if n_scale.x == 0.0 or n_scale.y == 0.0 or n_scale.z == 0.0:
            raise ValueError("The scale of each axis must be non-zero.")
        n_range = vector(1.0 / n_scale.x, 1.0 / n_scale.y, 1.0 / n_scale.z)
        self.range(n_range)

    @property
    def center(self):
        return self.center

    @center.setter
    def center(self, n_center):
        self.center = n_center

    @property
    def fov(self):
        return self.fov

    @fov.setter
    def fov(self, n_fov):
        if n_fov == 0.0:
            raise ValueError("Orthogonal projection is not supported.")
        elif n_fov < 0.0 or n_fov >= pi:
            raise ValueError("attribute visual.display.fov must be between 0.0 and math.pi (exclusive)")
        self.fov = n_fov

    @property
    def lod_adjust(self):
        return self.lod_adjust

    @lod_adjust.setter
    def lod_adjust(self, n_lod):
        if n_lod > 0 or n_lod < -6:
            raise ValueError("attribute visual.display.lod must be between -6 and 0")
        self.lod_adjust = n_lod

    @property
    def uniform(self):
        return self.uniform

    @uniform.setter
    def uniform(self, n_uniform):
        self.uniform = n_uniform

    @property
    def background(self):
        return self.background

    @background.setter
    def background(self, n_background):
        self.background = n_background

    @property
    def foreground(self):
        return self.foreground

    @foreground.setter
    def foreground(self, n_foreground):
        self.foreground = n_foreground

    @property
    def auto_scale(self):
        return self.autoscale

    @auto_scale.setter
    def auto_scale(self, n_auto_scale):
        if not n_autoscale and self.autoscale:
            # Autoscale is disabled, but range_auto remains
            # set to the current autoscaled scene, until and unless
            #   range is set explicitly.
            self.recalc_extent()
            self.range = vector(0, 0, 0)
        self.auto_scale = n_autoscale

    @property
    def range(self):
        if self.auto_scale or not range.nonzero():
            raise Exception("Reading .scale and .range is not supported when autoscale is enabled.")
        return self.range

    @range.setter
    def range(self, n_range):
        if not type(n_range) == 'double':
            if n_range.x == 0.0 or n_range.y == 0.0 or n_range.z == 0.0:
                raise ValueError("attribute visual.display.range may not be zero.")
            self.auto_scale = False
            self.range = n_range
            self.range_auto = 0.0
        else:
            self.range = vector(n_range, n_range, n_range)

    @property
    def ambient(self):
        return self.ambient

    @ambient.setter
    def ambient(self, n_ambient):
        if type(n_ambient) == 'float':
            self.ambient = Rgb(n_ambient, n_ambient, n_ambient)
        else:
            self.ambient = n_ambient

    @property
    def stereo_depth(self):
        return self.stereo_depth

    @stereo_depth.setter
    def stereo_depth(self, n_stereo_depth):
        if self.visible:
            raise RuntimeError("Cannot change parameters of an active window")
        else:
            self.stereo_depth = n_stereo_depth

    @property
    def stereo_mode(self):
        # The only mode that cannot be changed after initialization is active,
        # which will result in a gl_error exception when rendered.  The completing
        # display class will have to perform some filtering on this parameter.  This
        # properties setter will not change the mode if the new one is invalid.
        stereo_values = {'NO_STEREO': 'no_stereo', 'ACTIVE_STEREO': 'active',
                         'PASSIVE_STEREO': 'passive', 'CROSS_EYED_STEREO': 'cross_eyed',
                         'RED_BLUE_STEREO': 'red_blue', 'RED_CYAN_STEREO': 'red_cyan',
                         'YELLOW_BLUE_STEREO': 'yellow_blue', 'GREEN_MAGENTA_STEREO': 'green_magenta'}
        if not hasattr(stereo_values, self.stereo_mode):
            # Not strictly required, this just silences a warning about control
            # reaching the end of a non-void funciton.
            return "no_stereo"
        else:
            return stereo_values[self.stereo_mode]

    @stereo_mode.setter
    def stereo_mode(self, mode):
        stereo_values = {'NO_STEREO': 'no_stereo', 'ACTIVE_STEREO': 'active',
                         'PASSIVE_STEREO': 'passive', 'CROSS_EYED_STEREO': 'cross_eyed',
                         'RED_BLUE_STEREO': 'red_blue', 'RED_CYAN_STEREO': 'red_cyan',
                         'YELLOW_BLUE_STEREO': 'yellow_blue', 'GREEN_MAGENTA_STEREO': 'green_magenta'}

        for key, value in stereo_values.iteritems():
            if mode == value:
                self.stereo_mode = key
                return
            raise ValueError("Unimplemented or invalid stereo mode")

    @property
    def objects(self):
        # A list of all objects rendered into this display_kernel.  Modifying it
        # does not propogate to the owning display_kernel.
        ret = vector()
        ret.insert(ret.end(), self.layer_world.begin(), self.layer_world.end())
        ret.insert(ret.end(), self.layer_world_transparent.begin(), self.layer_world_transparent.end())
        # ret[i]->get_children appends the immediate children of ret[i] to ret.  Since
        # ret.size() keeps increasing, we keep going until we have all the objects in the tree.
        for i in range(0, ret.size()):
            ret[i].get_children(ret)
        return ret

    def info(self):
        if not self.extensions:
            return "Renderer inactive.\n"
        else:
            s = "OpenGL renderer active.\n  Vendor: " + self.vendor + "\n  Version: " \
                 + self.version + "\n  Renderer: " + self.renderer + "\n  Extensions: "

            # self.extensions is a list of extensions
            copy(self.extensions.begin(), self.extensions.end(), buffer, "\n")
            s += buffer
            return s

    @property
    def window_x(self):
        return self.window_x

    @window_x.setter
    def window_x(self, n_x):
        if self.visible:
            raise RuntimeError("Cannot change parameters of an active window")
        else:
            self.window_x = n_x

    @property
    def window_y(self):
        return self.window_y

    @window_y.setter
    def window_y(self, n_y):
        if self.visible:
            raise RuntimeError("Cannot change parameters of an active window")
        else:
            self.window_y = n_y

    @property
    def window_z(self):
        return self.window_z

    @window_z.setter
    def window_z(self, n_z):
        if self.visible:
            raise RuntimeError("Cannot change parameters of an active window")
        else:
            self.window_z = n_z

    @property
    def window_width(self):
        return self.window_width

    @window_width.setter
    def window_width(self, n_width):
        if self.visible:
            raise RuntimeError("Cannot change parameters of an active window")
        else:
            self.window_width = n_width

    @property
    def window_height(self):
        return self.window_height

    @window_height.setter
    def window_height(self, n_height):
        if self.visible:
            raise RuntimeError("Cannot change parameters of an active window")
        else:
            self.window_height = n_height

    @property
    def visible(self):
        return self.visible

    @visible.setter
    def visible(self, vis):
        if not vis:
            self.explicitly_invisible = True
        if vis != self.visible:
            self.visible = vis
            set_display_visible(self, self.visible)
            # drive _activate (through wrap_display_kernel.cpp) in Python code
            self.activate(vis)

    @property
    def title(self):
        return self.title

    @title.setter
    def title(self, n_title):
        if self.visible:
            raise RuntimeError("Cannot change parameters of an active window")
        else:
            self.title = n_title

    @property
    def fullscreen(self):
        return self.fullscreen

    @fullscreen.setter
    def fullscreen(self, n_fullscreen):
        if self.visible:
            raise RuntimeError("Cannot change parameters of an active window")
        else:
            self.fullscreen = n_fullscreen

    @property
    def exit(self):
        return self.exit

    @exit.setter
    def exit(self, b):
        self.exit = b

    @property
    def show_toolbar(self):
        return self._show_toolbar

    @show_toolbar.setter
    def show_toolbar(self, n_show_toolbar):
        if self.visible:
            raise RuntimeError("Cannot change parameters of an active window")
        else:
            self._show_toolbar = n_show_toolbar

    def get_mouse(self):
        self.implicit_activate()
        return self.mouse.get_mouse()

    @property
    def selected(self):
        return self.selected

    @selected.setter
    def selected(self, d):
        self.selected = d

    def has_extension(self, ext):
        return self.extensions.find(ext) != extensions.end()

        # def pushkey(self, k):

        # typedef void (APIENTRYP EXTENSION_FUNCTION)()
        # virtual EXTENSION_FUNCTION getProcAddress( const char* )

        # EXTENSION_FUNCTION getProcAddress( const char* )

        # virtual void activate( bool active ) = 0
