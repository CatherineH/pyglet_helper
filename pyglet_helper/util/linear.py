""" pyglet_helper.util.linear contains vector and vertex objects needed for
transformations and describes linear algebra operations
"""
from __future__ import division, print_function
try:
    import pyglet.gl as gl
except Exception as error_msg:
    gl = None
from numpy import matrix, identity, nditer
from numpy.linalg import inv
from math import sqrt, acos, asin, pi


class Vector(object):
    """
    A vector object used for math operations, and for storing 3D points
    """
    def __init__(self, in_vector=None):
        """
        :param in_vector: an array_like of length 3 defining the components of
        the vector
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
        """
        add another vector or vertex to the current vector
        :param other: the other vector or vertex
        :type other: pyglet_helper.util.Vector or pyglet_helper.util.Vertex
        :return:
        """
        return Vector([self.x_component + other.x_component, self.y_component
                       + other.y_component, self.z_component +
                       other.z_component])

    def __sub__(self, vector):
        """
        subtract another vector or vertex to the current vector
        :param other: the other vector or vertex
        :type other: pyglet_helper.util.Vector or pyglet_helper.util.Vertex
        :return:
        """
        return Vector([self.x_component - vector.x_component, self.y_component -
                       vector.y_component,
                       self.z_component - vector.z_component])

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
        return Vector([vector * self.x_component, vector * self.y_component,
                       vector * self.z_component])

    def __div__(self, scale):
        """
        Python 2 and 3 compatibility
         divide the current vector by a single value
        :param scale: the factor to divide the vector by
        :type scale: float
        :return: the vector divided by scale
        :rtype: pyglet_helper.util.Vector
        """
        return self.__truediv__(scale)

    def __truediv__(self, scale):
        """
        divide the current vector by a single value
        :param scale: the factor to divide the vector by
        :type scale: float
        :return: the vector divided by scale
        :rtype: pyglet_helper.util.Vector
        """
        return Vector([self.x_component / scale, self.y_component / scale,
                       self.z_component / scale])

    def __eq__(self, vector):
        """
        measures whether each component in a vector is equal to the component
        in another vector
        :param vector: the vector to compare against
        :return: true if every component in the vector is the same as the
        current vector, false if any component is different
        :rtype: bool
        """
        return vector.x_component == self.x_component and \
               vector.y_component == self.y_component and \
               vector.z_component == self.z_component

    def __ne__(self, vector):
        return not vector == self

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
        magnitude = self.mag()
        if magnitude:
            # This step ensures that vector(0,0,0).norm() returns vector(0,0,0)
            # instead of NaN
            magnitude = 1.0 / magnitude
        return Vector([self.x_component * magnitude,
                       self.y_component * magnitude,
                       self.z_component * magnitude])

    def set_mag(self, magnitude):
        """
        Re-scale the vector to a set magnitude
        :param magnitude: the magnitude of the resulting vector
        :type magnitude: float
        :return:
        """
        result = self.norm() * magnitude
        self.x_component = result.x_component
        self.y_component = result.y_component
        self.z_component = result.z_component

    def __repr__(self):
        """
        Format the vector into a string
        :return:
        """
        return "Vector(" + str(self.x_component) + "," + str(self.y_component) \
               + "," + str(self.z_component) + ")"

    def dot(self, vector):
        """ Calculates the dot product of this vector and another.

        :param vector: The other vector to be multiplied with the current vector
        :type vector: Vertex or Vector
        :return: The dot product
        :rtype: float
        """
        return vector.x_component * self.x_component + \
               vector.y_component * self.y_component + \
               vector.z_component * self.z_component

    def cross(self, vector):
        """ Return the cross product of this vector and another.

        :param vector: The other vector to be crossed with the current vector
        :type vector: Vertex or Vector
        :return: The cross product of self and v
        :rtype: pyglet_helper.util.Vector
        """
        x_component = self.y_component * vector.z_component - \
                      self.z_component * vector.y_component
        y_component = self.z_component * vector.x_component \
                      - self.x_component * vector.z_component
        z_component = self.x_component * vector.y_component \
                      - self.y_component * vector.x_component
        return Vector([x_component, y_component, z_component])

    def comp(self, vector):
        """ Scalar projection of this to v

        :param vector: the vector or vertex the current vector will be compared
        to
        :type vector: Vector or Vertex
        :rtype: float
        :return: the scaling factor between v and the current vector
        """
        return self.dot(vector) / vector.mag()

    def proj(self, vector):
        """ Vector projection of this to vector

        :param vector: the vector to project the current vector onto
        :type vector: Vector
        :return: the projected vector
        :rtype: Vector
        """
        return self.dot(vector) / vector.mag() ** 2.0 * vector

    def diff_angle(self, vector):
        """ Calculates the angular difference between two vectors, in radians,
        between 0 and pi.

        :param vector: The vector to be calculated against
        :type vector: Vector
        :return: The angular difference between the current vector and vector,
        in radians
        :rtype: float
        """
        vn1 = self.norm()
        vn2 = vector.norm()
        dot_product = vn1.dot(vn2)
        if dot_product > 0.999:
            dot_product = Vector([vn2.x_component - vn1.x_component,
                                  vn2.y_component - vn1.y_component,
                                  vn2.z_component - vn1.z_component]).mag()
            return 2.0 * asin(dot_product / 2.0)
        elif dot_product < -0.999:
            dot_product = Vector([vn2.x_component + vn1.x_component,
                                  vn2.y_component + vn1.y_component,
                                  vn2.z_component + vn1.z_component]).mag()
            return pi - 2.0 * asin(dot_product / 2.0)

        return acos(dot_product)

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
            _rotation_matrix = rotation(angle, axis.norm())
        else:
            axis = Vector([0, 0, 1])
            _rotation_matrix = rotation(angle, axis.norm())
        return _rotation_matrix * self

    @property
    def x_component(self):
        """ Get the x component of the vector
        :return: the x component of the vector
        """
        return self._x_component

    @x_component.setter
    def x_component(self, new_value):
        """
        Set the x component of the vector
        :param new_value: the new value of the x component
        :type new_value: float
        :return:
        """
        self._x_component = new_value

    @property
    def y_component(self):
        """ Get the y component of the vector
        :return: the y component of the vector
        """
        return self._y_component

    @y_component.setter
    def y_component(self, new_value):
        """
        Set the y component of the vector
        :param new_value: the new value of the y component
        :type new_value: float
        :return:
        """
        self._y_component = new_value

    @property
    def z_component(self):
        """ Get the z component of the vector
        :return: the z component of the vector
        """
        return self._z_component

    @z_component.setter
    def z_component(self, new_value):
        """
        Set the z component of the vector
        :param new_value: the new value of the z component
        :type new_value: float
        :return:
        """
        self._z_component = new_value

    def clear(self):
        """
        Zero the state of the vector.
        :return:
        """
        self.x_component = 0.0
        self.y_component = 0.0
        self.z_component = 0.0

    def __getitem__(self, i):
        """
        get the component of the vector by an integer address
        :param i: the integer, with a value from -3 to 2
        :type i: int
        :return:
        """
        if i == 0 or i == -3:
            return self.x_component
        if i == 1 or i == -2:
            return self.y_component
        if i == 2 or i == -1:
            return self.z_component
        if i > 2 or i < -3:
            raise IndexError("index not available")

    def __setitem__(self, i, value):
        """
        set the component of the vector by an integer address
        :param i: the integer, with a value from -3 to 2
        :type i: int
        :param value: the new value to set the component to
        :type value: float
        :return:
        """
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
        gl.glVertex3d(gl.GLdouble(self.x_component),
                             gl.GLdouble(self.y_component),
                             gl.GLdouble(self.z_component))

    def gl_normal(self):
        """
        Add the current vector as an OpenGL Normal
        :return:
        """
        gl.glNormal3dv(self.x_component)

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

        :param in_vertex: a source of numeric values for the vertex, either a
        vector, vertex, list or tuple. If a vector is provided, the w component
        is assumed to be 1.
        :type in_vertex: pyglet_helper.util.Vertex, pyglet_helper.util.Vector,
        tuple, or list
        """
        self._x_component = None
        self._y_component = None
        self._z_component = None
        self._w_component = None
        if in_vertex is None:
            self.x_component = 0.0
            self.y_component = 0.0
            self.z_component = 0.0
            self.w_component = 1.0
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
            if len(in_vertex) > 3:
                self.w_component = in_vertex[3]

    def project(self):
        """ Project the vector according to its normalization factor

        :return: A copy of the current vector scaled to w.
        :rtype: pyglet_helper.util.Vector
        """
        w_i = 1.0 / self.w_component
        return Vector([self.x_component * w_i, self.y_component * w_i,
                       self.z_component * w_i])

    def gl_render(self):
        """
        Send the vertex to OpenGl
        """
        gl.glVertex4d(self.x_component, self.y_component,
                             self.z_component, self.w_component)

    @property
    def x_component(self):
        """ Get the x component of the vertex
        :return: the x component of the vertex
        """
        return self._x_component

    @x_component.setter
    def x_component(self, new_value):
        """
        Set the x component of the vertex
        :param new_value: the new value of the x component
        :type new_value: float
        :return:
        """
        self._x_component = new_value

    @property
    def y_component(self):
        """ Get the y component of the vertex
        :return: the y component of the vertex
        """
        return self._y_component

    @y_component.setter
    def y_component(self, new_value):
        """
        Set the y component of the vertex
        :param new_value: the new value of the y component
        :type new_value: float
        :return:
        """
        self._y_component = new_value

    @property
    def z_component(self):
        """ Get the z component of the vertex
        :return: the z component of the vertex
        """
        return self._z_component

    @z_component.setter
    def z_component(self, new_value):
        """
        Set the z component of the vertex
        :param new_value: the new value of the z component
        :type new_value: float
        :return:
        """
        self._z_component = new_value

    @property
    def w_component(self):
        """ Get the w component of the vertex
        :return: the w component of the vertex
        """
        return self._w_component

    @w_component.setter
    def w_component(self, new_value):
        """
        Set the w component of the vertex
        :param new_value: the new value of the w component
        :type new_value: float
        :return:
        """
        self._w_component = new_value

    def __getitem__(self, i):
        """
        get the component of the vertex by an integer address
        :param i: the integer, with a value from -4 to 3
        :type i: int
        :return:
        """
        if i == 0 or i == -4:
            return self.x_component
        if i == 1 or i == -3:
            return self.y_component
        if i == 2 or i == -2:
            return self.z_component
        if i == 3 or i == -1:
            return self.w_component
        if i > 3 or i < -4:
            raise IndexError("index not available")

    def __setitem__(self, i, value):
        """
        set the component of the vertex by an integer address
        :param i: the integer, with a value from -4 to 3
        :type i: int
        :param value: the new value to set the component to
        :type value: float
        :return:
        """
        if i == 0 or i == -4:
            self.x_component = value
        if i == 1 or i == -3:
            self.y_component = value
        if i == 2 or i == -2:
            self.z_component = value
        if i == 3 or i == -1:
            self.w_component = value
        if i > 3 or i < -4:
            raise IndexError("index not available")


    def __repr__(self):
        """
        Format the vertex into a string
        :return:
        """
        return "Vertex(" + str(self.x_component) + "," + \
               str(self.y_component) + "," + str(self.z_component) + "," + \
               str(self.w_component) + ")"



