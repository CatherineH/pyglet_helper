"""
pyglet_helper.cone contains an object for drawing a cone
"""
try:
   import pyglet.gl as gl
except Exception as error_msg:
    gl = None
from pyglet_helper.objects import Axial
from pyglet_helper.util import Quadric, Rgb, Vector


class Cone(Axial):
    """
    A Cone object
    """
    def __init__(self, radius=1.0, color=Rgb(), pos=Vector([0, 0, 0]),
                 axis=Vector([1, 0, 0])):
        """

        :param radius: The cone's bottom radius.
        :type radius: float
        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param pos: The object's position.
        :type pos: pyglet_helper.util.Vector
        :param axis: The cone points from the base to the point along the axis.
        :type axis: pyglet_helper.util.Vector
        :return:
        """
        super(Cone, self).__init__(radius=radius, color=color, pos=Vector(pos))
        self.axis = Vector(axis)

    def init_model(self, scene):
        """Add the cone quadrics to the view.

        :param scene: The view to render the model to.
        :type scene: pyglet_helper.objects.View
        """
        # The number of faces corresponding to each level of detail.
        n_sides = [8, 16, 32, 46, 68, 90]
        n_stacks = [1, 2, 4, 7, 10, 14]
        for i in range(0, 6):
            scene.cone_model[i].gl_compile_begin()
            _quadric = Quadric()
            _quadric.render_cylinder(1.0, 1.0, n_sides[i], n_stacks[i],
                                     top_radius=0.0)
            _quadric.render_disk(1.0, n_sides[i], n_stacks[i] * 2, -1)
            scene.cone_model[i].gl_compile_end()

    def render(self, scene):
        """Add the cone to the scene.

        :param scene: The view to render the model into
        :type scene: pyglet_helper.objects.View
        """
        if self.radius == 0:
            return

        self.init_model(scene)

        coverage_levels = [10, 30, 90, 250, 450]
        lod = self.lod_adjust(scene, coverage_levels, self.pos, self.radius)

        length = self.axis.mag()
        gl.glPushMatrix()
        self.model_world_transform(scene.gcf, Vector([length, self.radius,
                                                      self.radius])).gl_mult()

        self.color.gl_set(self.opacity)
        if self.translucent:
            gl.glEnable(gl.GL_CULL_FACE)

            # Render the back half.
            gl.glCullFace(gl.GL_FRONT)
            scene.cone_model[lod].gl_render()

            # Render the front half.
            gl.glCullFace(gl.GL_BACK)
            scene.cone_model[lod].gl_render()
        else:
            scene.cone_model[lod].gl_render()
        gl.glPopMatrix()

    @property
    def center(self):
        """ Get the center of the object.

        :return: position + axis/2
        :rtype: float
        """
        return self.pos + self.axis / 2.0

    @property
    def degenerate(self):
        """

        :return: True if radius == 0 or the length is 0
        :rtype: bool
        """
        return self.radius == 0.0 or self.axis.mag() == 0.0
