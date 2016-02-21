from pyglet.gl import glDeleteObjectARB, GL_VERTEX_SHADER_ARB, \
    GL_FRAGMENT_SHADER_ARB, GL_OBJECT_LINK_STATUS_ARB, \
    GL_OBJECT_INFO_LOG_LENGTH_ARB


def uniform_matrix(view, loc, _in):
    matrix = [0] * 16
    in_p = _in.matrix_addr()
    for i in range(0, 16):
        matrix[i] = in_p[i]
    view.glext.glUniformMatrix4fvARB(loc, 1, False, matrix)


class ShaderProgram(object):
    def __init__(self, source=None):
        self._source = None
        self.source = source
        self.program = 0
        self.uniforms = ['', 0]

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = source

    def uniform_location(self, view, name):
        # TODO: change interface to cache the uniforms we actually want and
        # avoid string comparisons
        if self.program <= 0 or not view.glext.ARB_shader_objects:
            return -1
        cache = self.uniforms[name]
        if cache == 0:
            cache = 2 + view.glext.glGetUniformLocationARB(self.program, name)
        return cache - 2

    def realize(self, view):
        if self.program != -1:
            return

        if not view.enable_shaders:
            return

        if not view.glext.ARB_shader_objects:
            return

        self.program = view.glext.glCreateProgramObjectARB()

        self.compile(view, GL_VERTEX_SHADER_ARB)
        self.compile(view, GL_FRAGMENT_SHADER_ARB)

        view.glext.glLinkProgramARB(self.program)

        # Check if linking succeeded
        link_ok = view.glext.\
            glGetObjectParameterivARB(self.program, GL_OBJECT_LINK_STATUS_ARB)

        if not link_ok:
            # Some drivers (incorrectly?) set the GL error in
            # glLinkProgramARB() in this situation
            length = view.glext.\
                glGetObjectParameterivARB(self.program,
                                          GL_OBJECT_INFO_LOG_LENGTH_ARB)
            temp = ['a'] * (length + 2)
            length, temp[0] = view.glext.glGetInfoLogARB(self.program,
                                                         length + 1)

            # TODO: A way to report infoLog to the program?
            print( "VPython WARNING: errors in shader program:\n" + str(temp) +
                   "\n")

            # Get rid of the program, since it can't be used without generating
            # GL errors.  We set program to 0 instead of -1 so that binding it
            # will revert to the fixed function pipeline, and realize() won't
            # be called again.
            view.glext.glDeleteObjectARB(self.program)
            self.program = 0
            return

    def compile(self, v, shader_type):
        shader = v.glext.glCreateShaderObjectARB(shader_type)
        v.glext.glShaderSourceARB(shader, 1)
        v.glext.glCompileShaderARB(shader)
        v.glext.glAttachObjectARB(self.program, shader)
        v.glext.glDeleteObjectARB(shader)

    def get(self):
        return self.program

    def gl_free(self, program):
        glDeleteObjectARB(program)

    def get_section(self, name):
        """
        Extract section beginning with \n[name]\n and ending with \n[
        e.g.
        [vertex]
        void main() {}
        [fragment]
        void main() {}
        :param name: the name of the section to extract
        :type name: str
        :returns: the section of interest
        :rtype: str
        """
        header = "\n[" + name + "]\n"
        _source = "\n" + self.source

        section = ""
        pos = _source.find(header)
        while pos < len(_source):
            pos += len(header)
            end = self.source.find("\n[", pos)
            if end == self.source.npos:
                end = self.source.size()

            section += self.source.substr(pos, end - pos)
            pos = end
            pos = _source.find(header, pos)

        return section


class UseShaderProgram(object):
    def __init__(self, view, program=None):
        # use_shader_program(NULL) does nothing, rather than enabling the fixed
        # function pipeline explicitly.  This is convenient, but maybe we need
        # a way to do the other thing?
        self.view = view
        self.program = program
        self.oldProgram = None
        self.init()

    def __exit__(self, type, value, traceback):
        if self.oldProgram < 0 or not self.view.glext.ARB_shader_objects:
            return
        self.view.glext.glUseProgramObjectARB(self.oldProgram)

    @property
    def ok(self):
        return self.m_ok  # true if the shader program was successfully invoked

    def init(self):
        self.m_ok = False
        if not self.program or not self.view.glext.ARB_shader_objects or not \
                self.view.enable_shaders:
            self.oldProgram = -1
            return

        self.program.realize(self.view)

        # For now, nested shader invocations aren't supported.
        # oldProgram = v.glext.glGetHandleARB( GL_PROGRAM_OBJECT_ARB )
        self.oldProgram = 0

        self.view.glext.glUseProgramObjectARB(self.program.program)
        self.m_ok = (self.program.program != 0)
