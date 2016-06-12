from pyglet_helper.objects import Box, Sphere
from pyglet_helper.util import color, Vector, Rgb
from pyglet_helper import vsetup, vrun

vsetup()

def update(dt):
    global ball
    global t
    t = t + dt
    ball.pos = ball.pos + (ball.p / ball.mass) * dt
    if not (side > ball.pos.x_component > -side):
      ball.p.x_component = -ball.p.x_component
    if not (side > ball.pos.y_component > -side):
      ball.p.y_component = -ball.p.y_component
    if not (side > ball.pos.z_component > -side):
      ball.p.z_component = -ball.p.z_component

print("""
Right button drag or Ctrl-drag to rotate "camera" to view scene.
Middle button or Alt-drag to drag up or down to zoom in or out.
  On a two-button mouse, middle is left + right.
""")

side = 4.0
thk = 0.3
s2 = 2*side - thk
s3 = 2*side + thk
'''
wallR = Box(pos=Vector([side, 0, 0]), size=Vector([thk, s2, s3]),  color=color.RED)
wallL = Box(pos=Vector([-side, 0, 0]), size=Vector([thk, s2, s3]),  color=color.RED)
wallB = Box(pos=Vector([0, -side, 0]), size=Vector([s3, thk, s3]),  color=color.BLUE)
wallT = Box(pos=Vector([0,  side, 0]), size=Vector([s3, thk, s3]),  color=color.BLUE)
wallBK = Box(pos=Vector([0, 0, -side]), size=Vector([s2, s2, thk]), color=Rgb(0.7, 0.7, 0.7))
'''
ball = Sphere(color=color.GREEN, radius=0.4, make_trail=True, retain=200,
              trail_type="curve")
ball.trail_object.radius = 0.5
ball.mass = 1.0
ball.p = Vector([-0.15, -0.23, +0.27])

side = side - thk*0.5 - ball.radius

dt = 0.1
t = 0.0



vrun(update, render_images=True, max_frames=101, interval=1)
