from __future__ import print_function

# Note that Python variables starting with "_" are not accessible to the importing program,
# so variables intended to be private in this module start with "_"

import os as _os
import sys as _sys
import time as _time
import numpy as _numpy
import atexit as _atexit
from inspect import getargspec
import pyglet
from pyglet.canvas.base import Display
from pyglet.window import Window
import platform

from display_kernel import display_kernel
from material import diffuse
from light import distant_light

def wait(*args): # called by mouseobject.cpp/pop_click, which is called by scene.mouse.getclick()
    _Interact()
    if len(args) == 0: return
    elif len(args) == 1: _time.sleep(args[0])
    else: raise ValueError("Too many arguments for the wait() function.")

_App = pyglet.app

_plat = platform.system()

#it is unnecessary to implement the window class, as it already exists in pyglet.
_window = Window()
_screenwidth = _window.get_size()[0]
_screenheight = _window.get_size()[1]

def exit():
    pyglet.exit()

class _mouseTracker:
    """
    mouseTracker is a simple class that's whole purpose in life is to
    keep track of the physical and logical state of the mouse so the
    display handler can focus on display. It's also easily separately
    testable this way.
    """

    def __init__(self):
        """
        leftDown, rightDown, middleDown are *physical* states
        spinning and zooming are *logical* states that depend
        on history and optional key-states. lastSpinning and
        lastZooming are used to check for the lock state when
        zooming and spinning are initiated.
        """
        self.leftIsDown = self.rightIsDown = self.middleIsDown = 0
        self.lastSpinning = self.lastZooming = 0
        self.macCtrl = 0  # mac ctrl is tricky..

    def macCtrlDown(self):
        self.macCtrl = 1  # we don't always get these ;-(. Only if the window has focus... dang.

    def macCtrlUp(self):
        if self.rightIsDown:
            self.rightUp()

        self.macCtrl = 0

    def leftDown(self):
        self.leftIsDown = 1

    def leftUp(self):
        self.leftIsDown = 0

    def rightDown(self):
        self.rightIsDown = 1

    def rightUp(self):
        self.rightIsDown = 0

    def midDown(self):
        self.middleIsDown = 1

    def midUp(self):
        self.middleIsDown = 0

    def isZooming(self, evt, userzoom=True, userspin=True):
        """
        Check to see if we're zooming. On a three button mouse
        this is done with the middle button. On a two button mouse
        this is done with both left/right buttons pressed simultaneously
        On a one button mouse this is done with the 'alt' key pressed along
        with the left button.
        """
        zooming = 0

        if not userzoom:
            return zooming

        if self.middleIsDown:
            zooming = 1

        elif self.leftIsDown and self.rightIsDown:
            zooming = 1

        elif self.leftIsDown and evt.AltDown():
            zooming = 1

        return zooming

    def isSpinning(self, evt, userzoom=True, userspin=True, zooming=False):
        """
        Check to see if we're spinning. One a two button mouse
        this is done with the right button UNLESS the left
        button is also down. So.. check for zooming first and
        return False if we are. Then check for spinning and
        return accordingly.
        """

        spinning = 0
        if not userspin or zooming or self.isZooming(evt, userzoom, userspin):
            return spinning

        elif self.rightIsDown:
            spinning = 1

        elif self.leftIsDown and evt.CmdDown():
            #
            # For the mac we'll also take "cmd-left-click" to enable spinning
            #
            spinning = 1

        return spinning

    def checkLock(self, spinning, zooming):
        """
        Check to see if spinning and/or zooming has just
        been initiated. If so, return True, otherwise return False.
        """
        result = 0
        if spinning:
            if not self.lastSpinning:
                result = 1
                self.lastSpinning = 1
        else:
            self.lastSpinning = 0

        if zooming:
            if not self.lastZooming:
                result = 1
                self.lastZooming = 1
        else:
            self.lastZooming = 0

        return result

    def __repr__(self):
##      return '<%s lastZoom=%s, lastSpin=%s>' % (
##        self.__class__.__name__, `self.lastZooming`, `self.lastSpinning`)
      return '<%s lastZoom=%s, lastSpin=%s>' % (
        self.__class__.__name__, self.lastZooming, self.lastSpinning)

class binding_enabler(object):
    """
    just here to enable or disable bindings
    """
    def __init__(self, display, namestring, fn=None, enabled=True):
        self.display = display
        self.name = namestring
        self.fn = fn
        self.enabled = enabled

    def start(self):
        """
        try to support multiple events
        """
        if not self.enabled:
            self.enabled = True
            for name in self.name.split():
                self.display._enable_binding(name, self.fn, self.enabled)

    def stop(self):
        """
        try to support multiple events
        """
        if self.enabled:
            self.enabled = False
            for name in self.name.split():
                self.display._enable_binding(name, self.fn, self.enabled)

