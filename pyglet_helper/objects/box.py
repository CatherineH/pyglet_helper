from pyglet.gl import *
from pyglet_helper.objects import Rectangular
from pyglet_helper.util import Rgb, Vector


class Box(Rectangular):
    """
     A box object.
    """
    def __init__(self, width=1.0, height=1.0, length=1.0, color=Rgb(), pos=Vector(0, 0, 0)):
        """

        :param width: The box's width.
        :type width: float
        :param height: The box's height.
        :type height: float
        :param length: The box's length.
        :type length: float
        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param pos: The object's position.
        :type pos: pyglet_helper.util.Vector
        """
        super(Box, self).__init__(width=width, height=height, color=color, length=length, pos=pos)

    def init_model(self, scene, skip_right_face=False):
        """ Add the Vertexes and Normals to the compile list.

        :param scene: The view to render the model to.
        :type scene: pyglet_helper.objects.View
        :param skip_right_face: If True, the right face will not be rendered.
        :type skip_right_face: bool
        """
        # Note that this model is also used by arrow!
        scene.box_model.gl_compile_begin()
        glEnable(GL_CULL_FACE)
        glBegin(GL_TRIANGLES)

        s = 0.5
        vertices = [
            [[+s, +s, +s], [+s, -s, +s], [+s, -s, -s], [+s, +s, -s]],  # Right face
            [[-s, +s, -s], [-s, -s, -s], [-s, -s, +s], [-s, +s, +s]],  # Left face
            [[-s, -s, +s], [-s, -s, -s], [+s, -s, -s], [+s, -s, +s]],  # Bottom face
            [[-s, +s, -s], [-s, +s, +s], [+s, +s, +s], [+s, +s, -s]],  # Top face
            [[+s, +s, +s], [-s, +s, +s], [-s, -s, +s], [+s, -s, +s]],  # Front face
            [[-s, -s, -s], [-s, +s, -s], [+s, +s, -s], [+s, -s, -s]]  # Back face
        ]
        normals = [[+1, 0, 0], [-1, 0, 0], [0, -1, 0], [0, +1, 0], [0, 0, +1], [0, 0, -1]]
        # Draw inside (reverse winding and normals)
        for f in range(skip_right_face, 6):
            glNormal3f(-normals[f][0], -normals[f][1], -normals[f][2])
            for v in range(0, 3):
                glVertex3f(GLfloat(vertices[f][3 - v][0]), GLfloat(vertices[f][3 - v][1]),
                           GLfloat(vertices[f][3 - v][2]))
            for v in (0, 2, 3):
                glVertex3f(GLfloat(vertices[f][3 - v][0]), GLfloat(vertices[f][3 - v][1]),
                           GLfloat(vertices[f][3 - v][2]))
        # Draw outside
        for f in range(skip_right_face, 6):
            glNormal3f(GLfloat(normals[f][0]), GLfloat(normals[f][1]), GLfloat(normals[f][2]))
            for v in range(0, 3):
                glVertex3f(GLfloat(vertices[f][v][0]), GLfloat(vertices[f][v][1]), GLfloat(vertices[f][v][2]))
            for v in (0, 2, 3):
                glVertex3f(GLfloat(vertices[f][v][0]), GLfloat(vertices[f][v][1]), GLfloat(vertices[f][v][2]))
        glEnd()
        glDisable(GL_CULL_FACE)
        scene.box_model.gl_compile_end()

    def render(self, scene):
        """Render the box in the view

        :param scene: The view to render the model into
        :type scene: pyglet_helper.objects.View
        """
        if not scene.box_model.compiled:
            self.init_model(scene, False)
        self.color.gl_set(self.opacity)
        glPushMatrix()
        self.apply_transform(scene)
        scene.box_model.gl_render()
        glPopMatrix()