# temporary, until I get the setup working.

import sys
import os

filename = os.path.dirname(os.path.realpath(__file__))
filename = filename.replace("doc/examples", "src")
sys.path.append(filename)

from pygletHelper.objects.box import *
from pygletHelper.objects.sphere import *
from pygletHelper.objects.arrow import *
from pygletHelper.objects.cone import *
from pygletHelper.objects.cylinder import *
from pygletHelper.objects.pyramid import *
from pygletHelper.objects.ring import *
from pygletHelper.objects.ellipsoid import *
from pygletHelper.objects.create_display import *
from pygletHelper.objects.renderable import view
from pygletHelper.util import *

global scene
# scene = display()

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
from pygletHelper.objects.pyramid import pyramid
from pygletHelper.objects.box import box
from pygletHelper.objects.arrow import arrow
from pygletHelper.objects.cone import cone
from pygletHelper.objects.cylinder import cylinder
from pygletHelper.objects.ring import ring
from pygletHelper.objects.ellipsoid import ellipsoid
from pygletHelper.objects.renderable import view
from pygletHelper.util.vector import vector
from traceback import print_stack
from math import sin, cos, pi

window = pyglet.window.Window()
scene = view()


def update(dt):
    global rx, ry, rz
    rx += dt * pi / 30.0
    ry += dt * pi * 2.0 / 9.0
    rz += dt * pi * 1 / 120.0
    rx %= 2.0 * pi
    ry %= 2.0 * pi
    rz %= 2.0 * pi


pyglet.clock.schedule(update)


@window.event
def on_resize(width, height):
    print('resized!')
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / float(height), .1, 1000)

    gluLookAt(
        0, 0, 4,  # eye
        0, 0, 0,  # target
        0, 1, 0  # up
    )
    glMatrixMode(GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED


global screennum


@window.event
def on_draw():
    global screennum
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    _arrow.axis = vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _arrow.gl_render(scene)
    _ball.gl_render(scene)
    _box.axis = vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _box.gl_render(scene)
    _cone.axis = vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _cone.gl_render(scene)
    _pyramid.axis = vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _pyramid.gl_render(scene)
    _ellipsoid.axis = vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _ellipsoid.gl_render(scene)
    _cylinder.axis = vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _cylinder.gl_render(scene)
    _ring.axis = vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _ring.gl_render(scene)
    if screennum < 99:
        filename = '/home/cholloway/screenshot%02d.png' % (screennum, )
        pyglet.image.get_buffer_manager().get_color_buffer().save(filename)
        screennum += 1


screennum = 0


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


# put all objects in a scene together

_ball = sphere(pos=(1, 1, 0), radius=0.5, color=color.red)
_box = box(pos=(1, 0, 0), length=0.4, height=0.5, width=1, color=color.blue)
_pyramid = pyramid(pos=(1, -1, 0), size=(1, 1, 1), color=color.cyan)
_arrow = arrow(pos=(0, 1, 0), axis=(1, 0, 0), fixedwidth=False, headwidth=0.4, headlength=0.50, shaftwidth=0.20,
               color=color.yellow)
_cone = cone(pos=(0, 0, 0), axis=(1, 0, 0), radius=0.5, color=color.gray)
_ring = ring(pos=(0, -1, 0), axis=(0, 1, 0), radius=0.5, thickness=0.1, color=color.magenta)
_ellipsoid = ellipsoid(pos=(-1, -1, 0), length=0.75, height=0.5, width=0.75, color=color.green)
_cylinder = cylinder(pos=(-1, 0, 0), axis=(1.3, 0, 0), radius=0.24, color=color.orange)

setup()
rx = ry = rz = 0
ry = 0
rx = 1.57

pyglet.app.run()
