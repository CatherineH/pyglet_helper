# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pygletHelper.objects.axial import Axial
from pygletHelper.util.rgba import Rgb
from pygletHelper.util.vector import Vector
from pygletHelper.util.quadric import Quadric
from pygletHelper.util.gl_enable import gl_enable


class Cone(Axial):
    def __init__(self, radius=1.0, color=rgb(), pos=vector(0, 0, 0), axis=vector(1, 0, 0)):
        super(cone, self).__init__(radius=radius, color=color, pos=vector(pos))
        self.axis = vector(axis)

    def init_model(self, scene):
        # The number of faces corrisponding to each level of detail.
        n_sides = [8, 16, 32, 46, 68, 90]
        n_stacks = [1, 2, 4, 7, 10, 14]
        for i in range(0, 6):
            scene.cone_model[i].gl_compile_begin()
            self.render_cone_model(n_sides[i], n_stacks[i])
            scene.cone_model[i].gl_compile_end()

    @property
    def length(self):
        return self.axis.mag()

    @length.setter
    def length(self, l):
        self.axis = self.axis.norm() * l

    def render_cone_model(self, n_sides, n_stacks):
        q = quadric()
        q.render_cylinder(1.0, 1.0, n_sides, n_stacks, top_radius=0.0)
        q.render_disk(1.0, n_sides, n_stacks * 2, -1)

    def gl_pick_render(self, scene):
        if self.degenerate():
            print "cone is degenerate"
            return
        self.init_model(scene)

        lod = 2
        length = self.axis.mag()
        self.model_world_transform(scene.gcf, vector(length, self.radius, self.radius)).gl_mult()

        scene.cone_model[lod].gl_render()

    def gl_render(self, scene):
        if self.radius == 0:
            return

        self.init_model(scene)

        # See sphere.gl_render() for a description of the level of detail calc.
        coverage = scene.pixel_coverage(self.pos, self.radius)
        lod = 0
        if coverage < 0:
            lod = 5
        elif coverage < 10:
            lod = 0
        elif coverage < 30:
            lod = 1
        elif coverage < 90:
            lod = 2
        elif coverage < 250:
            lod = 3
        elif coverage < 450:
            lod = 4
        else:
            lod = 5
        lod += scene.lod_adjust
        if lod < 0:
            lod = 0
        elif lod > 5:
            lod = 5

        length = self.axis.mag()
        glPushMatrix()
        self.model_world_transform(scene.gcf, vector(length, self.radius, self.radius)).gl_mult()

        self.color.gl_set(self.opacity)
        if self.translucent:
            gl_enable(GL_CULL_FACE)

            # Render the back half.
            glCullFace(GL_FRONT)
            scene.cone_model[lod].gl_render()

            # Render the front half.
            glCullFace(GL_BACK)
            scene.cone_model[lod].gl_render()
        else:
            scene.cone_model[lod].gl_render()
        glPopMatrix()

    def grow_extent(self, e):
        if self.degenerate:
            return
        e.add_circle(self.pos, self.axis.norm(), self.radius)
        e.add_point(self.pos + self.axis)
        e.add_body()

    def get_center(self):
        return self.pos + self.axis / 2.0

    @property
    def degenerate(self):
        return self.radius == 0.0 or self.axis.mag() == 0.0