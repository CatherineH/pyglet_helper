from pyglet.gl import *


# Stack-unwind safe versions of gl{Enable,Disable}{ClientState,}()
class gl_enable(object):
    def __init__(self, value):

        self.value = GLenum(value)
        glEnable(self.value)
    def __del__(self):
        glDisable(self.value)


class gl_enable_client(object):
    def __init__(self, v):
        self.value = GLenum(v)
        glEnableClientState(self.value)

    def __del__(self):
        glDisableClientState(self.value)


class gl_disable(object):
    def __init__(self, v):
        self.value = GLenum(v)
        glDisable(self.value)

    def __del__(self):

        glEnable(self.value)
