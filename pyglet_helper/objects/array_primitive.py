class ArrayPrimitive(object):
    def __init__(self):
        self.pos = []
        self.color = []

    @property
    def count(self):
        return len(self.pos)

    def append(self, pos, retain=-1):
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
        self.pos.append(pos)




