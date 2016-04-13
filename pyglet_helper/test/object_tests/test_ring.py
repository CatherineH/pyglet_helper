from __future__ import print_function
from mock import patch
import pyglet_helper.test.fake_gl

def test_ring_thickness():
    from pyglet_helper.objects import Ring
    blo = Ring(thickness=100000.0)
    assert(blo.thickness == 100000.0)


def test_ring_material_matrix():
    from pyglet_helper.objects import Ring
    blo = Ring(thickness=100000.0, radius=0.01)
    assert(abs(blo.material_matrix[0, 0] - 4.9999995e-08) < 1e-7)
    assert(abs(blo.material_matrix[1, 1] - 4.9999995e-08) < 1e-7)
    assert(abs(blo.material_matrix[2, 2] - 4.9999995e-08) < 1e-7)
    assert(blo.material_matrix[3, 3] == 1.0)
    assert(blo.material_matrix[3, 0] == 0.5)
    assert(blo.material_matrix[3, 1] == 0.5)
    assert(blo.material_matrix[3, 2] == 0.5)


def test_ring_degenerate():
    from pyglet_helper.objects import Ring
    blo = Ring(radius=100000.0)
    assert(not blo.degenerate)


@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.ring.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
def test_ring_render():
    from pyglet_helper.objects import Ring
    from pyglet_helper.objects import View
    _ring = Ring()
    _view = View()
    _ring.render(_view)

def test_clamp():
    from pyglet_helper.objects.ring import clamp
    assert(clamp(0.5, 0.75, 1.0) == 0.75)
    assert(clamp(0.5, 1.75, 1.0) == 1.0)
    assert(clamp(0.5, 0.25, 1.0) == 0.5)