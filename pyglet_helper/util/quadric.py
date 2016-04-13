""" pyglet_helper.util.quadric contains objects required for drawing
quadric-type
geometric shapes
"""
try:
    import pyglet.gl as gl
except ImportError:
    gl = None
from enum import Enum


class DrawingStyle(Enum):
    """
    An enumeration of the possible quadric drawing styles.
    """
    POINT = 1
    LINE = 2
    FILL = 3
    SILHOUETTE = 4


class NormalStyle(Enum):
    """
    An enumeration of the possible options when generating a quadric's normals.
    """
    NONE = 1
    FLAT = 2
    SMOOTH = 3


class Orientation(Enum):
    """
    An enumeration of the possible winding styles when rendering a quadric.
    """
    OUTSIDE = 1
    INSIDE = 2


class Quadric(object):
    """
    Generates a Quadric. Used for cylinders, spheres, and disks.
    """
    def __init__(self):
        self.quadric = gl.glu.gluNewQuadric()
        gl.glu.gluQuadricDrawStyle(self.quadric, gl.glu.GLU_FILL)
        gl.glu.gluQuadricNormals(self.quadric, gl.glu.GLU_SMOOTH)
        gl.glu.gluQuadricOrientation(self.quadric, gl.glu.GLU_OUTSIDE)
        self._drawing_style = 1
        self._normal_style = 1
        self._orientation = 1

    def __del__(self):
        gl.glu.gluDeleteQuadric(self.quadric)

    @property
    def drawing_style(self):
        """
        Get the quadric's drawing style
        :return:
        """
        return self._drawing_style

    @drawing_style.setter
    def drawing_style(self, style):
        """ Set the quadric's drawing style.

        :param style: the quadric's drawing style
        :type style: int
        """
        self._drawing_style = style
        if style == DrawingStyle.POINT:
            gl.glu.gluQuadricDrawStyle(self.quadric, gl.glu.GLU_POINT)
        elif style == DrawingStyle.LINE:
            gl.glu.gluQuadricDrawStyle(self.quadric, gl.glu.GLU_LINE)
        elif style == DrawingStyle.FILL:
            gl.glu.gluQuadricDrawStyle(self.quadric, gl.glu.GLU_FILL)
        elif style == DrawingStyle.SILHOUETTE:
            gl.glu.gluQuadricDrawStyle(self.quadric, gl.glu.GLU_SILHOUETTE)

    @property
    def normal_style(self):
        """
        Get the quadric's normal generation style
        :return:
        """
        return self._normal_style

    @normal_style.setter
    def normal_style(self, style):
        """ Set the quadric's normal generation style.

        :param style: The quadric's normal generation style
        :type style: int
        """
        self._normal_style = style
        if style == NormalStyle.NONE:
            gl.glu.gluQuadricNormals(self.quadric, gl.glu.GLU_NONE)
        elif style == NormalStyle.FLAT:
            gl.glu.gluQuadricNormals(self.quadric, gl.glu.GLU_FLAT)
        elif style == NormalStyle.SMOOTH:
            gl.glu.gluQuadricNormals(self.quadric, gl.glu.GLU_SMOOTH)

    @property
    def orientation(self):
        """
        Get the quadric's current orientation, for rendering
        :return:
        """
        return self._orientation

    @orientation.setter
    def orientation(self, side):
        """ Set the quadric's orientation direction, for rendering

        :param side: The winding orientation
        :type side: int
        """
        self._orientation = side
        if side == Orientation.OUTSIDE:
            gl.glu.gluQuadricOrientation(self.quadric, gl.glu.GLU_OUTSIDE)
        else:
            gl.glu.gluQuadricOrientation(self.quadric, gl.glu.GLU_INSIDE)

    def render_sphere(self, radius, slices, stacks):
        """ Render a sphere.

        :param radius: The radius of the sphere
        :type radius: float
        :param slices: The number of longitudinal lines
        :type slices: int
        :param stacks: The number of latitudinal lines
        :type stacks: int
        """
        gl.glu.gluSphere(self.quadric, radius, slices, stacks)

    def render_cylinder(self, base_radius, height, slices, stacks,
                        top_radius=None):
        """ Generate the polygons for a cylinder

        :param base_radius: The radius of the bottom of the cylinder.
        :type base_radius: float
        :param height: The cylinder's height
        :type height: float
        :param slices: The number of longitudinal lines
        :type slices: int
        :param stacks: The number of latitudinal lines
        :type stacks: int
        :param top_radius: The radius of the top of the cylinder. If undefined,
         the top radius will be the same as the base radius
        :type top_radius: float
        """
        # rotate the cylinder so that it is drawn along the VPython axis
        # convention
        gl.glRotatef(90, 0, 1, 0)
        if top_radius is None:
            gl.glu.gluCylinder(self.quadric, base_radius, base_radius,
                               height, slices, stacks)
        else:
            gl.glu.gluCylinder(self.quadric, base_radius, top_radius,
                               height, slices, stacks)
        gl.glRotatef(-90, 0, 1, 0)

    def render_disk(self, radius, slices, rings, rotation):
        """ Generate the polygons for a disk

        :param radius: The disk's radius
        :type radius: float
        :param slices: The number of longitudinal lines
        :type slices: float
        :param rings: The number of concentric rings in the disk, for rendering
        :type rings: int
        :param rotation: The rotation of the disk along the z-axis
        :type rotation: float
        """
        # rotate the disk so that it is drawn along the VPython axis convention
        gl.glRotatef(90, 0, gl.GLfloat(rotation), 0)
        gl.glu.gluDisk(self.quadric, 0.0, radius, slices, rings)
        gl.glRotatef(-90, 0, gl.GLfloat(rotation), 0)
