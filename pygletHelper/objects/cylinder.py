# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pygletHelper.objects.axial import axial
from pygletHelper.util.vector import vector
from pygletHelper.util.rgba import rgb
from pygletHelper.util.quadric import quadric
from pygletHelper.util.tmatrix import gl_matrix_stackguard
from pygletHelper.util.gl_enable import gl_enable


class cylinder(axial):
    def __init__(self, pos=vector(0, 0, 0), axis=(1, 0, 0), radius=1.0, color=rgb(0, 0, 0)):
        super(cylinder, self).__init__(pos=pos, radius=radius, color=color)
        self.axis = vector(axis)

    def init_model(self, scene):
        #if not scene.cylinder_model[0].compiled():
        #    clear_gl_error()
            # The number of faces corrisponding to each level of detail.
        n_faces = [8, 16, 32, 64, 96, 188]
        n_stacks = [1, 1, 3, 6, 10, 20]
        for i in range(0, 6):

            scene.cylinder_model[i].gl_compile_begin()
            #glRotatef(90, 0, 90, 0)
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
        q = quadric()
        q.render_cylinder(1.0, 1.0, n_sides, n_stacks)
        glTranslatef(1.0, 0.0, 0.0)
        q.render_disk(1.0, n_sides, 1, 1)  # left end of cylinder
        glTranslatef(-1.0, 0.0, 0.0)
        #
        q.render_disk(1.0, n_sides, 1, -1)  # right end of

    def gl_pick_render(self, scene):
        if self.degenerate():
            return
        self.init_model(scene)

        lod = 2

        guard = gl_matrix_stackguard()
        length = self.axis.mag()

        self.model_world_transform(scene.gcf, vector(length, self.radius, self.radius)).gl_mult()

        scene.cylinder_model[lod].gl_render()

    def gl_render(self, scene):
        if self.radius ==0.0:
            return
        self.init_model(scene)

        # See sphere::gl_render() for a description of the level of detail calc.
        coverage = scene.pixel_coverage(self.pos, self.radius)
        lod = 0
        if (coverage < 0):
            lod = 5
        elif (coverage < 10):
            lod = 0
        elif (coverage < 25):
            lod = 1
        elif (coverage < 50):
            lod = 2
        elif (coverage < 196):
            lod = 3
        elif (coverage < 400):
            lod = 4
        else:
            lod = 5
        lod += scene.lod_adjust
        if (lod < 0):
            lod = 0
        elif (lod > 5):
            lod = 5

        length = self.axis.mag()
        glPushMatrix()
        self.model_world_transform(scene.gcf, vector(length, self.radius, self.radius)).gl_mult()

        if self.translucent:
            cull_face = gl_enable(GL_CULL_FACE)
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
        e.add_circle(self.pos, self.a, self.radius)
        e.add_circle(self.pos + self.axis, self.a, self.radius)
        e.add_body()

    def get_center(self):
        return self.pos + self.axis * 0.5
