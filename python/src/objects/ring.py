# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from axial import axial
from util.rgba import rgb
from util.vector import vector

class model :
    def __init__(self):
        self.indices = vector()
        self.vertex_pos = vector()
        self.vector_normal = vector()

class ring (axial):
    def __init__(self, thickness = 0.0, model_rings = -1, radius = 1.0, color = rgb(), pos = vector(0,0,0), axis = vector(1,0,0)):
        super(ring, self).__init__(radius = radius, color = color, pos = pos, axis = axis)
        # The radius of the ring's body.  If not specified, it is set to 1/10 of
        # the radius of the body.
        self.thickness = thickness
        self.PRIMITIVE_TYPEINFO_DECL = ring
        self.model = model()
        self.model_rings = model_rings
        self.model_bands = 0
        self.model_radius = 0
        self.model_thickness = 0

    @property
    def thickness(self):
        return self._thickness
    @thickness.setter
    def thickness(self, t):
        self._thickness = t

    @property
    def material_matrix(self, out):
        out.translate( vector(.5,.5,.5) )
        out.scale( vector(self.radius,self.radius,self.radius) * (.5 / (self.radius+self.thickness)) )
        return out

    def degenerate(self):
        return self.radius == 0.0

    def gl_pick_render(self, scene):
        self.gl_render(scene)

    def gl_render(self, scene):
        if self.degenerate():
            return
        # Level of detail estimation.  See sphere::gl_render().

        # The number of subdivisions around the hoop's radial direction.
        if self.thickness:
            band_coverage = scene.pixel_coverage( self.pos, self.thickness)
        else:
            band_coverage = scene.pixel_coverage(self.pos, self.radius*0.1)
        if (band_coverage<0):
            band_coverage = 1000
        bands = sqrt(band_coverage * 4.0)
        bands = clamp( 4, bands, 40)
        # The number of subdivions around the hoop's tangential direction.
        ring_coverage = scene.pixel_coverage( self.pos, self.radius)
        if (ring_coverage<0):
            ring_coverage = 1000
        rings = sqrt(ring_coverage * 4.0)
        rings = clamp( 4, rings, 80)

        if self.model_rings != rings or self.model_bands != bands or self.model_radius != self.radius or self.model_thickness != self.thickness:
            self.model_rings = rings
            self.model_bands = bands
            self.model_radius = self.radius
            self.model_thickness = self.thickness
            create_model( rings, bands, model )
        clear_gl_error()

        vertex_array = gl_enable_client ( GL_VERTEX_ARRAY)
        normal_array = gl_enable_client ( GL_NORMAL_ARRAY)

        guard = gl_matrix_stackguard()
        model_world_transform( scene.gcf, vector(self.radius,self.radius,self.radius) ).gl_mult()

        self.color.gl_set(self.opacity)

        self.model.vertex_pos[0] = glVertexPointer( 3, GL_FLOAT, 0 )
        self.model.vertex_normal[0] = glNormalPointer( GL_FLOAT, 0 )
        self.model.indices[0] = glDrawElements( GL_TRIANGLES, self.model.indices.size(), GL_UNSIGNED_SHORT)

        check_gl_error()

    def grow_extent(self, world):
        if (self.degenerate()):
            return
        # TODO: Not perfectly accurate (a couple more circles would help)
        a = self.axis.norm()
        if self.thickness:
            t = self.thickness
        else:
            t = self.radius * .1
        world.add_circle( self.pos, a, self.radius + t )
        world.add_circle( self.pos + a*t, a, self.radius )
        world.add_circle( self.pos - a*t, a, self.radius )
        world.add_body()
        return world

    def create_model(self, rings, bands):
        # In Visual 3, rendered thickness was (incorrectly) double what was documented.
        # The documentation said that thickness was the diameter of a cross section of
        # a solid part of the ring, but in fact ring.thickness was the radius of the
        # cross section. Presumably we have to maintain the incorrect Visual 3 behavior
        # and change the documentation.
        scaled_radius = 1.0
        scaled_thickness = 0.2
        if self.thickness != 0.0:
            scaled_thickness = 2*self.thickness / self.radius

        # First generate a circle of radius thickness in the xy plane
        if (bands > 80):
            raise ValueError("ring create_model: More bands than expected.")
        circle = [vector()]*80
        circle[0] = vector(0,scaled_thickness*0.5,0)
        rotator = rotation( 2.0 * M_PI / bands, vector( 0,0,1 ), vector( 0,0,0 ) )
        for i in range(1, bands):
            circle[i] = rotator * circle[i-1]
        m = model()
        m.vertex_pos.resize( rings * bands )
        m.vertex_normal.resize( rings * bands )
        vertexes = m.vertex_pos[0]
        normals = m.vertex_normal[0]

        # ... and then sweep it in a circle around the x axis
        radial = vector(0,1,0)
        i=0
        rotator = rotation( 2.0 * M_PI / rings, vector( 1,0,0 ), vector( 0,0,0 ) )
        for r in range(0, rings):
            for b in range(0, bands):
                normals[i].x = circle[b].x
                normals[i].y = radial.y * circle[b].y
                normals[i].z = radial.z * circle[b].y
                vertexes[i].x = normals[i].x
                vertexes[i].y = normals[i].y + radial.y
                vertexes[i].z = normals[i].z + radial.z
            radial = rotator * radial

        # Now generate triangle indices... could do this with triangle strips but I'm looking
        # ahead to next renderer design, where it would be nice to always use indexed tris
        m.indices.resize( rings*bands*6 )
        ind = m.indices[0]
        i = 0
        for r in range(0, rings):
            for b in range(0, bands):
                ind[0] = i
                ind[1] = i+bands
                ind[2] = i+1
                ind[3] = i+bands
                ind[4] = i+bands+1
                ind[5] = i+1
                i+=1
                #not 100% sure what this does...
                ind+=6
            ind[2-6] -= bands
            ind[4-6] -= bands
            ind[5-6] -= bands
        ind -= 6*bands
        for b in range(0,bands):
            ind[1] -= rings*bands
            ind[3] -= rings*bands
            ind[4] -= rings*bands
            ind += 6
