# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from util.vector import vector
from pyglet.gl import *
from numpy import matrix, identity
from numpy.linalg import inv

class vertex:
    def __init__(self, x = 0, y = 0, z = 0, w = 0, v = None):
        if not v is None:
            self.x = v.x
            self.y = v.y
            self.z = v.z
        self.w = w

    def project(self):
        w_i = 1.0/self.w
        return vector( self.x*w_i, self.y*w_i, self.z*w_i)

    def gl_render(self):
        glVertex4d( self.x, self.y, self.z, self.w)

'''
 A -precision 3D affine transformation matrix.
'''
class tmatrix:
    def __init__(self, t = None, A = None, B = None):
        # This is a -precision matrix in _COLUMN MAJOR ORDER_.  User's beware.
        # It is in this order since that is what OpenGL uses internally - thus
        #eliminating a reformatting penalty.
        if not t is None:
            self.M = t.M
        elif not A is None and not B is None:
            self.M = matrix(A*B)
        else:
             self.M = matrix(identity(4))

    def __getitem__(self, key):
        return self.M[key]

    def __mul__(self, o):
        return self.M*o

    def inverse(self):
        self.M = inv(self.M)

    #Projects v using the current tmatrix values.
    def project(self, v):
        o = vertex()
        o.x = self.M[0,0]*v.x + self.M[1,0]*v.y + self.M[2,0]*v.z + self.M[3,0]
        o.y = self.M[0,1]*v.x + self.M[1,1]*v.y + self.M[2,1]*v.z + self.M[3,1]
        o.z = self.M[0,2]*v.x + self.M[1,2]*v.y + self.M[2,2]*v.z + self.M[3,2]
        o.w = self.M[0,3]*v.x + self.M[1,3]*v.y + self.M[2,3]*v.z + self.M[3,3]
        return o

    # Right-multiply this matrix by a scaling matrix.
    def scale(self, v, w):
        self.M[0,0] *= v.x
        self.M[0,1] *= v.x
        self.M[0,2] *= v.x
        self.M[0,3] *= v.x

        self.M[1,0] *= v.y
        self.M[1,1] *= v.y
        self.M[1,2] *= v.y
        self.M[1,3] *= v.y

        self.M[2,0] *= v.z
        self.M[2,1] *= v.z
        self.M[2,2] *= v.z
        self.M[2,3] *= v.z

        self.M[3,0] *= w
        self.M[3,1] *= w
        self.M[3,2] *= w
        self.M[3,3] *= w

    # Right multiply the matrix by a translation matrix
    def translate(self, v):
        self.M[3,0] += v.x * self.M[0,0] + v.y * self.M[1,0] + v.z * M[2,0]
        self.M[3,1] += v.x * self.M[0,1] + v.y * self.M[1,1] + v.z * M[2,1]
        self.M[3,2] += v.x * self.M[0,2] + v.y * self.M[1,2] + v.z * M[2,2]
        self.M[3,3] += v.x * self.M[0,3] + v.y * self.M[1,3] + v.z * M[2,3]

    def times_inv(self, v, w):
        x = v.x - self.M[3,0]*w
        y = v.y - self.M[3,1]*w
        z = v.z - self.M[3,2]*w
        return vector(self.M[0,0]*x + self.M[0,1]*y + self.M[0,2]*z, \
            self.M[1,0]*x + self.M[1,1]*y + self.M[1,2]*z, \
            self.M[2,0]*x + self.M[2,1]*y + self.M[2,2]*z)

    def times_v(self, v):
        return vector(    self.M[0,0]*v.x + self.M[1,0]*v.y + self.M[2,0]*v.z, \
        self.M[0,1]*v.x + self.M[1,1]*v.y + self.M[2,1]*v.z, \
        self.M[0,2]*v.x + self.M[1,2]*v.y + self.M[2,2]*v.z )

    # Sets the first column to v
    def x_column(self, v = None, x = None, y = None, z = None):
        if not v is None:
            self.M[0,0] = v.x
            self.M[0,1] = v.y
            self.M[0,2] = v.z
        else:
            self.M[0,0] = x
            self.M[0,1] = y
            self.M[0,2] = z

    # Sets the second column to v
    def y_column(self, v = None, x = None, y = None, z = None):
        if not v is None:
            self.M[1,0] = v.x
            self.M[1,1] = v.y
            self.M[1,2] = v.z
        else:
            self.M[1,0] = x
            self.M[1,1] = y
            self.M[1,2] = z

    def origin(self):
        return vector( self.M[3,0], self.M[3,1], self.M[3,2])

    # Sets the third column to v
    def z_column(self, v = None, x = None, y = None, z = None):
        if not v is None:
            self.M[2,0] = v.x
            self.M[2,1] = v.y
            self.M[2,2] = v.z
        else:
            self.M[2,0] = x
            self.M[2,1] = y
            self.M[2,2] = z

    # Sets the fourth column to v
    def w_column(self, v = None, x = None, y = None, z = None):
        if not v is None:
            self.M[3,0] = v.x
            self.M[3,1] = v.y
            self.M[3,2] = v.z
        else:
            self.M[3,0] = x
            self.M[3,1] = y
            self.M[3,2] = z


    # Sets the bottom row to x, y, z, w
    def w_row(self, x=0, y=0, z=0,w=1):
        self.M[0,3]=x
        self.M[1,3]=y
        self.M[2,3]=z
        self.M[3,3]=w

    # Overwrites the currently active matrix in OpenGL with this one.
    def gl_load(self):
        glLoadMatrixd( self.M[0])

    # Multiplies the active OpenGL matrix by this one.
    def gl_mult(self):
        glMultMatrixd(self.M[0])

    '''
     Initialize this tmatrix with the contents of the OpenGL modelview,
     texture, color, or projection matricies.
     @return *this.
    '''
    def gl_modelview_get(self):
        m = [[0]*4]*4
        m[0] = glGetFloatv( GL_MODELVIEW_MATRIX, m[0])
        for i in range(0,4):
            for j in range(0,4):
                self.M[i,j] = m[i][j]
        return self.M

    def gl_texture_get(self):
        m = [[0]*4]*4
        m[0] = glGetFloatv( GL_TEXTURE_MATRIX)
        for i in range(0, 4):
            for j in range(0,4):
                self.M[i,j] = m[i][j]
        return self.M

    def gl_color_get(self):
        m = [[0]*4]*4
        m[0] = glGetFloatv( GL_COLOR_MATRIX)
        for i in range(0, 4):
            for j in range(0,4):
                self.M[i,j] = m[i][j]
        return self.M

    def gl_projection_get(self):
        m = [[0]*4]*4
        m[0] = glGetFloatv( GL_PROJECTION_MATRIX)
        for i in range(0, 4):
            for j in range(0,4):
                self.M[i,j] = m[i][j]
        return self.M

    '''
     Dump this matrix to a formatted string.
    '''
    def __str__(self):
        output = "| " + M[0,0] + " " + M[1,0] + " " + M[2,0] + " " + M[3,0] + "|\n"
        output += "| " + M[0,1] + " " + M[1,1] + " " + M[2,1] + " " + M[3,1] + "|\n"
        output +=  "| " + M[0,2] + " " + M[1,2] + " " + M[2,2] + " " + M[3,2] + "|\n"
        output +=  "| " + M[0,3] + " " + M[1,3] + " " + M[2,3] + " " + M[3,3] + "|\n"


