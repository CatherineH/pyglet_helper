from pyglet.gl import GLfloat, GLuint, glCallList, glDrawElements, \
    glEnableClientState, glEndList, glGenLists, glNewList, glNormalPointer, \
    glPopClientAttrib, glPushClientAttrib, glVertexPointer, \
    GL_CLIENT_VERTEX_ARRAY_BIT, GL_COMPILE, GL_FLOAT, GL_TRIANGLES, \
    GL_VERTEX_ARRAY, GL_NORMAL_ARRAY, GL_UNSIGNED_INT
from pyglet_helper.objects import Axial
from pyglet_helper.util import Rgb, Tmatrix, Vector
from math import pi, sin, cos, sqrt


class Ring(Axial):
    """
    A Ring object
    """
    def __init__(self, thickness=0.0, radius=1.0, color=Rgb(),
                 pos=Vector(0, 0, 0), axis=Vector(1, 0, 0)):
        """

        :param thickness: The ring's thickness.
        :type thickness: float
        :param radius: The ring's radius.
        :type radius: float
        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param pos: The object's position.
        :type pos: pyglet_helper.util.Vector
        :param axis: The cone points from the base to the point along the axis.
        :type axis: pyglet_helper.util.Vector
        """
        super(Ring, self).__init__(radius=radius, color=color, pos=pos,
                                   axis=axis)
        self._thickness = None
        self.list = None
        self.axis = axis
        # The radius of the ring's body.  If not specified, it is set to 1/10
        # of the radius of the body.
        self.thickness = thickness

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, t):
        self._thickness = t

    @property
    def material_matrix(self):
        out = Tmatrix()
        out.translate(Vector(.5, .5, .5))
        out.scale(Vector(self.radius, self.radius, self.radius) *
                  (.5 / (self.radius + self.thickness)))
        return out

    @property
    def degenerate(self):
        return self.radius == 0.0

    def render(self, scene):
        """ Add a ring to the view.

        :param scene: The view to render the model into
        :type scene: pyglet_helper.objects.View
        """
        if self.degenerate:
            return
        # The number of subdivisions around the hoop's radial direction.
        if self.thickness:
            band_coverage = scene.pixel_coverage(self.pos, self.thickness)
        else:
            band_coverage = scene.pixel_coverage(self.pos, self.radius * 0.1)
        if band_coverage < 0:
            band_coverage = 1000
        bands = sqrt(band_coverage * 4.0)
        bands = clamp(4, bands, 40)
        # The number of subdivisions around the hoop's tangential direction.
        ring_coverage = scene.pixel_coverage(self.pos, self.radius)
        if ring_coverage < 0:
            ring_coverage = 1000
        rings = sqrt(ring_coverage * 4.0)
        rings = clamp(4, rings, 80)
        slices = int(rings)
        inner_slices = int(bands)
        radius = self.radius
        inner_radius = self.thickness

        # Create the vertex and normal arrays.
        vertices = []
        normals = []

        u_step = 2 * pi / (slices - 1)
        v_step = 2 * pi / (inner_slices - 1)
        u = 0.
        for i in range(slices):
            cos_u = cos(u)
            sin_u = sin(u)
            v = 0.
            for j in range(inner_slices):
                cos_v = cos(v)
                sin_v = sin(v)

                d = (radius + inner_radius * cos_v)
                x = d * cos_u
                y = d * sin_u
                z = inner_radius * sin_v

                nx = cos_u * cos_v
                ny = sin_u * cos_v
                nz = sin_v

                vertices.extend([x, y, z])
                normals.extend([nx, ny, nz])
                v += v_step
            u += u_step

        # Create ctypes arrays of the lists
        vertices = (GLfloat * len(vertices))(*vertices)
        normals = (GLfloat * len(normals))(*normals)

        # Create a list of triangle indices.
        indices = []
        for i in range(slices - 1):
            for j in range(inner_slices - 1):
                p = i * inner_slices + j
                indices.extend([p, p + inner_slices, p + inner_slices + 1])
                indices.extend([p, p + inner_slices + 1, p + 1])
        indices = (GLuint * len(indices))(*indices)

        # Compile a display list
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)
        self.color.gl_set(self.opacity)

        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        self.model_world_transform(scene.gcf, Vector(self.radius, self.radius,
                                                     self.radius)).gl_mult()

        glVertexPointer(3, GL_FLOAT, 0, vertices)
        glNormalPointer(GL_FLOAT, 0, normals)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)
        glPopClientAttrib()

        glEndList()
        glCallList(self.list)


def clamp(lower, value, upper):
    """ Restrict a value to be between a lower value and upper value. Used to
    restrict the number of polygons in the ring object

    :param lower: the lowest possible value of value
    :type lower: float or int
    :param value: the value to check
    :type value: float or int
    :param upper: the largest possible value of value
    :type upper: float or int
    :rtype: float or int
    :return: the restricted value
    """
    if lower > value:
        return lower
    if upper < value:
        return upper
    return value