class eventInfo(object):
    """
    Generic object used to supply event information to event handlers
    in the users code.

    These can hold just about anything:

        obj = eventInfo(x=3, y=4, time=34, .....)

    produces and object with x, y and time attributes set accordingly.

    """
    def __init__(self, **kw):
        self.__dict__.update(kw)

class kb(object):
    def __init__(self):
        self.queue = []

    def pushkey(self, k):
        self.queue.append(k)

    def getkey(self):
        while len(self.queue) == 0:
            rate(30)
        ret = self.queue[0]
        self.queue = self.queue[1:]
        return ret

    def keys_in_queue(self):
        return len(self.queue)

    keys = property(keys_in_queue, None, None)

_legal_event_types = ['mousedown', 'mousemove', 'mouseup', 'click',
                      'keydown', 'keyup', 'char',
                      'redraw', 'draw_complete']

def set_cursor(win, visible):
        if visible:
            if 'phoenix' in _App.PlatformInfo:
                win.SetCursor(_App.Cursor(_App.CURSOR_ARROW)) # Phoenix
            else:
                win.SetCursor(_App.StockCursor(_App.CURSOR_ARROW)) # Classic
        else:
            if 'phoenix' in _App.PlatformInfo:
                win.SetCursor(_App.Cursor(_App.CURSOR_BLANK)) # Phoenix
            else:
                win.SetCursor(_App.StockCursor(_App.CURSOR_BLANK)) # Classic

class cursor(object): # used for both display.cursor.visible and window.cursor.visible
    def __init__(self, win=None, visible=True):
        self.win = win
        self._visible = visible

    def _get_visible(self):
        return self._visible

    def _set_visible(self, visible):
        self._visible = visible
        set_cursor(self.win, visible)

    visible = property(_get_visible, _set_visible)

