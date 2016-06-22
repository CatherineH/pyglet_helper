from ctypes import c_float, c_long


def make_pointer(index, component, data_type=c_float):
    """
    Return a ctypes pointer of the positions or the colors
    :param index: the starting point
    :return:
    """
    _list = []
    for i in range(index, len(component)):
        if hasattr(component[i], "__len__"):
            for j in range(0, len(component[i])):
                if data_type == c_float:
                    _list.append(float(component[i][j]))
                elif data_type == c_long:
                    _list.append(int(component[i][j]))
        else:
            if data_type == c_float:
                try:
                    _list.append(float(component[i]))
                except TypeError as e:
                    print(component[i], type(component[i]))
            elif data_type == c_long:
                _list.append(int(component[i]))
    return (data_type * len(_list))(*_list)