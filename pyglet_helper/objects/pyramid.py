from pyglet.gl import *
from pyglet_helper.objects import Rectangular
from pyglet_helper.util import Rgb, Tmatrix, Vector


class Pyramid(Rectangular):
    """
    A Pyramid Object
    """
    def __init__(self, pos=Vector(0, 0, 0), width=1.0, height=1.0, length=1.0, color=Rgb()):
        """
        Initiator
        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param pos: The object's position.
        :type pos: pyglet_helper.util.Vector
        :param width: The pyramid's width.
        :type width: float
        :param height: The pyramid's height.
        :type height: float
        :param length: The pyramid's length.
        :type length: float
        :return:
        """
        super(Pyramid, self).__init__(pos=pos, color=color, width=width, height=height, length=length)
        self.compiled = False

    def init_model(self, scene):
        """
        Add the pyramid normals and vertices to the View
        :param scene: The view to render the model to.
        :type scene: pyglet_helper.objects.View
        :return:
        """
        # Note that this model is also used by arrow!
        scene.pyramid_model.gl_compile_begin()

        vertices = [[0, .5, .5],
                    [0, -.5, .5],
                    [0, -.5, -.5],
                    [0, .5, -.5],
                    [1, 0, 0]]
        triangle_indices = [0, 0, 0] * 6
        triangle_indices[0] = [3, 0, 4]  # top
        triangle_indices[1] = [1, 2, 4]  # bottom
        triangle_indices[2] = [0, 1, 4]  # front
        triangle_indices[3] = [3, 4, 2]  # back
        triangle_indices[4] = [0, 3, 2]  # left (base) 1
        triangle_indices[5] = [0, 2, 1]  # left (base) 2

        normals = [[1, 2, 0], [1, -2, 0], [1, 0, 2], [1, 0, -2], [-1, 0, 0], [-1, 0, 0]]

        glEnable(GL_CULL_FACE)
        glBegin(GL_TRIANGLES)

        # Inside
        for f in range(0, 6):
            glNormal3f(-normals[f][0], -normals[f][1], -normals[f][2])
            for v in range(0, 3):
                vert = [GLfloat(i) for i in vertices[triangle_indices[f][2 - v]]]
                glVertex3f(*vert)

        # Outside
        for f in range(0, 6):
            glNormal3fv(*[GLfloat(i) for i in normals[f]])
            for v in range(0, 3):
                glVertex3f(*[GLfloat(i) for i in vertices[triangle_indices[f][v]]])

        glEnd()
        glDisable(GL_CULL_FACE)
        self.compiled = True

        scene.pyramid_model.gl_compile_end()

    @property
    def center(self):
        return self.pos + self.axis * 0.33333333333333

    @property
    def material_matrix(self):
        out = Tmatrix()
        out.translate(Vector(0, .5, .5))
        scale = Vector(self.axis.mag(), self.height, self.width)
        out.scale(self.scale * (1.0 / max(scale.x, max(scale.y, scale.z))))
        return out

    def render(self, scene):
        """
        Add a pyramid to the view.
        :param scene: The view to render the model into
        :type scene: pyglet_helper.objects.View
        :return:
        """
        if not scene.pyramid_model.compiled:
            self.init_model(scene)

        self.color.gl_set(self.opacity)
        glPushMatrix()
        self.apply_transform(scene)
        scene.pyramid_model.gl_render()
        glPopMatrix()
