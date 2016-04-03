from __future__ import print_function
from mock import patch
import sys
import os

test_filename = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(test_filename)

import fake_gl

@patch('pyglet.gl', fake_gl)
def test_renderable_material():
    from pyglet_helper.objects import Renderable
    from pyglet_helper.objects import Material
    mat = Material(translucent=True)
    blo = Renderable()
    blo.material = mat
    assert(blo.material.translucent)


@patch('pyglet.gl', fake_gl)
def test_renderable_lod():
    from pyglet_helper.objects import Renderable, View
    from pyglet_helper.util import Vector
    scene = View()
    blo = Renderable()
    lod = blo.lod_adjust(scene, coverage_levels=[1, 1], pos=Vector([0, 0, 0]),
                         radius=0)
    assert(lod==2)


@patch('pyglet.gl', fake_gl)
def test_view_pixel_coverage():
    from pyglet_helper.objects import View
    from pyglet_helper.util import Vector
    scene = View()
    pix_coverage = scene.pixel_coverage(pos=Vector([10, 0, 0]), radius=0.2)
    print(pix_coverage)
    assert(pix_coverage == 800.0)