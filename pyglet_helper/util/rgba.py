"""
pyglet_helper.util.rgba contains object to describe colors
"""
try:
    import pyglet.gl as gl
except Exception as error_msg:
    gl = None


class Rgba(object):
    """
    Defines a color to be used by OpenGl, including RGB and opacity.
    """
    def __init__(self, red=1.0, green=1.0, blue=1.0, opacity=1.0, color=None):
        """
        :param red: The red value of the color, value between 0 and 1
        :type red: float
        :param green: The green value of the color, value between 0 and 1
        :type green: float
        :param blue: The blue value of the color, value between 0 and 1
        :type blue: float
        :param opacity: The opacity value of the color, value between 0 and 1
        :type opacity: float
        :param c: A list of values to copy into a new color
        :type c: list
        """
        if color is not None:
            if len(color) == 4:
                for i in range(4):
                    self[i] = color[i]
            else:
                raise ValueError("RGBA color vector must be of length 4!")
        else:
            self.red = red
            self.green = green
            self.blue = blue
            self.opacity = opacity

    def __getitem__(self, item):
        if item == 0:
            return self.red
        elif item == 1:
            return self.green
        elif item == 2:
            return self.blue
        elif item == 3:
            return self.opacity
        else:
            raise ValueError("no such component")

    def __setitem__(self, item, value):
        if item == 0:
            self.red = value
        elif item == 1:
            self.green = value
        elif item == 2:
            self.blue = value
        elif item == 3:
            self.opacity = value
        else:
            raise ValueError("no such component")

    def __str__(self):
        return "color: r" + str(self.red) + " g" + str(self.green) + " b" + \
               str(self.blue) + " o"+str(self.opacity)

    def desaturate(self):
        """ Return a desaturated version of the color

        :rtype: pyglet_helper.util.Rgba
        :return: the desaturized color.
        """
        ret = Rgb(red=self.red, green=self.green, blue=self.blue).desaturate()
        return Rgba(red=ret.red, green=ret.green, blue=ret.blue,
                    opacity=self.opacity)

    def grayscale(self):
        """ Return a version of the color projected onto a grayscale space

        :return: the color, projected onto grayscale.
        :rtype: pyglet_helper.util.Rgba()
        """
        ret = Rgb(red=self.red, green=self.green, blue=self.blue).grayscale()
        return Rgba(red=ret.red, green=ret.green, blue=ret.blue,
                    opacity=self.opacity)

    def gl_set(self):
        """
        Set this color to the current material in OpenGL.
        """
        color = (gl.GLfloat * 4)(*[self.red, self.green, self.blue,
                                   self.opacity])
        gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, color)
        gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_SPECULAR, color)
        gl.glMaterialf(gl.GL_FRONT_AND_BACK, gl.GL_SHININESS, 50)


