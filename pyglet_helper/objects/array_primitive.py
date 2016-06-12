try:
    from pyglet.gl import gl
except Exception as error_msg:
    gl = None

from pyglet_helper.util import RED



class ArrayPrimitive(object):
    def __init__(self):
        self.pos = []
        self.color = []

    @property
    def count(self):
        return len(self.pos)


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




