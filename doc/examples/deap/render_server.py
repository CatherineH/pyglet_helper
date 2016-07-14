
from pyglet import window
from pyglet import image
from pyglet.clock import schedule, schedule_interval
from pyglet.app import run, exit
import pyglet_helper.objects as pho
import pyglet_helper.util.color as phc
from pyglet_helper.util import Vector
from PIL import Image
from os import listdir, remove, stat
from os.path import join
import pickle

TARGET_FILENAME = "pyglet_helper_generated.png"
state = 0
_filename = None

def update(dt):
    global scene
    global state
    global _filename
    if (state == 0):
        _filename = None
        # get all of the unrendered files
        for _file in listdir('to_render'):
            _file_size = stat(join('to_render', _file)).st_size
            if _file.find(".pickle") > 0 and _file_size > 0:
                _filename = _file
                break
        if _filename is None:
            return
        _filename = join('to_render', _filename)
        scene.screen_objects = []
        print("Rendering "+_filename)
        try:
            objects = pickle.load(open(_filename, "rb"))
            for object in objects:
                _pos = Vector([object['op']['x'], object['op']['y'], 0])
                _color = getattr(phc, object['op']['color'])
                _size = Vector([object['op']['s'],object['op']['s'],object['op'][
                    's']])
                _object = getattr(pho, object['op']['primitive'])(pos=_pos,
                                                                  color=_color,
                                                                  size=_size)
                scene.screen_objects.append(_object)
            state = 1
            remove(_filename)
            print("Done with: "+_filename)
        except OSError:
            print("waiting on "+_filename)
    elif state == 2:
        _out_filename = _filename.replace("pickle", "png")
        image.get_buffer_manager().get_color_buffer().save(_out_filename)
        state = 0

if __name__ == "__main__":
    size = Image.open(TARGET_FILENAME).size
    window = window.Window(width=size[0], height=size[1])


    @window.event
    def on_draw():
        global scene
        global state
        scene.setup()
        if state == 1:
            state = 2
    scene = pho.View(view_height=window.height, view_width=window.width)
    schedule_interval(update, 1)
    _light0 = pho.Light(position=(1, 0.5, 1, 0), specular=(.5, .5, 1, 0.5))
    _light1 = pho.Light(position=(1, 0, .5, 0), specular=(.5, .5, .5, 1))
    scene.lights.append(_light0)
    scene.lights.append(_light1)

    run()