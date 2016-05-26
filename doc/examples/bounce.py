from pyglet_helper.objects import Box, Sphere, View, Light, Window
from pyglet_helper.util import color, Vector
import os
from pyglet.window import Window
from pyglet.app import run
from pyglet.clock import schedule
from pyglet.image import get_buffer_manager

window = Window()
scene = View()


def update(dt):
    global ball
    ball.pos = ball.pos + ball.velocity * dt
    if ball.pos[1] < 1:
        ball.velocity.y_component = -ball.velocity.y_component
    else:
        ball.velocity.y_component = ball.velocity.y_component - 9.8 * dt

schedule(update)

floor = Box(length=4, height=0.5, width=4, color=color.BLUE)

ball = Sphere(pos=Vector([0, 4, 0]), color=color.RED)
ball.velocity = Vector([0, -1, 0])

dt = 0.01
screennum = 0

@window.event
def on_draw():
    global screennum
    global ball
    global floor
    scene.setup()
    ball.render(scene)
    floor.render(scene)
    if screennum < 99:
        path = os.path.dirname(__file__)
        filename = os.path.join(path, 'screenshot%02d.png' % (screennum, ))
        get_buffer_manager().get_color_buffer().save(filename)
        screennum += 1

_light0 = Light(position=(1, 0.5, 1, 0), specular=(.5, .5, 1, 0.5))
_light0.render(scene)
_light1 = Light(position=(1, 0, .5, 0), specular=(.5, .5, .5, 1))
_light1.render(scene)

run()