class display(display_kernel):
    # wrap_display_kernel.cpp makes available to Python, in addition to
    # render_scene, report_mouse_state, and report_mouse_state,
    # the methods report_window_resize, report_view_resize, and pick.

    #I don't understand how
    def __init__(self, **keywords):
        #super(display, self).__init__()
        display_kernel.__init__(self)
        self._window_initialized = False
        self.window = None
        self.menus = False
        self.N = -1
        self._lastx = self._lasty = None # previous mouse position
        self.fillswindow = True # assume canvas fills the window
        self._visible = True
        self._fullscreen = False

        self.material = diffuse
        # If visible is set before width (say), can get error "can't change window".
        # So deal with visible attribute separately.
        v = None
        if 'visible' in keywords:
            self._visible = keywords['visible']
            del keywords['visible']
        if 'fullscreen' in keywords:
            self._fullscreen = keywords['fullscreen']
            del keywords['fullscreen']
        keys = list(keywords.keys())
        keys.sort()
        for kw in keys:
            setattr(self, kw, keywords[kw])
        if v is not None: setattr(self, 'visible', v)
        if 'ambient' not in keywords:
            self.ambient = (0.2,0.2,0.2)
        if self.window is not None:
            self.fillswindow = False
            self.win = self.window.win
            self.panel = self.window.panel

        if self.window is None:
            w = _screenwidth
            h = _screenheight
        else:
            w = self.window.width - self.window.dwidth
            h = self.window.height - self.window.dheight

        if self.window_x > w - 100:
            raise ValueError('display x too near the right edge of the screen')
        if self.window_x + self.window_width < 100:
            raise ValueError('display x too far to the left edge of the screen')
        if self.window_y > h - 100:
            raise ValueError('display y too close to the bottom of the screen')
        if self.window_y + self.window_height < 100:
            raise ValueError('display y too far to the top of the screen')

        if self.window_x + self.window_width > w:
            self.window_width = w - self.window_x
        if self.window_x < 0:
            self.window_width = self.window_x + self.window_width
            self.window_x = 0
        if self.window_y + self.window_height > h:
            self.window_height = h - self.y
        if self.window_y < 0:
            self.window_height = self.window_y + self.window_height
            self.window_y = 0

        self._mt = _mouseTracker()
        self._captured = 0
        self._cursorx = self._cursory = 0

        self.select()

        if 'lights' not in keywords:
            distant_light( direction=(0.22, 0.44, 0.88), color=(0.8,0.8,0.8) )
            distant_light( direction=(-0.88, -0.22, -.44), color=(0.3,0.3,0.3) )

        self._bindings = {}
        self._waiting = []
        self.keyboard = eventInfo()
        self.kb = kb()

    def select(self):
        display_kernel.selected = self

    def waitfor_event(self, evt):
        """
        driven by waitfor
        """
        self.waitfor_event_evt = evt
        self.waiting = False

    def waitfor(self, namestring):
        """
        wait for events listed in namestring, then proceed
        """
        names = namestring.split()
        s = ''
        for name in names:
            if name == 'redraw' or name == 'draw_complete' or name not in _legal_event_types:
                s += name+' or '
        if s != '':
            s = s[:-4]
            raise ValueError('waitfor event type cannot be '+s)
        self.waiting = True
        self.bind(namestring, self.waitfor_event)
        while self.waiting:
            rate(30)
        self.unbind(namestring, self.waitfor_event)
        return self.waitfor_event_evt

    def bind(self, namestring, fn, *args, **kw):
        """
        attach events listed in namestring to function 'fn'
        """
        names = namestring.split()
        enabled = True # start out enabled
        for name in names:
            elist = self._bindings.get(name,[])
            elist.append((enabled, fn, args, kw))  # each entry is a list [enabled, fn]
            self._bindings[name] = elist

        return binding_enabler(self, namestring, fn, enabled)

    def unbind(self, namestring, in_fn=None):
        """
        take a particular function out of binding, or all bindings
        from events in namestring if fn is None.
        """
        for name in namestring.split():
            new_list = []
            if in_fn is not None:
                for enabled, fn, args, kw in self._bindings.get(name,[]):
                    if in_fn != fn:
                        new_list.append((enabled, fn, args, kw))

            if new_list:
                self._bindings[name] = new_list
            else:
                del self._bindings[name]

    def _enable_binding(self, name, in_fn, enable):
        new_list = []
        for enabled, fn, args, kw in self._bindings.get(name,[]):
            if in_fn is fn:
                new_list.append((enable, fn, args, kw))
            else:
                new_list.append((enabled, fn, args, kw))

        self._bindings[name] = new_list

    def _dispatch_event(self, name, evt=None, dargs=None, **kwArgs):
        if evt is not None:
            try:
                evt.event = name  # attempt to set the 'event' property to the name of the event
            except:
                pass

        for enabled, fn, args, kw in self._bindings.get(name,[]):
            if enabled:

                newKW = {}              # potential keyword arguments
                if evt is not None:
                    newArgs = (evt,) + args  # potential positional arguments
                else:
                    newArgs = args

                if dargs is not None:
                    newArgs += dargs   # args comes first... then dargs if not None

                argspec = getargspec(fn) # inspect the bound function and see what it's expecting

                newKW.update(kwArgs)
                if kw is not None:
                    newKW.update(kw)

                applyArgs = []
                if argspec.varargs is not None:
                    applyArgs = newArgs
                else:
                    if argspec.args is not None:
                        applyArgs = newArgs[:len(argspec.args)]

                if argspec.keywords is not None:
                    applyKW = newKW
                else:
                    applyKW = {}  # the keywords to actually apply to the bound function
                    [applyKW.update({name:newKW.get(name)}) for name in argspec.args if name is not 'self' and (name in newKW)] # populate the available keywords

                try:
                    # Not sure how to deal with the complexity of the applyKW dictionary, so ignore for now
                    fn(*applyArgs)
##                    apply(fn, applyArgs, applyKW)  # apply doesn't exist in Python 3
                except:
                    import traceback
                    traceback.print_exc()

    def trigger(self, namestring, *args, **kw):
        """
        trigger arbitrary events with keywords...
        """
        for name in namestring.split():
