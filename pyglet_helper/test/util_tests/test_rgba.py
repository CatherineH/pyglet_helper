from __future__ import print_function
from nose.tools import raises


@raises(ValueError)
def test_rgba_length_error():
    from pyglet_helper.util import Rgba
    Rgba(color=[1, 1, 1, 1, 1])


def test_rgba_init():
    from pyglet_helper.util import Rgba
    blo = Rgba(color=[0.5, 0.5, 0.5, 0.5])
    assert blo.red == 0.5
    assert blo.green == 0.5
    assert blo.blue == 0.5
    assert blo.opacity == 0.5
    blo = Rgba(red=0.5, green=0.5, blue=0.5, opacity=0.5)
    assert blo[0] == 0.5
    assert blo[1] == 0.5
    assert blo[2] == 0.5
    assert blo[3] == 0.5


@raises(ValueError)
def test_rgba_get_error():
    from pyglet_helper.util import Rgba
    blo = Rgba(color=[0.5, 0.5, 0.5, 0.5])
    print(blo[4])


@raises(ValueError)
def test_rgba_set_error():
    from pyglet_helper.util import Rgba
    blo = Rgba(color=[0.5, 0.5, 0.5, 0.5])
    blo[4] = 1.0


def test_rgba_str():
    from pyglet_helper.util import Rgba
    blo = Rgba(color=[0.5, 0.5, 0.5, 0.5])
    assert str(blo) == 'color: r0.5 g0.5 b0.5 o0.5'


def test_rgba_desaturate():
    from pyglet_helper.util import Rgba
    blo = Rgba(color=[1, 0.5, 0.25, 1.0])
    desat = blo.desaturate()
    assert(desat.red == 1)
    assert(desat.blue == 0.625)
    assert(desat.green == 0.75)
    assert(desat.opacity == 1.0)
    blo = Rgba(color=[0.25, 0.5, 1, 1.0])
    desat = blo.desaturate()
    assert(desat.red == 0.625)
    assert(desat.blue == 1)
    assert(desat.green == 0.75)
    assert(desat.opacity == 1.0)
    blo = Rgba(color=[0.5, 0.5, 0.5, 1.0])
    desat = blo.desaturate()
    assert(desat.red == 0.5)
    assert(desat.blue == 0.5)
    assert(desat.green == 0.5)
    assert(desat.opacity == 1.0)


def test_rgba_grayscale():
    from pyglet_helper.util import Rgba
    blo = Rgba(color=[1, 0.5, 0.25, 1.0])
    grayscale = blo.grayscale()
    assert(abs(grayscale.red - 0.697512082354)<1e-5)
    assert(grayscale.blue == grayscale.red)
    assert(grayscale.green == grayscale.red)
    assert(grayscale.opacity == 1.0)


@raises(ValueError)
def test_rgb_length_error():
    from pyglet_helper.util import Rgb
    Rgb(color=[1, 1, 1, 1, 1])


def test_rgb_str():
    from pyglet_helper.util import Rgb
    blo = Rgb(color=[0.5, 0.5, 0.5])
    assert str(blo) == 'color: r0.5 g0.5 b0.5'


@raises(ValueError)
def test_rgb_get_error():
    from pyglet_helper.util import Rgb
    blo = Rgb()
    print(blo[3])


@raises(ValueError)
def test_rgb_set_error():
    from pyglet_helper.util import Rgb
    blo = Rgb()
    blo[3] = 1.0


def test_rgb_rgb():
    from pyglet_helper.util import Rgb
    blo = Rgb(color=[0.1, 0.2, 0.3])
    tup = blo.rgb
    assert(tup[0]==0.1)
    assert(tup[1]==0.2)
    assert(tup[2]==0.3)
