from __future__ import print_function


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

