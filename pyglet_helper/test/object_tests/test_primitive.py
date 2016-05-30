from __future__ import print_function
from nose.tools import raises
from mock import patch
import pyglet_helper.test.fake_gl


@patch('pyglet_helper.window', new=pyglet_helper.test.fake_window)
def test_primitive_setup():
    from pyglet_helper import vsetup
    from pyglet_helper.objects import Primitive
    vsetup()
    from pyglet_helper import GLOBAL_VIEW
    _primitive = Primitive()
    assert _primitive in GLOBAL_VIEW.screen_objects


def test_primitive_center():
    from pyglet_helper.objects import Primitive
    from pyglet_helper.util import Vector
    _primitive = Primitive(pos=Vector([-1, 0, 1]))
    assert _primitive.center[0] == -1
    assert _primitive.center[1] == 0
    assert _primitive.center[2] == 1


def test_primitive_is_light():
    from pyglet_helper.objects import Primitive
    _primitive = Primitive()
    assert not _primitive.is_light


@raises(ValueError)
def test_primitive_length_error():
    from pyglet_helper.objects import Primitive
    _primitive = Primitive()
    _primitive.length = -1


@raises(ValueError)
def test_primitive_height_error():
    from pyglet_helper.objects import Primitive
    _primitive = Primitive()
    _primitive.height = -1


@raises(ValueError)
def test_primitive_width_error():
    from pyglet_helper.objects import Primitive
    _primitive = Primitive()
    _primitive.width = -1


@raises(ValueError)
def test_primitive_size_x_error():
    from pyglet_helper.objects import Primitive
    from pyglet_helper.util import Vector
    _primitive = Primitive()
    _primitive.size = Vector([-1, 0, 0])


@raises(ValueError)
def test_primitive_size_y_error():
    from pyglet_helper.objects import Primitive
    from pyglet_helper.util import Vector
    _primitive = Primitive()
    _primitive.size = Vector([0, -1, 0])


@raises(ValueError)
def test_primitive_size_z_error():
    from pyglet_helper.objects import Primitive
    from pyglet_helper.util import Vector
    _primitive = Primitive()
    _primitive.size = Vector([0, 0, -1])