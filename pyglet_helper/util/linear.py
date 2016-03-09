""" pyglet_helper.util.linear contains vector and vertex objects needed for
transformations and describes linear algebra operations
"""
from pyglet.gl import glNormal3dv, glVertex3d, glVertex4d, GLdouble, \
    glLoadMatrixd, glMultMatrixd, glGetFloatv, GLfloat, GL_MODELVIEW_MATRIX, \
    GL_TEXTURE_MATRIX, GL_COLOR_MATRIX, GL_PROJECTION_MATRIX
from numpy import matrix, identity, nditer
from numpy.linalg import inv
from math import sqrt, acos, asin, pi


class Vector(object):
    """
    A vector object used for math operations, and for storing 3D points
    """
    def __init__(self, in_vector=None):
        """
        :param in_vector: an array_like of length 3 defining the components of the
        vector 
        :type in_vector: array_like
        """
        self._x_component = None
        self._y_component = None
        self._z_component = None
        if in_vector is None:
            self.x_component = 0
            self.y_component = 0
            self.z_component = 0
        if type(in_vector) is tuple or type(in_vector) is list:
            self.x_component = in_vector[0]
            self.y_component = in_vector[1]
            self.z_component = in_vector[2]
        elif hasattr(in_vector, 'x_component') and \
                hasattr(in_vector, 'y_component') and \
                hasattr(in_vector, 'z_component'):
            self.x_component = getattr(in_vector, 'x_component')
            self.y_component = getattr(in_vector, 'y_component')
            self.z_component = getattr(in_vector, 'z_component')            

    def __add__(self, other):
        return Vector([self.x_component + other.x_component, self.y_component
                       + other.y_component, self.z_component + 
                       other.z_component])

    def __sub__(self, vector):
        return Vector([self.x_component - vector.x_component, self.y_component - 
                       vector.y_component, self.z_component - vector.z_component])

    def __mul__(self, vector):
        """
        Multiply the vector by a float or another vector
        :param vector: the multiplication factor
        :type vector: float or Vector or Vertex
        :return: resulting vector
        :rtype: Vector
        """
        if type(vector) == type(self):
            return Vector([self.x_component * vector.x_component, 
                           self.y_component * vector.y_component, 
                           self.z_component * vector.z_component])
        else:
            return Vector([self.x_component * vector, self.y_component * vector, 
                           self.z_component * vector])

    def __rmul__(self, vector):
        """
        Multiply the vector by a float or another vector
        :param vector: the multiplication factor
        :type vector: float or Vector or Vertex
        :return: resulting vector
        :rtype: Vector
        """
        if type(vector) == type(self):
            return Vector([vector.x_component * self.x_component,
                           vector.y_component * self.y_component,
                           vector.z_component * self.z_component])
        else:
            return Vector([vector * self.x_component, vector *
                           self.y_component,
                           vector * self.z_component])

    def __div__(self, scale):
        return Vector([self.x_component / scale, self.y_component / scale,
                       self.z_component / scale])

    def __eq__(self, vector):
        return vector.x_component == self.x_component and \
               vector.y_component == self.y_component and \
               vector.z_component == self.z_component

    def __ne__(self, vector):
        return not (vector == self)

    def nonzero(self):
        """ Check to see if any component of the vector is non-zero

        :rtype: bool
        :return: True if any component of the vector is nonzero, False
        otherwise
        """
        return self.x_component or self.y_component or self.z_component

    def __invert__(self):
        return Vector([-self.x_component, -self.y_component, -self.z_component])

    def mag(self):
        """ Calculate the vector's magnitude

        :return: the magnitude
        :rtype: float
        """
        return sqrt(self.x_component * self.x_component +
                    self.y_component * self.y_component +
                    self.z_component * self.z_component)

    def norm(self):
        """ Generate a vector of unit length from this vector

        :rtype: pyglet_helper.util.Vector
        :return: unit vector
        """
        magnitude = self.matrixag()
        if magnitude:
            # This step ensures that vector(0,0,0).norm() returns vector(0,0,0)
            # instead of NaN
            magnitude = 1.0 / magnitude
        return Vector([self.x_component * magnitude,
                       self.y_component * magnitude,
                      self.z_component * magnitude])

    def set_mag(self, m):
        self = self.norm() * m

    def __repr__(self):
        return "Vector(" + str(self.x_component) + "," + str(self.y_component) \
               + "," + str(self.z_component) + ")"

    def dot(self, vector):
        """ Calculates the dot product of this vector and another.

        :param vector: The other vector to be multiplied with the current vector
        :type vector: Vertex or Vector
        :return: The dot product
        :rtype: float
        """
        if type(vector) is not Vector:
            v = Vector(vector)
        return vector.x_component * self.x_component + vector.y_component * self.y_component + vector.z_component * self.z_component

    def cross(self, vector):
        """ Return the cross product of this vector and another.

        :param vector: The other vector to be crossed with the current vector
        :type vector: Vertex or Vector
        :return: The cross product of self and v
        :rtype: pyglet_helper.util.Vector
        """
        if type(vector) is not Vector:
            v = Vector(vector)

        x_component = self.y_component * vector.z_component - \
                      self.z_component * vector.y_component
        y_component = self.z_component * vector.x_component - \
                      self.x_component * vector.z_component
        z_component = self.x_component * vector.y_component - \
                      self.y_component * vector.x_component
        return Vector([x_component, y_component, z_component])

    def comp(self, vector):
        """ Scalar projection of this to v

        :param vector: the vector or vertex the current vector will be compared to
        :type vector: Vector or Vertex
        :rtype: float
        :return: the scaling factor between v and the current vector
        """
        return self.dot(vector) / vector.mag()

    def proj(self, vector):
        """ Vector projection of this to v

        :param vector: the vector to project the current vector onto
        :type vector: Vector
        :return: the projected vector
        :rtype: Vector
        """
        return self.dot(vector) / vector.mag()**2.0 * vector

    def diff_angle(self, vector):
        """ Calculates the angular difference between two vectors, in radians,
        between 0 and pi.

        :param vector: The vector to be calculated against
        :type vector: Vector
        :return: The angular difference between the current vector and vector, in
        radians
        :rtype: float
        """
        vn1 = self.norm()
        vn2 = vector.norm()
        d = vn1.dot(vn2)
        if d > 0.999:
            d = Vector([vn2.x - vn1.x, vn2.y - vn1.y, vn2.z - vn1.z]).mag()
            return 2.0 * asin(d / 2.0)
        elif d < -0.999:
            d = Vector([vn2.x + vn1.x, vn2.y + vn1.y, vn2.z + vn1.z]).mag()
            return pi - 2.0 * asin(d / 2.0)

        return acos(d)

    def scale(self, vector):
        """ Scale this vector to another, by elementwise multiplication

        :param vector: the Vector to scale by
        :type vector: Vector or Vertex
        :return: the scaled vector
        :rtype: pyglet_helper.util.Vector
        """
        return Vector([self.x_component * vector.x_component, 
                       self.y_component * vector.y_component, 
                       self.z_component * vector.z_component])

    def scale_inv(self, vector):
        """ Scale this vector to another, by elementwise division

        :param vector: the vector to scale by
        :type vector: Vector or Vertex
        :return: the scaled vector
        :rtype: pyglet_helper.util.Vector
        """
        return Vector([self.x_component / vector.x_component, 
                       self.y_component / vector.y_component, 
                       self.z_component / vector.z_component])

    def rotate(self, angle, axis=None):
        """ Rotates the vector.

        :param angle: The angle to rotate by
        :type angle: float
        :param axis: The axis to rotate around (optional, if not set, the axis
        will be the +z axis
        :type axis: Vector
        :return: rotated vector
        :rtype: pyglet_helper.util.Vector
        """
        if axis is not None:
            r = rotation(angle, axis.norm())
        else:
            axis = Vector([0, 0, 1])
            r = rotation(angle, axis.norm())
        return r * self

    @property
    def x(self):
        return self._x_component

    @x.setter
    def x(self, s):
        self._x_component = s

    @property
    def y(self):
        return self._y_component

    @y.setter
    def y(self, s):
        self._y_component = s

    @property
    def z(self):
        return self._z_component

    @z.setter
    def z(self, s):
        self._z_component = s

    def clear(self):
        """
        Zero the state of the vector.
        :return:
        """
        self.x_component = 0.0
        self.y_component = 0.0
        self.z_component = 0.0

    def __getitem__(self, i):
        if i == 0 or i == -3:
            return self.x_component
        if i == 1 or i == -2:
            return self.y_component
        if i == 2 or i == -1:
            return self.z_component
        if i > 2 or i < -3:
            raise IndexError("index not available")

    def __setitem__(self, i, value):
        if i == 0 or i == -3:
            self.x_component = value
        if i == 1 or i == -2:
            self.y_component = value
        if i == 2 or i == -1:
            self.z_component = value
        if i > 2 or i < -3:
            raise IndexError("index not available")

    def fabs(self):
        """
        Project the current vector into the positive quadrant
        :return: The vector in the positive quadrant
        :rtype: Vector
        """
        return Vector([abs(self.x_component), abs(self.y_component), 
                       abs(self.z_component)])

    def gl_render(self):
        """
        Add the current vector as an OpenGL Vertex
        :return:
        """
        glVertex3d(GLdouble(self.x_component), GLdouble(self.y_component), 
                   GLdouble(self.z_component))

    def gl_normal(self):
        """
        Add the current vector as an OpenGL Normal
        :return:
        """
        glNormal3dv(self.x_component)

    def sum(self):
        """
        Sum the components of the vector
        :return:
        """
        return self.x_component + self.y_component + self.z_component


