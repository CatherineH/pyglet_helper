# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet_helper.util.vector import Vector
from pyglet.gl import *
from numpy import matrix, identity, array, nditer
from numpy.linalg import inv


class Vertex(object):
    def __init__(self, x=0, y=0, z=0, w=0, v=None):
        self._x = None
        self._y = None
        self._z = None
        self._w = None
        if v is not None:
            self.x = v.x
            self.y = v.y
            self.z = v.z
        elif type(x) == Vector:
            self.x = x.x
            self.y = x.y
            self.z = x.z
        else:
            self.x = x
            self.y = y
            self.z = z
        self.w = w

    def project(self):
        w_i = 1.0 / self.w
        return vector(self.x * w_i, self.y * w_i, self.z * w_i)

    def gl_render(self):
        glVertex4d(self.x, self.y, self.z, self.w)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, s):
        self._x = s

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, s):
        self._y = s

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, s):
        self._z = s

    @property
    def w(self):
        return self._w

    @w.setter
    def w(self, s):
        self._w = s


'''
 A -precision 3D affine transformation matrix.
'''


class Tmatrix(object):
    def __init__(self, t=None, a=None, b=None):
        # This is a -precision matrix in _COLUMN MAJOR ORDER_.  User's beware.
        # It is in this order since that is what OpenGL uses internally - thus
        # eliminating a reformatting penalty.
        if t is not None:
            self.m = t.m
        elif a is not None and b is not None:
            self.m = matrix(a * b)
        else:
            self.m = matrix(identity(4))

    def __getitem__(self, key):
        return self.m[key]

    def __mul__(self, o):
        if type(o) == Vector:
            out_vect = self.project(o)
            '''
            vertex = self.project(o)
            out_vect = vector()
            out_vect.x = vertex.x
            out_vect.y = vertex.y
            out_vect.z = vertex.z
            '''
            return out_vect
        elif type(o) == Tmatrix:
            tmp = Tmatrix()
            tmp.m = self.m * o.m
            return tmp
        elif type(o) == Vertex:
            out_vect = self.project(o)
            return out_vect
        else:
            return self.m * o

    def inverse(self):
        self.m = inv(self.m)

    # Projects v using the current tmatrix values.
    def project(self, v):
        o = Vertex()
        if type(v) == Vertex:
            w = v.w
        else:
            w = 1.0
        o.x = self.m[0, 0] * v.x + self.m[1, 0] * v.y + self.m[2, 0] * v.z + self.m[3, 0] * w
        o.y = self.m[0, 1] * v.x + self.m[1, 1] * v.y + self.m[2, 1] * v.z + self.m[3, 1] * w
        o.z = self.m[0, 2] * v.x + self.m[1, 2] * v.y + self.m[2, 2] * v.z + self.m[3, 2] * w
        o.w = self.m[0, 3] * v.x + self.m[1, 3] * v.y + self.m[2, 3] * v.z + self.m[3, 3] * w
        return o

    # Right-multiply this matrix by a scaling matrix.
    def scale(self, v, w):
        self.m[0, 0] *= v.x
        self.m[0, 1] *= v.x
        self.m[0, 2] *= v.x
        self.m[0, 3] *= v.x

        self.m[1, 0] *= v.y
        self.m[1, 1] *= v.y
        self.m[1, 2] *= v.y
        self.m[1, 3] *= v.y

        self.m[2, 0] *= v.z
        self.m[2, 1] *= v.z
        self.m[2, 2] *= v.z
        self.m[2, 3] *= v.z

        self.m[3, 0] *= w
        self.m[3, 1] *= w
        self.m[3, 2] *= w
        self.m[3, 3] *= w

    # Right multiply the matrix by a translation matrix
    def translate(self, v):
        self.m[3, 0] += v.x * self.m[0, 0] + v.y * self.m[1, 0] + v.z * m[2, 0]
        self.m[3, 1] += v.x * self.m[0, 1] + v.y * self.m[1, 1] + v.z * m[2, 1]
        self.m[3, 2] += v.x * self.m[0, 2] + v.y * self.m[1, 2] + v.z * m[2, 2]
        self.m[3, 3] += v.x * self.m[0, 3] + v.y * self.m[1, 3] + v.z * m[2, 3]

    def times_inv(self, v, w):
        x = v.x - self.m[3, 0] * w
        y = v.y - self.m[3, 1] * w
        z = v.z - self.m[3, 2] * w
        return Vector(self.m[0, 0] * x + self.m[0, 1] * y + self.m[0, 2] * z,
                      self.m[1, 0] * x + self.m[1, 1] * y + self.m[1, 2] * z,
                      self.m[2, 0] * x + self.m[2, 1] * y + self.m[2, 2] * z)

    def times_v(self, v):
        return Vector(self.m[0, 0] * v.x + self.m[1, 0] * v.y + self.m[2, 0] * v.z,
                      self.m[0, 1] * v.x + self.m[1, 1] * v.y + self.m[2, 1] * v.z,
                      self.m[0, 2] * v.x + self.m[1, 2] * v.y + self.m[2, 2] * v.z)

    # Sets the first column to v
    def x_column(self, v=None, x=None, y=None, z=None):
        if v is not None:
            self.m[0, 0] = v.x
            self.m[0, 1] = v.y
            self.m[0, 2] = v.z
        else:
            self.m[0, 0] = x
            self.m[0, 1] = y
            self.m[0, 2] = z

    # Sets the second column to v
    def y_column(self, v=None, x=None, y=None, z=None):
        if v is not None:
            self.m[1, 0] = v.x
            self.m[1, 1] = v.y
            self.m[1, 2] = v.z
        else:
            self.m[1, 0] = x
            self.m[1, 1] = y
            self.m[1, 2] = z

    def origin(self):
        return Vector(self.m[3, 0], self.m[3, 1], self.m[3, 2])

    # Sets the third column to v
    def z_column(self, v=None, x=None, y=None, z=None):
        if v is not None:
            self.m[2, 0] = v.x
            self.m[2, 1] = v.y
            self.m[2, 2] = v.z
        else:
            self.m[2, 0] = x
            self.m[2, 1] = y
            self.m[2, 2] = z

    # Sets the fourth column to v
    def w_column(self, v=None, x=None, y=None, z=None):
        if v is not None:
            self.m[3, 0] = v.x
            self.m[3, 1] = v.y
            self.m[3, 2] = v.z
        elif v is None and x is not None:
            self.m[3, 0] = x
            self.m[3, 1] = y
            self.m[3, 2] = z
        else:
            self.m[3, 0] = 0
            self.m[3, 1] = 0
            self.m[3, 2] = 0

    # Sets the bottom row to x, y, z, w
    def w_row(self, x=0, y=0, z=0, w=1):
        self.m[0, 3] = x
        self.m[1, 3] = y
        self.m[2, 3] = z
        self.m[3, 3] = w

    # Overwrites the currently active matrix in OpenGL with this one.
    def gl_load(self):
        ctypes_matrix = (GLdouble * 16)(*[float(value) for value in nditer(self.m)])
        glLoadMatrixd(ctypes_matrix)

    # Multiplies the active OpenGL by this one.
    def gl_mult(self):

        ctype_matrix = (GLdouble * 16)(*[float(value) for value in nditer(self.m)])
        '''
        print "|"+str(ctypesMatrix[0])+"|"+str(ctypesMatrix[4])+"|"+str(ctypesMatrix[8])+"|"+str(ctypesMatrix[12])+"|"
        print "|"+str(ctypesMatrix[1])+"|"+str(ctypesMatrix[5])+"|"+str(ctypesMatrix[9])+"|"+str(ctypesMatrix[13])+"|"
        print "|"+str(ctypesMatrix[2])+"|"+str(ctypesMatrix[6])+"|"+str(ctypesMatrix[10])+"|"+str(ctypesMatrix[14])+"|"
        print "|"+str(ctypesMatrix[3])+"|"+str(ctypesMatrix[7])+"|"+str(ctypesMatrix[11])+"|"+str(ctypesMatrix[15])+"|"
        '''
        glMultMatrixd(ctype_matrix)

    '''
     Initialize this tmatrix with the contents of the OpenGL modelview,
     texture, color, or projection matricies.
     @return *this.
    '''

    def gl_modelview_get(self):
        ctypes_matrix = (GLfloat * 16)()

        glGetFloatv(GL_MODELVIEW_MATRIX, ctypes_matrix)
        for i in range(0, 4):
            for j in range(0, 4):
                self.m[i, j] = ctypes_matrix[i + 4 * j]
        return self

    def gl_texture_get(self):
        m = [[0] * 4] * 4
        m[0] = glGetFloatv(GL_TEXTURE_MATRIX)
        for i in range(0, 4):
            for j in range(0, 4):
                self.m[i, j] = m[i][j]
        return self.m

    def gl_color_get(self):
        m = [[0] * 4] * 4
        m[0] = glGetFloatv(GL_COLOR_MATRIX)
        for i in range(0, 4):
            for j in range(0, 4):
                self.m[i, j] = m[i][j]
        return self.m

    def gl_projection_get(self):
        ctypes_matrix = (GLfloat * 16)()
        glGetFloatv(GL_PROJECTION_MATRIX, ctypes_matrix)
        for i in range(0, 4):
            for j in range(0, 4):
                self.m[i, j] = ctypes_matrix[i + 4 * j]
        return self

    '''
     Dump this matrix to a formatted string.
    '''

    def __str__(self):
        output = "| " + str(self.m[0, 0]) + " " + str(self.m[1, 0]) + " " + str(self.m[2, 0]) + " " + str(
            self.m[3, 0]) + "|\n"
        output += "| " + str(self.m[0, 1]) + " " + str(self.m[1, 1]) + " " + str(self.m[2, 1]) + " " + str(
            self.m[3, 1]) + "|\n"
        output += "| " + str(self.m[0, 2]) + " " + str(self.m[1, 2]) + " " + str(self.m[2, 2]) + " " + str(
            self.m[3, 2]) + "|\n"
        output += "| " + str(self.m[0, 3]) + " " + str(self.m[1, 3]) + " " + str(self.m[2, 3]) + " " + str(
            self.m[3, 3]) + "|\n"
        return output


# Returns a rotation matrix to perform rotations about an axis passing through
# the origin through an angle in the direction specified by the Right Hand Rule.
def rotation(angle, axis, origin=None):
    from math import cos, sin

    ret = Tmatrix()
    if origin is not None:
        origin = Vector(origin)
        ret = rotation(angle, axis.norm())
        rot_vect = ret * origin

        vect = origin - rot_vect
        ret.w_column(v=vect)
    else:
        c = cos(angle)
        s = sin(angle)
        ic = 1.0 - c
        icxx = ic * axis.x * axis.x
        icxy = ic * axis.x * axis.y
        icxz = ic * axis.x * axis.z
        icyy = ic * axis.y * axis.y
        icyz = ic * axis.y * axis.z
        iczz = ic * axis.z * axis.z

        ret.x_column(x=icxx + c, y=icxy + axis.z * s, z=icxz - axis.y * s)
        ret.y_column(x=icxy - axis.z * s, y=icyy + c, z=icyz + axis.x * s)
        ret.z_column(x=icxz + axis.y * s, y=icyz - axis.x * s, z=iczz + c)
        ret.w_column()
        ret.w_row()
    return ret
