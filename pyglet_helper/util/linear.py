from pyglet.gl import *
from numpy import matrix, identity, array, nditer
from numpy.linalg import inv
from math import sqrt, acos, asin, pi


class Vector(object):
    """
    A vector object used for math operations, and for storing 3D points
    """
    def __init__(self, a=0.0, b=0.0, c=0.0, v=None):
        """
        :param a: Either the x component of the vector, a Vector, a Vertex, or an array_like
        :type a: float, Vector, Vertex, or array_like
        :param b: if a was a float, b is the y component of the vector
        :type b: float
        :param c: if a was a float, c is the z component of the vector
        :type c: float
        :param v: an array_like of length 3 defining the components of the vector (optional)
        :type v: array_like
        """
        self._x = None
        self._y = None
        self._z = None
        if v is not None:
            if len(v) == 3:
                self.x = v[0]
                self.y = v[1]
                self.z = v[2]
            else:
                raise ValueError("Vector must be of length 3!")
        else:
            if type(a) is tuple or type(a) is list:
                self.x = a[0]
                self.y = a[1]
                self.z = a[2]
            elif hasattr(a, 'x') and hasattr(a, 'y') and hasattr(a, 'z'):
                self.x = getattr(a, 'x')
                self.y = getattr(a, 'y')
                self.z = getattr(a, 'z')
            elif a is not None and b is not None and c is not None:
                self.x = a
                self.y = b
                self.z = c
            else:
                self.x = 0
                self.y = 0
                self.z = 0

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z)

    def __mul__(self, v):
        if type(v) == type(self):
            return Vector(self.x * v.x, self.y * v.y, self.z * v.z)
        else:
            return Vector(self.x * v, self.y * v, self.z * v)

    def __rmul__(self, v):
        if type(v) == type(self):
            return Vector(v.x * self.x, v.y * self.y, v.z * self.z)
        else:
            return Vector(v * self.x, v * self.y, v * self.z)

    def __div__(self, s):
        return Vector(self.x / s, self.y / s, self.z / s)

    def __eq__(self, v):
        return v.x == self.x and v.y == self.y and v.z == self.z

    def __ne__(self, v):
        return not (v == self)

    def nonzero(self):
        """ Check to see if any component of the vector is non-zero

        :rtype: bool
        :return: True if any component of the vector is nonzero, False otherwise
        """
        return self.x or self.y or self.z

    def __invert__(self):
        return Vector(-self.x, -self.y, -self.z)

    def mag(self):
        """ Calculate the vector's magnitude

        :return: the magnitude
        :rtype: float
        """
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def norm(self):
        """ Generate a vector of unit length from this vector

        :rtype: pyglet_helper.util.Vector
        :return: unit vector
        """
        magnitude = self.mag()
        if magnitude:
            # This step ensures that vector(0,0,0).norm() returns vector(0,0,0)
            # instead of NaN
            magnitude = 1.0 / magnitude
        return Vector(self.x * magnitude, self.y * magnitude, self.z * magnitude)

    def set_mag(self, m):
        self = self.norm() * m

    def __repr__(self):
        return "Vector(" + str(self.x) + "," + str(self.y) + "," + str(self.z) + ")"

    def dot(self, v):
        """ Calculates the dot product of this vector and another.

        :param v: The other vector to be multiplied with the current vector
        :type v: Vertex or Vector
        :return: The dot product
        :rtype: float
        """
        if type(v) is not Vector:
            v = Vector(v)
        return v.x * self.x + v.y * self.y + v.z * self.z

    def cross(self, v):
        """ Return the cross product of this vector and another.

        :param v: The other vector to be crossed with the current vector
        :type v: Vertex or Vector
        :return: The cross product of self and v
        :rtype: pyglet_helper.util.Vector
        """
        if type(v) is not Vector:
            v = Vector(v)

        a = self.y * v.z - self.z * v.y
        b = self.z * v.x - self.x * v.z
        c = self.x * v.y - self.y * v.x
        return Vector(a, b, c)

    def comp(self, v):
        """ Scalar projection of this to v

        :param v: the vector or vertex the current vector will be compared to
        :type v: Vector or Vertex
        :rtype: float
        :return: the scaling factor between v and the current vector
        """
        return self.dot(v) / v.mag()

    def proj(self, v):
        """ Vector projection of this to v

        :param v: the vector to project the current vector onto
        :type v: Vector
        :return: the projected vector
        :rtype: Vector
        """
        return self.dot(v) / v.mag()**2.0 * v

    def diff_angle(self, v):
        """ Calculates the angular difference between two vectors, in radians, between 0 and pi.

        :param v: The vector to be calculated against
        :type v: Vector
        :return: The angular difference between the current vector and v, in radians
        :rtype: float
        """
        vn1 = self.norm()
        vn2 = v.norm()
        d = vn1.dot(vn2)
        if d > 0.999:
            d = Vector(vn2.x - vn1.x, vn2.y - vn1.y, vn2.z - vn1.z).mag()
            return 2.0 * asin(d / 2.0)
        elif d < -0.999:
            d = Vector(vn2.x + vn1.x, vn2.y + vn1.y, vn2.z + vn1.z).mag()
            return pi - 2.0 * asin(d / 2.0)

        return acos(d)

    def scale(self, v):
        """ Scale this vector to another, by elementwise multiplication

        :param v: the Vector to scale by
        :type v: Vector or Vertex
        :return: the scaled vector
        :rtype: pyglet_helper.util.Vector
        """
        return Vector(self.x * v.x, self.y * v.y, self.z * v.z)

    def scale_inv(self, v):
        """ Scale this vector to another, by elementwise division

        :param v: the vector to scale by
        :type v: Vector or Vertex
        :return: the scaled vector
        :rtype: pyglet_helper.util.Vector
        """
        return Vector(self.x / v.x, self.y / v.y, self.z / v.z)

    def rotate(self, angle, axis=None):
        """ Rotates the vector.

        :param angle: The angle to rotate by
        :type angle: float
        :param axis: The axis to rotate around (optional, if not set, the axis will be the +z axis
        :type axis: Vector
        :return: rotated vector
        :rtype: pyglet_helper.util.Vector
        """
        if axis is not None:
            r = rotation(angle, axis.norm())
        else:
            axis = Vector(0, 0, 1)
            r = rotation(angle, axis.norm())
        return r * self

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

    def clear(self):
        """
        Zero the state of the vector.
        :return:
        """
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def __getitem__(self, i):
        if i == 0 or i == -3:
            return self.x
        if i == 1 or i == -2:
            return self.y
        if i == 2 or i == -1:
            return self.z
        if i > 2 or i < -3:
            raise IndexError("index not available")

    def __setitem__(self, i, value):
        if i == 0 or i == -3:
            self.x = value
        if i == 1 or i == -2:
            self.y = value
        if i == 2 or i == -1:
            self.z = value
        if i > 2 or i < -3:
            raise IndexError("index not available")

    def fabs(self):
        """
        Project the current vector into the positive quadrant
        :return: The vector in the positive quadrant
        :rtype: Vector
        """
        return Vector(abs(self.x), abs(self.y), abs(self.z))

    def gl_render(self):
        """
        Add the current vector as an OpenGL Vertex
        :return:
        """
        glVertex3d(GLdouble(self.x), GLdouble(self.y), GLdouble(self.z))

    def gl_normal(self):
        """
        Add the current vector as an OpenGL Normal
        :return:
        """
        glNormal3dv(self.x)

    def sum(self):
        """
        Sum the components of the vector
        :return:
        """
        return self.x + self.y + self.z


