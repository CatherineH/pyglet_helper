from __future__ import print_function


def test_ellipsoid_scale():
    from pyglet_helper.objects import Ellipsoid
    _ellipsoid = Ellipsoid(width=1.0, height=2.0, length=4.0)
    assert _ellipsoid.scale[0] == 2.0
    assert _ellipsoid.scale[1] == 1.0
    assert _ellipsoid.scale[2] == 0.5


def test_ellipsoid_degenerate():
    from pyglet_helper.objects import Ellipsoid
    _ellipsoid = Ellipsoid()
    _ellipsoid.visible = False
    assert _ellipsoid.degenerate
