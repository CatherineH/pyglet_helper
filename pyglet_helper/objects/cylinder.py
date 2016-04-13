"""
pyglet_helper.cylinder contains an object for drawing a cylinder
"""
try:
    import pyglet.gl as gl
except Exception as err_msg:
    gl = None
from pyglet_helper.objects import Axial
from pyglet_helper.util import Quadric, Rgb, Vector


class Cylinder(Axial):
    """
     A Cylinder object.
    """
    def __init__(self, pos=Vector([0, 0, 0]), axis=Vector([1, 0, 0]),
                 radius=1.0,
                 color=Rgb(0, 0, 0)):
        """

        :param radius: The cylinder's radius.
        :type radius: float
        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param pos: The object's position.
        :type pos: pyglet_helper.util.Vector
        :param axis: The cone points from the base to the point along the axis.
        :type axis: pyglet_helper.util.Vector
        """
        super(Cylinder, self).__init__(pos=pos, radius=radius, color=color,
                                       axis=axis)

    def init_model(self, scene):
        """ Add the cylinder quadrics to the view.

        :param scene: The view to render the model to.
        :type scene: pyglet_helper.objects.View
        """
        # The number of faces corresponding to each level of detail.
        n_faces = [8, 16, 32, 64, 96, 188]
        n_stacks = [1, 1, 3, 6, 10, 20]
        for i in range(0, 6):
            scene.cylinder_model[i].gl_compile_begin()
            _quadric = Quadric()
            _quadric.render_cylinder(1.0, 1.0, n_faces[i], n_stacks[i])
            gl.glTranslatef(1.0, 0.0, 0.0)
            _quadric.render_disk(1.0, n_faces[i], 1, 1)  # left end of cylinder
            gl.glTranslatef(-1.0, 0.0, 0.0)
            _quadric.render_disk(1.0, n_faces[i], 1, -1)  # right end of
            scene.cylinder_model[i].gl_compile_end()

    @property
    def degenerate(self):
        """
        Returns True if the cylinder is invisible or has length or radius of 0
        :return:
        """
        return not self.visible or self.radius == 0.0 or self.axis.mag() == 0.0

    def render(self, scene):
        """ Add the cylinder to the view.

        :param scene: The view to render the model into
        :type scene: pyglet_helper.objects.View
        """
        if self.radius == 0.0:
            return
        self.init_model(scene)

        coverage_levels = [10, 25, 50, 196, 400]
        lod = self.lod_adjust(scene, coverage_levels, self.pos, self.radius)

        gl.glPushMatrix()
        self.model_world_transform(scene.gcf, Vector([self.length, self.radius,
                                                      self.radius])).gl_mult()

        if self.translucent:
            gl.glEnable(gl.GL_CULL_FACE)
            self.color.gl_set(self.opacity)

            # Render the back half.
            gl.glCullFace(gl.GL_FRONT)
            scene.cylinder_model[lod].gl_render()

            # Render the front half.
            gl.glCullFace(gl.GL_BACK)
            scene.cylinder_model[lod].gl_render()
        else:
            self.color.gl_set(self.opacity)
            scene.cylinder_model[lod].gl_render()
        gl.glPopMatrix()

    @property
    def center(self):
        """
        :return: Position + axis/2
        :rtype: float
        """
        return self.pos + self.axis * 0.5
