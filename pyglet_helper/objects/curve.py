from __future__ import print_function, division, absolute_import

try:
    from pyglet.gl import gl
except Exception as error_msg:
    gl = None

from . import ArrayPrimitive
from ..util import Rgb, Vector, make_pointer
from math import pi, cos, sin
from numpy import zeros
from ctypes import sizeof, c_uint, c_int, byref




class Curve(ArrayPrimitive):
    def __init__(self, color=Rgb(), antialias=True, radius=0.0, sides=4):
        super(Curve, self).__init__()
        # since wxPython is not being used, the frame argument is not important for now
        self.antialias = antialias
        self.radius = radius
        self.projected = []
        self.sides = sides
        self.curve_sc = zeros(sides*2)
        for i in range(0, sides):
            self.curve_sc[i] = cos(i * 2 * pi / sides)
            self.curve_sc[i+self.sides] = sin(i * 2 * pi / sides)

    @property
    def curve_slice(self):
        """
        Generates the order of indices to render a triangle strip of a cylinder
           2,4     5,8      9


        1      3,6      7,10     11
        :return: list of indicies
        :rtype: list
        """
        self._curve_slice = []
        self._curve_slice.append(0)
        for i in range(0, self.sides):
            # point 1
            self._curve_slice.append(i+1)
            # point 2
            self._curve_slice.append(i + self.sides)
            # point 3
            if i == self.sides -1:
                self._curve_slice.append(self.sides)
            else:
                self._curve_slice.append(i + 1 + self.sides)
            # point 4
            if i == self.sides - 1:
                self._curve_slice.append(0)
            else:
                self._curve_slice.append(i + 1)
            # point 5 is the point 1 of the next triangle
        # wrap points back on itself

        return self._curve_slice

    @property
    def degenerate(self):
        return self.count < 2

    def monochrome(self):
        """
        Checks whether all colors in a list are the same
        :param tcolor: the list of colors
        :type tcolor: list
        :param pcount: the number of colors in the ArrayPrimitive to check
        :type pcount: int
        :return: boolean, either True if all colors are the same, false otherwise
        :rtype: boolean
        """
        first_color = self.color[0]
        for nn in range(0, self.count):
            if self.color[nn] != first_color:
                return False
        return True

    def render(self, scene):
        if self.degenerate:
            return
        # Set up the leading and trailing points for the joins.  See
        # glePolyCylinder() for details.  The intent is to create joins that are
        # perpendicular to the path at the last segment.  When the path appears
        # to be closed, it should be rendered that way on-screen.

        # Do scaling if necessary
        if scene.gcf != 1.0 or scene.gcfvec[0] != scene.gcfvec[1]:
            for i in range(0, self.count):
                self.pos[i] = self.pos[i].scale(scene.gcfvec)

        if self.radius == 0.0:
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
                gl.glColorPointer(3, gl.GL_FLOAT, 0,
                                  make_pointer(curr_point, self.color))
                gl.glVertexPointer(3, gl.GL_FLOAT, 0, make_pointer(curr_point, self.pos))
                gl.glDrawArrays(gl.GL_POINTS, 0, block)
                curr_point += block
            gl.glEnable(gl.GL_LIGHTING)
            if self.antialias:
                gl.glDisable(gl.GL_LINE_SMOOTH)
        else:
            self.thickline(scene)

    def adjust_colors(self, scene):
        """

        :param scene:
        :param tcolor:
        :param pcount:
        :return:
        """
        mono = self.monochrome()
        if mono:
            # We can get away without using a color array.
            rendered_color = Rgb(self.color[0][0], self.color[0][1], self.color[0][2])
            if scene.anaglyph:
                if scene.coloranaglyph:
                    rendered_color.desaturate()#.gl_set(self.opacity)
                else:
                    rendered_color.grayscale()#.gl_set(self.opacity)
            else:
                rendered_color#.gl_set(self.opacity)
        else:
            gl.glEnableClientState(gl.GL_COLOR_ARRAY)
            if scene.anaglyph:
                # Must desaturate or grayscale the color.

                for i in range(0, self.count):
                    rendered_color = Rgb(self.color[i])
                    if scene.coloranaglyph:
                        rendered_color = rendered_color.desaturate()
                    else:
                        rendered_color = rendered_color.grayscale()
                    self.color[i] = rendered_color
        return mono

    def thickline(self, scene):
        """

        :param scene:
        :param spos:
        :param tcolor:
        :param pcount:
        :param scaled_radius:
        :return:
        """
        #print("thickline")
        cost = self.curve_sc[0:self.sides]
        sint = self.curve_sc[self.sides:]
        lastA = Vector()  # unit vector of previous segment

        if self.count < 2:
            return
        self.projected = self.count*self.sides*[Vector()]
        normals = self.count*self.sides*[Vector()]
        light = self.count*self.sides*[Rgb()]

        mono = self.adjust_colors(scene)

        # eliminate initial duplicate points
        start = self.pos[0]
        reduce = 0
        pos_index = 0
        while pos_index < self.count:
            next = self.pos[pos_index]
            A = (next-start).norm()
            if not A:
                reduce += 1
                del self.pos[pos_index]
                del self.color[pos_index]
                continue
            pos_index += 1
        if self.count < 2:
            return

        for segment in range(0, self.count):
            if segment == 0:
                current = self.pos[segment]
            else:
                current = self.pos[segment-1]
            next = self.pos[segment]  # The next vector in pos
            A = (next - current).norm()
            if not A:
                A = lastA
            bisecting_plane_normal = (A + lastA).norm()
            if not bisecting_plane_normal:  # < Exactly 180 degree bend
                bisecting_plane_normal = Vector([0, 0, 1]).cross(A)
                if not bisecting_plane_normal:
                    bisecting_plane_normal = Vector([0, 1, 0]).cross(A)
            sectheta = bisecting_plane_normal.dot(lastA)
            if sectheta:
                sectheta = 1.0 / sectheta

            y = Vector([0, 1, 0])
            x = A.cross(y).norm()

            if not x:
                x = A.cross(Vector([0, 0, 1])).norm()
            y = x.cross(A).norm()
            if (not x or not y or x == y) and segment != 0:
                raise RuntimeError("Degenerate curve case!")

            # scale radii
            x *= self.radius
            y *= self.radius

            for a in range(0, self.sides):
                rel = x*sint[a] + y*cost[a]  # first point is "up"

                normals[a+segment*self.sides] = rel.norm()
                self.projected[a+segment*self.sides] = next + rel
                if not mono:
                    light[a+segment*self.sides] = self.color[pos_index]

            '''
            else:
                Adot = A.dot(next - current)
                for a in range(0, self.sides):
                    prev_start = self.projected[i+a-self.sides]
                    rel = current - prev_start
                    t = rel.dot(lastA)
                    if corner != self.count-1 and sectheta > 0.0:
                        t1 = (rel.dot(bisecting_plane_normal)) * sectheta
                        t1 = max(t1, t - Adot)
                        t = max(0.0, min(t, t1))
                    prev_end = prev_start + lastA*t

                    self.projected[i+a] = prev_end
                    normals[i+a] = normals[i+a-self.sides]
                    if not mono:
                        light[i+a] = self.color[pos_index]

                    if corner != self.count-1:
                        diff_normal = bisecting_plane_normal*2*(prev_end-current).dot(
                            bisecting_plane_normal)
                        next_start = prev_end - diff_normal
                        rel = next_start - current

                        self.projected[i+a+self.sides] = next_start
                        normals[i+a+self.sides] = (rel - A*A.dot(next_start-current))\
                            .norm()
                        if not mono:
                            light[i+a+self.sides] = light[i+a]
                    elif not closed:
                        # Cap end of curve
                        for a in range(0, self.sides):
                            self.projected[i+a+self.sides] = current
                            normals[i+a+self.sides] = lastA
                            if not mono:
                                light[i+a+self.sides] = light[a+i]
                i += 2*self.sides
                '''
            lastA = A
            pos_index += 1

        '''
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
        if not mono:
            gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        for segment in range(0, self.count-1):
            vertexPointer = make_pointer(segment * self.sides, self.projected)
            print("segment: ", segment)
            for k in range(0, len(self.curve_slice)):
                print(self.curve_slice[k], self.projected[segment * self.sides +int(
                    self.curve_slice[k])])

            gl.glVertexPointer(3, gl.GL_FLOAT, 6, vertexPointer)
            if not mono:
                colorPointer = make_pointer(segment*self.sides, light)
                gl.glColorPointer(3, gl.GL_FLOAT, 0, colorPointer)
            normalPointer = make_pointer(segment*self.sides, normals)
            gl.glNormalPointer(gl.GL_FLOAT, 0, normalPointer)
            # assuming that there are two triangles per side
            pointer = make_pointer(0, self.curve_slice, c_int)
            gl.glDrawElements(gl.GL_TRIANGLE_STRIP, self.sides, gl.GL_UNSIGNED_INT,
                              pointer)

            if not mono:
                gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        '''
        self.draw_triangles()

    def draw_triangles(self):
        """
        an alternative to glDrawElements, to confirm that the values are correct
        :return:
        """
        gl.glBegin(gl.GL_TRIANGLES)
        for i in range(0, self.count-1):
            ind_j = 0
            for j in range(0, 2*self.sides):
                #print("\n")
                #print(i, j)
                for k in range(0, 3):
                    _vert = self.projected[i+self.curve_slice[ind_j]]
                #    print(i, k, ind_j, self.curve_slice[ind_j], _vert)
                    gl.glVertex3f(_vert[0], _vert[1], _vert[2])
                    if k != 2:
                        ind_j += 1
                    if ind_j == 2*self.sides:
                        ind_j = 0
        gl.glEnd(gl.GL_TRIANGLES)

        '''

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointer(3, gl.GL_FLOAT, 0, vertices)

        # draw a cube
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)

        # deactivate vertex arrays after drawing
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        '''
