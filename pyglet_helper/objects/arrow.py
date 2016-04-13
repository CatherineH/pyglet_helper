"""
pyglet_helper.arrow contains an object for drawing an arrow
"""
try:
    from pyglet.gl import gl
except Exception as error_msg:
    gl = None
from pyglet_helper.objects import Box, Material, Primitive, Pyramid
from pyglet_helper.util import Rgb, Tmatrix, Vector


class Arrow(Primitive):
    """
     A 3D 4-sided arrow, with adjustable head and shaft. By default, pointing
     along +x, unit length.
    """
    def __init__(self, fixed_width=False, head_width=0.0, head_length=0.0,
                 shaft_width=0.0, color=Rgb(),
                 pos=Vector([0, 0, 0]), axis=(1, 0, 0)):
        """

        :param fixed_width: if True, the arrow's head width and length will not
         be scaled in proportion to its length.
        :type fixed_width: bool
        :param head_width: The width of the arrow's head section.
        :type head_width: float
        :param head_length: The length of the arrow's length section
        :type head_length: float
        :param shaft_width: The length of the arrow's shaft section
        :type shaft_width: float
        :param color: The arrow's color.
        :type color: pyglet_helper.util.Rgb
        :param pos: The arrow's position
        :type pos: pyglet_helper.util.pos
        :param axis: The arrow's axis direction
        :type axis: pyglet_helper.util.Vector
        """
        super(Arrow, self).__init__(color=color, pos=pos, axis=axis)
        # True if the width of the point and shaft should not vary with the
        # length
        # of the arrow.
        self.fixed_width = fixed_width
        self._head_width = None
        self._head_length = None
        self._shaft_width = None
        self._fixed_width = None
        # If zero, then use automatic scaling for the width's of the parts of
        # the arrow.  If nonzero, they specify proportions for the arrow in
        # world space.
        self.head_width = head_width
        self.head_length = head_length
        self.shaft_width = shaft_width
        self.box = None
        self.pyramid = None

    @property
    def degenerate(self):
        """
        :return: True if the arrow has an effective length of 0
        :rtype: bool
        """
        return self.axis.mag() == 0.0

    @property
    def head_width(self):
        """
        Get the width of the arrow's head, if undefined, it returns the
        default value of 2x the width of the shaft, if the the shaft width
        is undefined it returns a fifth of the arrow length
        :return: the arrow's head width
        :rtype: float
        """
        if self._head_width:
            return self._head_width
        if self._shaft_width:
            return 2.0 * self._shaft_width
        return 0.2 * self.axis.mag()

    @head_width.setter
    def head_width(self, new_head_width):
        """
        Set the value of the head width
        :param new_head_width: the new value of the head width
        :type new_head_width: float
        """
        self._head_width = new_head_width

    @property
    def head_length(self):
        """
        Get the length of the arrow's head. If undefined, it returns the
        default value of 3x the shaft width. If shaft width is also
        undefined, it returns the default value of 3/10 of the arrow's length.
        :return: the arrow's head length
        :rtype: float
        """
        if self._head_length:
            return self._head_length
        if self._shaft_width:
            return 3.0 * self._shaft_width
        return 0.3 * self.axis.mag()

    @head_length.setter
    def head_length(self, new_head_length):
        """
        Set the arrow's head length
        :param new_head_length: the new head length
        :type new_head_length: float
        :return:
        """
        self._head_length = new_head_length

    @property
    def shaft_width(self):
        """
        Get the arrow's shaft width. If undefined, it returns the default
        value of a tenth of the length of the arrow
        :return:
        """
        if self._shaft_width:
            return self._shaft_width
        return 0.1 * self.axis.mag()

    @shaft_width.setter
    def shaft_width(self, new_shaft_width):
        """
        set the arrow's shaft width. Once set, the value fixed_width is set
        to true, meaning default values will not be calculated on render
        :param new_shaft_width: the new shaft width
        :type new_shaft_width: float
        :return:
        """
        self._shaft_width = new_shaft_width
        self._fixed_width = True

    @property
    def fixed_width(self):
        """
        Returns true if the shaft_width property has been set,
        false otherwise. If fixed_width is false, default values for the
        shaft width, head with and head length will be calculated on render.
        :rtype: bool
        """
        return self._fixed_width

    @fixed_width.setter
    def fixed_width(self, fixed):
        """
        Sets the fixed width boolean parameter. If fixed_width is false,
        default values for the shaft width, head with and head length will be
        calculated on render.
        :param fixed: the new value for the fixed width parameter
        :type fixed: bool
        :return:
        """
        self._fixed_width = fixed

    @property
    def center(self):
        """ Calculates the center of the arrow by subtracting the axis off of
        the position

        :return: The arrow's center (position+axis)/2
        :rtype: float
        """
        return (self.pos + self.axis) / 2.0

    def render(self, scene):
        """ Render the arrow on the current view.

        :param scene: The view to render the model into.
        :type scene: pyglet_helper.objects.View
        """
        mat = Material()
        if self.degenerate:
            return
        self.init_model(scene)
        self.color.gl_set(self.opacity)
        _head_width, _shaft_width, _len, _head_length = \
            self.effective_geometry(1.0)
        if self.mat and self.mat.get_shader_program():
            model_material_loc = self.mat.get_shader_program().\
                get_uniform_location(scene, "model_material")
        else:
            model_material_loc = -1
        # Render the shaft and the head in back to front order (the shaft is in
        # front of the head if axis points away from the camera)
        shaft = self.axis.dot(scene.camera - (self.pos + self.axis *
                                              (1 - _head_length / _len))) < 0
        gl.glPushMatrix()
        self.model_world_transform(scene.gcf).gl_mult()

        for part in range(0, 2):
            if part == shaft:
                gl.glScaled(_len - _head_length, _shaft_width, _shaft_width)
                gl.glTranslated(0.5, 0, 0)
                if model_material_loc >= 0:
                    model_mat = Tmatrix()
                    scale = 1.0 / max(_len, _head_width)
                    _translation_magnitude = (_len - _head_length) * scale *\
                                             0.5
                    model_mat.translate(Vector([_translation_magnitude, 0.5,
                                                0.5]))
                    model_mat.scale(Vector([(_len - _head_length),
                                            _shaft_width,
                                            _shaft_width]) * scale)
                    mat.get_shader_program().\
                        set_uniform_matrix(scene, model_material_loc,
                                           model_mat)
                scene.box_model.gl_render()
                gl.glTranslated(-0.5, 0, 0)
                gl.glScaled(1 / (_len - _head_length), 1 / _shaft_width,
                         1 / _shaft_width)
            else:
                gl.glTranslated(_len - _head_length, 0, 0)
                gl.glScaled(_head_length, _head_width, _head_width)
                if model_material_loc >= 0:
                    model_mat = Tmatrix()
                    _scale = 1.0 / max(_len, _head_width)
                    model_mat.translate(Vector([(_len - _head_length) * _scale,
                                                0.5, 0.5]))
                    model_mat.scale(Vector([_head_length, _head_width,
                                            _head_width]) * _scale)
                    mat.get_shader_program().\
                        set_uniform_matrix(scene, model_material_loc,
                                           model_mat)
                scene.pyramid_model.gl_render()
                gl.glScaled(1 / _head_length, 1 / _head_width, 1 / _head_width)
                gl.glTranslated(-_len + _head_length, 0, 0)
        gl.glPopMatrix()

    def init_model(self, scene):
        """Add the arrow head and shaft to the scene.

        :param scene: The view to render the model into.
        :type scene: pyglet_helper.objects.View
        """
        if not scene.box_model.compiled:
            self.box = Box()
            self.box.init_model(scene)
        if not scene.pyramid_model.compiled:
            self.pyramid = Pyramid()
            self.pyramid.init_model(scene)

    def effective_geometry(self, gcf):
        """Initializes these four variables with the effective geometry for the
        arrow.  The resulting geometry is scaled to view space, but oriented
        and positioned in model space.  The only required transforms are
        reorientation and translation.

        :param gcf: The scaling factor
        :type gcf: float
        """
        # First calculate the actual geometry based on the specs for headwidth,
        # shaftwidth, shaftlength, and fixedwidth.  This geometry is calculated
        # in world space and multiplied
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
