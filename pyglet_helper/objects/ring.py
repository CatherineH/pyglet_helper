"""pyglet_helper.ring contains an object for drawing a ring"""
try:
    import pyglet.gl as gl
except Exception as error_msg:
    gl = None
from pyglet_helper.objects import Axial
from pyglet_helper.util import Rgb, Tmatrix, Vector
from math import pi, sin, cos, sqrt


class Ring(Axial):
    """
    A Ring object
    """
    def __init__(self, thickness=0.0, radius=1.0, color=Rgb(),
                 pos=Vector([0, 0, 0]), axis=Vector([1, 0, 0])):
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
        """
        Get the ring's thickness (minor radius)
        :return: the ring's minor radius
        :rtype: float
        """
        return self._thickness

    @thickness.setter
    def thickness(self, new_thickness):
        """
        Set the ring's thickness. Will not update until render() is called
        again
        :param new_thickness: the new thickness (minor radius)
        :type new_thickness: float
        """
        self._thickness = new_thickness

    @property
    def material_matrix(self):
        """
        Creates a transformation matrix scaled to the size of the torus
        :return: the transformation matrix
        :return: pyglet_helper.util.Tmatrix
        """
        out = Tmatrix()
        out.translate(Vector([.5, .5, .5]))
        out.scale(Vector([self.radius, self.radius, self.radius]) *
                  (.5 / (self.radius + self.thickness)))
        return out

    @property
    def degenerate(self):
        """
        True if the Ring's major radius is 0
        :return:
        """
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

        outer_angle_step = 2 * pi / (slices - 1)
        inner_angle_step = 2 * pi / (inner_slices - 1)
        outer_angle = 0.
        for i in range(slices):
            cos_outer_angle = cos(outer_angle)
            sin_outer_angle = sin(outer_angle)
            inner_angle = 0.
            for j in range(inner_slices):
                cos_inner_angle = cos(inner_angle)
                sin_inner_angle = sin(inner_angle)

                diameter = (radius + inner_radius * cos_inner_angle)
                vertex_x = diameter * cos_outer_angle
                vertex_y = diameter * sin_outer_angle
                vertex_z = inner_radius * sin_inner_angle

                normal_x = cos_outer_angle * cos_inner_angle
                normal_y = sin_outer_angle * cos_inner_angle
                normal_z = sin_inner_angle

                vertices.extend([vertex_x, vertex_y, vertex_z])
                normals.extend([normal_x, normal_y, normal_z])
                inner_angle += inner_angle_step
            outer_angle += outer_angle_step

        # Create ctypes arrays of the lists
        vertices = (gl.GLfloat *len(vertices))(*vertices)
        normals = (gl.GLfloat * len(normals))(*normals)

        # Create a list of triangle indices.
        indices = []
        for i in range(slices - 1):
            for j in range(inner_slices - 1):
                pos = i * inner_slices + j
                indices.extend([pos, pos + inner_slices, pos + inner_slices +
                                1])
                indices.extend([pos, pos + inner_slices + 1, pos + 1])
        indices = (gl.GLuint * len(indices))(*indices)

        # Compile a display list
        self.list = gl.glGenLists(1)
        gl.glNewList(self.list, gl.GL_COMPILE)
        self.color.gl_set(self.opacity)

        gl.glPushClientAttrib(gl.GL_CLIENT_VERTEX_ARRAY_BIT)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
        self.model_world_transform(scene.gcf,
                                   Vector([self.radius, self.radius,
                                           self.radius])).gl_mult()

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, vertices)
        gl.glNormalPointer(gl.GL_FLOAT, 0, normals)
        gl.glDrawElements(gl.GL_TRIANGLES, len(indices), gl.GL_UNSIGNED_INT,
                          indices)
        gl.glPopClientAttrib()

        gl.glEndList()
        gl.glCallList(self.list)


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
