from pyglet_helper import *
from pyglet import *

window = window.Window()
scene = objects.View(view_height=window.height, view_width=window.width)


def update(dt):
    global ball
    ball.pos = ball.pos + ball.velocity * dt
    if ball.pos[1] < 1:
        ball.velocity.y_component = -ball.velocity.y_component
    else:
        ball.velocity.y_component = ball.velocity.y_component - 9.8 * dt

schedule(update)

floor = objects.Box(length=4, height=0.5, width=4, color=util.color.BLUE)

ball = objects.Sphere(pos=util.Vector([0, 4, 0]), color=util.color.RED)
ball.velocity = util.Vector([0, -1, 0])

scene.screen_objects.append(ball)
scene.screen_objects.append(floor)
dt = 0.01

@window.event
def on_draw():
    scene.setup()

_light0 = objects.Light(position=(1, 0.5, 1, 0), specular=(.5, .5, 1, 0.5))
_light1 = objects.Light(position=(1, 0, .5, 0), specular=(.5, .5, .5, 1))
scene.lights.append(_light0)
scene.lights.append(_light1)

run()