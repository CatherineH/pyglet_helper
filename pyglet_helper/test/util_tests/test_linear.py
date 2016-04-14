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