class Tmatrix(object):
    """
    A 3D affine transformation matrix.
    """

    def __init__(self, in_tmatrix=None):
        """
        :param t: A tmatrix to copy to the current matrix
        :type t: pyglet_helper.util.Tmatrix
        """
        # This is a -precision matrix in _COLUMN MAJOR ORDER_.  User's beware.
        # It is in this order since that is what OpenGL uses internally - thus
        # eliminating a reformatting penalty.
        if in_tmatrix is not None:
            self.matrix = in_tmatrix.matrix
        else:
            self.matrix = matrix(identity(4))

    def __getitem__(self, key):
        """
        Get a specified element from a key
        :param key: the x, y component of the matrix to get
        :type key: tuple
        :return:
        """
        return self.matrix[key]

    def __mul__(self, input_data):
        """
        Multiply the data in the input by the current matrix
        :param input_data: the data to be multiplied
        :type input_data: Vector, Tmatrix, Vertex, float
        :return: self.matrix*input_data
        """
        if type(input_data) == Vector:
            out_vect = self.project(input_data)
            return out_vect
        elif type(input_data) == Tmatrix:
            tmp = Tmatrix()
            tmp.matrix = self.matrix * input_data.matrix
            return tmp
        elif type(input_data) == Vertex:
            out_vect = self.project(input_data)
            return out_vect
        else:
            tmp = Tmatrix()
            tmp.matrix = self.matrix * input_data
            return tmp

    def __rmul__(self, input_data):
        """
        Multiply the data in the input by the current matrix
        :param input_data: the data to be multiplied
        :type input_data: float or int
        :return: self.matrix*input_data
        """
        tmp = Tmatrix()
        tmp.matrix = self.matrix * input_data
        return tmp

    def inverse(self):
        """
        invert the current matrix
        :return:
        """
        self.matrix = inv(self.matrix)

    def project(self, vector):
        """ Multply a vector or vertex by the current matrix to produce a new
        vertex

        :param vector: the vertex or vector to be transformed
        :type vector: Vertex or Vector
        :return: The transformed vertex
        :rtype: pyglet_helper.util.Vertex
        """
        output_vertex = Vertex()
        if type(vector) == Vertex:
            w_component = vector.w_component
        else:
            w_component = 1.0
        output_vertex.x_component = self.matrix[0, 0] * vector.x_component + \
                        self.matrix[1, 0] * vector.y_component + \
                        self.matrix[2, 0] * vector.z_component + \
                        self.matrix[3, 0] * w_component
        output_vertex.y_component = self.matrix[0, 1] * vector.x_component + \
                        self.matrix[1, 1] * vector.y_component + \
                        self.matrix[2, 1] * vector.z_component + \
                        self.matrix[3, 1] * w_component
        output_vertex.z_component = self.matrix[0, 2] * vector.x_component + \
                        self.matrix[1, 2] * vector.y_component + \
                        self.matrix[2, 2] * vector.z_component + \
                        self.matrix[3, 2] * w_component
        output_vertex.w_component = self.matrix[0, 3] * vector.x_component + \
              self.matrix[1, 3] * vector.y_component + \
              self.matrix[2, 3] * vector.z_component + \
              self.matrix[3, 3] * w_component
        return output_vertex

    def scale(self, vector, w_component=None):
        """ Scale the transformation matrix by a vector or vertex

        :param vector: The vector or vertex describing the scaling
        :type vector: Vertex or Vector
        :param w_component: The scaling factor for the normalization column. If
        undefined, the value will be taken from the vextex, or set to 1.0
        :type w_component: float
        """
        if w_component is None:
            if type(vector) == Vertex:
                w_component = vector.w_component
            else:
                w_component = 1.0

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

        self.matrix[3, 0] *= w_component
        self.matrix[3, 1] *= w_component
        self.matrix[3, 2] *= w_component
        self.matrix[3, 3] *= w_component

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
        :param w_component: The vector's normalization factor. If None, it will
        be taken from v or set to 1.0
        :type w_component; float
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

    def x_column(self, vector=None):
        """ Sets the first column of the matrix

        :param vector: The vector to set the first column to
        :type vector: pyglet_helper.util.Vector, pyglet_helper.util.Vertex,
        tuple or list
        """
        if vector is not None:
            if type(vector) is not Vector and type(vector) is not Vertex:
                vector = Vector(vector)
            self.matrix[0, 0] = vector.x_component
            self.matrix[0, 1] = vector.y_component
            self.matrix[0, 2] = vector.z_component

    def y_column(self, vector=None):
        """ Sets the second column of the matrix

        :param vector: The vector to set the second column to
        :type vector: pyglet_helper.util.Vector, pyglet_helper.util.Vertex,
        tuple or list
        """
        if vector is not None:
            if type(vector) is not Vector and type(vector) is not Vertex:
                vector = Vector(vector)
            self.matrix[1, 0] = vector.x_component
            self.matrix[1, 1] = vector.y_component
            self.matrix[1, 2] = vector.z_component

    def z_column(self, vector=None):
        """ Sets the third column of the matrix

        :param vector: The vector to set the third column to
        :type vector: pyglet_helper.util.Vector, pyglet_helper.util.Vertex,
        tuple or list
        """
        if vector is not None:
            if type(vector) is not Vector and type(vector) is not Vertex:
                vector = Vector(vector)

            self.matrix[2, 0] = vector.x_component
            self.matrix[2, 1] = vector.y_component
            self.matrix[2, 2] = vector.z_component

    def w_column(self, vector=None):
        """ Sets the fourth column of the matrix

        :param vector: The vector to set the fourth column to
        :type vector: pyglet_helper.util.Vector, pyglet_helper.util.Vertex,
        tuple or list
        """
        if vector is not None:
            self.matrix[3, 0] = vector.x_component
            self.matrix[3, 1] = vector.y_component
            self.matrix[3, 2] = vector.z_component
        else:
            self.matrix[3, 0] = 1.0
            self.matrix[3, 1] = 1.0
            self.matrix[3, 2] = 1.0

    def w_row(self, x_component=0, y_component=0, z_component=0, w_component=1):
        """ Set the bottom row of the matrix

        :param x_component: the value to set the first column to
        :type x_component: float
        :param y_component: the value to set the second column to
        :type y_component: float
        :param z_component: the value to set the third column to
        :type z_component: float
        :param w_component: the value to set the fourth column to
        :type w_component: float
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
        ctypes_matrix = (gl.GLdouble * 16)(*[float(value) for value in
                                          nditer(self.matrix)])
        gl.glLoadMatrixd(ctypes_matrix)

    def gl_mult(self):
        """
        Multiplies the active OpenGL by this one.
        """
        ctype_matrix = (gl.GLdouble * 16)(*[float(value) for value in
                                         nditer(self.matrix)])
        gl.glMultMatrixd(ctype_matrix)

    def gl_modelview_get(self):
        """ Initialize the matrix with the contents of the OpenGL modelview

        :return: the current matrix
        :rtype: matrix
        """
        ctypes_matrix = (gl.GLfloat * 16)()

        gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX, ctypes_matrix)
        for i in range(0, 4):
            for j in range(0, 4):
                self.matrix[i, j] = ctypes_matrix[i + 4 * j]
        return self.matrix

    def gl_texture_get(self):
        """Initialize the matrix with the contents of the OpenGL texture matrix

        :return: the current matrix
        :rtype: matrix
        """
        ctypes_matrix = (gl.GLfloat * 16)()
        gl.glGetFloatv(gl.GL_TEXTURE_MATRIX, ctypes_matrix)
        for i in range(0, 4):
            for j in range(0, 4):
                self.matrix[i, j] = ctypes_matrix[i + 4 * j]
        return self.matrix

    def gl_color_get(self):
        """ Initialize the matrix with the contents of the OpenGL color matrix

        :return: the current matrix
        :rtype: matrix
        """
        ctypes_matrix = (gl.GLfloat * 16)()
        gl.glGetFloatv(gl.GL_COLOR_MATRIX, ctypes_matrix)
        for i in range(0, 4):
            for j in range(0, 4):
                self.matrix[i, j] = ctypes_matrix[i + 4 * j]
        return self.matrix

    def gl_projection_get(self):
        """Initialize the matrix with the contents of the OpenGL projection
        matrix

        :return: the current matrix
        :rtype: matrix
        """
        ctypes_matrix = (gl.GLfloat * 16)()
        gl.glGetFloatv(gl.GL_PROJECTION_MATRIX, ctypes_matrix)
        for i in range(0, 4):
            for j in range(0, 4):
                self.matrix[i, j] = ctypes_matrix[i + 4 * j]
        return self

    def __str__(self):
        """
        format the matrix as a string
        :return: the formatted string, four lines long
        :rtype: str
        """
        output = "| " + str(self.matrix[0, 0]) + " " +str(self.matrix[1, 0]) \
                 + " " + str(self.matrix[2, 0]) + " " + str(self.matrix[3, 0])\
                 + "|\n"
        output += "| " + str(self.matrix[0, 1]) + " " + str(self.matrix[1, 1])\
                  + " " + str(self.matrix[2, 1]) + " " + \
                  str(self.matrix[3, 1]) + "|\n"
        output += "| " + str(self.matrix[0, 2]) + " " + str(self.matrix[1, 2])\
                  + " " + str(self.matrix[2, 2]) + " " + \
                  str(self.matrix[3, 2]) + "|\n"
        output += "| " + str(self.matrix[0, 3]) + " " + str(self.matrix[1, 3])\
                  + " " + str(self.matrix[2, 3]) + " " + \
                  str(self.matrix[3, 3]) + "|\n"
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
        ret.w_column(vector=vect)
    else:
        _cos = cos(angle)
        _sin = sin(angle)
        inverse_cos = 1.0 - _cos
        components = [[inverse_cos * axis[i] * axis[j] for i in range(0, 3)]
                      for j in range(0, 3)]

        ret.x_column([components[0][0] + _cos,
                      components[0][1] + axis.z_component * _sin,
                      components[0][2] - axis.y_component * _sin])
        ret.y_column([components[1][0] - axis.z_component * _sin,
                      components[1][1] + _cos,
                      components[1][2] + axis.x_component * _sin])
        ret.z_column([components[0][1] + axis.y_component * _sin,
                      components[1][2] - axis.x_component * _sin,
                      components[2][2] + _cos])

        ret.w_column()
        ret.w_row()
    return ret
