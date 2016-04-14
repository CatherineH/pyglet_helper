from __future__ import print_function
from mock import patch
from nose.tools import raises
import pyglet_helper.test.fake_gl


@patch('pyglet_helper.objects.light.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_light_is_light():
    from pyglet_helper.objects import Light
    _light = Light()
    assert _light.is_light


@raises(ValueError)
@patch('pyglet_helper.objects.light.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_light_material_get_error():
    from pyglet_helper.objects import Light
    _light = Light()
    blo = _light.material


@raises(ValueError)
@patch('pyglet_helper.objects.light.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_light_material_set_error():
    from pyglet_helper.objects import Light
    _light = Light()
    _light.material = "blo"


@patch('pyglet_helper.objects.light.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_light_render():
    from pyglet_helper.objects import Light
    from pyglet_helper.objects import View
    _light = Light()
    _view = View()
    _light.render(_view)

@patch('pyglet_helper.objects.light.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_light_center():
    from pyglet_helper.objects import Light
    from pyglet_helper.util import Vector
    _light = Light()
    assert _light.center == Vector()


@patch('pyglet_helper.objects.light.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_light_center():
    from pyglet_helper.objects import Light
    from pyglet_helper.util import Rgba
    _light = Light()
    _my_col = Rgba(color=[.2, .30, .4, 1.0])
    _light.rgb = _my_col
    assert _light.rgb[0] == 0.2
    assert _light.rgb[1] == 0.3
    assert _light.rgb[2] == 0.4