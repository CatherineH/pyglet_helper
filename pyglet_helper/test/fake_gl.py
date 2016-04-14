"""
The following file contains definitions for GL functions when pyglet can't
be used, such as on testing on continuous integration systems.
"""
from ctypes import c_float, c_double, c_uint


GLfloat = c_float
GLdouble = c_double
GLuint = c_uint
GL_COLOR_BUFFER_BIT = 16384
GL_CULL_FACE = 2884
GL_DEPTH_BUFFER_BIT = 256
GL_DEPTH_TEST = 2929
GL_LIGHTING = 2896
GL_LIGHT0 = 16384
GL_LIGHT1 = 16385
GL_LIGHT2 = 16386
GL_LIGHT3 = 16387
GL_LIGHT4 = 16388
GL_LIGHT5 = 16389
GL_LIGHT6 = 16390
GL_LIGHT7 = 16391


GL_COMPILE = 0
GL_FRONT = 0
GL_BACK = 0
GL_FLOAT = 0
GL_MODELVIEW_MATRIX = 0
GL_TEXTURE_MATRIX = 0
GL_COLOR_MATRIX = 0
GL_PROJECTION_MATRIX = 0
GL_FRONT_AND_BACK = 0
GL_AMBIENT_AND_DIFFUSE = 0
GL_SPECULAR = 0
GL_SHININESS = 0
GL_CLIENT_VERTEX_ARRAY_BIT = 0
GL_VERTEX_ARRAY = 0
GL_NORMAL_ARRAY = 0
GL_TRIANGLES = 0
GL_UNSIGNED_INT = 0
GL_VERTEX_SHADER_ARB = 0
GL_FRAGMENT_SHADER_ARB = 0
GL_OBJECT_LINK_STATUS_ARB = 0
GL_OBJECT_INFO_LOG_LENGTH_ARB = 0
GL_POSITION = 0
GL_DIFFUSE = 0

class GLException(Exception):
   def __init__(self, value):
        self.value = value
   def __str__(self):
        return repr(self.value)


def glNormal3f(a, b, c):
    pass


def glVertex3f(a, b, c):
    pass


def glNormal3dv(component):
    pass


def glVertex3d(a, b, c):
    pass


def glVertex4d(a, b, c, d):
    pass


def glGenLists(handle):
    return handle


def glEnable(lighting):
    pass


def glClearColor(a, b, c, d):
    pass


def glColor3f(a, b, c):
    pass


def glClear(a):
    pass


def glLoadIdentity():
    pass


def glRotatef(x, y, z, w):
    pass


def glNewList(handle, compile):
    pass


def glEndList(handle=None):
    pass


def glPushMatrix():
    pass


def glCullFace(front):
    pass


def glCallList(handle):
    pass


def glPopMatrix():
    pass


def glLoadMatrixd(ctypes_matrix):
    pass


def glMultMatrixd(ctype_matrix):
    pass


def glGetFloatv(matrix, ctypes_matrix):
    return [-1.0, -1.0, -1.0, -1.0]


def glMaterialf(front_and_back, shininess, val):
    pass


def glMaterialfv(front_and_back, shininess, val):
    pass


def glPushClientAttrib(array_bit):
    pass


def glEnableClientState(array):
    pass


def glVertexPointer(pointer, type, index, vertices):
    pass


def glNormalPointer(type, index, normals):
    pass

def glDrawElements(triangles, indices_leng, type, indices):
    pass


def glPopClientAttrib():
    pass


def glBegin(triangles):
    pass


def glNormal3fv(a, b, c):
    pass


def glEnd():
    pass


def glDisable(cull_face):
    pass


def glTranslatef(a, b, c):
    pass


def glTranslated(x, y, z):
    pass


def glScaled(x, y, z):
    pass


def glLightfv(defined_light, position, light_position):
    pass


class glext_arb(object):
    GL_ARB_shader_objects = 1

    @staticmethod
    def glGetUniformLocationARB(program, name):
        return 0

    @staticmethod
    def glCreateShaderObjectARB(shader_type):
        return 1

    @staticmethod
    def glShaderSourceARB(shader, handle):
        pass

    @staticmethod
    def glCompileShaderARB(shader):
        pass

    @staticmethod
    def glAttachObjectARB(program, shader):
        pass

    @staticmethod
    def glDeleteObjectARB(shader):
        pass

    @staticmethod
    def glCreateProgramObjectARB():
        pass

    @staticmethod
    def glLinkProgramARB(program):
        pass

    @staticmethod
    def glGetObjectParameterivARB(program, link_status):
        return False

    @staticmethod
    def glGetInfoLogARB(program, length):
        return (0.0, 0.0)

class glu(object):
    GLU_FILL = 1
    GLU_SMOOTH = 1
    GLU_OUTSIDE = 1
    GLU_INSIDE = 1
    GLU_POINT = 1
    GLU_LINE = 1
    GLU_FILL = 1
    GLU_SILHOUETTE = 1

    @staticmethod
    def gluDisk(quadric, thickness, radius, slices, rings):
        pass

    @staticmethod
    def gluCylinder(quadric, base_radius, top_radius, height, slices, stacks):
        pass

    @staticmethod
    def gluNewQuadric():
        return -1

    @staticmethod
    def gluQuadricDrawStyle(quadric, fill):
        pass

    @staticmethod
    def gluQuadricNormals(quadric, smooth):
        pass

    @staticmethod
    def gluQuadricOrientation(quadric, outside):
        pass

    @staticmethod
    def gluQuadricDrawStyle(quadric, point):
        pass

    @staticmethod
    def gluQuadricNormals(quadric, style):
        pass

    @staticmethod
    def gluSphere(quadric, radius, slices, stacks):
        pass

    @staticmethod
    def gluDeleteQuadric(quadric):
        pass

