from pyglet_helper import *

vsetup()


def update(dt):
    global ball
    ball.pos = ball.pos + ball.velocity * dt
    if ball.pos[1] < 1:
        ball.velocity.y_component = -ball.velocity.y_component
    else:
        ball.velocity.y_component = ball.velocity.y_component - 9.8 * dt

floor = objects.Box(length=4, height=0.5, width=4, color=util.color.BLUE)

ball = objects.Sphere(pos=util.Vector([0, 4, 0]), color=util.color.RED)
ball.velocity = util.Vector([0, -1, 0])

dt = 0.01

vrun(update)
