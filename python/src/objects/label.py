# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from renderable import renderable

class label(renderable):
    def __init__(self, pos = [0, 0, 0], space = 0, xoffset = 0, yoffset = 0, \
	  border = 5, font_description = None, font_size = 13, text_changed = False, \
	  box_enabled = True, line_enabled = True, linecolor = color(), opacity = 0.66f, \
	  handle = 0, other = None):
        self.background = rgb(0.0, 0.0, 0.0)
        if not other == None:
            self.pos = other.pos
            self.space = other.space
            self.xoffset = other.xoffset
            self.yoffset = other.yoffset
            self.border = other.border
            self.font_description = other.font_description
            self.font_size = other.font_size
            self.text_changed = other.text_changed
            self.box_enabled = other.box_enabled
            self.line_enabled = other.line_enabled
            self.linecolor = other.linecolor
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
    @red.property
    def red(self, r):
        self.color.red = r
	    self.text_changed = True

	@property
    def green(self):
        return self.color.green
    @green.property
    def green(self, r):
        self.color.green = r
        self.text_changed = True

	@property
    def blue(self):
        return self.color.blue
    @blue.property
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


	void set_bitmap(array bm, int width, int height, int back0, int back1, int back2)

	GLuint handle
	static void gl_free( GLuint handle )

	# Sets handle and registers it to be freed at shutdown
	void set_handle( const view&, unsigned int handle )
	unsigned get_handle() { return handle }


	#/ A common name for the font.
	std::wstring font_description
	#/ The nominal size of the font, in pixels.
	double font_size

	bool box_enabled #/< True to draw a box around the text
	bool line_enabled #/< True to draw a line to the text.

	# bitmap_font* font
	rgb linecolor #/< The color of the lines in the label. (color is for text)
	float opacity #/< The opacity of the background for the text.

	rgb background # by default, the color of scene.background

	std::wstring text

	virtual void gl_render(view&)
	virtual vector get_center() const
	virtual void grow_extent( extent& )

	void gl_initialize(const view&)
	void gl_render_to_quad(const view& v, const vector& text_pos)
	void draw_quad()

	boost::python::object primitive_object

	void get_bitmap()
