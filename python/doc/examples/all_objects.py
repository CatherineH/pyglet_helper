import os
from pyglet.gl import *
from pyglet_helper.objects import *
from pyglet_helper.util import color, Vector
from math import sin, cos, pi

window = pyglet.window.Window()
scene = View()


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


@window.event
def on_draw():
    global screennum
    scene.setup()

    _ellipsoid.axis = _ellipsoid.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _ellipsoid.render(scene)

    # The sphere will look the same from all angles, so rotating it doesn't make sense
    _ball.render(scene)

    _pyramid.axis = _pyramid.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _pyramid.render(scene)

    _box.axis = _box.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _box.render(scene)

    _cylinder.axis = _cylinder.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _cylinder.render(scene)

    _arrow.axis = _arrow.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _arrow.render(scene)

    _cone.axis = _cone.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _cone.render(scene)

    _ring.axis = Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _ring.render(scene)
    if screennum < 99:
        path = os.path.dirname(__file__)
        filename = os.path.join(path, 'screenshot%02d.png' % (screennum, ))
        pyglet.image.get_buffer_manager().get_color_buffer().save(filename)
        screennum += 1

screennum = 0


# put all objects in a scene together
_ball = Sphere(pos=(1, 1, 0), radius=0.5, color=color.red)
_box = Box(pos=(-1, 0, 0), length=0.4, height=0.5, width=1, color=color.blue)
_pyramid = Pyramid(pos=(1, -1, 0), size=(1, 1, 1), color=color.cyan)
_arrow = Arrow(pos=(0, 1, 0), axis=(1, 0, 0), fixed_width=False, head_width=0.4, head_length=0.50, shaft_width=0.20,
               color=color.yellow)
_cone = Cone(pos=(0, 0, 0), axis=(1, 0, 0), radius=0.5, color=color.gray)
_ring = Ring(pos=(0, -1, 0), axis=(0, 1, 0), radius=0.5, thickness=0.1, color=color.magenta)
_ellipsoid = Ellipsoid(pos=(-1, -1, 0), length=0.75, height=0.5, width=0.75, color=color.green)
_cylinder = Cylinder(pos=(1, 0, 0), axis=(0.3, 0, 0), radius=0.4, color=color.orange)
_light0 = Light(position=(1, 0.5, 1, 0), specular=(.5, .5, 1, 0.5))
_light0.render(scene)
_light1 = Light(position=(1, 0, .5, 0), specular=(.5, .5, .5, 1))
_light1.render(scene)


rx = ry = rz = 0
ry = 0
rx = 0.4

pyglet.app.run()
