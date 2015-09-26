from pyglet.gl import *


# Stack-unwind safe versions of gl{Enable,Disable}{ClientState,}()
class DlEnable(object):
    def __init__(self, value):
        self.value = GLenum(value)
        glEnable(self.value)

    def __del__(self):
        glDisable(self.value)


class GlEnableClient(object):
    def __init__(self, v):
        self.value = GLenum(v)
        glEnableClientState(self.value)

    def __del__(self):
        glDisableClientState(self.value)


class GlDisable(object):
    def __init__(self, v):
        self.value = GLenum(v)
        glDisable(self.value)

    def __del__(self):
        glEnable(self.value)
