from pyglet_helper.objects import Box, Sphere
from pyglet_helper.util import color, Vector
from pyglet_helper import setup, vrun

setup()


def update(dt):
    global ball
    ball.pos = ball.pos + ball.velocity * dt
    if ball.pos[1] < 1:
        ball.velocity.y_component = -ball.velocity.y_component
    else:
        ball.velocity.y_component = ball.velocity.y_component - 9.8 * dt

floor = Box(length=4, height=0.5, width=4, color=color.BLUE)

ball = Sphere(pos=Vector([0, 4, 0]), color=color.RED)
ball.velocity = Vector([0, -1, 0])

dt = 0.01

vrun(update)