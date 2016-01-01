from pyglet.gl.glu import *
from pyglet.gl import *
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
    An enumeration of the possible options when generating a quadric's normals
    """
    NONE = 1
    FLAT = 2
    SMOOTH = 3


class Orientation(Enum):
    """
    An enumeration of the possible winding styles when rendering a quadric
    """
    OUTSIDE = 1
    INSIDE = 2


class Quadric(object):
    """
    Generates a Quadric. Used for cylinders, spheres, and disks
    """
    def __init__(self):
        self.q = gluNewQuadric()
        gluQuadricDrawStyle(self.q, GLU_FILL)
        gluQuadricNormals(self.q, GLU_SMOOTH)
        gluQuadricOrientation(self.q, GLU_OUTSIDE)
        self._drawing_style = 1
        self._normal_style = 1
        self._orientation = 1

    def __del__(self):
        gluDeleteQuadric(self.q)

    @property
    def drawing_style(self):
        """
        returns the current drawing style
        :return:
        """
        return self._drawing_style

    @drawing_style.setter
    def drawing_style(self, style):
        """
        Set the quadric's drawing style.
        :param style: the quadric's drawing style
        :type style: int
        :return:
        """
        self._drawing_style = style
        if style == DrawingStyle.POINT:
            gluQuadricDrawStyle(self.q, GLU_POINT)
        elif style == DrawingStyle.LINE:
            gluQuadricDrawStyle(self.q, GLU_LINE)
        elif style == DrawingStyle.FILL:
            gluQuadricDrawStyle(self.q, GLU_FILL)
        elif style == DrawingStyle.SILHOUETTE:
            gluQuadricDrawStyle(self.q, GLU_SILHOUETTE)

    @property
    def normal_style(self):
        """
        returns the current normal style
        :return:
        """
        return self._normal_style

    @normal_style.setter
    def normal_style(self, style):
        """
        Set the quadric's normal generation style
        :param style: The quadric's normal generation style
        :type style: int
        :return:
        """
        self._normal_style = style
        if style == NormalStyle.NONE:
            gluQuadricNormals(self.q, GLU_NONE)
        elif style == NormalStyle.FLAT:
            gluQuadricNormals(self.q, GLU_FLAT)
        elif style == NormalStyle.SMOOTH:
            gluQuadricNormals(self.q, GLU_SMOOTH)

    @property
    def orientation(self):
        """
        returns the current orientation
        :return:
        """
        return self._orientation

    @orientation.setter
    def orientation(self, side):
        """
        Set the quadric's orientation direction, for rendering
        :param side: The winding orientation
        :type side: int
        :return:
        """
        self._orientation = side
        if side == Orientation.OUTSIDE:
            gluQuadricOrientation(self.q, GLU_OUTSIDE)
        else:
            gluQuadricOrientation(self.q, GLU_INSIDE)

    def render_sphere(self, radius, slices, stacks):
        """
        Render a sphere.
        :param radius: The radius of the sphere
        :type radius: float
        :param slices: The number of longitudinal lines
        :type slices: int
        :param stacks: The number of latitudinal lines
        :type stacks: int
        :return:
        """
        gluSphere(self.q, radius, slices, stacks)

    def render_cylinder(self, base_radius, height, slices, stacks, top_radius=None):
        """
        Render a cylinder
        :param base_radius: The radius of the bottom of the cylinder.
        :type base_radius: float
        :param height: The cylinder's height
        :type height: float
        :param slices: The number of longitudinal lines
        :type slices: int
        :param stacks: The number of latitudinal lines
        :type stacks: int
        :param top_radius: The radius of the top of the cylinder. If undefined, the top radius will be the same as the base radius
        :type top_radius: float
        :return:
        """
        # rotate the cylinder so that it is drawn along the VPython axis convention
        glRotatef(90, 0, 1, 0)
        if top_radius is None:
            gluCylinder(self.q, base_radius, base_radius, height, slices, stacks)
        else:
            gluCylinder(self.q, base_radius, top_radius, height, slices, stacks)
        glRotatef(-90, 0, 1, 0)

    def render_disk(self, radius, slices, rings, rotation):
        """
        Render a disk
        :param radius: The disk's radius
        :type radius: float
        :param slices: The number of longitudinal lines
        :type slices: float
        :param rings: The number of concentric rings in the disk, for rendering
        :type rings: int
        :param rotation: The rotation of the disk along the z-axis
        :type rotation: float
        :return:
        """
        # rotate the disk so that it is drawn along the VPython axis convention
        glRotatef(90, 0, GLfloat(rotation), 0)
        gluDisk(self.q, 0.0, radius, slices, rings)
        glRotatef(-90, 0, GLfloat(rotation), 0)