##            if args:
##                kw.update({'dargs':args})
##            apply(self._dispatch_event, (name,), kw)  # apply doesn't exist in Python 3
            self._dispatch_event(name, args[0])

    def _make_canvas(self, parent):
        x = y = 0
        w = self._width-_dwidth
        h = self._height-_dheight
        if _plat == 'Unix' or _plat == 'Linux':
            y = 0
            h = h
        if self.fillswindow: # the canvas fills a window created by us
            if self.window._fullscreen:
                w, h = _App.GetDisplaySize()
                self._width = w
                self._height = h
                self._x = self._y = 0
                self._report_resize()
        else: # place canvas in window already created by user
            x = self._x
            y = self._y
            w = self._width
            h = self._height
        # For backward compatibility, maintain self._canvas as well as self.canvas

        attribList = [_App.glcanvas.WX_GL_DEPTH_SIZE, 24,
                      _App.glcanvas.WX_GL_DOUBLEBUFFER, 1,
                      0]
        if _App.glcanvas.GLCanvas_IsDisplaySupported(attribList):
            c = self.canvas = self._canvas = _App.glcanvas.GLCanvas(parent, -1, pos=(x, y), size=(w, h), attribList = attribList)
        else:
            attribList = [_App.glcanvas.WX_GL_DEPTH_SIZE, 16,
                          _App.glcanvas.WX_GL_DOUBLEBUFFER, 1,
                          0]
            if _App.glcanvas.GLCanvas_IsDisplaySupported(attribList):
                c = self.canvas = self._canvas = _App.glcanvas.GLCanvas(parent, -1, pos=(x, y), size=(w, h), attribList = attribList)
            else:
                c = self.canvas = self._canvas = _App.glcanvas.GLCanvas(parent, -1, pos=(x, y), size=(w, h))

        self._context = _App.glcanvas.GLContext(c)

        if self.fillswindow: c.SetFocus()

        c.Bind(_App.EVT_LEFT_DOWN, self._OnLeftMouseDown)
        c.Bind(_App.EVT_LEFT_UP, self._OnLeftMouseUp)
        c.Bind(_App.EVT_MIDDLE_DOWN, self._OnMiddleMouseDown)
        c.Bind(_App.EVT_MIDDLE_UP, self._OnMiddleMouseUp)
        c.Bind(_App.EVT_RIGHT_DOWN, self._OnRightMouseDown)
        c.Bind(_App.EVT_RIGHT_UP, self._OnRightMouseUp)
        c.Bind(_App.EVT_MOTION, self._OnMouseMotion)
        c.Bind(_App.EVT_LEFT_DCLICK, self._OnLeftDClick)
        c.Bind(_App.EVT_RIGHT_DCLICK, self._OnRightDClick)
        c.Bind(_App.EVT_MIDDLE_DCLICK, self._OnMiddleDClick)
        c.Bind(_App.EVT_MOUSE_CAPTURE_LOST, self._OnCaptureLost)

        #c.Bind(_App.EVT_MOUSEWHEEL, self.OnMouseWheel)

        #c.Bind(_App.EVT_CHAR, self._OnCharEvent)
        c.Bind(_App.EVT_KEY_DOWN, self._OnKeyDown)
        c.Bind(_App.EVT_KEY_UP, self._OnKeyUp)

    def _report_resize(self):
        self.report_window_resize(int(self._x), int(self._y), int(self._width), int(self._height))
        w = self._width-_dwidth
        if _plat == 'Unix' or _plat == 'Linux':
            h = self._height-_menuheight
        else:
            h = self._height-_dheight
        if self.menus: h -= _menuheight
        if not self.fillswindow: # canvas was placed in user-created window
            w = self._width
            h = self._height
        self.report_view_resize(int(w), int(h))

    def _activate( self, a ): # this is called from C++ code in display_kernel.cpp
        self._activated = a
        if a:
            global _do_loop
            _do_loop = True # if a display has been activated, execute wait loop at exit
            _displays.add(self)
            if not self._window_initialized:
                self._create()
                self._window_initialized = True

    def _create(self):
        _displays.display_num += 1
        self.N = _displays.display_num
        self._x = self.x
        self._y = self.y
        self._width = self.window_width
        self._height = self.window_height
        if self.fillswindow: # the display fills the window; no panel created
            self.window = window(menus=self.menus, _make_panel=False, x=self._x, y=self._y,
                                 width=self._width, height=self._height, title=self.title,
                                 visible=self._visible, fullscreen=self._fullscreen)
            self.window._add_display(self)
            self._make_canvas(self.window.win)
        else:
            self._make_canvas(self.window.panel)
        self.cursor = cursor(win=self.canvas)
        self.win = self.window.win

        self.panel = self.window.panel
        self.menubar = self.window.menubar
        self._report_resize()
        _Interact()

    def delete(self):
        if self.fillswindow:
            self.window.delete()
        else:
            for obj in self.objects:
                obj.visible = False
                del obj
            self.lights = []
            _displays.remove(self)
            self.report_closed()
            self.canvas.Destroy()

    def _destroy(self):
        _displays.remove(self)
        self.win.Destroy()
        self.win = None
        self.report_closed()

    def _paint(self):
        print("checking if window is initalized")
        if not self._window_initialized:
            print("window not initialized") 
            return
        self._canvas.SetCurrent(self._context)
        print ("about to call render")
        self.render_scene()
        self._canvas.SwapBuffers()

    def _OnLeftDClick(self, evt):
        self._OnLeftMouseDown(evt)
        self._OnLeftMouseUp(evt)
        self._OnLeftMouseDown(evt)

    def _OnRightDClick(self, evt):
        self._OnRightMouseDown(evt)
        self._OnRightMouseUp(evt)
        self._OnRightMouseDown(evt)

    def _OnMiddleDClick(self, evt):
        self._OnMiddleMouseDown(evt)
        self._OnMiddleMouseUp(evt)
        self._OnMiddleMouseDown(evt)

    def _OnLeftMouseDown(self, evt):
        self._mt.leftDown()
        self._report_mouse_state(evt)
        evt.Skip() # to permit setting focus

    def _OnLeftMouseUp(self, evt):
        self._mt.leftUp()
        self._report_mouse_state(evt)

    def _OnRightMouseDown(self, evt):
        self._mt.rightDown()
        self._report_mouse_state(evt)
        evt.Skip() # to permit setting focus

    def _OnRightMouseUp(self, evt):
        self._mt.rightUp()
        self._report_mouse_state(evt)

    def _OnMiddleMouseDown(self, evt):
        self._mt.midDown()
        self._report_mouse_state(evt)
        evt.Skip() # to permit setting focus

    def _OnMiddleMouseUp(self, evt):
        self._mt.midUp()
        self._report_mouse_state(evt)

