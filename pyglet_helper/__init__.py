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
    try:
        import pyglet.window as window
    except Exception as error_msg:
        window = None
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

    _light0 = objects.light.Light(position=(1, 0.5, 1, 0), specular=(.5, .5, 1, 0.5))
    _light1 = objects.light.Light(position=(1, 0, .5, 0), specular=(.5, .5, .5, 1))
    GLOBAL_VIEW.lights.append(_light0)
    GLOBAL_VIEW.lights.append(_light1)

    GLOBAL_VIEW.draw_lights()

class VApp(object):
    try:
        import pyglet.image as image
    except Exception as error_msg:
        image = None
    def __init__(self, update, max_frames=99, render_images=False):
        self.update = update
        self.max_frames = max_frames
        self.render_images = render_images
        self.screennum = 0

    def vupdate(self, dt):
        import os
        self.update(dt)
        if self.screennum < self.max_frames and self.render_images:
            path = os.path.dirname(__file__)
            filename = os.path.join(path, 'screenshot%02d.png' % (self.screennum, ))
            self.image.get_buffer_manager().get_color_buffer().save(filename)
            self.screennum += 1


def vrun(update, max_frames=99, render_images=False):
    _vapp = VApp(update, max_frames, render_images)
    schedule(_vapp.vupdate)
    run()