from pyglet.gl import *
from pyglet_helper.objects.sphere import Sphere
from pyglet_helper.util import color
from pyglet_helper.objects.renderable import View

window = pyglet.window.Window()
scene = View()
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
# Define a simple function to create ctypes arrays of floats:
def vec(*args):
    return (GLfloat * len(args))(*args)

glLightfv(GL_LIGHT0, GL_POSITION, vec(1, 0.5, 1, 0))
glLightfv(GL_LIGHT0, GL_SPECULAR, vec(.5, .5, 1, 0.5))
glLightfv(GL_LIGHT0, GL_DIFFUSE, vec(1, 1, 1, 1))

_ball = Sphere(pos=(0, 0, 0), radius=0.5, color=color.red)

_ball.gl_render(scene)
pyglet.app.run()
