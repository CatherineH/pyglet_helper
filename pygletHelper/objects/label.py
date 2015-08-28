# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pygletHelper.objects.renderable import renderable
from pygletHelper.util.rgba import rgb

class label(renderable):
    def __init__(self, pos = [0, 0, 0], space = 0, xoffset = 0, yoffset = 0, \
      border = 5, font_description = None, font_size = 13, text_changed = False, \
      box_enabled = True, line_enabled = True, linecolor = rgb(), opacity = 0.66, \
      handle = 0, other = None):
        # by default, the color of scene.background
        self.background = rgb(0.0, 0.0, 0.0)
        self.text = ''
        if not other == None:
            self.pos = other.pos
            self.space = other.space
            self.xoffset = other.xoffset
            self.yoffset = other.yoffset
            self.border = other.border
            #/ A common name for the font.
            self.font_description = other.font_description
            #/ The nominal size of the font, in pixels.
            self.font_size = other.font_size
            self.text_changed = other.text_changed
            #/< True to draw a box around the text
            self.box_enabled = other.box_enabled
            #/< True to draw a line to the text.
            self.line_enabled = other.line_enabled
             #/< The color of the lines in the label. (color is for text)
            self.linecolor = other.linecolor
            #/< The opacity of the background for the text.
            self.opacity = other.opacity
            self.handle = other.handle
        else:
            self.pos = pos
            self.space = space
            self.xoffset = xoffset
            self.yoffset = yoffset
            self.border = border
            self.font_description = font_description
            self.font_size = font_size
            self.text_changed = text_changed
            self.box_enabled = box_enabled
            self.line_enabled = line_enabled
            self.linecolor = linecolor
            self.opacity = opacity
            self.handle = handle

    @property
    def pos(self):
        return self.pos
    @pos.setter
    def pos( self, n_pos):
        self.pos = n_pos

    @property
    def x(self):
        return self.pos.x
    @x.setter
    def x( self, n_x):
        self.pos.x = x

    @property
    def y(self):
        return self.pos.y
    @y.setter
    def y( self, n_y):
        self.pos.y = y

    @property
    def z(self):
        return self.pos.z
    @z.setter
    def z( self, n_z):
        self.pos.z = z

    @property
    def color(self):
        return self.color
    @color.setter
    def color( self, n_color):
        self.color = n_color

    @property
    def red(self):
        return self.color.red
    @red.setter
    def red(self, r):
        self.color.red = r
        self.text_changed = True

    @property
    def green(self):
        return self.color.green
    @green.setter
    def green(self, r):
        self.color.green = r
        self.text_changed = True

    @property
    def blue(self):
        return self.color.blue
    @blue.setter
    def blue(self, r):
        self.color.blue = r
        self.text_changed = True

    @property
    def opacity(self):
        return self.opacity
    @opacity.setter
    def opacity( self, n_opacity):
        self.opacity = n_opacity

    @property
    def text(self):
        return self.text
    @text.setter
    def text( self, n_text):
        self.text = n_text
        self.text_changed = True

    @property
    def space(self):
        return self.space
    @space.setter
    def space( self, n_space):
        self.space = n_space

    @property
    def xoffset(self):
        return self.xoffset
    @xoffset.setter
    def xoffset( self, n_xoffset):
        self.xoffset = n_xoffset

    @property
    def yoffset(self):
        return self.yoffset
    @yoffset.setter
    def yoffset( self, n_yoffset):
        self.yoffset = n_yoffset

    @property
    def border(self):
        return self.border
    @border.setter
    def border( self, n_border):
        self.border = n_border

    @property
    def font_family(self):
        return self.font_family
    @font_family.setter
    def font_family( self, n_font_family):
        self.font_family = n_font_family
        self.text_changed = True

    @property
    def font_size(self):
        return self.font_size
    @font_size.setter
    def font_size( self, n_font_size):
        self.font_size = n_font_size
        self.text_changed = True

    def render_box(self, enabled):
        self.box_enable = enabled
    def has_box(self):
        return self.box_enable

    def render_line(self, enabled):
        self.line_enabled = enabled
    def has_line(self):
        return self.line_enabled

    @property
    def linecolor(self):
        return self.linecolor
    @linecolor.setter
    def linecolor( self, n_linecolor):
        self.linecolor = n_linecolor

    @property
    def background(self):
        return self.background
    @background.setter
    def background( self, n_background):
        self.background = n_background

    @property
    def bitmap(self):
        return self.bitmap
    @bitmap.setter
    def bitmap(self, bm, width, height, back0, back1, back2):
        # bitmap is called from primitives.py/get_bitmap
        # bm.data is RGB unsigned bytes
        # http:#mail.python.org/pipermail/cplusplus-sig/2003-March/003202.html :
        self.data = bm.data
        self.bitmap_width = width
        self.bitmap_height = height
        self.text_changed = True
        self.bitmap = []*4*width*height

        for j in range(0, height):
            for i in range(0, width):
                is_background = True

                b = data[3*width*j + 3*i]
                bitmap[4*width*j + 4*i] = b
                if (b != back0):
                    is_background = False

                b = data[3*width*j + 3*i + 1]
                bitmap[4*width*j + 4*i + 1] = b
                if (b != back1):
                    is_background = False

                b = data[3*width*j + 3*i + 2]
                bitmap[4*width*j + 4*i + 2] = b
                if (b != back2):
                    is_background = False

                if is_background:
                    bitmap[4*width*j + 4*i + 3] = 0
                else:
                    bitmap[4*width*j + 4*i + 3] = 255

    # Sets handle and registers it to be freed at shutdown
    @property
    def handle(self):
        return self.handle
    @handle.setter
    def handle(self, view, h):
        if (self.handle):
            on_gl_free.free( bind( self.gl_free(), self.handle ) )
        self.handle = h
        on_gl_free.connect( bind(self.gl_free(), self.handle) )

    @property
    def center(self):
        return self.pos

    def gl_free(self, handle):
         glDeleteTextures(1, handle)

    def gl_render(self, scene):

        if (self.text_changed):
            # Call get_bitmap in primitives.py, which calls set_bitmap in this file
            # to set bitmap, bitmap_width, and bitmap_height
            self.bitmap()
            self.text_changed = False


        # Compute the width of the text box.
        box_width = self.bitmap_width + 2*self.border

        # Compute the positions of the text in the text box, and the height of the
        # text box.  The text positions are relative to the lower left corner of
        # the text box.
        box_height = self.bitmap_height + 2*self.border

        text_pos = vector( self.border, box_height - self.border)

        clear_gl_error()
        label_pos = pos.scale(scene.gcfvec)
        lst = tmatrix().gl_projection_get() * tmatrix().gl_modelview_get()

        translate = tmatrix
        translate.w_column( label_pos)
        lst = lst * translate

        origin = vector(lst * vertex(vector(), 1.0)).project()

        # It is very important to make sure that the texture is positioned
        # accurately at a screen pixel location, to avoid artifacts around the texture.
        kx = scene.view_width/2.0
        ky = scene.view_height/2.0
        if (origin.x >= 0):
            origin.x = ((kx*origin.x+0.5))/kx
        else:
            origin.x = -((-kx*origin.x+0.5))/kx

        if (origin.y >= 0):
            origin.y = ((ky*origin.y+0.5))/ky
        else:
            origin.y = -((-ky*origin.y+0.5))/ky

        halfwidth = (0.5*box_width+0.5)
        halfheight = (0.5*box_height+0.5)

        stereo_linecolor = self.linecolor
        if (scene.anaglyph):
            if (scene.coloranaglyph):
                stereo_linecolor = self.linecolor.desaturate()
            else:
                stereo_linecolor = self.linecolor.grayscale()
        list = displaylist()
        list.gl_compile_begin()

        stereo_linecolor.gl_set(1.0)
        # Zero out the existing matrices, rendering will be in screen coords.
        guard = gl_matrix_stackguard()
        identity = tmatrix()
        identity.gl_load()
        glMatrixMode( GL_PROJECTION)  #< Zero out the projection matrix, too
        guard2 = gl_matrix_stackguard()
        identity.gl_load()

        glTranslated( origin.x, origin.y, origin.z)
        glScaled( 1.0/kx, 1.0/ky, 1.0)
        # At this point, all further translations are in direction of label space.
        if (self.space and (self.xoffset or self.yoffset)):
            # Move the origin away from the body.
            space_offset = vector(xoffset, yoffset).norm() *fabs(self.space)
            glTranslated( space_offset.x, space_offset.y, space_offset.z)

        # Optionally draw the line, and move the origin to the bottom left
        # corner of the text box.
        if (self.xoffset or self.yoffset):
            if (self.line_enabled):
                glBegin( GL_LINES)
                vector().gl_render()
                vector(self.xoffset, self.yoffset).gl_render()
                glEnd()

            if (fabs(self.xoffset) > fabs(self.yoffset)):
                if self.xoffset > 0:
                    glTranslated(self.xoffset, self.yoffset - halfheight, 0)
                else:
                    glTranslated(self.xoffset -2.0*halfwidth, self.yoffset - halfheight, 0)
            else:
                if self.yoffset > 0:
                    glTranslated( self.xoffset - halfwidth, self.yoffset , 0)
                else:
                    glTranslated( self.xoffset - halfwidth, self.yoffset + -2.0*halfheight, 0)
        else:
            glTranslated( -halfwidth, -halfheight, 0.0)

        if (self.opacity):
            # Occlude objects behind the label.
            rgba( self.background[0], self.background[1], self.background[2], self.opacity).gl_set()
            glBegin( GL_QUADS)
            vector().gl_render()
            vector( 2.0*halfwidth, 0).gl_render()
            vector( 2.0*halfwidth, 2.0*halfheight).gl_render()
            vector( 0, 2.0*halfheight).gl_render()
            glEnd()

        if (self.box_enabled):
            # Draw a box around the text.
            stereo_linecolor.gl_set(1.0)
            glBegin( GL_LINE_LOOP)
            vector().gl_render()
            vector( 2.0*halfwidth, 0).gl_render()
            vector( 2.0*halfwidth, 2.0*halfheight).gl_render()
            vector( 0, 2.0*halfheight).gl_render()
            glEnd()


        # Render the text itself.
        gl_render_to_quad(scene, self.text_pos)

        glMatrixMode( GL_MODELVIEW)  # Pops the matrices back off the stack
        list.gl_compile_end()
        check_gl_error()
        scene.screen_objects.insert( make_pair(self.pos, list))

    def grow_extent(self, e):
        e.add_point( self.pos )

    def gl_initialize(self, view):
        bottom_up = self.bitmap_height < 0
        if (self.bitmap_height < 0):
            self.bitmap_height = -self.bitmap_height

        # next_power_of_two is in texture.cpp
        tx_width = int(next_power_of_two( self.bitmap_width ))
        tx_height = int(next_power_of_two( self.bitmap_height ))
        tc_x = (self.bitmap_width) / tx_width
        tc_y = (self.bitmap_height) / tx_height

        type = GL_TEXTURE_2D

        if not self.handle:
            self.handle = glGenTextures(1, self.handle)
            set_handle( view,self.handle )

        glBindTexture(type, self.handle)

        # No filtering - we want the exact pixels from the texture
        glTexParameteri( type, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri( type, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        glPixelStorei( GL_UNPACK_ALIGNMENT, 1 )
        glPixelStorei( GL_UNPACK_ROW_LENGTH, self.bitmap_width )

        check_gl_error()

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tx_width, tx_height, 0,
                        GL_RGBA, GL_UNSIGNED_BYTE, NULL)
        check_gl_error()
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, self.bitmap_width, self.bitmap_height,
                        GL_RGBA, GL_UNSIGNED_BYTE, self.bitmap)
        check_gl_error()

        glPixelStorei( GL_UNPACK_ALIGNMENT, 4 )
        glPixelStorei( GL_UNPACK_ROW_LENGTH, 0 )


        self.coord[0] = vector()
        self.coord[1] = vector(0, -self.bitmap_height)
        self.coord[2] = vector(self.bitmap_width, -self.bitmap_height)
        self.coord[3] = vector(self.bitmap_width, 0)

        self.tcoord[0**bottom_up] = vector()
        self.tcoord[1**bottom_up] = vector(0, tc_y)
        self.tcoord[2**bottom_up] = vector(tc_x, tc_y)
        self.tcoord[3**bottom_up] = vector(tc_x, 0)

    def gl_render_to_quad(self, v, text_pos ):
        gl_initialize(v)

        glBindTexture(GL_TEXTURE_2D, self.handle)

        glTranslated( text_pos.x, text_pos.y, text_pos.z )
        glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE )
        self.draw_quad()

        check_gl_error()

    def draw_quad(self):
        glBegin(GL_QUADS)
        for i in range(0,4):
            glTexCoord2d( self.tcoord[i].x, self.tcoord[i].y )
            self.coord[i].gl_render()
        glEnd()
