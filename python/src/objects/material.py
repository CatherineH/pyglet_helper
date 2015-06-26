# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from util.shader_program import shader_program
from util.texture import texture

class material:
    def __init__(self, translucent = False):
        self.translucent = translucent
        self.textures = [texture()]
        self.shader = [shader_program()]

    @property
    def textures(self):
        return self.textures
    @textures.setter
    def textures(self, tex):
        self.textures = tex

    @property
    def shader(self):
        if (self.shader):
            return self.shader.get_source()
        else:
    	    return ''

    @shader.setter
    def shader(self, source):
        if (source.size()):
    	    self.shader.reset(shader_program( source ))
        else:
            self.shader.reset( None )

    @property
    def translucent(self):
        return self.translucent
    @translucent.setter
    def translucent(self, t):
        self.translucent = t

    def get_shader_program(self):
        return self.shader.get()


class apply_material:
    def __init__(self, v, m, material_matrix, sp = None, shader_program = shader_program()):
        self.v = v
        self.m = m
        self.material_matrix = material_matrix
        if sp == None:
            if m:
                sp = shader_program(v, m.shader)
            else:
                sp = shader_program(v, None)
        self.sp = sp
        if not self.m or not sp.ok():
            return
	    self.texa = "tex0"
        for t in range(0,self.m.textures.size()):
            if (t and self.v.glext.ARB_multitexture):
                self.v.glext.glActiveTexture(GL_TEXTURE0 + t)
            self.m.textures[t].gl_activate(self.v)
            if self.m.shader and self.v.glext.ARB_shader_objects:
                texa[3] = '0'+t
                self.v.glext.glUniform1iARB( self.m.shader.get_uniform_location( self.v, self.texa ), t )
            if not self.v.glext.ARB_multitexture:
                break

        # For compatibility, set the texture unit back
        if self.m.textures.size() > 1 and self.v.glext.ARB_multitexture:
            self.v.glext.glActiveTexture(GL_TEXTURE0)
        loc = self.m.shader.get_uniform_location( self.v, "model_material" )
        if ( loc >= 0 ):
            self.m.shader.set_uniform_matrix( self.v, self.loc, self.model_material )
        loc = self.m.shader.get_uniform_location( self.v, "light_count" )
        if ( loc >= 0 ):
            self.v.glext.glUniform1iARB( self.loc, self.v.light_count[0] )
        loc = self.m.shader.get_uniform_location( self.v, "light_pos" )
        if ( loc >= 0 and self.v.light_count[0]):
            self.v.light_pos[0] = self.v.glext.glUniform4fvARB( loc, self.v.light_count[0])
        loc = self.m.shader.get_uniform_location( self.v, "light_color" )
        if ( loc >= 0 and self.v.light_count[0] ):
            self.v.light_color[0] = self.v.glext.glUniform4fvARB( loc, self.v.light_count[0])
