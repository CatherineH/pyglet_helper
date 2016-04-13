from __future__ import print_function
from mock import patch
import pyglet_helper.test.fake_gl

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


@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.cylinder.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.quadric.gl', new=pyglet_helper.test.fake_gl)
def test_cylinder_render():
    from pyglet_helper.objects import Cylinder
    from pyglet_helper.objects import View
    _cylinder = Cylinder()
    _view = View()
    _cylinder.render(_view)