from pyglet_helper.objects import Box, Sphere, View, Light
from pyglet_helper.util import color, Vector
from pyglet.window import Window
from pyglet.app import run
from pyglet.clock import schedule

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
scene.screen_objects.append(ball)
scene.screen_objects.append(floor)
dt = 0.01

@window.event
def on_draw():
    scene.setup()

_light0 = Light(position=(1, 0.5, 1, 0), specular=(.5, .5, 1, 0.5))
_light1 = Light(position=(1, 0, .5, 0), specular=(.5, .5, .5, 1))
scene.lights.append(_light0)
scene.lights.append(_light1)

run()