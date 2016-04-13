from __future__ import print_function
from mock import patch
import pyglet_helper.test.fake_gl

@patch('pyglet_helper.objects.cone.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.quadric.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_cone_render():
    from pyglet_helper.objects import Cone
    from pyglet_helper.objects import View
    _cone = Cone()
    _view = View()
    _cone.opacity = 0.0
    _cone.render(_view)
    _cone.opacity = 1.0
    _cone.render(_view)
    _cone.radius = 0
    _cone.render(_view)


@patch('pyglet_helper.objects.cone.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.quadric.gl', new=pyglet_helper.test.fake_gl)
def test_cone_center():
    from pyglet_helper.objects import Cone
    from pyglet_helper.util import Vector
    _cone = Cone(pos=Vector([0.5, 0, 0]), axis=Vector([-1.0, 0.0, 0.0]))
    assert _cone.center[0] == 0
    assert _cone.center[1] == 0
    assert _cone.center[2] == 0

@patch('pyglet_helper.objects.cone.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.quadric.gl', new=pyglet_helper.test.fake_gl)
def test_cone_degenerate():
    from pyglet_helper.objects import Cone
    _cone = Cone()
    _cone.radius = 0.0
    assert _cone.degenerate
