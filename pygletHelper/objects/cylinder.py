# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pygletHelper.objects.axial import Axial
from pygletHelper.util.vector import Vector
from pygletHelper.util.rgba import Rgb
from pygletHelper.util.quadric import Quadric


class Cylinder(Axial):
    def __init__(self, pos=Vector(0, 0, 0), axis=Vector(1, 0, 0), radius=1.0, color=Rgb(0, 0, 0)):
        super(Cylinder, self).__init__(pos=pos, radius=radius, color=color)
        self.axis = Vector(axis)
        print self.axis

    def init_model(self, scene):
        # The number of faces corrisponding to each level of detail.
        n_faces = [8, 16, 32, 64, 96, 188]
        n_stacks = [1, 1, 3, 6, 10, 20]
        for i in range(0, 6):
            scene.cylinder_model[i].gl_compile_begin()
            self.render_cylinder_model(n_faces[i], n_stacks[i])
            scene.cylinder_model[i].gl_compile_end()

    @property
    def degenerate(self):
        return not self.visible or self.radius == 0.0 or self.axis.mag() == 0.0

    @property
    def length(self):
        return self.axis.mag()

    @length.setter
    def length(self, l):
        self.axis = self.axis.norm() * l

    def render_cylinder_model(self, n_sides, n_stacks=1):
        q = Quadric()
        q.render_cylinder(1.0, 1.0, n_sides, n_stacks)
        glTranslatef(1.0, 0.0, 0.0)
        q.render_disk(1.0, n_sides, 1, 1)  # left end of cylinder
        glTranslatef(-1.0, 0.0, 0.0)
        q.render_disk(1.0, n_sides, 1, -1)  # right end of

    def gl_pick_render(self, scene):
        if self.degenerate():
            return
        self.init_model(scene)

        lod = 2
        self.model_world_transform(scene.gcf, Vector(length, self.radius, self.radius)).gl_mult()

        scene.cylinder_model[lod].gl_render()

    def gl_render(self, scene):
        if self.radius == 0.0:
            return
        self.init_model(scene)

        # See sphere.gl_render() for a description of the level of detail calc.
        coverage = scene.pixel_coverage(self.pos, self.radius)
        lod = 0
        if coverage < 0:
            lod = 5
        elif coverage < 10:
            lod = 0
        elif coverage < 25:
            lod = 1
        elif coverage < 50:
            lod = 2
        elif coverage < 196:
            lod = 3
        elif coverage < 400:
            lod = 4
        else:
            lod = 5
        lod += scene.lod_adjust
        if lod < 0:
            lod = 0
        elif lod > 5:
            lod = 5

        glPushMatrix()
        self.model_world_transform(scene.gcf, Vector(self.length, self.radius, self.radius)).gl_mult()

        if self.translucent:
            gl_enable(GL_CULL_FACE)
            self.color.gl_set(self.opacity)

            # Render the back half.
            glCullFace(GL_FRONT)
            scene.cylinder_model[lod].gl_render()

            # Render the front half.
            glCullFace(GL_BACK)
            scene.cylinder_model[lod].gl_render()
        else:
            self.color.gl_set(self.opacity)
            scene.cylinder_model[lod].gl_render()
        glPopMatrix()

    def grow_extent(self, e):
        if self.degenerate():
            return
        a = self.axis.norm()
        e.add_circle(self.pos, a, self.radius)
        e.add_circle(self.pos + self.axis, a, self.radius)
        e.add_body()

    def get_center(self):
        return self.pos + self.axis * 0.5
