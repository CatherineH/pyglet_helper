def test_thickline():
    from pyglet_helper.objects import Curve, View

    from pyglet_helper.util import Vector
    bloop = Curve()
    _scene = View()
    bloop.pos = [Vector([0, 0, 0]), Vector([0, 0, 10]), Vector([0, 0, 20])]
    bloop.radius = 1.0
    bloop.thickline(_scene)
    print(bloop.count)
    assert bloop.projected[0] == Vector([0, 0, 0])
    assert bloop.projected[4] == Vector([0, 2, 10])
    assert bloop.curve_slice == [2, 1]