##    def OnMouseWheel(self, evt): # not supported by VPython 5.x
##        print(evt.GetWheelRotation(), evt.GetWheelDelta())

    def _OnMouseMotion(self, evt):
        x, y = evt.GetPosition()
        if x != self._lastx or y != self._lasty:
            self._report_mouse_state(evt)
            self._dispatch_event('mousemove', self.mouse)
        evt.Skip() # to permit setting focus

    def _OnCaptureLost(self, evt):
        pass

# On Mac:
# CTRL + 1-button mouse = no CTRL, right button, presumably because CTRL-mouse == "right button"
# ALT  + 1-button mouse = ALT, left button
# CMD  + 1-button mouse = CTRL and CMD, left button

    def _report_mouse_state(self, evt): # wx gives x,y relative to upper left corner
        x, y = evt.GetPosition()
        if self._lastx is None:
            self._lastx = x
            self._lasty = y

        zooming = self._mt.isZooming(evt, self.userzoom, self.userspin)
        spinning = self._mt.isSpinning(evt, self.userzoom, self.userspin, zooming)
        lock = self._mt.checkLock(spinning, zooming)

        if lock and not self._captured:
            self.cursor_state = self.cursor.visible
            set_cursor(self.canvas, False)
            if self.fillswindow:
                self._cursorx, self._cursory = (x, y)
            else:
                # cursor is based on (0,0) of the window; our (x,y) is based on (0,0) of the 3D display
                self._cursorx, self._cursory = (int(self._x)+x, int(self._y)+y)
            self._canvas.CaptureMouse()
            self._captured = True
        elif self._captured and not (spinning or zooming):
            self.win.WarpPointer(self._cursorx, self._cursory)
            self._lastx = x = self._cursorx
            self._lasty = y = self._cursory
            set_cursor(self.canvas, self.cursor_state)
            self._canvas.ReleaseMouse()
            self._captured = False


        #
        # So... we're going to report left/right/middle
        #

        left = self._mt.leftIsDown and not spinning and not zooming
        right = spinning or self._mt.rightIsDown
        middle = zooming or self._mt.middleIsDown
        shift = evt.ShiftDown()
        ctrl = evt.ControlDown()
        alt = evt.AltDown()
        cmd = evt.CmdDown()

        if _plat == 'Macintosh' and ctrl and cmd:
            #
            # Weird... if the user holds the cmd key, evt.ControlDown() returns True even if it's a lie.
            # So... we don't know if it's *really* down or not. ;-(
            #
            ctrl = False

#         labels = [s.strip() for s in "x, y, left, middle, right, shift, ctrl, alt, cmd, spin, zoom, lock, cap".split(',')]
#         vals = (x, y, left, middle, right, shift, ctrl, alt, cmd, spinning, zooming, lock, self._captured)
#         fmts = ["%9s"]*len(vals)
#         for l,f in zip(labels,fmts):
#             print(f % l, end='')
#         print()
#         for v,f in zip(vals,fmts):
#             print(f % `v`, end='')
#         print()
##        if trigger == 'leftdown' and not self._rightdown:
##            if ctrl:
##                right = 1
##                left = 0
##            elif alt:
##                middle = 1
##                left = 0

