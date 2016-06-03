from pyglet_helper.objects import Renderable
from pyglet_helper.util import Rgb
from numpy import array


class ArrayPrimitiveArray(array):
    def __init__(self, in_array=list(), allocated=256):
        super(ArrayPrimitiveArray, self).__init__(in_array)
        self._length = None
        self.length = self.size
        self.allocated = allocated

    def data(self, index):
        return self[index]

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, new_val):
        self._length = new_val

    def end(self):
        return self[-1]


class ArrayPrimitive(Renderable):
    def __init__(self, count=0):
        super(ArrayPrimitive, self).__init__()
        self.pos = ArrayPrimitiveArray([0, 0, 0])
        self.all = slice(0, count)

    @property
    def count(self):
        return self.all.stop


class ColorArrayPrimitive(ArrayPrimitive):
    def __init__(self, color=Rgb()):
        super(ColorArrayPrimitive, self).__init__()
        self.color = color

