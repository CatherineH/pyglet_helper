# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from objects.rectangular import rectangular
from objects.arrow import arrow

from util.rgba import rgb
from util.vector import vector
from util.displaylist import displaylist

class pyramid(rectangular):
    def __init__(self, pos = vector(0,0,0), size = (1,1,1),color = rgb()):
        super(pyramid, self).__init__(pos = pos, color = color, width = size[0], height = size[1], length = size[2])
        #self.model = displaylist()

    def init_model(self):#, scene):
        # Note that this model is also used by arrow!
        #scene.pyramid_model.gl_compile_begin()

        vertices = [[0, .5, .5], \
            [0,-.5, .5], \
            [0,-.5,-.5], \
            [0, .5,-.5], \
            [1,  0,  0]]
        triangle_indices = [0, 0, 0]*6
        triangle_indices[0] = [3, 0, 4]  # top
        triangle_indices[1] = [1, 2, 4]  # bottom
        triangle_indices[2] = [0, 1, 4]  # front
        triangle_indices[3] = [3, 4, 2]  # back
        triangle_indices[4] = [0, 3, 2]  # left (base) 1
        triangle_indices[5] = [0, 2, 1]  # left (base) 2

        normals = [ [1,2,0], [1,-2,0], [1,0,2], [1,0,-2], [-1,0,0], [-1,0,0] ]

        glEnable(GL_CULL_FACE)
        glBegin( GL_TRIANGLES)

        # Inside
        for f in range(0,6):
            glNormal3f( -normals[f][0], -normals[f][1], -normals[f][2] )
            for v in range(0,3):
                vert = [GLfloat(i) for i in vertices[ triangle_indices[f][2-v] ]]
                glVertex3f( *vert )

        # Outside
        for f in range(0, 6):
            glNormal3fv( *[GLfloat(i) for i in normals[f]] )
            for v in range(0, 3):
                glVertex3f(*[GLfloat(i) for i in vertices[ triangle_indices[f][v] ]] )

        glEnd()
        glDisable(GL_CULL_FACE)

        #scene.pyramid_model.gl_compile_end()
        #check_gl_error()

    @property
    def center(self):
        return self.pos + self.axis * 0.33333333333333

    @property
    def material_matrix(self):
        out.translate( vector(0,.5,.5) )
        scale = vector( self.axis.mag(), self.height, self.width )
        out.scale( self.scale * (1.0 / max(scale.x, max(scale.y, scale.z))) )
        return out

    def gl_pick_render(self, scene):
        gl_render(scene)

    def gl_render(self, scene):
        if not scene.pyramid_model.compiled():
            self.init_model(scene)

        self.color.gl_set(self.opacity)

        guard = gl_matrix_stackguard()
        apply_transform( scene )

        scene.pyramid_model.gl_render()
        check_gl_error()

    def grow_extent( world_extent):
        orient = model_world_transform()
        vwidth = orient * vector( 0, 0, self.width * 0.5)
        vheight = orient * vector( 0, self.height * 0.5, 0)
        world_extent.add_point( self.pos + self.axis)
        world_extent.add_point( self.pos + vwidth + vheight)
        world_extent.add_point( self.pos - vwidth + vheight)
        world_extent.add_point( self.pos + vwidth - vheight)
        world_extent.add_point( self.pos - vwidth - vheight)
        world_extent.add_body()
        return world_extent

    #PRIMITIVE_TYPEINFO_DECL