#        if (spinning or zooming) and (x == self._lastx) and (y == self._lasty): return

        self.report_mouse_state([left, right, middle],
                self._lastx, self._lasty, x, y,
                [shift, ctrl, alt, cmd])
        # For some reason, handling spin/zoom in terms of movements away
        # from a fixed cursor position fails on the Mac. As you drag the
        # mouse, repeated move mouse events mostly give the fixed cursor position.
        # Hence, for now, dragging off-screen stops spin/zoom on the Mac.
        # Similar problems on Ubuntu 12.04, plus wx.CURSOR_BLANK not available on Linux.
        if (spinning or zooming) and (_plat != 'Macintosh'): # reset mouse to original location
            self.win.WarpPointer(self._cursorx, self._cursory)
            if self.fillswindow:
                self._lastx = self._cursorx
                self._lasty = self._cursory
            else:
                # cursor is based on (0,0) of the window; our (x,y) is based on (0,0) of the 3D display
                self._lastx = self._cursorx - int(self._x)
                self._lasty = self._cursory - int(self._y)
        else:
            self._lastx = x
            self._lasty = y

    def _ProcessChar(self, evt):
        #
        # Process event to keystroke for Char events.
        #
        key = evt.GetKeyCode()
        shift = evt.ShiftDown()
        if key > 127:
            if   key == 310: k = 'break'
            elif key == 312: k = 'end'
            elif key == 313: k = 'home'
            elif key == 314: k = 'left'
            elif key == 315: k = 'up'
            elif key == 316: k = 'right'
            elif key == 317: k = 'down'
            elif key == 322: k = 'insert'
            elif key == 340: k = 'f1'
            elif key == 341: k = 'f2'
            elif key == 342: k = 'f3'
            elif key == 343: k = 'f4'
            elif key == 344: k = 'f5'
            elif key == 345: k = 'f6'
            elif key == 346: k = 'f7'
            elif key == 347: k = 'f8'
            elif key == 348: k = 'f9'
            elif key == 349: k = 'f10'
            elif key == 366: k = 'page up'
            elif key == 367: k = 'page down'
            else: k = 'invalid key'
        else:
            # key code 311 is the caps lock key
            if shift or _App.GetKeyState(311): k = _shifted[key]
            else: k = _unshifted[key]
        if k == 'invalid key':
            return k
        self.keyboard.key = k
        self.keyboard.ctrl = evt.ControlDown()
        self.keyboard.alt = evt.AltDown()
        self.keyboard.shift = evt.ShiftDown()
        self.keyboard.cmd = evt.CmdDown()
        prefix = ''
        if self.keyboard.ctrl:
            prefix += 'ctrl+'
        if self.keyboard.alt:
            prefix += 'alt+'
        if self.keyboard.shift and len(k) != 1:
            prefix += 'shift+'
        if _plat == 'Macintosh' and self.keyboard.cmd:
            prefix += 'cmd+'
        return prefix+k

    def _OnKeyDown(self, evt):
        k = self._ProcessChar(evt)
        if k != 'invalid key':
            self.kb.pushkey(k)
            self._dispatch_event('keydown', self.keyboard)
        #print ("got keydown:", evt.GetKeyCode(), codeLookup.get(evt.GetKeyCode(),k))
        if evt.GetKeyCode() == VPY_MAC_CTRL and _plat=='Macintosh':
            self._mt.macCtrlDown()
        #evt.Skip()

    def _OnKeyUp(self, evt):
        k = self._ProcessChar(evt)
        if k != 'invalid key':
            # old key up didn't count as an event
            self._dispatch_event('keyup', self.keyboard)
        #print ("got keyup:",evt.GetKeyCode(), codeLookup.get(evt.GetKeyCode(),k))
        if evt.GetKeyCode() == VPY_MAC_CTRL and _plat=='Macintosh':
            self._mt.macCtrlUp()
        evt.Skip()

    def _return_objects(self):
        return tuple([ o for o in self._get_objects() if not isinstance(o, light) ])
    objects = property( _return_objects, None, None)

    def _get_lights(self):
        # TODO: List comprehension used for Python 2.3 compatibility; replace with
        #   generator comprehension
        return tuple([ o for o in self._get_objects() if isinstance(o, light) ])

    def _set_lights(self, n_lights):
        old_lights = self._get_lights()
        for lt in old_lights:
            lt.visible = False

        if (type(n_lights) is not list) and (type(n_lights) is not tuple):
            n_lights = [n_lights] # handles case of scene.lights = single light
        for lt in n_lights:
            if isinstance( lt, light ):  #< TODO: should this be allowed?
                lt.display = self
                lt.visible = True
            else:
                lum = vector(lt).mag
                distant_light( direction=vector(lt).norm(),
                               color=(lum,lum,lum),
                               display=self )

    def _get_visible(self):
        if self.fillswindow:
            return self.window.visible
        else:
            raise AttributeError('When a graphics -display- is only part of a window, get -visible- of the window.')

    def _set_visible(self, v):
        if self.fillswindow:
            if self.window: # means that a window has been created for the display
                self.window.visible = v
            else:
                self._visible = v
        else:
            raise AttributeError('When a graphics -display- is only part of a window, set -visible- of the window.')

    def _get_fullscreen(self):
        if self.fillswindow:
            return self.window.fullscreen
        else:
            raise AttributeError('When a graphics -display- is only part of a window, get -fullscreen- of the window.')

    def _set_fullscreen(self, full):
        if self.fillswindow:
            if self.window: # means that a window has been created for the display
                self.window.fullscreen = full
            else:
                self._fullscreen = full
        else:
            raise AttributeError('When a graphics -display- is only part of a window, set -fullscreen- of the window.')

    visible = property( _get_visible, _set_visible )
    fullscreen = property( _get_fullscreen, _set_fullscreen )

    lights = property( _get_lights, _set_lights, None)

