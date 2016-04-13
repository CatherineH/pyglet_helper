"""
pyglet_helper.pyramid contains an object for drawing a pyramid
"""
try:
    import pyglet.gl as gl
except Exception as error_msg:
    gl = None
from pyglet_helper.objects import Rectangular
from pyglet_helper.util import Rgb, Tmatrix, Vector


class Pyramid(Rectangular):
    """
    A Pyramid Object
    """
    def __init__(self, axis=Vector([1, 0, 0]), pos=Vector([0, 0, 0]),
                 width=1.0, height=1.0, length=1.0, color=Rgb()):
        """
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
        super(Pyramid, self).__init__(axis=axis, pos=pos, color=color,
                                      width=width, height=height,
                                      length=length)
        self.compiled = False

    def init_model(self, scene):
        """ Add the pyramid normals and vertices to the View

        :param scene: The view to render the model to.
        :type scene: pyglet_helper.objects.View
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

        normals = [[1, 2, 0], [1, -2, 0], [1, 0, 2], [1, 0, -2], [-1, 0, 0],
                   [-1, 0, 0]]

        gl.glEnable(gl.GL_CULL_FACE)
        gl.glBegin(gl.GL_TRIANGLES)

        # Inside
        for face in range(0, 6):
            gl.glNormal3f(-normals[face][0], -normals[face][1], -normals[face][2])
            for vertex in range(0, 3):
                #print triangle_indices[face]
                #print vertices[triangle_indices[face]][2 - vertex]
                vert = [gl.GLfloat(i) for i in
                        vertices[triangle_indices[face][2 - vertex]]]
                gl.glVertex3f(*vert)

        # Outside
        for face in range(0, 6):
            gl.glNormal3fv(*[gl.GLfloat(i) for i in normals[face]])
            for vertex in range(0, 3):
                gl.glVertex3f(*[gl.GLfloat(i) for i in vertices[triangle_indices[
                                face][vertex]]])

        gl.glEnd()
        gl.glDisable(gl.GL_CULL_FACE)
        self.compiled = True

        scene.pyramid_model.gl_compile_end()

    @property
    def center(self):
        """
        Gets the object's position
        :return: the object's position
        :rtype: pyglet_helper.util.Vector
        """
        return self.pos + self.height*self.axis/3.0

    @property
    def material_matrix(self):
        """
        Creates a transformation matrix for pyramid objects
        :return: the transformation matrix
        :rtype: pyglet_helper.util.Tmatrix
        """
        out = Tmatrix()
        out.translate(Vector([0, .5, .5]))
        scale = Vector([self.axis.mag(), self.height, self.width])
        out.scale(Vector([self.scale,self.scale,self.scale]) *
                  (1.0 /max(scale.x_component, max(scale.y_component,
                                              scale.z_component))))
        return out

    def render(self, scene):
        """Add a pyramid to the view.

        :param scene: The view to render the model into
        :type scene: pyglet_helper.objects.View
        """
        if not scene.pyramid_model.compiled:
            self.init_model(scene)

        self.color.gl_set(self.opacity)
        gl.glPushMatrix()
        self.apply_transform(scene)
        scene.pyramid_model.gl_render()
        gl.glPopMatrix()
