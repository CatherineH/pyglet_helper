# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pyglet_helper.objects.primitive import Primitive
from pyglet_helper.objects.box import Box
from pyglet_helper.objects.pyramid import Pyramid
from pyglet_helper.util.rgba import Rgb
from pyglet_helper.util.vector import Vector
from pyglet_helper.util.tmatrix import Tmatrix


# A 3D 4-sided arrow, with adjustable head and shaft.
class Arrow(Primitive):
    # Default arrow.  Pointing along +x, unit length,
    # Where does axis come from????
    def __init__(self, fixed_width=False, head_width=0, head_length=0, shaft_width=0, color=Rgb(), pos=Vector(0, 0, 0),
                 axis=(1, 0, 0)):
        super(Arrow, self).__init__(color=color, pos=pos, axis=axis)
        # True if the width of the point and shaft should not vary with the length
        # of the arrow.
        self.fixed_width = fixed_width
        self._head_width = None
        self._head_length = None
        self._shaft_width = None
        self._fixed_width = None
        # If zero, then use automatic scaling for the width's of the parts of the
        # arrow.  If nonzero, they specify proportions for the arrow in world
        # space.
        self.head_width = head_width
        self.head_length = head_length
        self.shaft_width = shaft_width
        self.box = None
        self.pyramid = None

    @property
    def degenerate(self):
        return self.axis.mag() == 0.0

    @property
    def head_width(self):
        if self._head_width:
            return self._head_width
        if self._shaft_width:
            return 2.0 * self._shaft_width
        return 0.2 * self.axis.mag()

    @head_width.setter
    def head_width(self, hw):
        self._head_width = hw

    @property
    def head_length(self):
        if self._head_length:
            return self._head_length
        if self._shaft_width:
            return 3.0 * self._shaft_width
        return 0.3 * self.axis.mag()

    @head_length.setter
    def head_length(self, hl):
        self._head_length = hl

    @property
    def shaft_width(self):
        if self._shaft_width:
            return self._shaft_width
        return 0.1 * self.axis.mag()

    @shaft_width.setter
    def shaft_width(self, sw):
        self._shaft_width = sw
        self._fixed_width = True

    @property
    def fixed_width(self):
        return self._fixed_width

    @fixed_width.setter
    def fixed_width(self, fixed):
        self._fixed_width = fixed

    @property
    def length(self):
        return self.axis.mag()

    @length.setter
    def length(self, l):
        self.axis = self.axis.norm() * l

    def get_center(self):
        return (self.pos + self.axis) / 2.0

    def gl_pick_render(self, scene):
        # TODO: material related stuff in this file really needs cleaning up!
        m = material()
        m.swap(self.mat)
        self.render(scene)
        m.swap(self.mat)

    def render(self, scene):
        if self.degenerate:
            return
        self.init_model(scene)
        self.color.gl_set(self.opacity)
        hw, sw, len, hl = self.effective_geometry(1.0)
        if self.mat and self.mat.get_shader_program():
            model_material_loc = self.mat.get_shader_program().get_uniform_location(scene, "model_material")
        else:
            model_material_loc = -1
        # Render the shaft and the head in back to front order (the shaft is in front
        # of the head if axis points away from the camera)
        shaft = self.axis.dot(scene.camera - (self.pos + self.axis * (1 - hl / len))) < 0
        glPushMatrix()
        self.model_world_transform(scene.gcf).gl_mult()

        for part in range(0, 2):
            if part == shaft:
                glScaled(len - hl, sw, sw)
                glTranslated(0.5, 0, 0)
                if model_material_loc >= 0:
                    model_mat = Tmatrix()
                    s = 1.0 / max(len, hw)
                    model_mat.translate(Vector((len - hl) * s * 0.5, 0.5, 0.5))
                    model_mat.scale(Vector((len - hl), sw, sw) * s)
                    mat.get_shader_program().set_uniform_matrix(scene, model_material_loc, model_mat)
                scene.box_model.gl_render()
                glTranslated(-0.5, 0, 0)
                glScaled(1 / (len - hl), 1 / sw, 1 / sw)
            else:
                glTranslated(len - hl, 0, 0)
                glScaled(hl, hw, hw)
                if model_material_loc >= 0:
                    model_mat = Tmatrix()
                    s = 1.0 / max(len, hw)
                    model_mat.translate(Vector((len - hl) * s, 0.5, 0.5))
                    model_mat.scale(Vector(hl, hw, hw) * s)
                    mat.get_shader_program().set_uniform_matrix(scene, model_material_loc, model_mat)
                scene.pyramid_model.gl_render()
                glScaled(1 / hl, 1 / hw, 1 / hw)
                glTranslated(-len + hl, 0, 0)
        glPopMatrix()

    def grow_extent(self, world):
        if self.degenerate:
            return
        hw, sw, len, hl = self.effective_geometry(1.0)
        x = self.axis.cross(self.up).norm() * 0.5
        y = self.axis.cross(x).norm() * 0.5
        base = self.pos + self.axis.norm() * (len - hl)
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                world.add_point(self.pos + x * (i * sw) + y * (j * sw))
                world.add_point(base + x * (i * hw) + y * (j * hw))
        world.add_point(self.pos + self.axis)
        world.add_body()

    def init_model(self, scene):
        if not scene.box_model.compiled():
            self.box = Box()
            self.box.init_model(scene)
        if not scene.pyramid_model.compiled():
            self.pyramid = Pyramid()
            self.pyramid.init_model(scene)

    '''
    Initializes these four variables with the effective geometry for the
        arrow.  The resulting geometry is scaled to view space, but oriented
        and positioned in model space.  The only requred transforms are
        reorientation and translation.
    '''

    def effective_geometry(self, gcf):
        """
        First calculate the actual geometry based on the specs for headwidth,
        shaftwidth, shaftlength, and fixedwidth.  This geometry is calculated
        in world space and multiplied
        """
        min_sw = 0.02  # minimum shaftwidth
        def_sw = 0.1  # default shaftwidth
        def_hw = 2.0  # default headwidth multiplier. (x shaftwidth)
        def_hl = 3.0  # default headlength multiplier. (x shaftwidth)

        # maximum fraction of the total arrow length allocated to the head.
        max_head_length = 0.5

        eff_length = self.axis.mag() * gcf

        if self.shaft_width:
            eff_shaft_width = self.shaft_width * gcf
        else:
            eff_shaft_width = eff_length * def_sw

        if self.head_width:
            eff_head_width = self.head_width * gcf
        else:
            eff_head_width = eff_shaft_width * def_hw

        if self.head_length:
            eff_head_length = self.head_length * gcf
        else:
            eff_head_length = eff_shaft_width * def_hl

        if self.fixed_width:
            if eff_head_length > max_head_length * eff_length:
                eff_head_length = max_head_length * eff_length
        else:
            if eff_shaft_width < eff_length * min_sw:
                scale = eff_length * min_sw / eff_shaft_width
                eff_shaft_width = eff_length * min_sw
                eff_head_width *= scale
                eff_head_length *= scale
            if eff_head_length > eff_length * max_head_length:
                scale = eff_length * max_head_length / eff_head_length
                eff_head_length = eff_length * max_head_length
                eff_head_width *= scale
                eff_shaft_width *= scale
        return [eff_head_width, eff_shaft_width, eff_length, eff_head_length]
