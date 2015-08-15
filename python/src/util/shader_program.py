# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from traceback import print_stack

class shader_program:
    def __init__(self, source = None):
        self.source = source
        self.program = 0
        self.uniforms = ['', 0]

    @property
    def source(self):
        return self._source
    @source.setter
    def source(self, source):
        self._source = source

    @property
    def uniform_location(self, v, name):
        # TODO: change interface to cache the uniforms we actually want and avoid string comparisons
        if (self.program <= 0 or not v.glext.ARB_shader_objects):
            return -1
        cache = self.uniforms[ name ]
        if (cache == 0):
            cache = 2 + self.v.glext.glGetUniformLocationARB( self.program, name )
        return cache - 2

    def uniform_matrix(self, v, loc, _in ):
        matrix = [0]*16
        in_p = _in.matrix_addr()
        for i in range(0, 16):
            matrix[i] = in_p[i]
        v.glext.glUniformMatrix4fvARB( loc, 1, False, matrix )


    def realize(self, v ):
        if (self.program != -1):
            return

        if ( not v.enable_shaders ):
            return

        if ( not v.glext.ARB_shader_objects ):
            return

        self.program = v.glext.glCreateProgramObjectARB()
        check_gl_error()

        self.compile( v, GL_VERTEX_SHADER_ARB, self.getSection("varying")+self.getSection("vertex") )
        self.compile( v, GL_FRAGMENT_SHADER_ARB, self.getSection("varying")+self.getSection("fragment") )

        v.glext.glLinkProgramARB( self.program )

        # Check if linking succeeded
        link_ok = v.glext.glGetObjectParameterivARB( self.program, GL_OBJECT_LINK_STATUS_ARB )

        if ( not link_ok ):
            # Some drivers (incorrectly?) set the GL error in glLinkProgramARB() in this situation
            print("!linkok\n")
            clear_gl_error()
            infoLog = []
            length = v.glext.glGetObjectParameterivARB( program, GL_OBJECT_INFO_LOG_LENGTH_ARB)
            temp = ['a']*(length+2 )
            length, temp[0] = v.glext.glGetInfoLogARB( self.program, length+1)
            temp[0] = infoLog.append( length )

            # TODO: A way to report infoLog to the program?
            print( "VPython WARNING: errors in shader program:\n" + infoLog + "\n")

            # Get rid of the program, since it can't be used without generating GL errors.  We set
            #   program to 0 instead of -1 so that binding it will revert to the fixed function pipeline,
            #   and realize() won't be called again.
            v.glext.glDeleteObjectARB( self.program )
            self.program = 0
            return
        check_gl_error()

    def compile(self, v, type, source ):
        shader = v.glext.glCreateShaderObjectARB( type )
        str = self.source.c_str()
        len = self.source.size()
        str, len = v.glext.glShaderSourceARB( shader, 1 )
        v.glext.glCompileShaderARB( shader )
        v.glext.glAttachObjectARB( self.program, shader )
        v.glext.glDeleteObjectARB( shader )

    def getSection( self, name ):
      '''
      Extract section beginning with \n[name]\n and ending with \n[
      e.g.
      [vertex]
      void main() {}
      [fragment]
      void main() {}
      '''
      header = "\n[" + name + "]\n"
      _source = "\n" + self.source

      p = _source.find( header, p )
      while ( p != _source.npos ):
          p += header.size()
          end = source.find( "\n[", p )
          if (end == source.npos):
              end = source.size()

          section += source.substr( p, end-p )
          p = end
          p = _source.find( header, p )

          return section

    def gl_free(self, program ):
        glDeleteObjectARB(program)

class use_shader_program :
    def __init__(self, v, program = -1):
        # use_shader_program(NULL) does nothing, rather than enabling the fixed function
        #   pipeline explicitly.  This is convenient, but maybe we need a way to do the other thing?
        self.v = v
        self.program = program
        self.init()
    def __exit__(self):
        if (self.oldProgram < 0 or not self.v.glext.ARB_shader_objects):
            return
        self.v.glext.glUseProgramObjectARB( self.oldProgram )

    @property
    def ok(self):
        return self.m_ok # true if the shader program was successfully invoked

    def init(self, program):
        self.m_ok = False
        if (not self.program or not self.v.glext.ARB_shader_objects or not self.v.enable_shaders):
            self.oldProgram = -1
            return

        self.program.realize(v)

        # For now, nested shader invocations aren't supported.
        #oldProgram = v.glext.glGetHandleARB( GL_PROGRAM_OBJECT_ARB )
        self.oldProgram = 0

        self.v.glext.glUseProgramObjectARB( self.program.program )
        check_gl_error()

        self.m_ok = (self.program.program != 0)
