# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
import sys
import os

filename = os.path.dirname(os.path.realpath(__file__))
filename = filename.replace("objects", "")
sys.path.append(filename)


from util.vector import vector
from objects.renderable import renderable

from enum import Enum

#'buttonstate' contains the following state flags as defined by 'button'.
class modifiers_t(Enum):
    shift = 1
    ctrl = 2
    alt = 3
    command = 4

#'eventtype' contains state flags as defined by 'event'.
class event_t(Enum):
    press = 1
    release = 2
    click = 3
    drag = 4
    drop = 5

class button_t(Enum):
    none = 0
    left = 1
    right = 2
    middle = 3


'''
 This common base class implements common functionality for event and mouse.
 It should never be used directly.
'''
class mousebase:
    def __init__(self):
        self.button_name = ''
        self.modifiers = [False]*4
        self.eventtype = [False]*5
        self.buttons = [False]*3
        # The position of the mouse, either currently, or when the even happened.
        self.position = vector()
        # The position of the camera in the scene.
        self.cam = vector()
        # The object nearest to the cursor when this event happened.
        self.pick = renderable()
        # The position on the object that intersects with ray.
        self.pickpos = vector()


    @property
    def press(self):
        return eventtype.test( self.press)
    @press.setter
    def press( self, _press) :
        eventtype.set( self.press, _press)

    @property
    def release(self):
        return eventtype.test( self.release)
    @release.setter
    def release( self, _release) :
        return eventtype.set( self.release, _release)

    @property
    def click(self) :
        return eventtype.test( self.click)
    @click.setter
    def click(self, _click) :
        eventtype.set( self.click, _click)

    @property
    def drag(self) :
        return eventtype.test( self.drag)
    @drag.setter
    def drag(self, _drag) :
        eventtype.set( self.drag, _drag)

    @property
    def drop(self) :
        return eventtype.test( self.drop)
    @drop.setter
    def set_drop(self, _drop) :
        eventtype.set( self.drop, _drop)

    def get_buttons(self) :
        if (self.buttons.test( self.left)):
            return ( "left")
        elif (self.buttons.test( self.right)):
            return ( "right")
        elif (self.buttons.test( self.middle)):
            return ( "middle")
        else:
            return 0
    @property
    def shift(self)  :
        return modifiers.test( shift)
    @shift.setter
    def shift(self, _shift):
        modifiers.set( self.shift, _shift)

    @property
    def ctrl(self)  :
        return modifiers.test( self.ctrl)
    @ctrl.setter
    def ctrl( self, _ctrl) :
        modifiers.set( self.ctrl, _ctrl)

    @property
    def alt(self)  :
        return modifiers.test( self.alt)  # option on Mac keyboard
    @alt.setter
    def alt(self, _alt):
        modifiers.set( self.alt,  _alt)  # option on Mac keyboard

    @property
    def command(self)  :
        return modifiers.test( self.command)
    @command.setter
    def command( self, _command) :
        modifiers.set( self.command,  _command)

    def get_camera(self)  :
        return self.cam
    def get_ray(self)  :
        return (self.position - self.cam).norm(self)
    def get_pickpos(self)  :
        return pickpos

    def get_pos(self) :
        return self.position

    def leftdown(self, _ld) :
        self.buttons.set( self.left, _ld)

    def rightdown(self, _rd) :
        self.buttons.set( self.right, _rd)

    def middledown(self, _md) :
        self.buttons.set( self.middle, _md)


    def project1(self, normal, dist):
        ndc = normal.dot(self.cam) - dist
        ndr = normal.dot(self.get_ray())
        t = -ndc / ndr
        v = self.cam + self.get_ray()*t
        return v

    def project2(self, normal, point = vector(0,0,0)):
        dist = normal.dot(point)
        ndc = normal.dot(cam) - dist
        ndr = normal.dot(get_ray())
        t = -ndc / ndr
        v = cam + get_ray()*t
        return v

'''
 Objects of this class represent the state of the mouse at a distinct event:
 either press, release, click, drag, or drop.
'''
#class event(mousebase):
#    event():



