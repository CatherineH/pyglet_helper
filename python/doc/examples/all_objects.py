from pyglet.gl import *
from pyglet_helper.objects.sphere import Sphere
from pyglet_helper.objects.pyramid import Pyramid
from pyglet_helper.objects.box import Box
from pyglet_helper.objects.arrow import Arrow
from pyglet_helper.objects.cone import Cone
from pyglet_helper.objects.cylinder import Cylinder
from pyglet_helper.objects.ring import Ring
from pyglet_helper.objects.ellipsoid import Ellipsoid
from pyglet_helper.objects.renderable import View
from pyglet_helper.util.vector import Vector
from pyglet_helper.util import color
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
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    _ellipsoid.axis = _ellipsoid.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _ellipsoid.gl_render(scene)

    # The sphere will look the same from all angles, so rotating it doesn't make sense
    _ball.gl_render(scene)

    _pyramid.axis = _pyramid.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _pyramid.gl_render(scene)

    _box.axis = _box.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _box.gl_render(scene)

    _cylinder.axis = _cylinder.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _cylinder.gl_render(scene)

    _arrow.axis = _arrow.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _arrow.gl_render(scene)

    _cone.axis = _cone.length*Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _cone.gl_render(scene)

    _ring.axis = Vector(sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx))
    _ring.gl_render(scene)
    if screennum < 99:
        path = os.path.dirname(__file__)
        filename = os.path.join(path, 'screenshot%02d.png' % (screennum, ))
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

    glLightfv(GL_LIGHT0, GL_POSITION, vec(1, 0.5, 1, 0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 0.5))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
    glLightfv(GL_LIGHT1, GL_POSITION, vec(1, 0, .5, 0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(.5, .5, .5, 1))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1, 1, 1, 1))


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

setup()
rx = ry = rz = 0
ry = 0
rx = 0.4

pyglet.app.run()
