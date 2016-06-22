try:
    from pyglet.gl import gl
except Exception as error_msg:
    gl = None

from pyglet_helper.util import RED, Rgb


class ArrayPrimitive(object):
    def __init__(self):
        self.pos = []
        self.color = self.color_template()

    @property
    def count(self):
        return len(self.pos)

    class color_template(object):
        def __init__(self):
            self._data = []

        def append(self, value):
            self._data.append(value)

        def __setitem__(self, key, value):
            self.fill(key)
            self._data[key] = value

        def __getitem__(self, key):
            self.fill(key)
            return self._data[key]

        def fill(self, key):
            if key+1 > len(self._data):
                if len(self._data) == 0:
                    self._data.append(RED)
                for i in range(len(self._data), key+1):
                    self._data.append(self._data[-1])

    def append(self, pos, col=None, retain=-1):
        """
        Add a new position to the ArrayPrimitive
        :param new_pos:
        :param retain:
        :return:
        """
        if retain > 0 and self.count >= (retain - 1):
            self.length = retain - 1  # shifts arrays
        elif retain == 0:
            self.pos = []
            self.color = []
        if col is not None:
            self.color.append(col)
        elif self.count > 0:
            self.color.append(self.color[-1])
        else:
            # default color is red
            self.color.append(RED)
        self.pos.append(pos)

    def __str__(self):
        output = ""
        for i in range(self.count):
            output += "("+str(self.pos[i].x_component)+", "+str(self.pos[i].y_component)\
                      + ", " + str(self.pos[i].z_component) + ")"
            if i == self.count-1:
                output += ","
        return output