class Vertex(object):
    """
     A homogeneous Vertex
    """
    def __init__(self, in_vertex=None):
        """

        :param x: The x coordinate of the vertex
        :type x: float
        :param y: The y coordinate of the vertex
        :type y: float
        :param z: The z coordinate of the vertex
        :type z: float
        :param w: The normalization factor of the x,y, and z components
        :type w: float
        :param vector: A list of values to copy into the vertex
        :type vector: list
        """
        self._x_component = None
        self._y_component = None
        self._z_component = None
        self._w_component = None
        if in_vertex is None:
            self.x_component = 0.0
            self.y_component = 0.0
            self.z_component = 0.0
            self._w_component = 1.0
        elif type(in_vertex) == Vector:
            self.x_component = getattr(in_vertex, 'x_component')
            self.y_component = getattr(in_vertex, 'y_component')
            self.z_component = getattr(in_vertex, 'z_component')
            self._w_component = 1.0
        elif type(in_vertex) == Vertex:
            self.x_component = getattr(in_vertex, 'x_component')
            self.y_component = getattr(in_vertex, 'y_component')
            self.z_component = getattr(in_vertex, 'z_component')
            self.w_component = getattr(in_vertex, 'w_component')
        elif type(in_vertex) is tuple or type(in_vertex) is list:
            self.x_component = in_vertex[0]
            self.y_component = in_vertex[1]
            self.z_component = in_vertex[2]
            self.w_component = in_vertex[3]

    def project(self):
        """ Project the vector according to its normalization factor

        :return: A copy of the current vector scaled to w.
        :rtype: pyglet_helper.util.Vector
        """
        w_i = 1.0 / self.w
        return Vector([self.x_component * w_i, self.y_component * w_i, 
                       self.z_component * w_i])

    def gl_render(self):
        """
        Send the vertex to OpenGl
        """
        glVertex4d(self.x_component, self.y_component, self.z_component, self.w)

    @property
    def x(self):
        return self._x_component

    @x.setter
    def x(self, s):
        self._x_component = s

    @property
    def y(self):
        return self._y_component

    @y.setter
    def y(self, s):
        self._y_component = s

    @property
    def z(self):
        return self._z_component

    @z.setter
    def z(self, s):
        self._z_component = s

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
            self.matrix = t.matrix
        elif a is not None and b is not None:
            self.matrix = matrix(a * b)
        else:
            self.matrix = matrix(identity(4))

    def __getitem__(self, key):
        return self.matrix[key]

    def __mul__(self, o):
        if type(o) == Vector:
            out_vect = self.project(o)
            return out_vect
        elif type(o) == Tmatrix:
            tmp = Tmatrix()
            tmp.m = self.matrix * o.matrix
            return tmp
        elif type(o) == Vertex:
            out_vect = self.project(o)
            return out_vect
        else:
            return self.matrix * o

    def inverse(self):
        self.matrix_component = inv(self.matrix)

    def project(self, vector):
        """ Multply a vector or vertex by the current matrix to produce a new
        vertex

        :param vector: the vertex or vector to be transformed
        :type vector: Vertex or Vector
        :return: The transformed vertex
        :rtype: pyglet_helper.util.Vertex
        """
        o = Vertex()
        if type(vector) == Vertex:
            w = vector.w
        else:
            w = 1.0
        o.x_component = self.matrix[0, 0] * vector.x_component + \
              self.matrix[1, 0] * vector.y_component + \
              self.matrix[2, 0] * vector.z_component + \
              self.matrix[3, 0] * w
        o.y_component = self.matrix[0, 1] * vector.x_component + \
              self.matrix[1, 1] * vector.y_component + \
              self.matrix[2, 1] * vector.z_component + \
              self.matrix[3, 1] * w
        o.z_component = self.matrix[0, 2] * vector.x_component + \
              self.matrix[1, 2] * vector.y_component + \
              self.matrix[2, 2] * vector.z_component + \
              self.matrix[3, 2] * w
        o.w = self.matrix[0, 3] * vector.x_component + \
              self.matrix[1, 3] * vector.y_component + \
              self.matrix[2, 3] * vector.z_component + \
              self.matrix[3, 3] * w
        return o

    def scale(self, vector, w=None):
        """ Scale the transformation matrix by a vector or vertex

        :param vector: The vector or vertex describing the scaling
        :type vector: Vertex or Vector
        :param w: The scaling factor for the normalization column. If
        undefined, the value will be taken from the vextex, or set to 1.0
        :type w: float
        """
        if w is None:
            if type(vector) == Vertex:
                w = vector.w
            else:
                w = 1.0

        self.matrix[0, 0] *= vector.x_component
        self.matrix[0, 1] *= vector.x_component
        self.matrix[0, 2] *= vector.x_component
        self.matrix[0, 3] *= vector.x_component

        self.matrix[1, 0] *= vector.y_component
        self.matrix[1, 1] *= vector.y_component
        self.matrix[1, 2] *= vector.y_component
        self.matrix[1, 3] *= vector.y_component

        self.matrix[2, 0] *= vector.z_component
        self.matrix[2, 1] *= vector.z_component
        self.matrix[2, 2] *= vector.z_component
        self.matrix[2, 3] *= vector.z_component

        self.matrix[3, 0] *= w
        self.matrix[3, 1] *= w
        self.matrix[3, 2] *= w
        self.matrix[3, 3] *= w

    def translate(self, vector):
        """ Translate the transformation by a 3D value described in v

        :param vector: The vertex or vector describing the transformation
        :type vector: Vertex or Vector
        """
        self.matrix[3, 0] += vector.x_component * self.matrix[0, 0] + \
                             vector.y_component * self.matrix[1, 0] + \
                             vector.z_component * self.matrix[2, 0]
        self.matrix[3, 1] += vector.x_component * self.matrix[0, 1] + \
                             vector.y_component * self.matrix[1, 1] + \
                             vector.z_component * self.matrix[2, 1]
        self.matrix[3, 2] += vector.x_component * self.matrix[0, 2] + \
                             vector.y_component * self.matrix[1, 2] + \
                             vector.z_component * self.matrix[2, 2]
        self.matrix[3, 3] += vector.x_component * self.matrix[0, 3] + \
                             vector.y_component * self.matrix[1, 3] + \
                             vector.z_component * self.matrix[2, 3]

    def times_inv(self, vector, w_component=None):
        """ Multiply a vector or vertex v by the inverted transformation matrix

        :param vector: the vector to be transformed
        :type vector: Vector or Vertex
        :param w: The vector's normalization factor. If None, it will be taken
        from v or set to 1.0
        :type w; float
        :rtype: Vector or Vertex
        :return: The transformed Vector or Vertex
        """
        if w_component is None:
            if type(vector) == Vertex:
                w_component = vector.w_component
            else:
                w_component = 1.0
        x_component = vector.x_component - self.matrix[3, 0] * w_component
        y_component = vector.y_component - self.matrix[3, 1] * w_component
        z_component = vector.z_component - self.matrix[3, 2] * w_component
        if type(vector) == Vector:
            return Vector([self.matrix[0, 0] * x_component +
                           self.matrix[0, 1] * y_component +
                           self.matrix[0, 2] * z_component,
                           self.matrix[1, 0] * x_component +
                           self.matrix[1, 1] * y_component +
                           self.matrix[1, 2] * z_component,
                           self.matrix[2, 0] * x_component +
                           self.matrix[2, 1] * y_component +
                           self.matrix[2, 2] * z_component])
        if type(vector) == Vertex:
            return Vertex([self.matrix[0, 0] * x_component +
                           self.matrix[0, 1] * y_component +
                           self.matrix[0, 2] * z_component,
                           self.matrix[1, 0] * x_component +
                           self.matrix[1, 1] * y_component +
                           self.matrix[1, 2] * z_component,
                           self.matrix[2, 0] * x_component +
                           self.matrix[2, 1] * y_component +
                           self.matrix[2, 2] * z_component, w_component])

    def times_v(self, vector):
        """ Multiply a vector or vertex by the transformation matrix

        :param vector: the vector or vertex to be transformed
        :type vector: Vector or Vertex
        :return: the transformed vector or vertex
        :rtype: Vector or Vertex
        """
        if type(vector) == Vector:
            return Vector([self.matrix[0, 0] * vector.x_component +
                           self.matrix[1, 0] * vector.y_component +
                          self.matrix[2, 0] * vector.z_component,
                          self.matrix[0, 1] * vector.x_component +
                           self.matrix[1, 1] * vector.y_component +
                          self.matrix[2, 1] * vector.z_component,
                          self.matrix[0, 2] * vector.x_component +
                           self.matrix[1, 2] * vector.y_component +
                          self.matrix[2, 2] * vector.z_component])
        if type(vector) == Vertex:
            return Vertex([self.matrix[0, 0] * vector.x_component +
                           self.matrix[1, 0] * vector.y_component +
                           self.matrix[2, 0] * vector.z_component,
                           self.matrix[0, 1] * vector.x_component +
                           self.matrix[1, 1] * vector.y_component +
                           self.matrix[2, 1] * vector.z_component,
                           self.matrix[0, 2] * vector.x_component +
                           self.matrix[1, 2] * vector.y_component +
                           self.matrix[2, 2] * vector.z_component,
                           vector.w_component])

    def x_column(self, vector=None, x_component=None, y_component=None,
                 z_component=None):
        """ Sets the first column of the matrix

        :param vector: The vector to set the first column to
        :type vector: Vector or Vertex
        :param x: The value of the first row (if v is set, it will be ignored)
        :type x: float
        :param y: The value of the second row (if v is set, it will be ignored)
        :type y: float
        :param z: The value of the third row (if v is set, it will be ignored)
        :type z: float
        """
        if vector is not None:
            self.matrix[0, 0] = vector.x_component
            self.matrix[0, 1] = vector.y_component
            self.matrix[0, 2] = vector.z_component
        else:
            self.matrix[0, 0] = x_component
            self.matrix[0, 1] = y_component
            self.matrix[0, 2] = z_component

    def y_column(self, vector=None, x_component=None, y_component=None,
                 z_component=None):
        """ Sets the second column of the matrix

        :param vector: The vector to set the second column to
        :type vector: Vector or Vertex
        :param x: The value of the first row (if v is set, it will be ignored)
        :type x: float
        :param y: The value of the second row (if v is set, it will be ignored)
        :type y: float
        :param z: The value of the third row (if v is set, it will be ignored)
        :type z: float
        """
        if vector is not None:
            self.matrix[1, 0] = vector.x_component
            self.matrix[1, 1] = vector.y_component
            self.matrix[1, 2] = vector.z_component
        else:
            self.matrix[1, 0] = x_component
            self.matrix[1, 1] = y_component
            self.matrix[1, 2] = z_component

    def z_column(self, vector=None, x_component=None, y_component=None,
                 z_component=None):
        """ Sets the third column of the matrix

        :param vector: The vector to set the third column to
        :type vector: Vector or Vertex
        :param x: The value of the first row (if v is set, it will be ignored)
        :type x: float
        :param y: The value of the second row (if v is set, it will be ignored)
        :type y: float
        :param z: The value of the third row (if v is set, it will be ignored)
        :type z: float
        """
        if vector is not None:
            self.matrix[2, 0] = vector.x_component
            self.matrix[2, 1] = vector.y_component
            self.matrix[2, 2] = vector.z_component
        else:
            self.matrix[2, 0] = x_component
            self.matrix[2, 1] = y_component
            self.matrix[2, 2] = z_component

    def w_column(self, vector=None, x_component=None, y_component=None,
                 z_component=None):
        """ Sets the fourth column of the matrix

        :param vector: The vector to set the fourth column to
        :type vector: Vector or Vertex
        :param x: The value of the first row (if v is set, it will be ignored)
        :type x: float
        :param y: The value of the second row (if v is set, it will be ignored)
        :type y: float
        :param z: The value of the third row (if v is set, it will be ignored)
        :type z: float
        """
        if vector is not None:
            self.matrix[3, 0] = vector.x_component
            self.matrix[3, 1] = vector.y_component
            self.matrix[3, 2] = vector.z_component
        elif vector is None and x_component is not None:
            self.matrix[3, 0] = x_component
            self.matrix[3, 1] = y_component
            self.matrix[3, 2] = z_component
        else:
            self.matrix[3, 0] = 1.0
            self.matrix[3, 1] = 1.0
            self.matrix[3, 2] = 1.0

    def w_row(self, x_component=0, y_component=0, z_component=0, w_component=1):
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
        self.matrix[0, 3] = x_component
        self.matrix[1, 3] = y_component
        self.matrix[2, 3] = z_component
        self.matrix[3, 3] = w_component

    def origin(self):
        """ Get the matrix's origin as a vector

        :return: the origin
        :rtype: pyglet_helper.util.Vector
        """
        return Vector([self.matrix[3, 0], self.matrix[3, 1], self.matrix[3, 2]])

    def gl_load(self):
        """
        Overwrites the currently active matrix in OpenGL with this one.
        """
        ctypes_matrix = (GLdouble * 16)(*[float(value) for value in
                                          nditer(self.matrix)])
        glLoadMatrixd(ctypes_matrix)

    def gl_mult(self):
        """
        Multiplies the active OpenGL by this one.
        """
        ctype_matrix = (GLdouble * 16)(*[float(value) for value in
                                         nditer(self.matrix)])
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
                self.matrix[i, j] = ctypes_matrix[i + 4 * j]
        return self.matrix

    def gl_texture_get(self):
        """Initialize the matrix with the contents of the OpenGL texture matrix

        :return: the current matrix
        :rtype: matrix
        """
        m = [[0] * 4] * 4
        m[0] = glGetFloatv(GL_TEXTURE_MATRIX)
        for i in range(0, 4):
            for j in range(0, 4):
                self.matrix[i, j] = m[i][j]
        return self.matrix

    def gl_color_get(self):
        """ Initialize the matrix with the contents of the OpenGL color matrix

        :return: the current matrix
        :rtype: matrix
        """
        m = [[0] * 4] * 4
        m[0] = glGetFloatv(GL_COLOR_MATRIX)
        for i in range(0, 4):
            for j in range(0, 4):
                self.matrix[i, j] = m[i][j]
        return self.matrix

    def gl_projection_get(self):
        """Initialize the matrix with the contents of the OpenGL projection
        matrix

        :return: the current matrix
        :rtype: matrix
        """
        ctypes_matrix = (GLfloat * 16)()
        glGetFloatv(GL_PROJECTION_MATRIX, ctypes_matrix)
        for i in range(0, 4):
            for j in range(0, 4):
                self.matrix[i, j] = ctypes_matrix[i + 4 * j]
        return self

    def __str__(self):
        output = "| " + str(self.matrix[0, 0]) + " " + str(self.matrix[1, 0]) + " " + \
                 str(self.matrix[2, 0]) + " " + str(
            self.matrix[3, 0]) + "|\n"
        output += "| " + str(self.matrix[0, 1]) + " " + str(self.matrix[1, 1]) + " " + \
                  str(self.matrix[2, 1]) + " " + str(
            self.matrix[3, 1]) + "|\n"
        output += "| " + str(self.matrix[0, 2]) + " " + str(self.matrix[1, 2]) + " " + \
                  str(self.matrix[2, 2]) + " " + str(
            self.matrix[3, 2]) + "|\n"
        output += "| " + str(self.matrix[0, 3]) + " " + str(self.matrix[1, 3]) + " " + \
                  str(self.matrix[2, 3]) + " " + str(
            self.matrix[3, 3]) + "|\n"
        return output


def rotation(angle, axis, origin=None):
    """ Returns a rotation matrix to perform rotations about an axis passing
    through the origin through an angle in the direction specified by the Right
    Hand Rule.

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
        icxx = ic * axis.x_component * axis.x_component
        icxy = ic * axis.x_component * axis.y_component
        icxz = ic * axis.x_component * axis.z_component
        icyy = ic * axis.y_component * axis.y_component
        icyz = ic * axis.y_component * axis.z_component
        iczz = ic * axis.z_component * axis.z_component

        ret.x_column(x=icxx + c, y=icxy + axis.z * s, z=icxz - axis.y * s)
        ret.y_column(x=icxy - axis.z * s, y=icyy + c, z=icyz + axis.x * s)
        ret.z_column(x=icxz + axis.y * s, y=icyz - axis.x * s, z=iczz + c)
        ret.w_column()
        ret.w_row()
    return ret
