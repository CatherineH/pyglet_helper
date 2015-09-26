# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pyglet.graphics.vertexbuffer import create_buffer

from numpy import zeros, asarray

from pygletHelper.objects.axial import Axial
from pygletHelper.util.rgba import Rgb
from pygletHelper.util.vector import Vector
from pygletHelper.util.tmatrix import Rotation
from pygletHelper.util.gl_enable import gl_enable_client

from math import pi, sin, cos, sqrt


class Model(object):
    def __init__(self):
        self._vertex_pos = None
        self._vector_normal = None
        self._indices = None
        self.vertices_gl = None
        self.normals_gl = None
        self.indices_gl = None
        self.indices = zeros(0)
        self.vertex_pos = zeros(0)
        self.vector_normal = zeros(0)

    @property
    def vertex_pos(self):
        return self._vertex_pos

    @vertex_pos.setter
    def vertex_pos(self, n_vertex_pos):
        self._vertex_pos = []
        for i in range(0, len(n_vertex_pos)):
            self._vertex_pos.append(n_vertex_pos[i].x)
            self._vertex_pos.append(n_vertex_pos[i].y)
            self._vertex_pos.append(n_vertex_pos[i].z)
        self.vertices_gl = (GLfloat * len(self._vertex_pos))(*self._vertex_pos)

    @property
    def vector_normal(self):
        return self._vector_normal

    @vector_normal.setter
    def vector_normal(self, n_vector_normal):
        self._vector_normal = []
        for i in range(0, len(n_vector_normal)):
            self._vector_normal.append(n_vector_normal[i].x)
            self._vector_normal.append(n_vector_normal[i].y)
            self._vector_normal.append(n_vector_normal[i].z)
        self.normals_gl = (GLfloat * len(self._vector_normal))(*self._vector_normal)

    @property
    def indices(self):
        return self._indices

    @indices.setter
    def indices(self, n_indices):
        self._indices = [int(i) for i in n_indices]
        self.indices_gl = (GLuint * len(self._indices))(*self._indices)


class Ring(Axial):
    def __init__(self, thickness=0.0, model_rings=-1, radius=1.0, color=Rgb(), pos=Vector(0, 0, 0),
                 axis=Vector(1, 0, 0)):
        super(Ring, self).__init__(radius=radius, color=color, pos=pos, axis=axis)
        self._thickness = None
        self.list = None
        self.axis = axis
        # The radius of the ring's body.  If not specified, it is set to 1/10 of
        # the radius of the body.
        self.thickness = thickness
        self.PRIMITIVE_TYPEINFO_DECL = ring
        self.model = model()
        self.model_rings = model_rings
        self.model_bands = 0
        self.model_radius = 0
        self.model_thickness = 0
        self.pos = pos

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, t):
        self._thickness = t

    @property
    def material_matrix(self, out):
        out.translate(vector(.5, .5, .5))
        out.scale(vector(self.radius, self.radius, self.radius) * (.5 / (self.radius + self.thickness)))
        return out

    @property
    def degenerate(self):
        return self.radius == 0.0

    def gl_pick_render(self, scene):
        self.gl_render(scene)

    def gl_render(self, scene):
        if self.degenerate:
            return
        # Level of detail estimation.  See sphere::gl_render().

        # The number of subdivisions around the hoop's radial direction.
        if self.thickness:
            band_coverage = scene.pixel_coverage(self.pos, self.thickness)
        else:
            band_coverage = scene.pixel_coverage(self.pos, self.radius * 0.1)
        if band_coverage < 0:
            band_coverage = 1000
        bands = sqrt(band_coverage * 4.0)
        bands = clamp(4, bands, 40)
        # The number of subdivions around the hoop's tangential direction.
        ring_coverage = scene.pixel_coverage(self.pos, self.radius)
        if ring_coverage < 0:
            ring_coverage = 1000
        rings = sqrt(ring_coverage * 4.0)
        rings = clamp(4, rings, 80)
        slices = int(rings)
        inner_slices = int(bands)
        radius = self.radius
        inner_radius = self.thickness

        # Create the vertex and normal arrays.
        vertices = []
        normals = []

        u_step = 2 * pi / (slices - 1)
        v_step = 2 * pi / (inner_slices - 1)
        u = 0.
        for i in range(slices):
            cos_u = cos(u)
            sin_u = sin(u)
            v = 0.
            for j in range(inner_slices):
                cos_v = cos(v)
                sin_v = sin(v)

                d = (radius + inner_radius * cos_v)
                x = d * cos_u
                y = d * sin_u
                z = inner_radius * sin_v

                nx = cos_u * cos_v
                ny = sin_u * cos_v
                nz = sin_v

                vertices.extend([x, y, z])
                normals.extend([nx, ny, nz])
                v += v_step
            u += u_step

        # Create ctypes arrays of the lists
        vertices = (GLfloat * len(vertices))(*vertices)
        normals = (GLfloat * len(normals))(*normals)

        # Create a list of triangle indices.
        indices = []
        for i in range(slices - 1):
            for j in range(inner_slices - 1):
                p = i * inner_slices + j
                indices.extend([p, p + inner_slices, p + inner_slices + 1])
                indices.extend([p, p + inner_slices + 1, p + 1])
        indices = (GLuint * len(indices))(*indices)

        # Compile a display list
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)
        self.color.gl_set(self.opacity)

        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        self.model_world_transform(scene.gcf, vector(self.radius, self.radius, self.radius)).gl_mult()

        glVertexPointer(3, GL_FLOAT, 0, vertices)
        glNormalPointer(GL_FLOAT, 0, normals)
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)
        glPopClientAttrib()

        glEndList()
        glCallList(self.list)

    def grow_extent(self, world):
        if self.degenerate:
            return
        # TODO: Not perfectly accurate (a couple more circles would help)
        a = self.axis.norm()
        if self.thickness:
            t = self.thickness
        else:
            t = self.radius * .1
        world.add_circle(self.pos, a, self.radius + t)
        world.add_circle(self.pos + a * t, a, self.radius)
        world.add_circle(self.pos - a * t, a, self.radius)
        world.add_body()
        return world

    def create_model(self, rings, bands):
        scaled_thickness = 0.2
        # if self.thickness != 0.0:
        #    scaled_thickness = 2*self.thickness / self.radius
        m = model()
        m.vertices = []
        m.normals = []

        u_step = 2 * pi / (rings - 1)
        v_step = 2 * pi / (bands - 1)
        u = 0.
        for i in range(rings):
            cos_u = cos(u)
            sin_u = sin(u)
            v = 0.
            for j in range(bands):
                cos_v = cos(v)
                sin_v = sin(v)

                d = (self.radius + self.thickness * cos_v)
                x = d * cos_u
                y = d * sin_u
                z = self.thickness * sin_v

                nx = cos_u * cos_v
                ny = sin_u * cos_v
                nz = sin_v

                m.vertices.extend([x, y, z])
                m.normals.extend([nx, ny, nz])
                v += v_step
            u += u_step

        # Create ctypes arrays of the lists
        m.vertices_gl = (GLfloat * len(m.vertices))(*m.vertices)
        m.normals_gl = (GLfloat * len(m.normals))(*m.normals)

        # Create a list of triangle indices.
        m.indices = []
        for i in range(rings - 1):
            for j in range(bands - 1):
                p = i * bands + j
                m.indices.extend([p, p + bands, p + bands + 1])
                m.indices.extend([p, p + bands + 1, p + 1])
        m.indices_gl = (GLuint * len(m.indices))(*m.indices)
        return m


def clamp(lower, value, upper):
    if lower > value:
        return lower
    if upper < value:
        return upper
    return value
