from __future__ import print_function, division, absolute_import

from mock import patch
import pyglet_helper


@patch('pyglet_helper.objects.box.gl', new=pyglet_helper.test.fake_gl)
def test_box_generate_model():
    from pyglet_helper.objects import Box
    box = Box()
    box.generate_model()


@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.box.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_sphere_render():
    from pyglet_helper.objects import Box
    from pyglet_helper.objects import View
    _box = Box()
    _view = View()
    _box.render(_view)