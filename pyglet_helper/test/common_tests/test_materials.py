from __future__ import print_function, division, absolute_import

from nose.tools import raises


@raises(ValueError)
def test_rawtexture_error():
    from pyglet_helper.common import RawTexture
    _raw_texture = RawTexture(data=None)


def test_shadermaterial_init():
    from pyglet_helper.common import ShaderMaterial
    _shader_material = ShaderMaterial()
    assert _shader_material.name == "no_name"


def test_convert_data():
    from pyglet_helper.common import convert_data
    from numpy import identity
    _data = identity(2)*0.45587
    _output = convert_data(_data)
    assert _output[0, 0] == 116
    assert _output[1, 0] == 0


def test_shader():
    from pyglet_helper.common import shader
    _shader = shader('my_shader', '', (5.01, 5.09))
    assert _shader.name == 'my_shader'
    _shader = shader('my_shader', '', 5.01)
    assert _shader.name == 'my_shader'

@raises(ValueError)
def test_shader_error():
    from pyglet_helper.common import shader
    _shader = shader('my_shader', '', 4.01)