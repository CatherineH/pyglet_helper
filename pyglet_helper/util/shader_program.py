""" pyglet_helper.util.shader_program contains objects for creating programs to
describe how the light treats the object
"""
try:
    import pyglet.gl as gl
except ImportError:
    gl = None


class ShaderProgram(object):
    """
    An interface for storing and executing shader programs
    """
    def __init__(self, source=None):
        self._source = None
        self.source = source
        self.program = 0
        self.uniforms = {'': 0}

    @property
    def source(self):
        """
        Get the shader program's source as a string
        :return: the shader program's source
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source):
        """
        Set the shader program's source
        :param source: valid shader program
        :type source: str
        """
        self._source = source

    def uniform_location(self, name):
        """
        Get the location of the shader by name in the view.
        :param view: the view to inspect
        :type view: str
        :param name: the View to examine
        :type name: pyglet_helper.objects.view
        :return:
        """
        if self.program <= 0 or not gl.glext_arb.GL_ARB_shader_objects:
            return -1
        cache = self.uniforms[name]
        if cache == 0:
            cache = 2 + gl.glext_arb.glGetUniformLocationARB(self.program, name)
        return cache - 2

    def realize(self, view):
        """
        Render the shader program
        :param view: the view to render the shader program in
        :type view: pyglet_helper.objects.View
        """
        if self.program != -1:
            return

        if not view.enable_shaders:
            return

        if not gl.glext_arb.GL_ARB_shader_objects:
            return

        self.program = gl.glext_arb.glCreateProgramObjectARB()

        self.compile(gl.GL_VERTEX_SHADER_ARB)
        self.compile(gl.GL_FRAGMENT_SHADER_ARB)

        gl.glext_arb.glLinkProgramARB(self.program)

        # Check if linking succeeded
        link_ok = gl.glext_arb.glGetObjectParameterivARB\
            (self.program, gl.GL_OBJECT_LINK_STATUS_ARB)

        if not link_ok:
            # Some drivers (incorrectly?) set the GL error in
            # glLinkProgramARB() in this situation
            length = gl.glext_arb.\
                glGetObjectParameterivARB(self.program,
                                          gl.GL_OBJECT_INFO_LOG_LENGTH_ARB)
            temp = ['a'] * (length + 2)
            length, temp[0] = gl.glext_arb.glGetInfoLogARB(self.program,
                                                         length + 1)

            print("VPython WARNING: errors in shader program:\n" + str(temp)
                  + "\n")

            # Get rid of the program, since it can't be used without generating
            # GL errors.  We set program to 0 instead of -1 so that binding it
            # will revert to the fixed function pipeline, and realize() won't
            # be called again.
            gl.glext_arb.glDeleteObjectARB(self.program)
            self.program = 0
            return

    def compile(self, shader_type):
        """
        Compiles and attaches the current shader
        :param view: the view to render the shader program to
        :type view: pyglet_helper.objects.View
        :param shader_type: the shader type, e.g., GL_VERTEX_SHADER,
        GL_GEOMETRY_SHADER
        :type shader_type: valid opengl shader type
        """
        shader = gl.glext_arb.glCreateShaderObjectARB(shader_type)
        gl.glext_arb.glShaderSourceARB(shader, 1)
        gl.glext_arb.glCompileShaderARB(shader)
        gl.glext_arb.glAttachObjectARB(self.program, shader)
        gl.glext_arb.glDeleteObjectARB(shader)

    def get(self):
        """
        gets a handle to the current program
        :return: handle to the current program
        :rtype: glShaderObject
        """
        return self.program

    def gl_free(self):
        """
        Remove the current program from memory
        """
        gl.glext_arb.glDeleteObjectARB(self.program)


class UseShaderProgram(object):
    """
    A Class to handle the initialization of ShaderPrograms
    """
    def __init__(self, view, program=None):

        self.view = view
        self.m_ok = None
        self.program = program
        self.old_program = None
        self.init()

    def __exit__(self, _type, value, traceback):
        if self.old_program < 0 or not self.view.glext.ARB_shader_objects:
            return
        gl.glUseProgramObjectARB(self.old_program)

    @property
    def invoked(self):
        """
        Has the shader program been invoked?
        :return: True if the shader program was successfully invoked
        :rtype: boolean
        """
        return self.m_ok

    def init(self):
        """
        Initialize the shader program
        :return: Nothing
        """
        self.m_ok = False
        if not self.program or not self.view.glext.ARB_shader_objects or not \
                self.view.enable_shaders:
            self.old_program = -1
            return

        self.program.realize(self.view)

        # For now, nested shader invocations aren't supported.
        # old_program = v.glext.glGetHandleARB( GL_PROGRAM_OBJECT_ARB )
        self.old_program = 0

        self.view.glext.glUseProgramObjectARB(self.program.program)
        self.m_ok = (self.program.program != 0)