from vis.site_settings import enable_shaders
display.enable_shaders = enable_shaders

# This is an atexit handler so that programs remain 'running' after they've finished
# executing the code in the program body. For visual this is important so that the
# windows don't close before the user can interact with them.
# _do_loop is set to True if a window is created or a display is activated.
# Otherwise we exit immediately (pure calculations with no displays).

_do_loop = False

def _close_final(): # There is a window, or an activated display
    global _do_loop
    if _do_loop:
        _do_loop = False # make sure we don't trigger this twice
        while True: # at end of user program, wait for user to close the program
            rate(1)
    #_App.EventLoop().exit()

_atexit.register(_close_final)
# The following is needed by Python 3, else running from vidle3/run.py
# doesn't drive _close_final:
_sys.exitfunc = _close_final

class _ManageDisplays(): # a singleton
    def __init__(self):
        #I don't believe this does anything at the moment
        #set_wait(wait)
        self.displays = []
        self.window_num = 0
        self.display_num = 0

    def add(self, d):
        self.displays.append(d)

    def remove(self, d):
        dl = self.displays[:]
        self.displays = []
        for disp in dl:
            if disp is d: continue
            self.displays.append(disp)

    def paint_displays(self):
        for d in self.displays:
            d._paint()

_displays = _ManageDisplays()
_evtloop = _App.EventLoop()
#_evtloop.run()
_isMac = False #('wxOSX' in _App.PlatformInfo)

if _plat == 'Windows':
    # On Windows, the best timer is supposedly time.clock()
    _clock = _time.clock
else:
    # On most other platforms, the best timer is supposedly time.time()
    _clock = _time.time

_mouse_binding_names = set(['mousedown','mouseup','click'])   # these are the events that we need to grab using display.mouse.getevents()

def _Interact():
# The essence of _Interact was provided by Robin Dunn, developer of wxPython

##    global _lastInteract
##    _lastInteract = _clock()

    # Detect changes to ball.pos.x, which are not caught by the C++ code that
    # drives primitives/trail_update (changes to ball.x are caught)
    for obj in trail_list:
        try:
            if obj.make_trail and obj.interval > 0 and not obj.updated:
                if len(obj.trail_object.pos) == 0:
                    obj.trail_object.append(pos=obj.pos)
                elif obj.pos != obj.trail_object.pos[-1]:
                    obj.trail_object.append(pos=obj.pos, retain=obj.retain)
        except:
            trail_list.remove(obj)

    for d in _displays.displays:
        d._dispatch_event("redraw")

    _displays.paint_displays()

    for d in _displays.displays:
        d._dispatch_event("draw_complete")

    while not _evtloop.Pending() and _evtloop.ProcessIdle(): pass
    if _App.GetApp(): _App.GetApp().ProcessPendingEvents()
    if _isMac and not _evtloop.Dispatch(): return
    # Currently on wxOSX Pending always returns true, so the
    # ProcessIdle above is not ever called. Call it here instead.
    if _isMac: _evtloop.ProcessIdle()

    while True:
        checkAgain = False
        if _App.GetApp() and _App.GetApp().HasPendingEvents():
            _App.GetApp().ProcessPendingEvents()
            checkAgain = True
        if not _isMac and _evtloop.Pending():
            _evtloop.Dispatch()
            checkAgain = True
        if not checkAgain:
            break

    for d in _displays.displays:
        events = set(d._bindings.keys())
        if _mouse_binding_names.intersection(events):
            #
            # only dispatch these if bindings are registered
            #
            while d.mouse.events:
                event = d.mouse.getevent()
                #
                # Depending on event type.. forward to event handlers
                #
                if event.press:
                    d._dispatch_event("mousedown", event)
                elif event.release:
                    d._dispatch_event("mouseup", event)
                if event.click:
                    d._dispatch_event("click", event)

