from pyglet.gl import *
from pyglet_helper.objects import *
from pyglet_helper.util.color import *

window = pyglet.window.Window()
scene = View()
_ball = Sphere(pos=(0, 0, 0), radius=0.5, color=red)
_light = Light()
_light.render(scene)
_ball.render(scene)

pyglet.app.run()
