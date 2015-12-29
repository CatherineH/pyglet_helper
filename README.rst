Pyglet Helper
=============

.. image:: python/doc/examples/all_objects.gif

The goal of this project is to make [pyglet](http://pyglet.org) a little more user-friendly by adding the functionality introduced by [VPython](https://github.com/BruceSherwood/vpython-wx) for drawing 3D objects.

Installation
------------

To Install this project, either pull it from the PyPI:

::
pip install -i https://testpypi.python.org/pypi PygletHelper
::

or clone it and build from source:

::
git clone https://github.com/CatherineH/pyglet_helper
cd pyglet_helper
python setup.py install
::

Usage
-----
The following example will show how to create a window with a sphere:
.. image:: python/doc/examples/sphere.png

First, create a pyglet window to draw the shapes to:
::
from pyglet.gl import *
window = pyglet.window.Window()
::

Then, create a pyglet_helper view:
::
from pyglet_helper.objects.renderable import View
scene = View()
::

Create a gl light:
::
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
# Define a simple function to create ctypes arrays of floats:
def vec(*args):
    return (GLfloat * len(args))(*args)

glLightfv(GL_LIGHT0, GL_POSITION, vec(1, 0.5, 1, 0))
glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 0.5))
glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))
::

Geometric objects can be added to scene. For example, to define a red sphere in the center of the view:
::
from pyglet_helper.util import color
from pyglet_helper.objects.sphere import Sphere
_ball = Sphere(pos=(1, 1, 0), radius=0.5, color=color.red)
::

Finally, render the object, and run the pyglet window:
::
_ball.gl_render(scene)
pyglet.app.run()
::
