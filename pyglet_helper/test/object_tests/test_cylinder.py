from __future__ import print_function


def test_cylinder_degenerate():
    from pyglet_helper.objects import Cylinder
    blo = Cylinder(radius=0.0)
    assert(blo.degenerate)


def test_cylinder_center():
    from pyglet_helper.objects import Cylinder
    from pyglet_helper.util import Vector
    blo = Cylinder(radius=0.0, pos=Vector([0, -0.5, 0]),
                   axis=Vector([0, 1, 0]))
    assert(abs(blo.center[0]) < 1e-7)
    assert(blo.center[1] == 0)
    assert(blo.center[2] == 0)