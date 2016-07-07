from __future__ import print_function, division, absolute_import

def test_thickline():
    from pyglet_helper.objects import Curve, View

    from pyglet_helper.util import Vector
    bloop = Curve()
    _scene = View()
    bloop.pos = [Vector([0, 0, 0]), Vector([0, 0, 10])]
    bloop.radius = 1.0
    bloop.thickline(_scene)
    assert bloop.projected[0] == Vector([0, 0, 0])
    assert bloop.projected[4] == Vector([0, 1, 10])