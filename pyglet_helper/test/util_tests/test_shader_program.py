from __future__ import print_function
from mock import patch
import pyglet_helper.test.fake_gl


def test_shader_program_source():
    from pyglet_helper.util.shader_program import ShaderProgram
    bloop = ShaderProgram(source="hello world")
    assert bloop.source == "hello world"


@patch('pyglet_helper.util.shader_program.gl', new=pyglet_helper.test.fake_gl)
def test_shader_program_uniform_location():
    from pyglet_helper.util.shader_program import ShaderProgram
    bloop = ShaderProgram()
    assert bloop.uniform_location('') == -1
    bloop.program = 1
    assert bloop.uniform_location('') == 0


@patch('pyglet_helper.util.shader_program.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.objects.renderable.gl', new=pyglet_helper.test.fake_gl)
@patch('pyglet_helper.util.display_list.gl', new=pyglet_helper.test.fake_gl)
def test_shader_program_realize():
    from pyglet_helper.util.shader_program import ShaderProgram
    from pyglet_helper.objects.renderable import View
    shader = ShaderProgram()
    view = View()
    shader.realize(view)


def test_shader_program_get():
    from pyglet_helper.util.shader_program import ShaderProgram
    blo = ShaderProgram()
    blo.program = 1
    assert blo.get() == 1

@patch('pyglet_helper.util.shader_program.gl', new=pyglet_helper.test.fake_gl)
def test_shader_program_gl_free():
    from pyglet_helper.util.shader_program import ShaderProgram
    blo = ShaderProgram()
    blo.gl_free()

