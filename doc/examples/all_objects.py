from pyglet_helper import vsetup, vrun
from pyglet_helper.objects import *
from pyglet_helper.util import color, Vector
from math import sin, cos, pi

_view = View()
vsetup(_view)


def update(dt):
    global rx, ry, rz
    rx += dt * pi / 30.0
    ry += dt * pi * 2.0 / 9.0
    rz += dt * pi * 1 / 120.0
    rx %= 2.0 * pi
    ry %= 2.0 * pi
    rz %= 2.0 * pi
    spin = Vector([sin(rx) * cos(ry), sin(rx) * sin(ry), cos(rx)])
    for object in _view.screen_objects:
        object.axis = object.length*spin

spacing = 3

# put all objects in a scene together
_ball = Sphere(pos=Vector([spacing, spacing, 0]), radius=1, color=color.RED)
_box = Box(pos=Vector([-spacing, 0, 0]), length=0.8, height=1, width=2, color=color.BLUE)
_pyramid = Pyramid(pos=Vector([spacing, -spacing, 0]), length=2.0, height=2.0, width=2.0,
                   color=color.CYAN)
_arrow = Arrow(pos=Vector([0, spacing, 0]), axis=Vector([2, 0, 0]), fixed_width=False,
               head_width=0.8, head_length=1.0, shaft_width=0.40, color=color.YELLOW)
_cone = Cone(pos=Vector([0, 0, 0]), axis=Vector([1, 0, 0]), radius=1, color=color.GRAY)
_ellipsoid = Ellipsoid(pos=Vector([-spacing, -spacing, 0]), length=1.5, height=1.0, width=1.5,
                       color=color.GREEN)
_cylinder = Cylinder(pos=Vector([spacing, 0, 0]), axis=Vector([0.3, 0, 0]), radius=0.8,
                     color=color.ORANGE)
_ring = Ring(pos=Vector([0, -spacing, 0]), axis=Vector([0, 1, 0]), radius=1.0, thickness=0.2,
             color=color.MAGENTA)


rx = ry = rz = 0

vrun(update)
