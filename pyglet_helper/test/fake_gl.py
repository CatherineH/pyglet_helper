"""
The following file contains definitions for GL functions when pyglet can't
be used, such as on testing on continuous integration systems.
"""
from ctypes import c_float


GLfloat = c_float
GL_LIGHT0 = 16384
GL_LIGHT1 = 16385
GL_LIGHT2 = 16386
GL_LIGHT3 = 16387
GL_LIGHT4 = 16388
GL_LIGHT5 = 16389
GL_LIGHT6 = 16390
GL_LIGHT7 = 16391


def glNormal3f(a, b, c):
    pass


def glVertex3f(a, b, c):
    pass