from __future__ import print_function
# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from traceback import print_stack


class displaylist_impl(object):
    def __init__(self):
        self.handle = glGenLists(1)
        # on_gl_free.connect( gl_free, self.handle)
        glNewList(self.handle, GL_COMPILE)

    #def __del__(self):
        #self.compile_end()

    # on_gl_free.free( gl_free, self.handle)

    def gl_free(self, handle):
        glDeleteLists(handle, 1)

    def compile_end(self):
        #print_stack()
        #print("is list? :"+str(glIsList(self.handle)))
        glEndList(self.handle)
        '''
        try:
            glEndList(self.handle)
        except GLException as e:
            print("Got GL Exception on end list: " + str(e))
        '''

    def call(self):
        try:
            glCallList(self.handle)
        except GLException as e:
            print("Got GL Exception on call list: "+str(e))


# A manager for OpenGL displaylists
class displaylist(object):
    def __init__(self, built=False):
        self.built = built
        self.impl = None

    # Begin compiling a new displaylist.  Nothing is drawn to the screen
    #	when rendering commands into the displaylist.  Be sure to call
    #	gl_compile_end() when you are done.
    def gl_compile_begin(self):
        self.impl = displaylist_impl()

    # Completes compiling the displaylist.
    def gl_compile_end(self):
        self.impl.compile_end()
        self.built = True

    # Perform the OpenGL commands cached with gl_compile_begin() and
    #	gl_compile_end().
    def gl_render(self):
        self.impl.call()
        self.built = True

    # @return true iff this object contains a compiled OpenGL program.
    def compiled(self):
        return self.built
