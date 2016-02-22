from pyglet.gl import GLfloat
from pyglet_helper.objects import Renderable
from pyglet_helper.util import Rgb, Vector
import abc


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
        self.specular = (GLfloat * 4)(*specular)
        self.diffuse = (GLfloat * 4)(*diffuse)
        self.position = (GLfloat * 4)(*position)

    @property
    def rgb(self):
        return self.color

    @rgb.setter
    def rgb(self, r):
        self.color = r

    @property
    def center(self):
        return Vector()

    @property
    def material(self):
        raise ValueError("light object does not have a material.")

    @material.setter
    def material(self, mat):
        raise ValueError("light object does not have a material.")

    @property
    def is_light(self):
        return True

    def render(self, scene):
        """ Add the light to the scene.
        :param scene: The view to render the model into
        :type scene: pyglet_helper.objects.View
        """
        scene.lights.append(self)
        scene.draw_lights()

    @abc.abstractmethod
    def get_vertex(self):
        return 0
