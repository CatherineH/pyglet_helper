from pyglet.gl import *
from pyglet_helper.objects import Axial
from pyglet_helper.util import Quadric, Rgb, Vector


class Cone(Axial):
    """
    A Cone object
    """
    def __init__(self, radius=1.0, color=Rgb(), pos=Vector(0, 0, 0), axis=Vector(1, 0, 0)):
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
            q = Quadric()
            q.render_cylinder(1.0, 1.0, n_sides[i], n_stacks[i], top_radius=0.0)
            q.render_disk(1.0, n_sides[i], n_stacks[i] * 2, -1)
            scene.cone_model[i].gl_compile_end()

    @property
    def length(self):
        return self.axis.mag()

    @length.setter
    def length(self, l):
        self.axis = self.axis.norm() * l

    def render(self, scene):
        """Add the cone to the scene.

        :param scene: The view to render the model into
        :type scene: pyglet_helper.objects.View
        """
        if self.radius == 0:
            return

        self.init_model(scene)

        # See sphere.gl_render() for a description of the level of detail calc.
        coverage = scene.pixel_coverage(self.pos, self.radius)
        lod = 0
        if coverage < 0:
            lod = 5
        elif coverage < 10:
            lod = 0
        elif coverage < 30:
            lod = 1
        elif coverage < 90:
            lod = 2
        elif coverage < 250:
            lod = 3
        elif coverage < 450:
            lod = 4
        else:
            lod = 5
        lod += scene.lod_adjust
        if lod < 0:
            lod = 0
        elif lod > 5:
            lod = 5

        length = self.axis.mag()
        glPushMatrix()
        self.model_world_transform(scene.gcf, Vector(length, self.radius, self.radius)).gl_mult()

        self.color.gl_set(self.opacity)
        if self.translucent:
            glEnable(GL_CULL_FACE)

            # Render the back half.
            glCullFace(GL_FRONT)
            scene.cone_model[lod].gl_render()

            # Render the front half.
            glCullFace(GL_BACK)
            scene.cone_model[lod].gl_render()
        else:
            scene.cone_model[lod].gl_render()
        glPopMatrix()

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