"""
The following file contains definitions for GL functions when pyglet can't
be used, such as on testing on continuous integration systems.
"""
from ctypes import c_float

'''
class gl(object):

    GLfloat = c_float
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


    def glNormal3f(a, b, c):
        print("hello from fakegl")


    def glVertex3f(a, b, c):
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
'''

GLfloat = c_float
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


def glNormal3f(a, b, c):
    print("hello from fakegl")


def glVertex3f(a, b, c):
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