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

#dt = 0.01



def setup(scene=None):
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

    GLOBAL_VIEW.draw_lights()


def vrun(update):
    schedule(update)
    run()