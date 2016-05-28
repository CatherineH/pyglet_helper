import os
from pyglet.gl import glViewport, glMatrixMode, GL_PROJECTION, \
    gluPerspective, glLoadIdentity, gluLookAt, GL_MODELVIEW
from pyglet.window import Window
from pyglet.app import run
from pyglet.clock import schedule
from pyglet.event import EVENT_HANDLED
from pyglet.image import get_buffer_manager
from pyglet_helper.objects import *
from pyglet_helper.util import color, Vector
from math import sin, cos, pi

_window = Window()
scene = View()


def update(dt):
    global rx, ry, rz
    rx += dt * pi / 30.0
    ry += dt * pi * 2.0 / 9.0
    rz += dt * pi * 1 / 120.0
    rx %= 2.0 * pi
    ry %= 2.0 * pi
    rz %= 2.0 * pi

schedule(update)


@_window.event
def on_resize(width, height):
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
    return EVENT_HANDLED

@_window.event
def on_draw():
    global screennum
    scene.setup()
    spin = Vector([sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx)])
    _ellipsoid.axis = _ellipsoid.length*spin
    _ellipsoid.render(scene)

    # The sphere will look the same from all angles, so rotating it doesn't make sense
    _ball.render(scene)

    _pyramid.axis = _pyramid.length*spin
    _pyramid.render(scene)

    _box.axis = _box.length*spin
    _box.render(scene)

    _cylinder.axis = _cylinder.length*spin
    _cylinder.render(scene)

    _arrow.axis = _arrow.length*spin
    _arrow.render(scene)

    _cone.axis = _cone.length*spin
    _cone.render(scene)

    _ring.axis = spin
    _ring.render(scene)
    if screennum < 99 and render_images:
        path = os.path.dirname(__file__)
        filename = os.path.join(path, 'screenshot%02d.png' % (screennum, ))
        get_buffer_manager().get_color_buffer().save(filename)
        screennum += 1

screennum = 0
render_images = False

# put all objects in a scene together
_ball = Sphere(pos=Vector([1, 1, 0]), radius=0.5, color=color.RED)
_box = Box(pos=Vector([-1, 0, 0]), length=0.4, height=0.5, width=1, color=color.BLUE)
_pyramid = Pyramid(pos=Vector([1, -1, 0]), length=1.0, height=1.0, width=1.0,
                   color=color.CYAN)
_arrow = Arrow(pos=Vector([0, 1, 0]), axis=Vector([1, 0, 0]), fixed_width=False, head_width=0.4, head_length=0.50,
               shaft_width=0.20, color=color.YELLOW)
_cone = Cone(pos=Vector([0, 0, 0]), axis=Vector([1, 0, 0]), radius=0.5, color=color.GRAY)
_ring = Ring(pos=Vector([0, -1, 0]), axis=Vector([0, 1, 0]), radius=0.5, thickness=0.1,
             color=color.MAGENTA)
_ellipsoid = Ellipsoid(pos=Vector([-1, -1, 0]), length=0.75, height=0.5, width=0.75,
                       color=color.GREEN)
_cylinder = Cylinder(pos=Vector([1, 0, 0]), axis=Vector([0.3, 0, 0]), radius=0.4,
                     color=color.ORANGE)
_light0 = Light(position=(1, 0.5, 1, 0), specular=(.5, .5, 1, 0.5))
_light0.render(scene)
_light1 = Light(position=(1, 0, .5, 0), specular=(.5, .5, .5, 1))
_light1.render(scene)


rx = ry = rz = 0

run()
print("hello world")