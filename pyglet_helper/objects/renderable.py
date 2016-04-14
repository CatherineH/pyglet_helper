"""
pyglet_helper.renderable contains objects needed to draw all geometric shapes
"""
try:
    import pyglet.gl as gl
except ImportError:
    gl = None

from pyglet_helper.util import DisplayList, Rgb, Tmatrix, Vector
from pyglet_helper.objects import Material

class Renderable(object):
    """
    A base class for all geometric shapes and lights.
    """

    def __init__(self, color=Rgb(), mat=Material(), opacity=1.0,
                 visible=False):
        """
        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param material: The object's material
        :type material: pyglet_helper.util.Material
        :param opacity: The transparency value of the object
        :type opacity: float
        :param visible: If True, the object will be rendered on the screen
        :type visible: bool
        """
        # The base color of this body.  Ignored by the variable-color 
        # composites (curve, faces, frame).
        self.color = color
        # Fully opaque is 1.0, fully transparent is 0.0:
        self.opacity = opacity
        # True if the object should be rendered on the screen.
        self.visible = visible
        self.mat = mat

    @property
    def material(self):
        """
        Get the renderable's current material
        :return: the material
        :rtype: pyglet_helper.util.Matieral
        """
        return self.mat

    @material.setter
    def material(self, new_material):
        """
        Set the renderable's current material
        :param new_material: the new material
        :type: pyglet_helper.util.Matieral
        """
        self.mat = new_material

    @property
    def translucent(self):
        """
        True if the renderable is translucent (either the opacity is less
        than 1 or the material is translucent)
        :return:
        """
        return self.opacity != 1.0 or (self.mat and self.mat.translucent)

    def lod_adjust(self, scene, coverage_levels, pos, radius):
        """
        Calculate the level of detail required when rendering a glu object
        :param scene: the scene the the object is rendered into
        :type scene: pyglet_helper.objects.View
        :param coverage_levels: list with coverage comparison levels
        :type coverage_levels: list of int
        :param pos: the object's position within the scene
        :type pos: Vector
        :param radius: the object's size within the scene
        :type radius: float
        :return: level of detail (lod)
        :rtype: int
        """
        # See sphere.render() for a description of the level of detail calc.
        coverage = scene.pixel_coverage(pos, radius)
        lod = len(coverage_levels)
        for i in range(0, len(coverage_levels)):
            if coverage < coverage_levels[i]:
                lod = i
        lod += scene.lod_adjust
        if lod < 0:
            lod = 0
        elif lod > len(coverage_levels):
            lod = len(coverage_levels)
        return lod


class View(object):
    """
    A class for handling the environment in which all objects are rendered
    """

    def __init__(self, gcf=1.0, view_width=800, view_height=600,
                 anaglyph=False, coloranaglyph=False, forward_changed=False,
                 gcf_changed=False, lod_adjust=0, tan_hfov_x=0, tan_hfov_y=0,
                 enable_shaders=True, background_color=Rgb()):
        """
        :param gcf: The global scaling factor, a coefficient applied to all 
        objects in the view
        :type gcf: float
        :param view_width: The width of the viewport in pixels.
        :type view_width: int
        :param view_height: The height of the viewport in pixels.
        :type view_height: int
        :param anaglyph: If True, the scene will be rendered in anaglyph stereo
         mode.
        :type anaglyph: bool
        :param coloranaglyph: If True, the scene will be rendered in 
        coloranaglyph stereo mode.
        :type coloranaglyph: bool
        :param forward_changed: True if the forward vector changed since the 
        last rending operation.
        :type forward_changed: bool
        :param gcf_changed: True if the global scaling factor changed since 
        the last render cycle.
        :type gcf_changed: bool
        :param lod_adjust: The level-of-detail.
        :type lod_adjust: int
        :param tan_hfov_x: The tangent of half the horizontal field of view.
        :type tan_hfov_x: int
        :param tan_hfov_y: The tangent of half the vertical field of view.
        :type tan_hfov_y: int
        :param enable_shaders: If True, shader programs will be allowed
        :type enable_shaders: bool
        :param background_color: The scene's background color
        :type background_color: pyglet_helper.util.Rgb
        """
        # The position of the camera in world space.
        self.camera = Vector()
        # The direction the camera is pointing - a unit vector.
        self.forward = Vector()
        # The center of the scene in world space.
        self.center = Vector()
        # The true up direction of the scene in world space.
        self.up_vector = Vector()
        self.view_width = view_width
        self.view_height = view_height
        self.forward_changed = forward_changed
        self.gcf = gcf
        # The vector version of the Global Scaling Factor, for scene.uniform=0
        self.gcfvec = Vector()
        self.gcf_changed = gcf_changed
        self.lod_adjust = lod_adjust
        self.anaglyph = anaglyph
        self.coloranaglyph = coloranaglyph
        self.tan_hfov_x = tan_hfov_x
        self.tan_hfov_y = tan_hfov_y

        self.box_model = DisplayList()
        self.sphere_model = [DisplayList()] * 6
        self.cylinder_model = [DisplayList()] * 6
        self.cone_model = [DisplayList()] * 6
        self.pyramid_model = DisplayList()

        self.camera_world = Tmatrix()

        self.background_color = background_color
        self.lights = []

        self.enable_shaders = enable_shaders
        self.screen_objects = []
        self.is_setup = False
        self.setup()

    def setup(self):
        """ Does some one-time OpenGL setup.
        """
        gl.glEnable(gl.GL_LIGHTING)
        gl.glClearColor(1, 1, 1, 1)
        gl.glColor3f(1, 0, 0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        self.is_setup = True

    def draw_lights(self):
        """ Render the lights in the scene
        """
        GL_DEFINED_LIGHTS = [gl.GL_LIGHT0, gl.GL_LIGHT1,
                         gl.GL_LIGHT2, gl.GL_LIGHT3,
                         gl.GL_LIGHT4, gl.GL_LIGHT5,
                         gl.GL_LIGHT6, gl.GL_LIGHT7]
        max_lights = min(len(self.lights), 8)
        # add all of the lights to the scene
        for i in range(0, max_lights):
            # enable all of the lights
            gl.glEnable(GL_DEFINED_LIGHTS[i])
            gl.glLightfv(GL_DEFINED_LIGHTS[i], gl.GL_POSITION, self.lights[
                i].position)
            gl.glLightfv(GL_DEFINED_LIGHTS[i], gl.GL_SPECULAR,
                      self.lights[i].specular)
            gl.glLightfv(GL_DEFINED_LIGHTS[i], gl.GL_DIFFUSE,
                                self.lights[i].diffuse)

    def pixel_coverage(self, pos, radius):
        """ Compute the apparent diameter, in pixels, of a circle that is
        parallel to the screen, with a center at pos, and some radius.  If pos
        is behind the camera, it will return negative.

        :param pos: The position in the view to examine
        :type pos: pyglet_helper.util.Vector
        :param radius: The radius of coverage to examine
        :type radius: float
        :return: The diameter in pixels.
        :rtype: float
        """
        # The distance from the camera to this position, in the direction of 
        # the camera.  This is the distance to the viewing plane that the 
        # coverage circle lies in.

        pos = Vector(pos)
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
