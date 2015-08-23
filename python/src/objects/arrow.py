# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from objects.primitive import primitive
from objects.box import box
from objects.pyramid import pyramid
from util.rgba import rgb
from util.tmatrix import tmatrix, gl_matrix_stackguard

# A 3D 4-sided arrow, with adjustable head and shaft.
class arrow(primitive):
    # Default arrow.  Pointing along +x, unit length,
    # Where does axis come from????
    def __init__(self, fixedwidth=False, headwidth=0, headlength=0, shaftwidth=0, color=rgb()):
        super(arrow, self).__init__(color=color)
        # True if the width of the point and shaft should not vary with the length
        #  of the arrow.
        self.fixedwidth = fixedwidth
        # If zero, then use automatic scaling for the width's of the parts of the
        # arrow.  If nonzero, they specify proportions for the arrow in world
        # space.
        self.headwidth = headwidth
        self.headlength = headlength
        self.shaftwidth = shaftwidth
        self.box = None
        self.pyramid = None

    def degenerate(self):
        return self.axis.mag() == 0.0

    @property
    def headwidth(self):
        if (self._headwidth): return self._headwidth
        if (self._shaftwidth): return 2.0 * self._shaftwidth
        return 0.2 * self.axis.mag()

    @headwidth.setter
    def headwidth(self, hw):
        self._headwidth = hw

    @property
    def headlength(self):
        if (self._headlength): return self._headlength
        if (self._shaftwidth): return 3.0 * self._shaftwidth
        return 0.3 * self.axis.mag()

    @headlength.setter
    def headlength(self, hl):
        self._headlength = hl

    @property
    def shaftwidth(self):
        if (self._shaftwidth): return self._shaftwidth
        return 0.1 * self.axis.mag()

    @shaftwidth.setter
    def shaftwidth(self, sw):
        self._shaftwidth = sw
        self._fixedwidth = True

    @property
    def fixedwidth(self):
        return self._fixedwidth

    @fixedwidth.setter
    def fixedwidth(self, fixed):
        self._fixedwidth = fixed

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
        self.gl_render(scene)
        m.swap(self.mat)

    def gl_render(self, scene):
        if (self.degenerate()):
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
        for part in range(0, 2):
            guard = gl_matrix_stackguard()
            self.model_world_transform(scene.gcf).gl_mult();
            if (part == shaft):
                glScaled(len - hl, sw, sw)
                glTranslated(0.5, 0, 0)

                if (model_material_loc >= 0):  # TODO simplify
                    model_mat = tmatrix()
                    s = 1.0 / max(len, hw)
                    model_mat.translate(vector((len - hl) * s * 0.5, 0.5, 0.5))
                    model_mat.scale(vector((len - hl), sw, sw) * s)
                    mat.get_shader_program().set_uniform_matrix(scene, model_material_loc, model_mat)
                scene.box_model.gl_render()
            else:
                glTranslated(len - hl, 0, 0)
                glScaled(hl, hw, hw)
                if (model_material_loc >= 0):  # TODO simplify
                    model_mat = tmatrix()
                    s = 1.0 / max(len, hw)
                    model_mat.translate(vector((len - hl) * s, 0.5, 0.5))
                    model_mat.scale(vector(hl, hw, hw) * s)
                    mat.get_shader_program().set_uniform_matrix(scene, model_material_loc, model_mat)
                scene.pyramid_model.gl_render()

    def grow_extent(self, world):
        if (self.degenerate()):
            return
        hw, sw, len, hl = effective_geometry(1.0)
        x = self.axis.cross(up).norm() * 0.5;
        y = self.axis.cross(x).norm() * 0.5;
        base = self.pos + self.axis.norm() * (len - hl);
        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                world.add_point(self.pos + x * (i * sw) + y * (j * sw))
                world.add_point(self.base + x * (i * hw) + y * (j * hw))
        world.add_point(self.pos + self.axis)
        world.add_body()

    def init_model(self, scene):
        if not scene.box_model.compiled():
            self.box = box()
            self.box.init_model(scene)
        if not scene.pyramid_model.compiled():
            self.pyramid = pyramid()
            self.pyramid.init_model(scene)

    '''
    Initializes these four variables with the effective geometry for the
        arrow.  The resulting geometry is scaled to view space, but oriented
        and positioned in model space.  The only requred transforms are
        reorientation and translation.
    '''

    def effective_geometry(self, gcf):
        '''
        First calculate the actual geometry based on the specs for headwidth,
        shaftwidth, shaftlength, and fixedwidth.  This geometry is calculated
        in world space and multiplied
        '''
        min_sw = 0.02  # minimum shaftwidth
        def_sw = 0.1  # default shaftwidth
        def_hw = 2.0  # default headwidth multiplier. (x shaftwidth)
        def_hl = 3.0  # default headlength multiplier. (x shaftwidth)

        # maximum fraction of the total arrow length allocated to the head.
        max_headlength = 0.5

        eff_length = self.axis.mag() * gcf
        if (self.shaftwidth):
            eff_shaftwidth = self.shaftwidth * gcf
        else:
            eff_shaftwidth = eff_length * def_sw

        if (self.headwidth):
            eff_headwidth = self.headwidth * gcf
        else:
            eff_headwidth = eff_shaftwidth * def_hw

        if (self.headlength):
            eff_headlength = self.headlength * gcf
        else:
            eff_headlength = eff_shaftwidth * def_hl

        if (self.fixedwidth):
            if (eff_headlength > max_headlength * eff_length):
                eff_headlength = max_headlength * eff_length
        else:
            if (eff_shaftwidth < eff_length * min_sw):
                scale = eff_length * min_sw / eff_shaftwidth
                eff_shaftwidth = eff_length * min_sw
                eff_headwidth *= scale
                eff_headlength *= scale
            if (eff_headlength > eff_length * max_headlength):
                scale = eff_length * max_headlength / eff_headlength
                eff_headlength = eff_length * max_headlength
                eff_headwidth *= scale
                eff_shaftwidth *= scale
        return [eff_headwidth, eff_shaftwidth, eff_length, eff_headlength]