#from .rate_function import RateKeeper as _rk
#rate = _rk(interactFunc=_Interact)

def sleep(dt):
    tend = _clock() + dt
    _Interact() # make sure we call _Interact at least once
    while _clock() < tend:
        rate(30)

# Title bar height is FRAMESIZE_Y + CAPTION_Y = 30 on Windows
# Menu bar height is MENU_Y = 20 on Windows
# Thickness of bottom is FRAMESIZE_Y = 8 on Windows
#   So height of canvas is scene.height - 58
#   and width of canvas is scene.width - 16

# The canvas size is (self._width-_dwidth, self._height-_dheight)
# except for Xubuntu, where some ad hoc corrections had to be made.
# _dy is the number of pixels from the top of the window to the top of the display area
if _plat == 'Macintosh':
    _dwidth = 0
    _dheight = 22
    _menuheight = 0
elif _plat == 'Unix' or _plat == 'Linux': # e.g., Linux
    # Xubuntu: title bar 49 high, menubar 27 high, mouse offset 52
    # Ubuntu 12.04: title bar 27, menubar ?, mouse offset ?
    _dwidth = 0
    _dheight = 27
    _menuheight = 27
else: # Windows
    _dwidth = 2*(_App.SystemSettings.GetMetric(_App.SYS_FRAMESIZE_X))
    _dheight = 2*(_App.SystemSettings.GetMetric(_App.SYS_FRAMESIZE_Y)) + \
            _App.SystemSettings.GetMetric(_App.SYS_CAPTION_Y)
    _menuheight = _App.SystemSettings.GetMetric(_App.SYS_FRAMESIZE_Y) + \
            _App.SystemSettings.GetMetric(_App.SYS_CAPTION_Y)


# Tables for converting US keyboard inputs to characters
_unshifted = ['', '', '', '', '', '', '', '', 'backspace', 'tab', # 0-9
   '', '', '', '\n', '', '', 'shift', 'ctrl', 'alt', '', # 10-19
   'caps lock', '', '', '', '', '', '', 'esc', '', '', #20-29
   '', '', ' ', '', '', '', '', '', '', "'", # 30-39
   '', '', '', '', ',', '-', '.', '/', '0', '1', # 40-49
   '2', '3', '4', '5', '6', '7', '8', '9', '', ';', # 50-59
   '', '=', '', '', '', 'a', 'b', 'c', 'd', 'e', # 60-69
   'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', # 70-79
   'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', # 80-89
   'z', '[', '\\', ']', '', '', '`', '', '', '', # 90-99
   '', '', '', '', '', '', '', '', '', '', # 100-109
   '', '', '', '', '', '', '', '', '', '', # 110-119
   '', '', '', '', '', '', '', 'delete'] #120-127

_shifted = ['', '', '', '', '', '', '', '', 'backspace', 'tab', # 0-9
   '', '', '', '\n', '', '', 'shift', 'ctrl', 'alt', 'break', # 10-19
   'caps lock', '', '', '', '', '', '', 'esc', '', '', #20-29
   '', '', '', '!', '"', '#', '$', '%', '&', '"', # 30-39
   '(', ')', '*', '+', '<', '_', '>', '?', ')', '!', # 40-49
   '@', '#', '$', '%', '^', '&', '*', '(', ':', ':', # 50-59
   '<', '+', '>', '?', '@', 'A', 'B', 'C', 'D', 'E', # 60-69
   'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', # 70-79
   'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', # 80-89
   'Z', '{', '|', '}', '^', '_', '~', '', '', '', # 90-99
   '', '', '', '', '', '', '*', '+', '', '', # 100-109
   '', '', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', # 110-119
   'f9', 'f10', '', '{', '|', '}', '~', 'delete'] #120-127



#
# the mac 'ctrl' key seems to come in as key code 396, not in WXK list.
# the mac 'cmd' key comes through as WXK_CTRL, oddly enough.
#

VPY_MAC_CTRL = 396

##
##codeLookup = dict(zip(codeVals, codeStrings))
if __name__ == "__main__":
    scene = display()