'''
 A class exported to python as the single object display.mouse.
 All of the python access for data within this class get the present value of
 the data.
'''
class mouse_t(mousebase):
    def __init__(self, click_count = 0):
        self.events = atomic_queue()
        self.click_count = click_count# number of queued events which are left clicks

    # The following member functions are synchronized - no additional locking
    # is requred.
    def num_events(self):
        return self.events.size()
    def clear_events(self):
        self.events.clear()
        return
    def num_clicks(self):
        return self.click_count
    # Exposed as the function display.mouse.getevent()
    def pop_event(self):
        # In VPython 5.x, the while loop was interrupted by the render thread
        # In VPython 6.x, the while loop needs a wait statement to get events
        ret = event()
        while (True):
            if (self.events.size() > 0) :
                ret = self.events.pop()
                if (ret.is_click()) :
                    click_count-=1
                return ret
            call_wait()
    # Exposed as the function mouse.getclick()
    def pop_click(self):
        # In VPython 5.x, the while loop was interrupted by the render thread
        # In VPython 6.x, the while loop needs a wait statement to get events
        ret = event()
        while (True) :
            while (self.events.size() > 0) :
                ret = self.events.pop()
                if (ret.is_click()) :
                    click_count -= 1
                    return ret
            call_wait()

    # Exposed as the function mouse.peekevent()
    def peek_event(self):
        ret = self.events.peek()
        return ret

    # Push a new event onto the queue.  This function is not exposed to Python.
    def push_event( self, e):
        if (e.is_click()):
            click_count += 1
        self.events.push( e)


# Convenience functions for creating event objects.
# which represents which mouse button is involved:
# 1 for left
# 2 for right
# 3 for middle
# no other number is valid.
def init_event( self, _which, ret, mouse):
    ret.position = mouse.position
    ret.pick = mouse.pick
    ret.pickpos = mouse.pickpos
    ret.cam = mouse.cam
    ret.set_shift( mouse.is_shift())
    ret.set_ctrl( mouse.is_ctrl())
    ret.set_alt( mouse.is_alt())
    ret.set_command( mouse.is_command())
    if _which == 1 :
        ret.set_leftdown( True)
    elif _which == 2:
        ret.set_rightdown( True)
    elif _which == 3:
        ret.set_middledown( True)
    else:
        button_is_known = False
        assert( button_is_known == True)

def press_event(self, _which, mouse):
    ret = event()
    ret.set_press( True)
    init_event( _which, ret, mouse)
    return ret

def drop_event(self, _which, mouse):
    ret = event()
    ret.set_release( True)
    ret.set_drop( True)
    init_event( _which, ret, mouse)
    return ret

def release_event(self, _which, mouse):
    ret = event()
    ret.set_release( True)
    init_event(_which, ret, mouse)
    return ret

def click_event(self, _which, mouse):
    ret = event()
    ret.set_release( True)
    ret.set_click( True)
    init_event( _which, ret, mouse)
    return ret

def drag_event(self, _which, mouse):
    ret = event()
    ret.set_drag( True)
    init_event( _which, ret, mouse)
    return ret


# Utility object for tracking mouse press, release, clicks, drags, and drops.
class mousebutton:
    def __init__(self, down = False, dragging = False, last_down_x = -1.0, \
     last_down_y = -1.0):
        self.down = down
        self.dragging = dragging
        self.last_down_x = last_down_x
        self.last_down_y = last_down_y

    # When the button is pressed, call this function with its screen
    # coordinate position.  It returns true if this is a unique event
    def press(self, x, y):
        if (self.down) :
            return False

        self.down = True
        self.last_down_x = x
        self.last_down_y = y
        self.dragging = False
        return True

    # Returns true when a drag event should be generated, false otherwise
    def is_dragging(self):
        if (self.down and not self.dragging) :
            self.dragging = True
            return True
        return False

    # Returns (is_unique, is_drop)
    def release(self):
        unique = self.down
        self.down = False
        self.last_down_x = -1
        self.last_down_y = -1
        return [unique, self.dragging]



'''
 A thin wrapper for buffering cursor visibility information between the python loop
 and the rendering loop.
'''
class cursor_object:
    def __init__(self, visible = True, last_visible = True):
        self.visible = visible # whether cursor should be visible
        self.last_visible = last_visible # previous state of cursor visibility

    @property
    def visible(self):
        return self.visible
    @visible.setter
    def visible( self, vis) :
        self.visible = vis