class Rgb(object):
    """
    Define an RGB color to be used by OpenGl
    """
    def __init__(self, red=1.0, green=1.0, blue=1.0, color=None):
        """
        :param red: The red value of the color, value between 0 and 1
        :type red: float
        :param green: The green value of the color, value between 0 and 1
        :type green: float
        :param blue: The blue value of the color, value between 0 and 1
        :type blue: float
        :param color: A list of values to copy into a new color
        :type color: list
        """
        if color is not None:
            if len(color) == 3:
                for i in range(3):
                    self[i] = color[i]
            else:
                raise ValueError("RGB color vector must be of length 4!")
        else:
            self.red = red
            self.green = green
            self.blue = blue

    def __str__(self):
        return "color: r" + str(self.red) + " g" + str(self.green) \
               + " b" + str(self.blue)

    def __getitem__(self, item):
        if item == 0:
            return self.red
        elif item == 1:
            return self.green
        elif item == 2:
            return self.blue
        else:
            raise ValueError("no such component")

    def __setitem__(self, item, value):
        if item == 0:
            self.red = value
        elif item == 1:
            self.green = value
        elif item == 2:
            self.blue = value
        else:
            raise ValueError("no such component")

    @property
    def rgb(self):
        """
        Get a tuple with the three components of the rgba color
        :return: (red, green, blue)
        :rtype: tuple
        """
        return (self.red, self.green, self.blue)

    @rgb.setter
    def rgb(self, grayscale):
        """
        Set the current rgb color to a grayscale value
        :param grayscale: the grayscale value'
        :type grayscale: float
        """
        self.red = grayscale
        self.green = grayscale
        self.blue = grayscale

    def desaturate(self):
        """ Convert the color to HSV space, reduce the saturation by a factor
        of 0.5, then convert back to RGB space

        :rtype: pyglet_helper.util.Rgb()
        :return: the desaturated color.
        """
        cut_saturation = 0.5  # cut the saturation by this factor

        # r,g,b values are from 0 to 1
        # h = [0,360], s = [0,1], v = [0,1]
        # if s == 0, then arbitrarily set h = 0

        cmin = self.red
        if self.green < cmin:
            cmin = self.green
        if self.blue < cmin:
            cmin = self.blue

        cmax = self.red
        if self.green > cmax:
            cmax = self.green
        if self.blue > cmax:
            cmax = self.blue
        value = cmax  # v
        delta = cmax - cmin

        if cmin == cmax:  # completely unsaturated color is some gray
            # if r = g = b = 0, s = 0, v in principle undefined but set to 0
            saturation = 0.0
            hue = 0.0
        else:
            saturation = delta / cmax  # s
            if self.red == cmax:
                # between yellow & magenta
                hue = (self.green - self.blue) / delta
            elif self.green == cmax:
                # between cyan & yellow
                hue = 2.0 + (self.blue - self.red) / delta
            else:
                # between magenta & cyan
                hue = 4.0 + (self.red - self.green) / delta

            if hue < 0.0:
                hue += 6.0  # make it 0 <= h < 6

        # unsaturate somewhat to make sure both eyes have something to see
        saturation *= cut_saturation
        ret = Rgb()
        if saturation == 0.0:
            # achromatic (grey)
            ret.red = ret.green = ret.blue = value
        else:
            i = int(hue)  # hue represents sector 0 to 5
            fraction = hue - i  # fractional part of hue
            p_vandam = value * (1.0 - saturation)
            q_vandam = value * (1.0 - saturation * fraction)
            t_vandam = value * (1.0 - saturation * (1.0 - fraction))

            if i == 0:
                ret.red = value
                ret.green = t_vandam
                ret.blue = p_vandam
            elif i == 1:
                ret.red = q_vandam
                ret.green = value
                ret.blue = p_vandam
            elif i == 2:
                ret.red = p_vandam
                ret.green = value
                ret.blue = t_vandam
            elif i == 3:
                ret.red = p_vandam
                ret.green = q_vandam
                ret.blue = value
            elif i == 4:
                ret.red = t_vandam
                ret.green = p_vandam
                ret.blue = value
            else:  # case 5:
                ret.red = value
                ret.green = p_vandam
                ret.blue = q_vandam
        return ret

    def grayscale(self):
        """ Convert the color to grayscale

        :return: the color, projected onto grayscale.
        :rtype: pyglet_helper.util.Rgb()
        """
        # The constants 0.299, 0.587, and 0.114 are intended to account for the
        # relative intensity of each color to the human eye.
        gamma = 2.5
        black = pow(0.299 * pow(self.red, gamma) + 0.587 * pow(self.green,
                                                               gamma)
                    + 0.114 * pow(self.blue, gamma), 1.0 / gamma)
        return Rgb(red=black, green=black, blue=black)

    def gl_set(self, opacity=1.0):
        """ Set the current material to this color

        :param opacity: the opacity value of the color
        :type opacity: float
        """
        color = (gl.GLfloat * 4)(*[self.red, self.green, self.blue, opacity])
        gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, color)
        gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_SPECULAR, color)
        gl.glMaterialf(gl.GL_FRONT_AND_BACK, gl.GL_SHININESS, 50)
