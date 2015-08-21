# temporary, until I get the setup working.

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
from objects.create_display import *
from objects.renderable import view
from util import *

global scene
#scene = display()

#print (scene)

from numpy import zeros
# !/usr/bin/env python
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------


from pyglet.gl import *
#import pyglet
from objects.pyramid import pyramid
from objects.box import box
from objects.arrow import arrow
from objects.cone import cone
from objects.cylinder import cylinder
from objects.ring import ring
from objects.ellipsoid import ellipsoid
from traceback import print_stack

window = pyglet.window.Window()


def update(dt):
    global rx, ry, rz
    rx += dt * 1
    ry += dt * 80
    rz += dt * 30
    rx %= 360
    ry %= 360
    rz %= 360


pyglet.clock.schedule(update)

@window.event
def on_resize(width, height):
    print('resized!')
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / float(height), .1, 1000)

    gluLookAt(
     1, 4, 3, # eye
     0, 0, 0, # target
     0, 1, 0  # up
    );
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED

@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0, -4)
    glRotatef(rz, 0, 0, 1)
    glRotatef(ry, 0, 1, 0)
    glRotatef(rx, 1, 0, 0)
    #print("rs "+str(rx)+" "+str(ry)+" "+str(rz))
    glTranslatef(0,0,2)
    _pyramid.init_model()
    glTranslatef(0,0,-2)
    _box.init_model()
    glTranslatef(0,0,4)
    _cone.init_model()
    glTranslatef(0,0,-4)
    glTranslatef(0, 2, 0)
    _ball.init_model()
    glTranslatef(2,0,0)
    _ellipsoid.init_model()
    glTranslatef(2, 0,0)
    _ring.init_model()

    glTranslatef(-4, -2, 0)

def setup():
    # One-time GL setup
    glClearColor(1, 1, 1, 1)
    glColor3f(1, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    # Uncomment this line for a wireframe view
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always
    # include it.
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    # Define a simple function to create ctypes arrays of floats:
    def vec(*args):
        return (GLfloat * len(args))(*args)

    glLightfv(GL_LIGHT0, GL_POSITION, vec(.5, .5, 1, 0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
    glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

# put all objects in a scene together

_ball = sphere(pos=(0,4,0), color = color.red)

_box = box(length=2, height=0.5, width=2, color=color.blue)
_pyramid = pyramid(pos=(0,0,0), size=(1,1,1), color = color.cyan)
_arrow = arrow(fixedwidth = False, headwidth = 0.4, headlength = 1.0, shaftwidth = 2.0, color = color.yellow)
_cone = cone(pos=[5,2,0], axis=(12,0,0), radius=1, color = color.green)
_cylinder = cylinder(pos=(0,2,1), axis=(5,0,0), radius=1, color = color.black)
_ring = ring(pos=(1,1,1), axis=(0,1,0), radius=0.5, thickness=0.1, color = color.magenta)
_ellipsoid = ellipsoid(pos=(3,3,3), length=2, height=1, width=3, color = color.white)


#setup()
rx = ry = rz = 0


pyglet.app.run()
