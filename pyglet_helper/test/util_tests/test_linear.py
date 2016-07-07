from __future__ import print_function, division, absolute_import

from nose.tools import raises
from mock import patch
import pyglet_helper.test.fake_gl

def test_rotation_with_origin():
    from pyglet_helper.util import rotation, Vector
    bloop = rotation(0.1, Vector([0, 0, 1]), Vector([0, 1, 0]))
    assert bloop[0, 0] == 0.99500416527802582


def test_rotation_without_origin():
    from pyglet_helper.util import rotation, Vector
    bloop = rotation(0.1, Vector([0, 0, 1]))
    assert bloop[1, 0] == -0.099833416646828155


def test_vector_mult():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec2 = Vector([0, 1.0, 0.5])
    vec3 = vec1*vec2
    assert vec3[0] == 0
    assert vec3[1] == 0
    assert vec3[2] == 1.0


def test_vector_eq():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec2 = Vector([0, 1.0, 0.5])
    assert not vec1 == vec2


def test_vector_neq():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec2 = Vector([0, 1.0, 0.5])
    assert vec1 != vec2


def test_vector_nonzero():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec2 = Vector([0, 0, 0])
    assert vec1.nonzero()
    assert not vec2.nonzero()


def test_vector_invert():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec2 = ~vec1
    assert vec2[0] == -1
    assert vec2[1] == 0


def test_vector_set_mag():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec1.set_mag(0.1)
    print(vec1)
    assert vec1[0] == 0.044721359549995794
    assert vec1[1] == 0


def test_vector_str():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0.0, 2.0])
    assert str(vec1).find("Vector(1.0,0.0,2.0)") == 0


def test_vector_comp():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec2 = Vector([0, 1.0, 0])
    vec3 = vec1.comp(vec2)
    assert vec3 == 0


def test_vector_proj():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec2 = Vector([0, 1.0, 0])
    result = vec1.proj(vec2)
    assert result == Vector([0.0, 0.0, 0.0])

def test_vector_diff_angle():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 1.0, 1.0])
    vec2 = Vector([1.0, 1.0, 1.0])
    result = vec1.diff_angle(vec2)
    print(result)
    assert result == 0.0
    vec1 = Vector([1.0, 1.0, 1.0])
    vec2 = Vector([-1.0, -1.0, -1.0])
    result = vec1.diff_angle(vec2)
    print(result)
    assert result == 3.141592653589793


def test_vector_scale():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec2 = Vector([0, 1.0, 1.0])
    vec3 = vec1.scale(vec2)
    print(vec3)
    assert vec3[0] == 0
    assert vec3[2] == 2.0

def test_vector_rotate():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec2 = Vector([0, 1.0, 1.0])
    vec3 = vec1.rotate(angle=1.0, axis=vec2)
    assert abs(vec3[0] - 2.73032198493) < 0.01
    assert vec3[3] == 1.0
    vec3 = vec1.rotate(angle=1.0)
    assert vec3[2] == 3.0
    assert vec3[3] == 1.0

@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_vector_render():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec1.gl_normal()
    vec1.gl_render()

def test_vector_clear():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec1.clear()
    assert vec1[0] == 0.0
    assert vec1[1] == 0.0
    assert vec1[2] == 0.0


@raises(IndexError)
def test_vector_bad_index():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec1[4]


def test_vector_set_index():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec1[0] = -1.0
    vec1[1] = -2.0
    vec1[2] = -3.0
    assert vec1.x_component == -1.0
    assert vec1.y_component == -2.0
    assert vec1.z_component == -3.0


@raises(IndexError)
def test_vector_set_bad_index():
    from pyglet_helper.util import Vector
    vec1 = Vector([1.0, 0, 2.0])
    vec1[4] = 0.0


def test_vector_fabs():
    from pyglet_helper.util import Vector
    vec1 = Vector([-1.0, 0, -2.0])
    vec1 = vec1.fabs()
    assert vec1.x_component == 1.0
    assert vec1.z_component == 2.0


def test_vector_sum():
    from pyglet_helper.util import Vector
    vec1 = Vector([-1.0, 0, -2.0])
    assert vec1.sum() == -3.0


def test_vertex_init():
    from pyglet_helper.util import Vector, Vertex
    vec1 = Vector([-1.0, 0, -2.0])
    ver1 = Vertex(vec1)
    assert ver1[0] == -1.0
    assert ver1[1] == 0
    assert ver1[2] == -2.0
    ver2 = Vertex([0.0, 1.0, 2.0, 3.0])
    ver1 = Vertex(ver2)
    assert ver1[0] == 0.0
    assert ver1[1] == 1.0
    assert ver1[2] == 2.0


