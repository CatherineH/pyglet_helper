from __future__ import print_function, division, absolute_import

try:
    from pyglet.gl import gl
except Exception as error_msg:
    gl = None

from pyglet_helper.objects import ArrayPrimitive
from pyglet_helper.util import make_pointer, Rgb, Vector, Vertex, Tmatrix
from enum import Enum
from ctypes import sizeof, c_float


class SizeUnits(Enum):
    WORLD = 0
    PIXELS = 1


class PointsShape(Enum):
    ROUND = 1
    SQUARE = 0


class Points(ArrayPrimitive):
    def __init__(self, color=Rgb(), points_shape=PointsShape.ROUND,
                 size_units=SizeUnits.PIXELS, size=5.0):
        super(Points, self).__init__()
        # since wxPython is not being used, the frame argument is not important for now
        self.points_shape = points_shape
        self.size_units = size_units
        self.size = size
        self.color.append(color)

    @property
    def degenerate(self):
        return self.count == 0

    def render(self, scene):
        if self.degenerate:
            return

        if scene.gcf != 1.0 or scene.gcfvec[0] != scene.gcfvec[1]:
            for i in range(0, self.count):
                self.pos[i] = self.pos[i].scale(scene.gcfvec)

        if scene.anaglyph:
            if scene.coloranaglyph:
                for i in range(0, self.count):
                    self.color[i] = self.color[i].desaturate()
            else:
                for i in range(0, self.count):
                    self.color[i] = self.color[i].grayscale()

        if self.points_shape == PointsShape.ROUND:
            gl.glEnable(gl.GL_POINT_SMOOTH)

        if self.size_units == SizeUnits.WORLD and scene.glext.ARB_point_parameters:
            gl.glPointSize(1)
        elif self.size_units == SizeUnits.PIXELS:
            gl.glPointSize(self.size)

        gl.glDisable(gl.GL_LIGHTING)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        # Render opaque points( if any)
        if self.count > 0:
            chunk = 256
        curr_point = 0
        while curr_point < self.count:
            # this needs to be cleaned up to convert opaque_points to pointers
            block = min(chunk, self.count - curr_point)
            #print(self.color[-1])
            gl.glColorPointer(3, gl.GL_FLOAT, 0, make_pointer(curr_point, self.color))
            gl.glVertexPointer(3, gl.GL_FLOAT, 0, make_pointer(curr_point, self.pos))
            gl.glDrawArrays(gl.GL_POINTS, 0, block)
            curr_point += block

        if self.points_shape == PointsShape.ROUND:
            gl.glDisable(gl.GL_POINT_SMOOTH)

    @property
    def center(self):
        if self.degenerate or self.points_shape != PointsShape.ROUND:
            return Vector()
        ret = Vector()
        for i in range(0, self.count):
            ret += Vector(self.pos[i])
        ret /= self.count
        return ret
