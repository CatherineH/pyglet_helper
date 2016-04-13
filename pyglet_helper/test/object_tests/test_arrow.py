from __future__ import print_function
from mock import patch
import pyglet_helper.test.fake_gl

def test_arrow_degenerate():
    from pyglet_helper.objects import Arrow
    from pyglet_helper.util import Vector
    blo = Arrow(axis=Vector([0, 0, 0]))
    assert(blo.degenerate)


def test_arrow_head_width():
    from pyglet_helper.objects import Arrow
    from pyglet_helper.util import Vector
    blo = Arrow(head_width=0.75)
    assert(blo.head_width == 0.75)
    blo = Arrow(shaft_width=0.75)
    assert(blo.head_width == 1.50)
    blo = Arrow(axis=Vector([10.0, 0, 0]))
    assert(blo.head_width == 2.0)

def test_arrow_head_length():
    from pyglet_helper.objects import Arrow
    from pyglet_helper.util import Vector
    blo = Arrow(head_length=0.75)
    assert(blo.head_length == 0.75)
    blo = Arrow(shaft_width=0.75)
    assert(blo.head_length == 2.25)
    blo = Arrow(axis=Vector([10.0, 0, 0]))
    assert(blo.head_length == 3.0)


def test_arrow_shaft_width():
    from pyglet_helper.objects import Arrow
    from pyglet_helper.util import Vector
    blo = Arrow(shaft_width=0.75)
    assert(blo.shaft_width == 0.75)
    blo = Arrow(axis=Vector([10.0, 0, 0]))
    assert(blo.shaft_width == 1.0)


def test_arrow_fixed_width():
    from pyglet_helper.objects import Arrow
    blo = Arrow()
    blo.fixed_width = True
    assert(blo.fixed_width)


def test_arrow_center():
    from pyglet_helper.objects import Arrow
    from pyglet_helper.util import Vector
    blo = Arrow(pos=Vector([-10, -10, -10]), axis=Vector([10, 10, 10]))
    assert(blo.center[0] == 0)
    assert(blo.center[1] == 0)
    assert(blo.center[2] == 0)


def test_arrow_effective_geometry():
    from pyglet_helper.objects import Arrow
    blo = Arrow(head_width=1.0, shaft_width=1.0, head_length=1.0)
    assert(blo.effective_geometry(0.2)[0] == 0.2)
    assert(blo.effective_geometry(0.2)[1] == 0.2)
    assert(blo.effective_geometry(0.2)[2] == 0.2)
    blo = Arrow(head_width=0.0, shaft_width=0.0, head_length=0.0)
    assert(blo.effective_geometry(1.0)[0] == 0.2)
    assert(blo.effective_geometry(1.0)[1] == 0.1)
    assert(blo.effective_geometry(1.0)[2] == 1.0)
    blo = Arrow()
    blo.fixed_width = True
    assert(blo.effective_geometry(1.0)[0] == 0.2)
    assert(blo.effective_geometry(1.0)[1] == 0.1)
    assert(blo.effective_geometry(1.0)[2] == 1.0)
    blo = Arrow(shaft_width=0.001)
    blo.fixed_width = False
    assert(blo.effective_geometry(1.0)[0] == 0.04)
    assert(blo.effective_geometry(1.0)[1] == 0.02)
    assert(blo.effective_geometry(1.0)[2] == 1.0)
    blo = Arrow(head_length=1000.0)
    blo.fixed_width = False
    assert(blo.effective_geometry(1.0)[0] == 0.0001)
    assert(blo.effective_geometry(1.0)[1] == 5e-5)
    assert(blo.effective_geometry(1.0)[2] == 1.0)


@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.arrow.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.box.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.pyramid.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.rgba.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.box.gl', new=pyglet_helper.test.fake_gl)
def test_arrow_render():
    from pyglet_helper.objects import Arrow
    from pyglet_helper.objects import View
    _arrow = Arrow()
    _view = View()
    _arrow.render(_view)