# Returns a rotation matrix to perform rotations about an axis passing through
# the origin through an angle in the direction specified by the Right Hand Rule.
def rotation(angle, axis, origin = None):
    from math import cos, sin
    ret = tmatrix()
    if not origin is None:
        ret = rotation(angle, axis.norm())
        ret.w_column( origin - ret * origin)
    else:
        c = cos(angle)
        s = sin(angle)
        ic = 1.0-c
        icxx = ic * axis.x * axis.x
        icxy = ic * axis.x * axis.y
        icxz = ic * axis.x * axis.z
        icyy = ic * axis.y * axis.y
        icyz = ic * axis.y * axis.z
        iczz = ic * axis.z * axis.z


        ret.x_column( icxx +        c, icxy + axis.z*s, icxz - axis.y*s )
        ret.y_column( icxy - axis.z*s, icyy +     c   , icyz + axis.x*s )
        ret.z_column( icxz + axis.y*s, icyz - axis.x*s, iczz +        c )
        ret.w_column()
        ret.w_row()
    return ret


# Pushes its constructor argument onto the active OpenGL matrix stack, and
# multiplies the active matrix by the new one when constructed, and pops it off
# when destructed.
class gl_matrix_stackguard:
    # A stackguard that only performs a push onto the matrix stack.
    # Postcondition: the stack is one matrix taller, but identical to before.

    def __init__(self, m = None):
        glPushMatrix()
        if not m is None:
            m.gl_mult()

    def __del__(self):
        glPopMatrix()