class Vertex(object):
    """
     A homogeneous Vertex
    """
    def __init__(self, x=0, y=0, z=0, w=0, v=None):
        """

        :param x: The x coordinate of the vertex
        :type x: float
        :param y: The y coordinate of the vertex
        :type y: float
        :param z: The z coordinate of the vertex
        :type z: float
        :param w: The normalization factor of the x,y, and z components
        :type w: float
        :param v: A list of values to copy into the vertex
        :type v: list
        """
        self._x = None
        self._y = None
        self._z = None
        self._w = None
        if v is not None:
            self.x = v.x
            self.y = v.y
            self.z = v.z
        elif type(x) == Vector:
            self.x = getattr(x, 'x')
            self.y = getattr(x, 'y')
            self.z = getattr(x, 'z')
        else:
            self.x = x
            self.y = y
            self.z = z
        self.w = w

    def project(self):
        """ Project the vector according to its normalization factor

        :return: A copy of the current vector scaled to w.
        :rtype: pyglet_helper.util.Vector
        """
        w_i = 1.0 / self.w
        return Vector(self.x * w_i, self.y * w_i, self.z * w_i)

    def gl_render(self):
        """
        Send the vertex to OpenGl
        """
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


class Tmatrix(object):
    """
    A 3D affine transformation matrix.
    """
    def __init__(self, t=None, a=None, b=None):
        """
        :param t: A tmatrix to copy to the current matrix
        :type t: pyglet_helper.util.Tmatrix
        :param a: A matrix factor of the current matrix
        :type a: array_like
        :param b: A matrix factor of the current matrix
        :type b: array_like
        """
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

    def project(self, v):
        """ Multply a vector or vertex by the current matrix to produce a new vertex

        :param v: the vertex or vector to be transformed
        :type v: Vertex or Vector
        :return: The transformed vertex
        :rtype: pyglet_helper.util.Vertex
        """
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

    def scale(self, v, w=None):
        """ Scale the transformation matrix by a vector or vertex

        :param v: The vector or vertex describing the scaling
        :type v: Vertex or Vector
        :param w: The scaling factor for the normalization column. If undefined, the value will be taken from the vextex, or set to 1.0
        :type w: float
        """
        if w is None:
            if type(v) == Vertex:
                w = v.w
            else:
                w = 1.0

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

    def translate(self, v):
        """ Translate the transformation by a 3D value described in v

        :param v: The vertex or vector describing the transformation
        :type v: Vertex or Vector
        """
        self.m[3, 0] += v.x * self.m[0, 0] + v.y * self.m[1, 0] + v.z * self.m[2, 0]
        self.m[3, 1] += v.x * self.m[0, 1] + v.y * self.m[1, 1] + v.z * self.m[2, 1]
        self.m[3, 2] += v.x * self.m[0, 2] + v.y * self.m[1, 2] + v.z * self.m[2, 2]
        self.m[3, 3] += v.x * self.m[0, 3] + v.y * self.m[1, 3] + v.z * self.m[2, 3]

    def times_inv(self, v, w=None):
        """ Multiply a vector or vertex v by the inverted transformation matrix

        :param v: the vector to be transformed
        :type v: Vector or Vertex
        :param w: The vector's normalization factor. If None, it will be taken from v or set to 1.0
        :type w; float
        :rtype: Vector or Vertex
        :return: The transformed Vector or Vertex
        """
        if w is None:
            if type(v) == Vertex:
                w = v.w
            else:
                w = 1.0
        x = v.x - self.m[3, 0] * w
        y = v.y - self.m[3, 1] * w
        z = v.z - self.m[3, 2] * w
        if type(v) == Vector:
            return Vector(self.m[0, 0] * x + self.m[0, 1] * y + self.m[0, 2] * z,
                          self.m[1, 0] * x + self.m[1, 1] * y + self.m[1, 2] * z,
                          self.m[2, 0] * x + self.m[2, 1] * y + self.m[2, 2] * z)
        if type(v) == Vertex:
            return Vertex(self.m[0, 0] * x + self.m[0, 1] * y + self.m[0, 2] * z,
                          self.m[1, 0] * x + self.m[1, 1] * y + self.m[1, 2] * z,
                          self.m[2, 0] * x + self.m[2, 1] * y + self.m[2, 2] * z, w)

    def times_v(self, v):
        """ Multiply a vector or vertex by the transformation matrix

        :param v: the vector or vertex to be transformed
        :type v: Vector or Vertex
        :return: the transformed vector or vertex
        :rtype: Vector or Vertex
        """
        if type(v) == Vector:
            return Vector(self.m[0, 0] * v.x + self.m[1, 0] * v.y + self.m[2, 0] * v.z,
                          self.m[0, 1] * v.x + self.m[1, 1] * v.y + self.m[2, 1] * v.z,
                          self.m[0, 2] * v.x + self.m[1, 2] * v.y + self.m[2, 2] * v.z)
        if type(v) == Vertex:
            return Vertex(self.m[0, 0] * v.x + self.m[1, 0] * v.y + self.m[2, 0] * v.z,
                          self.m[0, 1] * v.x + self.m[1, 1] * v.y + self.m[2, 1] * v.z,
                          self.m[0, 2] * v.x + self.m[1, 2] * v.y + self.m[2, 2] * v.z, v.w)

    def x_column(self, v=None, x=None, y=None, z=None):
        """ Sets the first column of the matrix

        :param v: The vector to set the first column to
        :type v: Vector or Vertex
        :param x: The value of the first row (if v is set, it will be ignored)
        :type x: float
        :param y: The value of the second row (if v is set, it will be ignored)
        :type y: float
        :param z: The value of the third row (if v is set, it will be ignored)
        :type z: float
        """
        if v is not None:
            self.m[0, 0] = v.x
            self.m[0, 1] = v.y
            self.m[0, 2] = v.z
        else:
            self.m[0, 0] = x
            self.m[0, 1] = y
            self.m[0, 2] = z

    def y_column(self, v=None, x=None, y=None, z=None):
        """ Sets the second column of the matrix

        :param v: The vector to set the second column to
        :type v: Vector or Vertex
        :param x: The value of the first row (if v is set, it will be ignored)
        :type x: float
        :param y: The value of the second row (if v is set, it will be ignored)
        :type y: float
        :param z: The value of the third row (if v is set, it will be ignored)
        :type z: float
        """
        if v is not None:
            self.m[1, 0] = v.x
            self.m[1, 1] = v.y
            self.m[1, 2] = v.z
        else:
            self.m[1, 0] = x
            self.m[1, 1] = y
            self.m[1, 2] = z

    def z_column(self, v=None, x=None, y=None, z=None):
        """ Sets the third column of the matrix

        :param v: The vector to set the third column to
        :type v: Vector or Vertex
        :param x: The value of the first row (if v is set, it will be ignored)
        :type x: float
        :param y: The value of the second row (if v is set, it will be ignored)
        :type y: float
        :param z: The value of the third row (if v is set, it will be ignored)
        :type z: float
        """
        if v is not None:
            self.m[2, 0] = v.x
            self.m[2, 1] = v.y
            self.m[2, 2] = v.z
        else:
            self.m[2, 0] = x
            self.m[2, 1] = y
            self.m[2, 2] = z

    def w_column(self, v=None, x=None, y=None, z=None):
        """ Sets the fourth column of the matrix

        :param v: The vector to set the fourth column to
        :type v: Vector or Vertex
        :param x: The value of the first row (if v is set, it will be ignored)
        :type x: float
        :param y: The value of the second row (if v is set, it will be ignored)
        :type y: float
        :param z: The value of the third row (if v is set, it will be ignored)
        :type z: float
        """
        if v is not None:
            self.m[3, 0] = v.x
            self.m[3, 1] = v.y
            self.m[3, 2] = v.z
        elif v is None and x is not None:
            self.m[3, 0] = x
            self.m[3, 1] = y
            self.m[3, 2] = z
        else:
            self.m[3, 0] = 1.0
            self.m[3, 1] = 1.0
            self.m[3, 2] = 1.0

    def w_row(self, x=0, y=0, z=0, w=1):
        """ Set the bottom row of the matrix

        :param x: the value to set the first column to
        :type x: float
        :param y: the value to set the second column to
        :type y: float
        :param z: the value to set the third column to
        :type z: float
        :param w: the value to set the fourth column to
        :type w: float
        """
        self.m[0, 3] = x
        self.m[1, 3] = y
        self.m[2, 3] = z
        self.m[3, 3] = w

    def origin(self):
        """ Get the matrix's origin as a vector

        :return: the origin
        :rtype: pyglet_helper.util.Vector
        """
        return Vector(self.m[3, 0], self.m[3, 1], self.m[3, 2])

    def gl_load(self):
        """
        Overwrites the currently active matrix in OpenGL with this one.
        """
        ctypes_matrix = (GLdouble * 16)(*[float(value) for value in nditer(self.m)])
        glLoadMatrixd(ctypes_matrix)

    def gl_mult(self):
        """
        Multiplies the active OpenGL by this one.
        """
        ctype_matrix = (GLdouble * 16)(*[float(value) for value in nditer(self.m)])
        glMultMatrixd(ctype_matrix)

    def gl_modelview_get(self):
        """ Initialize the matrix with the contents of the OpenGL modelview

        :return: the current matrix
        :rtype: matrix
        """
        ctypes_matrix = (GLfloat * 16)()

        glGetFloatv(GL_MODELVIEW_MATRIX, ctypes_matrix)
        for i in range(0, 4):
            for j in range(0, 4):
                self.m[i, j] = ctypes_matrix[i + 4 * j]
        return self.m

    def gl_texture_get(self):
        """Initialize the matrix with the contents of the OpenGL texture matrix

        :return: the current matrix
        :rtype: matrix
        """
        m = [[0] * 4] * 4
        m[0] = glGetFloatv(GL_TEXTURE_MATRIX)
        for i in range(0, 4):
            for j in range(0, 4):
                self.m[i, j] = m[i][j]
        return self.m

    def gl_color_get(self):
        """ Initialize the matrix with the contents of the OpenGL color matrix

        :return: the current matrix
        :rtype: matrix
        """
        m = [[0] * 4] * 4
        m[0] = glGetFloatv(GL_COLOR_MATRIX)
        for i in range(0, 4):
            for j in range(0, 4):
                self.m[i, j] = m[i][j]
        return self.m

    def gl_projection_get(self):
        """Initialize the matrix with the contents of the OpenGL projection matrix

        :return: the current matrix
        :rtype: matrix
        """
        ctypes_matrix = (GLfloat * 16)()
        glGetFloatv(GL_PROJECTION_MATRIX, ctypes_matrix)
        for i in range(0, 4):
            for j in range(0, 4):
                self.m[i, j] = ctypes_matrix[i + 4 * j]
        return self

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


def rotation(angle, axis, origin=None):
    """ Returns a rotation matrix to perform rotations about an axis passing through
    the origin through an angle in the direction specified by the Right Hand Rule.

    :param angle: the angle of the rotation about the axis
    :type angle: float
    :param axis: the axis of rotation
    :type axis: Vector or Vertex
    :param origin: the location of the rotation axis
    :type origin: Vector or Vertex
    :return: the new transformation matrix
    :rtype: pyglet_helper.util.Tmatrix
    """

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
