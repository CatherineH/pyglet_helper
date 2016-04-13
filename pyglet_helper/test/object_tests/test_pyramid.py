from __future__ import print_function
from mock import patch
import pyglet_helper.test.fake_gl

def test_pyramid_center():
    from pyglet_helper.objects import Pyramid
    from pyglet_helper.util import Vector
    blo = Pyramid(pos=Vector([10, 0, 0]), axis=Vector([-1, 0, 0]),
                  height=30)
    assert(blo.center[0] == 0)
    assert(blo.center[1] == 0)
    assert(blo.center[2] == 0)


def test_pyramid_material_matrix():
    from pyglet_helper.objects import Pyramid
    from pyglet_helper.util import Vector
    blo = Pyramid(pos=Vector([10, 0, 0]), axis=Vector([-1, 0, 0]),
                  height=40)
    assert(blo.material_matrix[0, 0] == 0.025)
    assert(blo.material_matrix[1, 1] == 0.025)
    assert(blo.material_matrix[2, 2] == 0.025)
    assert(blo.material_matrix[3, 3] == 1.0)

@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.pyramid.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_pyramid_render():
    from pyglet_helper.objects import Pyramid
    from pyglet_helper.objects import View
    _pyramid = Pyramid()
    _view = View()
    _pyramid.render(_view)

