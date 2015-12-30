# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pyglet_helper.objects.axial import Axial
from pyglet_helper.util.tmatrix import Tmatrix
from pyglet_helper.util.rgba import Rgb
from pyglet_helper.util.vector import Vector
from pyglet_helper.util.quadric import Quadric
from pyglet_helper.objects.material import Material


'''
A simple monochrome sphere.
'''


class Sphere(Axial):
    def __init__(self, other=None, color=Rgb(), pos=Vector(0, 0, 0), radius=1.0, material=Material()):
        super(Sphere, self).__init__(color=color, pos=pos, radius=radius, material=material)
        # Construct a unit sphere at the origin.
        if other is not None:
            self.axial = other
        self.PRIMITIVE_TYPEINFO_IMPL = Sphere
        self.compiled = False

    @property
    def scale(self):
        """
         Exposed for the benefit of the ellipsoid object, which overrides it.
         The default is to use <radius, radius, radius> for the scale.
        """
        return Vector(self.radius, self.radius, self.radius)

    @property
    def material_matrix(self, out=Tmatrix()):
        out.translate(Vector(.5, .5, .5))
        scale = self.scale()
        out.scale(scale * (.5 / max(scale.x, max(scale.y, scale.z))))
        return out

    @property
    def degenerate(self):
        """
        Returns true if this object should not be drawn.  Conditions are:
        zero radius, or visible is false.  (overridden by the ellipsoid class).
        """
        return self.radius == 0.0

    def grow_extent(self, e):
        e.add_sphere(self.pos, self.radius)
        e.add_body()

    # True until the first sphere is rendered, then false.
    def init_model(self, scene):
        sph = Quadric()

        scene.sphere_model[0].gl_compile_begin()
        sph.render_sphere(1.0, 13, 7)
        scene.sphere_model[0].gl_compile_end()

        scene.sphere_model[1].gl_compile_begin()
        sph.render_sphere(1.0, 19, 11)
        scene.sphere_model[1].gl_compile_end()

        scene.sphere_model[2].gl_compile_begin()
        sph.render_sphere(1.0, 35, 19)
        scene.sphere_model[2].gl_compile_end()

        scene.sphere_model[3].gl_compile_begin()
        sph.render_sphere(1.0, 55, 29)
        scene.sphere_model[3].gl_compile_end()

        scene.sphere_model[4].gl_compile_begin()
        sph.render_sphere(1.0, 70, 34)
        scene.sphere_model[4].gl_compile_end()

        # Only for the very largest bodies.
        scene.sphere_model[5].gl_compile_begin()
        sph.render_sphere(1.0, 140, 69)
        scene.sphere_model[5].gl_compile_end()

    def gl_pick_render(self, geometry):
        if self.degenerate:
            return
        self.init_model(geometry)

        self.model_world_transform(geometry.gcf, self.scale()).gl_mult()

        geometry.sphere_model[0].gl_render()

    def render(self, geometry):
        # Renders a simple sphere with the #2 level of detail.
        if self.radius == 0.0:
            return
        self.init_model(geometry)

        # coverage is the radius of this sphere in pixels:
        coverage = geometry.pixel_coverage(self.pos, self.radius)
        lod = 0

        if coverage < 0:  # Behind the camera, but still visible.
            lod = 4
        elif coverage < 30:
            lod = 0
        elif coverage < 100:
            lod = 1
        elif coverage < 500:
            lod = 2
        elif coverage < 5000:
            lod = 3
        else:
            lod = 4

        lod += geometry.lod_adjust  # allow user to reduce level of detail
        if lod > 5:
            lod = 5
        elif lod < 0:
            lod = 0
        glPushMatrix()

        self.model_world_transform(geometry.gcf, self.scale).gl_mult()
        self.color.gl_set(self.opacity)

        if self.translucent:
            # Spheres are convex, so we don't need to sort
            glEnable(GL_CULL_FACE)

            # Render the back half (inside)
            glCullFace(GL_FRONT)
            geometry.sphere_model[lod].gl_render()

            # Render the front half (outside)
            glCullFace(GL_BACK)
            geometry.sphere_model[lod].gl_render()
        else:
            # Render a simple sphere.
            geometry.sphere_model[lod].gl_render()
        glPopMatrix()