# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *

''' A helper class to manage OpenGL color attributes.  The data is layout
	compatable with OpenGL's needs for the various vector forms of commands,
	like glColor4fv(), and glColorPointer().
'''


class Rgba(object):
    def __init__(self, red=1.0, green=1.0, blue=1.0, opacity=1.0, c=None):
        if c is not None:
            if len(c) == 4:
                self.red = c[0]
                self.green = c[1]
                self.blue = c[2]
                self.opacity = c[3]
            else:
                raise ValueError("RGBA color vector must be of length 4!")
        else:
            self.red = red
            self.green = green
            self.blue = blue
            self.opacity = opacity

    def desaturate(self):
        """ Convert to HSVA, lower saturation by 50%, convert back to RGBA.
            @return The desaturated color.
        """
        ret = rgb(red=self.red, green=self.green, blue=self.blue).desaturate()
        return rgba(red=ret.red, green=ret.green, blue=ret.blue, opacity=self.opacity)

    def grayscale(self):
        """ Convert to greyscale, accounting for differences in perception.  This
            function makes 4 calls to pow(), and is very slow.
            @return The scaled color.
        """
        ret = rgb(red=self.red, green=self.green, blue=self.blue).grayscale()
        return rgba(red=ret.red, green=ret.green, blue=ret.blue, opacity=self.opacity)

    def gl_set(self):
        """
         Make this the active OpenGL color using glColor().
        """
        color = (GLfloat * 4)(*[self.red, self.green, self.blue, self.opacity])
        glColor4fv(color)


class Rgb:
    def __init__(self, red=1.0, green=1.0, blue=1.0, c=None):
        if c is not None:
            if len(c) == 3:
                self.red = c[0]
                self.green = c[1]
                self.blue = c[2]
            else:
                raise ValueError("RGB color vector must be of length 4!")
        else:
            self.red = red
            self.green = green
            self.blue = blue

    def __str__(self):
        return "color: r" + str(self.red) + " b" + str(self.blue) + " g" + str(self.green)

    def __getitem__(self, item):
        if item == 0:
            return self.red
        elif item == 1:
            return self.green
        elif item == 2:
            return self.blue
        else:
            raise ValueError("no such component")

    @property
    def rgb(self):
        return [self.red, self.green, self.blue]

    @rgb.setter
    def rgb(self, bw):
        self = rgb(red=bw, green=bw, blue=bw)

    def desaturate(self):
        saturation = 0.5  # cut the saturation by this factor

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
        v = cmax  # v
        delta = cmax - cmin

        if cmin == cmax:  # completely unsaturated color is some gray
            # if r = g = b = 0, s = 0, v in principle undefined but set to 0
            s = 0.0
            h = 0.0
        else:
            s = delta / cmax  # s
            if self.red == cmax:
                h = (self.green - self.blue) / delta  # between yellow & magenta
            elif self.green == cmax:
                h = 2.0 + (self.blue - self.red) / delta  # between cyan & yellow
            else:
                h = 4.0 + (self.red - self.green) / delta  # between magenta & cyan

            if h < 0.0:
                h += 6.0  # make it 0 <= h < 6

        # unsaturate somewhat to make sure both eyes have something to see
        s *= saturation
        ret = Rgb()
        if s == 0.0:
            # achromatic (grey)
            ret.red = ret.green = ret.blue = v
        else:
            i = int(h)  # h represents sector 0 to 5
            f = h - i  # fractional part of h
            p = v * (1.0 - s)
            q = v * (1.0 - s * f)
            t = v * (1.0 - s * (1.0 - f))

            if i == 0:
                ret.red = v
                ret.green = t
                ret.blue = p
            elif i == 1:
                ret.red = q
                ret.green = v
                ret.blue = p
            elif i == 2:
                ret.red = p
                ret.green = v
                ret.blue = t
            elif i == 3:
                ret.red = p
                ret.green = q
                ret.blue = v
            elif i == 4:
                ret.red = t
                ret.green = p
                ret.blue = v
            else:  # case 5:
                ret.red = v
                ret.green = p
                ret.blue = q
        return ret

    def grayscale(self):
        # The constants 0.299, 0.587, and 0.114 are intended to account for the
        # relative intensity of each color to the human eye.
        gamma = 2.5
        black = pow(0.299 * pow(self.red, gamma) + 0.587 * pow(self.green, gamma)
                    + 0.114 * pow(self.blue, gamma), 1.0 / gamma)
        return rgb(red=black, green=black, blue=black)

    def gl_set(self, opacity):

        # glColor4f(self.red, self.green, self.blue, opacity)

        color = (GLfloat * 4)(*[self.red, self.green, self.blue, opacity])
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, color)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)
