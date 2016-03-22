def test_rotation_with_origin():
    from pyglet_helper.util import rotation, Vector
    bloop = rotation(0.1, Vector([0, 0, 1]), Vector([0, 1, 0]))
    assert bloop[0, 0] == 0.99500416527802582


def test_rotation_without_origin():
    from pyglet_helper.util import rotation, Vector
    bloop = rotation(0.1, Vector([0, 0, 1]))
    assert bloop[1, 0] == -0.099833416646828155