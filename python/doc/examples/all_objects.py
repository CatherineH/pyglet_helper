#temporary, until I get the setup working.

import sys
import os
filename = os.path.dirname(os.path.realpath(__file__))
filename = filename.replace("doc/examples", "src")
sys.path.append(filename)

from objects.box import *
from objects.sphere import *
from objects.arrow import *
from objects.cone import *
from objects.cylinder import *
from objects.pyramid import *
from objects.ring import *
from objects.ellipsoid import *
from util import *

from numpy import zeros

window = pyglet.window.Window()
n = [ [-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, -1.0] ]
faces = [[0, 1, 2, 3], [3, 2, 6, 7], [7, 6, 5, 4], [4, 5, 1, 0], [5, 6, 2, 1], [7, 4, 0, 3] ]
v = zeros([8,3])
v[0][0] = v[1][0] = v[2][0] = v[3][0] = -1
v[4][0] = v[5][0] = v[6][0] = v[7][0] = 1
v[0][1] = v[1][1] = v[4][1] = v[5][1] = -1
v[2][1] = v[3][1] = v[6][1] = v[7][1] = 1
v[0][2] = v[3][2] = v[4][2] = v[7][2] = 1
v[1][2] = v[2][2] = v[5][2] = v[6][2] = -1
for i in range(0,6):
    glBegin(GL_QUADS)
    print n[i][0]
    glNormal3fv(GLfloat(n[i][0]))
    glVertex3fv(GLfloat(v[faces[i][0]][0]))
    glVertex3fv(GLfloat(v[faces[i][1]][0]))
    glVertex3fv(GLfloat(v[faces[i][2]][0]))
    glVertex3fv(GLfloat(v[faces[i][3]][0]))
    glEnd()

#put all objects in a scene together
#_box = box(length = 4, height = 0.5, width = 4, color = color.blue)
'''
_ball = sphere(pos=(0,4,0), color = color.red)

_arrow = arrow(fixedwidth = False, headwidth = 0.4, headlength = 1.0, shaftwidth = 2.0, color = color.yellow)

_cone = cone(pos=[5,2,0], axis=(12,0,0), radius=1, color = color.green)

_cylinder = cylinder(pos=(0,2,1), axis=(5,0,0), radius=1, color = color.black)

_pyramid = pyramid(pos=(5,2,0), size=(12,6,4), color = color.cyan)

_ring = ring(pos=(1,1,1), axis=(0,1,0), radius=0.5, thickness=0.1, color = color.magenta)

_ellipsoid = ellipsoid(pos=(3,3,3), length=2, height=1, width=3, color = color.white)
'''

pyglet.app.run()
