# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pygletHelper.objects.axial import axial
from pygletHelper.util.tmatrix import tmatrix, gl_matrix_stackguard
from pygletHelper.util.rgba import rgb
from pygletHelper.util.vector import vector
from pygletHelper.util.quadric import quadric
from pygletHelper.util.gl_enable import gl_enable

'''
A simple monochrome sphere.
'''

class sphere (axial):
    def __init__(self, other = None, color = rgb(), pos = vector(0,0,0), radius = 1.0):
        super(sphere, self).__init__(color = color, pos = pos, radius = radius)
        # Construct a unit sphere at the origin.
        if not other is None:
            self.axial = other
        self.PRIMITIVE_TYPEINFO_IMPL = sphere
        self.compiled = False
        print("radius: "+str(self.radius))
    @property
    def scale(self):
        '''
         Exposed for the benefit of the ellipsoid object, which overrides it.
         The default is to use <radius, radius, radius> for the scale.
        '''
        return vector( self.radius, self.radius, self.radius)

    @property
    def material_matrix(self, out = tmatrix()):
        out.translate( vector(.5,.5,.5) )
        scale = self.scale()
        out.scale( scale * (.5 / max(scale.x, max(scale.y, scale.z))) )
        return out

    def degenerate(self):
        '''
        Returns true if this object should not be drawn.  Conditions are:
        zero radius, or visible is false.  (overridden by the ellipsoid class).
        '''
        return self.radius == 0.0

    def grow_extent(self, e):
        e.add_sphere( self.pos, self.radius)
        e.add_body()

    # True until the first sphere is rendered, then false.
    def init_model(self, scene):
        # TODO: make this work
        #if (scene.sphere_model[0].compiled()):
        '''
        if self.compiled:
            return
        '''
        sph = quadric()
        #sph.render_sphere( 1.0, 13, 7)


        scene.sphere_model[0].gl_compile_begin()
        sph.render_sphere( 1.0, 13, 7)
        scene.sphere_model[0].gl_compile_end()

        scene.sphere_model[1].gl_compile_begin()
        sph.render_sphere( 1.0, 19, 11)
        scene.sphere_model[1].gl_compile_end()

        scene.sphere_model[2].gl_compile_begin()
        sph.render_sphere( 1.0, 35, 19)
        scene.sphere_model[2].gl_compile_end()

        scene.sphere_model[3].gl_compile_begin()
        sph.render_sphere( 1.0, 55, 29)
        scene.sphere_model[3].gl_compile_end()

        scene.sphere_model[4].gl_compile_begin()
        sph.render_sphere( 1.0, 70, 34)
        scene.sphere_model[4].gl_compile_end()

        # Only for the very largest bodies.
        scene.sphere_model[5].gl_compile_begin()
        sph.render_sphere( 1.0, 140, 69)
        scene.sphere_model[5].gl_compile_end()

    def gl_pick_render(self, geometry):
        if (self.degenerate()):
            print("I'm a degenerate sphere!")
            return
        self.init_model(geometry)

        guard = gl_matrix_stackguard()
        self.model_world_transform( geometry.gcf, self.scale() ).gl_mult()

        geometry.sphere_model[0].gl_render()

    def gl_render(self, geometry):
        # Renders a simple sphere with the #2 level of detail.
        if self.radius==0.0:
            return
        self.init_model(geometry)

        # coverage is the radius of this sphere in pixels:
        coverage = geometry.pixel_coverage( self.pos, self.radius)
        lod = 0

        if (coverage < 0): # Behind the camera, but still visible.
            lod = 4
        elif (coverage < 30):
            lod = 0
        elif (coverage < 100):
            lod = 1
        elif (coverage < 500):
            lod = 2
        elif (coverage < 5000):
            lod = 3
        else:
            lod = 4

        lod += geometry.lod_adjust # allow user to reduce level of detail
        if (lod > 5):
            lod = 5
        elif (lod < 0):
            lod = 0
        guard = gl_matrix_stackguard()
        #self.model_world_transform( geometry.gcf, self.scale ).gl_mult()
        self.color.gl_set(self.opacity)

        lod = 3
        if self.translucent():
            # Spheres are convex, so we don't need to sort
            cull_face = gl_enable( GL_CULL_FACE)

            # Render the back half (inside)
            glCullFace( GL_FRONT )
            geometry.sphere_model[lod].gl_render()

            # Render the front half (outside)
            glCullFace( GL_BACK )
            geometry.sphere_model[lod].gl_render()
        else:
            # Render a simple sphere.
            #lod = 0
            geometry.sphere_model[lod].gl_render()