def test_vertex_project():
    from pyglet_helper.util import Vertex
    ver1 = Vertex([-1.0, 0, -2.0, .50])
    ver2 = ver1.project()
    assert ver2[0] == -2.0
    assert ver2[1] == 0.0
    assert ver2[2] == -4.0


@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_vertex_render():
    from pyglet_helper.util import Vertex
    vec1 = Vertex([1.0, 0, 2.0])
    vec1.gl_render()


@raises(IndexError)
def test_vertex_get_error():
    from pyglet_helper.util import Vertex
    vec1 = Vertex()
    vec1[4]


@raises(IndexError)
def test_vertex_set_error():
    from pyglet_helper.util import Vertex
    vec1 = Vertex()
    vec1[4] = 2


def test_vertex_set_test():
    from pyglet_helper.util import Vertex
    vec1 = Vertex()
    vec1[0] = 1.0
    vec1[1] = 1.0
    vec1[2] = 1.0
    vec1[3] = 1.0
    assert vec1[0] == 1.0
    assert vec1[1] == 1.0
    assert vec1[2] == 1.0
    assert vec1[3] == 1.0


def test_vertex_str():
    from pyglet_helper.util import Vertex
    vec1 = Vertex([0.0, 1.0, -1.0, 0.5])
    _str = str(vec1)
    assert _str == "Vertex(0.0,1.0,-1.0,0.5)"


def test_tmatrix_init():
    from pyglet_helper.util import Tmatrix
    _tmatrix1 = Tmatrix()
    _tmatrix1.matrix[2, 3] = 1.0
    _tmatrix2 = Tmatrix(_tmatrix1)
    assert _tmatrix2.matrix[2, 3] == 1.0


def test_tmatrix_mult():
    from pyglet_helper.util import Tmatrix, Vertex
    _tmatrix1 = Tmatrix()
    _tmatrix1.matrix[0, 1] = 1.0
    _tmatrix1.matrix[1, 0] = 1.0
    _tmatrix1.matrix[0, 0] = 0.0
    _tmatrix1.matrix[1, 1] = 0.0
    _result = _tmatrix1*_tmatrix1
    assert _result.matrix[0, 0] == 1.0
    assert _result.matrix[1, 1] == 1.0
    assert _result.matrix[0, 1] == 0.0
    assert _result.matrix[1, 0] == 0.0
    _result = 2.0*_tmatrix1
    assert _result.matrix[0, 0] == 0.0
    assert _result.matrix[1, 1] == 0.0
    assert _result.matrix[0, 1] == 2.0
    assert _result.matrix[1, 0] == 2.0
    _result = _tmatrix1*2.0
    assert _result.matrix[0, 0] == 0.0
    assert _result.matrix[1, 1] == 0.0
    assert _result.matrix[0, 1] == 2.0
    assert _result.matrix[1, 0] == 2.0
    _vert = Vertex([0, 1.0, 0, 1])
    _result = _tmatrix1*_vert
    assert _result[0] == 1.0
    assert _result[1] == 0.0


def test_tmatrix_inverse():
    from pyglet_helper.util import Tmatrix
    _tmatrix1 = Tmatrix()
    _tmatrix1.matrix[0, 1] = 1.0
    _tmatrix1.matrix[1, 0] = 0.0
    _tmatrix1.matrix[0, 0] = 0.50
    _tmatrix1.matrix[1, 1] = -0.50
    _tmatrix1.inverse()
    assert _tmatrix1.matrix[0, 1] == 4.0
    assert _tmatrix1.matrix[0, 0] == 2.0
    assert _tmatrix1.matrix[1, 0] == 0.0
    assert _tmatrix1.matrix[1, 1] == -2.0


def test_tmatrix_project():
    from pyglet_helper.util import Tmatrix, Vertex
    _tmatrix1 = Tmatrix()
    _tmatrix1.matrix[0, 0] = 0.0
    _tmatrix1.matrix[1, 1] = 0.0
    _tmatrix1.matrix[1, 0] = 1.0
    _tmatrix1.matrix[0, 1] = 1.0
    _vert = Vertex([0, 1.0, 0, 0.5])
    _outvert = _tmatrix1.project(_vert)
    assert _outvert[0] == 1.0
    assert _outvert[1] == 0.0


