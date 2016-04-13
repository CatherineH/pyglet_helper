""" pyglet_helper.sphere contains an object for drawing a sphere
"""
try:
    import pyglet.gl as gl
except Exception as error_msg:
    gl = None
from pyglet_helper.objects import Axial, Material
from pyglet_helper.util import Quadric, Rgb, Tmatrix, Vector


class Sphere(Axial):
    """
    A Sphere object
    """
    def __init__(self, color=Rgb(), pos=Vector([0, 0, 0]),
                 axis=Vector([1.0, 0.0, 0.0]), radius=1.0,
                 material=Material(), other=None):
        """
        :param radius: The sphere's radius.
        :type radius: float
        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param pos: The object's position.
        :type pos: pyglet_helper.util.Vector
        :param axis: The cone points from the base to the point along the axis.
        :type axis: pyglet_helper.util.Vector
        :param material: The object's material
        :type material: pyglet_helper.util.Material
        :param other: another sphere object to copy properties from (optional)
        :type other: pyglet_helper.objects.Sphere
        """
        super(Sphere, self).__init__(color=color, pos=pos, radius=radius,
                                     material=material, axis=axis)
        # Construct a unit sphere at the origin.
        if other is not None:
            self.axial = other
        self.compiled = False

    @property
    def scale(self):
        """ Exposed for the benefit of the ellipsoid object, which overrides it.
         The default is to use <radius, radius, radius> for the scale.
        """
        return Vector([self.radius, self.radius, self.radius])

    @property
    def material_matrix(self):
        """
        Creates a transformation matrix for spherical objects
        :return: the transformation matrix
        :rtype: pyglet_helper.util.Tmatrix
        """
        out = Tmatrix()
        out.translate(Vector([.5, .5, .5]))
        scale = self.scale
        out.scale(scale * (.5 / max(scale.x_component, max(scale.y_component,
                                                           scale.z_component))))
        return out

    @property
    def degenerate(self):
        """ Returns true if this object should not be drawn.  Conditions are:
        zero radius, or visible is false.  (overridden by the ellipsoid class).
        """
        return self.radius == 0.0

    def init_model(self, scene):
        """ Add the sphere quadrics to the View

        :param scene: The view to render the model to.
        :type scene: pyglet_helper.objects.View
        """
        sph = Quadric()

        scene.sphere_model[0].gl_compile_begin()
        sph.render_sphere(1.0, 13, 7)
        scene.sphere_model[0].gl_compile_end()

        scene.sphere_model[1].gl_compile_begin()
        sph.render_sphere(1.0, 19, 11)
        scene.sphere_model[1].gl_compile_end()

        scene.sphere_model[2].gl_compile_begin()
        sph.render_sphere(1.0, 35, 19)
        scene.sphere_model[2].gl_compile_end()

        scene.sphere_model[3].gl_compile_begin()
        sph.render_sphere(1.0, 55, 29)
        scene.sphere_model[3].gl_compile_end()

        scene.sphere_model[4].gl_compile_begin()
        sph.render_sphere(1.0, 70, 34)
        scene.sphere_model[4].gl_compile_end()

        # Only for the very largest bodies.
        scene.sphere_model[5].gl_compile_begin()
        sph.render_sphere(1.0, 140, 69)
        scene.sphere_model[5].gl_compile_end()

    def render(self, geometry):
        """ Add the sphere to the view.

        :param scene: The view to render the model into
        :type scene: pyglet_helper.objects.View
        """
        # Renders a simple sphere with the #2 level of detail.
        if self.radius == 0.0:
            return
        self.init_model(geometry)

        coverage_levels = [30, 100, 500, 5000]
        lod = self.lod_adjust(geometry, coverage_levels, self.pos, self.radius)
        gl.glPushMatrix()

        self.model_world_transform(geometry.gcf, self.scale).gl_mult()
        self.color.gl_set(self.opacity)

        if self.translucent:
            # Spheres are convex, so we don't need to sort
            gl.glEnable(gl.GL_CULL_FACE)

            # Render the back half (inside)
            gl.glCullFace(gl.GL_FRONT)
            geometry.sphere_model[lod].gl_render()

            # Render the front half (outside)
            gl.glCullFace(gl.GL_BACK)
            geometry.sphere_model[lod].gl_render()
        else:
            # Render a simple sphere.
            geometry.sphere_model[lod].gl_render()
        gl.glPopMatrix()
