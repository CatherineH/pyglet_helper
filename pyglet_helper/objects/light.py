""" pyglet_helper.light contains an object for creating lights
"""
try:
    import pyglet.gl as gl
except Exception as error_msg:
    gl = None
from pyglet_helper.objects import Renderable
from pyglet_helper.util import Rgb, Vector


class Light(Renderable):
    """
    A light object
    """
    def __init__(self, color=Rgb(), specular=(.5, .5, 1, 0.5),
                 diffuse=(1, 1, 1, 1), position=(1, 0.5, 1, 0)):
        """

        :param color: The object's color.
        :type color: pyglet_helper.util.Rgb
        :param specular: The color of the specular reflections on the objects
        in the scene.
        :type specular: array_like
        :param diffuse: The color of the diffuse reflections of the objects in
        the scene.
        :type position: array_like
        :param position: The object's position.
        :type position: array_like
        """
        super(Light, self).__init__(color=color)
        self.color = None
        self.rgb = color
        self.specular = (gl.GLfloat * 4)(*specular)
        self.diffuse = (gl.GLfloat * 4)(*diffuse)
        self.position = (gl.GLfloat * 4)(*position)

    @property
    def rgb(self):
        """
        Gets the light's color
        :return: the light's color
        :rtype: pyglet_helper.util.rgb
        """
        return self.color

    @rgb.setter
    def rgb(self, new_color):
        """
        Sets the light's color
        :param new_color: the new light color
        :type new_color: pyglet_helper.util.Rgb
        :return:
        """
        self.color = new_color

    @property
    def center(self):
        """
        Gets the light's center. Since the light is not a physical object,
        this will always be an empty vector
        :return: the light's center
        :rtype: pyglet_helper.util.Vector
        """
        return Vector()

    @property
    def material(self):
        """
        Though the Renderable object that Light inherits from has a
        material, the Light object does not. Will raise an exception if set
        or gotten.
        :return:
        """
        raise ValueError("light object does not have a material.")

    @material.setter
    def material(self, material):
        """
        Though the Renderable object that Light inherits from has a
        material, the Light object does not. Will raise an exception if set
        or gotten.
        :return:
        """
        _ = material
        raise ValueError("light object does not have a material.")

    @property
    def is_light(self):
        """
        Returns true if the parent object is a light
        :return: bool
        """
        return True

    def render(self, scene):
        """ Add the light to the scene.
        :param scene: The view to render the model into
        :type scene: pyglet_helper.objects.View
        """
        scene.lights.append(self)
        scene.draw_lights()