def test_tmatrix_scale():
    from pyglet_helper.util import Tmatrix, Vertex
    _tmatrix1 = Tmatrix()
    _tmatrix1.matrix[0, 0] = 0.0
    _tmatrix1.matrix[1, 1] = 0.0
    _tmatrix1.matrix[1, 0] = 1.0
    _tmatrix1.matrix[0, 1] = 1.0
    _vert = Vertex([0, 1.0, 0, 0.5])
    _tmatrix1.scale(_vert)
    assert _tmatrix1.matrix[0, 0] == 0.0
    assert _tmatrix1.matrix[1, 1] == 0.0
    assert _tmatrix1.matrix[0, 1] == 0.0
    assert _tmatrix1.matrix[3, 3] == 0.5


def test_tmatrix_times_inv():
    from pyglet_helper.util import Tmatrix, Vertex, Vector
    # test with a vector
    _tmatrix1 = Tmatrix()
    _vect = Vector([0.0, 1.0, 0.0])
    _tmatrix1.matrix[0, 0] = 0.0
    _tmatrix1.matrix[1, 1] = 0.0
    _tmatrix1.matrix[1, 0] = 1.0
    _tmatrix1.matrix[0, 1] = 1.0
    _outvect = _tmatrix1.times_inv(_vect)
    assert _outvect[0] == 1.0
    assert _outvect[1] == 0.0
    # test with a vertex
    _vert = Vertex([0, 1.0, 0, 0.5])
    _outvect = _tmatrix1.times_inv(_vert)
    assert _outvect[0] == 1.0
    assert _outvect[1] == 0.0


def test_tmatrix_times_v():
    from pyglet_helper.util import Tmatrix, Vertex, Vector
    # test with a vector
    _tmatrix1 = Tmatrix()
    _vect = Vector([0.0, 1.0, 0.0])
    _tmatrix1.matrix[0, 0] = 0.0
    _tmatrix1.matrix[1, 1] = 0.0
    _tmatrix1.matrix[1, 0] = 1.0
    _tmatrix1.matrix[0, 1] = 1.0
    _outvect = _tmatrix1.times_v(_vect)
    assert _outvect[0] == 1.0
    assert _outvect[1] == 0.0
    # test with a vertex
    _vert = Vertex([0, 1.0, 0, 0.5])
    _outvect = _tmatrix1.times_v(_vert)
    assert _outvect[0] == 1.0
    assert _outvect[1] == 0.0


def test_tmatrix_origin():
    from pyglet_helper.util import Tmatrix
    # test with a vector
    _tmatrix1 = Tmatrix()
    _tmatrix1.matrix[0, 0] = 0.50
    _tmatrix1.matrix[1, 1] = 0.0
    _tmatrix1.matrix[1, 0] = 2.0
    _tmatrix1.matrix[0, 1] = 1.0
    _tmatrix1.matrix[3, 0] = 1.0
    _outvect = _tmatrix1.origin()
    assert _outvect[0] == 1.0
    assert _outvect[1] == 0.0
    assert _outvect[2] == 0.0


def test_tmatrix_str():
    from pyglet_helper.util import Tmatrix
    # test with a vector
    _tmatrix1 = Tmatrix()
    _tmatrix1.matrix[0, 0] = 0.50
    _tmatrix1.matrix[1, 1] = 0.0
    _tmatrix1.matrix[1, 0] = 2.0
    _tmatrix1.matrix[0, 1] = 1.0
    _tmatrix1.matrix[3, 0] = 1.0
    _out_str = str(_tmatrix1)
    assert _out_str == "| 0.5 2.0 0.0 1.0|\n| 1.0 0.0 0.0 0.0|\n| 0.0 0.0 " \
                       "1.0 0.0|\n| 0.0 0.0 0.0 1.0|\n"


@patch('pyglet_helper.util.linear.gl', new=pyglet_helper.test.fake_gl)
def test_tmatrix_gl_calls():
    from pyglet_helper.util import Tmatrix
    from numpy import zeros, identity
    # test with a vector
    _tmatrix1 = Tmatrix()
    _tmatrix1.gl_load()
    _tmatrix1.gl_mult()
    _out_mat = _tmatrix1.gl_modelview_get()
    assert (_tmatrix1.matrix == _out_mat).all()
    _out_mat = _tmatrix1.gl_modelview_get()
    assert (_tmatrix1.matrix == _out_mat).all()
    _out_mat = _tmatrix1.gl_texture_get()
    assert (zeros([4, 4]) == _out_mat).all()
    _out_mat = _tmatrix1.gl_color_get()
    assert (zeros(4) == _out_mat).all()

