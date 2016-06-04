try:
    from pyglet.gl import gl
except Exception as error_msg:
    gl = None

from pyglet_helper.objects import ArrayPrimitive
from pyglet_helper.util import Rgb, Vector, Vertex, Tmatrix
from enum import Enum
from ctypes import sizeof


class SizeUnits(Enum):
    WORLD = 0
    PIXELS = 1


class PointsShape(Enum):
    ROUND = 0
    SQUARE = 1


class PointCoord(object):
    def __init__(self, center=Vector(), color=Rgb()):
        self.center = center
        self.color = color


class Points(ArrayPrimitive):
    def __init__(self, color=Rgb(), points_shape=PointsShape.ROUND, size_units=SizeUnits.PIXELS, size=5.0):
        super(Points, self).__init__()
        # since wxPython is not being used, the frame argument is not important for now
        self.points_shape = points_shape
        self.size_units = size_units
        self.size = size

    @property
    def degenerate(self):
        return self.count == 0

    def render(self, scene):
        if self.degenerate:
            return

        translucent_points = []
        opaque_points = []

        # Every point must be depth sorted
        for i in range(0, self.count):
            opaque_points.append(PointCoord(Vector(self.pos[i]), Rgb(self.color[i])))

        if scene.gcf != 1.0 or scene.gcfvec[0] != scene.gcfvec[1]:
            for i in opaque_points:
                i.center = i.center.scale(scene.gcfvec)

        if scene.anaglyph:
            if scene.coloranaglyph:
                for i in opaque_points:
                    i.color = i.color.desaturate()
            else:
                for i in opaque_points:
                    i.color = i.color.grayscale()

        if self.points_shape == PointsShape.ROUND:
            gl.glEnable(gl.GL_POINT_SMOOTH)

        if self.size_units == SizeUnits.WORLD and scene.glext.ARB_point_parameters:
            gl.glPointSize(1)
        elif self.size_units == SizeUnits.PIXELS:
            gl.glPointSize( self.size )

        gl.glDisable(gl.GL_LIGHTING)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        # Render opaque points( if any)
        if len(opaque_points)>0:
            chunk = 256
        begin = opaque_points[0]
        end = opaque_points[-1]
        while begin < end:
            block = min(chunk, end - begin)
            gl.glColorPointer()
            gl.glColorPointer(3, gl.GL_FLOAT, sizeof(PointCoord()), begin.color.red)
            gl.glVertexPointer(3, gl.GL_DOUBLE, sizeof(PointCoord()), begin.center.x_coordinate)
            gl.glDrawArrays(gl.GL_POINTS, 0, block)
            begin += block

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
