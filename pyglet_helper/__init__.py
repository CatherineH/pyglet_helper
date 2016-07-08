#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines globally-available subpackages and symbols for the pyglet_helper
package.
"""

from __future__ import absolute_import

GLOBAL_WINDOW = None
GLOBAL_VIEW = None

from . import objects
from . import common
from . import util

from pyglet.app import run
from pyglet.clock import schedule
from math import log
from os import path


try:
    import pyglet.window as window
except Exception as error_msg:
    window = None

__version__ = "0.0.1"
__author__ = "cholloway"

__title__ = "pyglet_helper"
__description__ = "3d modelling library"
__uri__ = "http://catherineh.github.io/pyglet_helper/"


__email__ = "milankie@gmail.com"

__license__ = "AGPLv3"
__copyright__ = "Copyright (c) 2014-2016 Catherine Holloway"


def vsetup(scene=None):
    """
    Initializes the GLOBAL_VIEW and GLOBAL_WINDOW variables. The window is initialized based on the settings in scene.
    If scene is undefined, a GLOBAL_VIEW will be created with default variables.
    :param scene: The scene with the default variables.
    :type scene: pyglet_helper.objects.View
    :return:
    """
    global GLOBAL_WINDOW
    global GLOBAL_VIEW
    # global view must be initialized first, it contains all of the variables that describe the window.
    if scene is not None:
        GLOBAL_VIEW = scene
    else:
        GLOBAL_VIEW = objects.renderable.View()
    GLOBAL_WINDOW = window.Window(width=GLOBAL_VIEW.view_width, height=GLOBAL_VIEW.view_height)

    @GLOBAL_WINDOW.event
    def on_resize(width, height):
        GLOBAL_VIEW.view_width = width
        GLOBAL_VIEW.view_height = height
        return GLOBAL_VIEW.resize()

    @GLOBAL_WINDOW.event
    def on_draw():
        GLOBAL_VIEW.setup()

    @GLOBAL_WINDOW.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        if buttons & window.mouse.RIGHT:
            GLOBAL_VIEW.rotate_camera(dx, dy)
        if buttons & window.mouse.MIDDLE:
            GLOBAL_VIEW.zoom_camera(dy)

    _light0 = objects.light.Light(position=(1, 0.5, 1, 0), specular=(.5, .5, 1, 0.5))
    _light1 = objects.light.Light(position=(1, 0, .5, 0), specular=(.5, .5, .5, 1))
    GLOBAL_VIEW.lights.append(_light0)
    GLOBAL_VIEW.lights.append(_light1)

    GLOBAL_VIEW.draw_lights()
    print("""
    Right button drag or Ctrl-drag to rotate "camera" to view scene.
    Middle button or Alt-drag to drag up or down to zoom in or out.
      On a two-button mouse, middle is left + right.
    """)


class VApp(object):
    try:
        import pyglet.image as image
    except Exception as error_msg:
        image = None
    def __init__(self, update, max_frames=99, render_images=False, interval=1,
                 foldername=None):
        self.update = update
        self.max_frames = max_frames
        self.render_images = render_images
        self.interval = interval
        self.screennum = 0
        if foldername is None:
            self.foldername = path.dirname(__file__)
        else:
            self.foldername = foldername

    def vupdate(self, dt):
        self.update(dt)
        name_width = int(log(self.max_frames)/log(10))
        format_str = 'screenshot%0'+str(name_width)+'d.png'
        if self.screennum < self.max_frames*self.interval and self.render_images:
            if self.screennum % self.interval == 0:
                filename = path.join(self.foldername, format_str % (self.screennum/self.interval, ))
                self.image.get_buffer_manager().get_color_buffer().save(filename)
            self.screennum += 1


def vrun(update, max_frames=99, render_images=False, interval=1, foldername=None):
    _vapp = VApp(update, max_frames, render_images, interval, foldername)
    schedule(_vapp.vupdate)
    run()