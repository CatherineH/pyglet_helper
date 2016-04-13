from __future__ import print_function
from mock import patch
import pyglet_helper.test.fake_gl

def test_sphere_scale():
    from pyglet_helper.objects import Sphere
    blo = Sphere(radius=0.1)
    assert(blo.scale[0] == 0.1)
    assert(blo.scale[1] == 0.1)
    assert(blo.scale[2] == 0.1)


def test_sphere_material_matrix():
    from pyglet_helper.objects import Sphere
    blo = Sphere(radius=0.1)
    assert(blo.material_matrix[0, 0] == 0.5)
    assert(blo.material_matrix[1, 1] == 0.5)
    assert(blo.material_matrix[2, 2] == 0.5)
    assert(blo.material_matrix[3, 3] == 1.0)


def test_sphere_degenerate():
    from pyglet_helper.objects import Sphere
    blo = Sphere(radius=0.1)
    assert( not blo.degenerate)


@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.sphere.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.quadric.gl', new=pyglet_helper.test.fake_gl)
def test_sphere_render():
    from pyglet_helper.objects import Sphere
    from pyglet_helper.objects import View
    _sphere = Sphere()
    _view = View()
    _sphere.render(_view)