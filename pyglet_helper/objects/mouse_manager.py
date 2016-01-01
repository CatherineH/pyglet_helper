from pyglet.gl import *
from enum import Enum


class MouseButton(Enum):
    NONE = 1
    LEFT = 2
    RIGHT = 3
    MIDDLE = 4


class MouseManager(object):
    def __init__(self, display, px=0, py=0, left_down=False, left_dragging=False, left_semidrag=False,
                 middle_down=False, middle_dragging=False, middle_semidrag=False, right_down=False,
                 right_dragging=False, right_semidrag=False):
        self._mouse = None
        self.display = display
        self.px = px
        self.py = py
        self.pz = pz
        self.left_down = left_down
        self.left_dragging = left_dragging
        self.left_semidrag = left_semidrag
        self.middle_down = middle_down
        self.middle_dragging = middle_dragging
        self.middle_semidrag = middle_semidrag
        self.right_down = right_down
        self.right_dragging = right_dragging
        self.right_semidrag = right_semidrag

        self.buttons = [False] * 2
        self.mouse = mouse()

    def report_mouse_state(self, physical_button_count, is_button_down, old_x, old_y, new_x, new_y, shift_state_count,
                           shift_state):
        """
        Called by the display driver to report mouse movement
        Ideally this should be called in event handlers so that each successive change in mouse state
        is captured in order, but a driver might just call this periodically with the current state.
        If the mouse is locked, but has "moved" by (dx,dy), the driver should pass get_x()+dx, get_y()+dy
        """
        # In is_button_down array, position 0=left, 1=right, 2=middle

        # A 2-button mouse with shift,ctrl,alt/option,command
        new_buttons = [physical_button_count, is_button_down]
        new_shift = [shift_state_count, shift_state]

        # if we have a 3rd button, pressing it is like pressing both left and right buttons.
        # This is necessary to make platforms that "emulate" a 3rd button behave sanely with
        # a two-button mouse.
        if physical_button_count >= 3 and is_button_down[2]:
            new_buttons[0] = new_buttons[1] = True

        # If there's been more than one button change, impose an order, so that update()
        # only sees one change at a time
        # We choose the order so that the right button is down as much as possible, to
        # avoid spurious left button activity
        # Not relevant if there is a real (or emulated) button 2 (e.g. Mac option key)
        if not new_buttons[2] and not buttons[2] and new_buttons[0] != buttons[0] and new_buttons[1] != buttons[1]:
            b = not new_buttons[1]
            new_buttons[b] = not new_buttons[b]
            self.update(new_buttons, old_x, old_y, new_x, new_y, new_shift)
            new_buttons[b] = not new_buttons[b]

        self.update(new_buttons, old_x, old_y, new_x, new_y, new_shift)

    # Get the current position of the mouse cursor relative to the window client area
    @property
    def x(self):
        return self.x

    @property
    def y(self):
        return self.y

    @property
    def mouse(self):
        return self._mouse
    @mouse.setter
    def mouse(self, n_mouse):
        self._mouse = n_mouse

    def update(self, new_buttons, old_px, old_py, new_px, new_py, new_shift):
        # Shift states are just passed directly to mouseobject
        self._mouse.set_shift(new_shift[0])
        self._mouse.set_ctrl(new_shift[1])
        self._mouse.set_alt(new_shift[2])
        self._mouse.set_command(new_shift[3])

        if new_buttons[1]:  # handle spin or zoom if allowed
            if new_buttons[0]:
                self.display.report_camera_motion((new_px - old_px), (new_py - old_py), mouse_button.MIDDLE)
            else:
                self.display.report_camera_motion((new_px - old_px), (new_py - old_py), mouse_button.RIGHT)

        # left_semidrag means that we've moved the mouse and so can't get a left click, but we aren't
        # necessarily actually dragging, because the movement might have occurred with the right button down.
        if self.left_down and not self.left_dragging and (new_px != old_px or new_py != old_py):
            self.left_semidrag = True
        if not self.left_down:
            self.left_semidrag = False

        if not self.display.spin_is_allowed():
            if self.right_down and not self.right_dragging and (new_px != old_px or new_py != self.py):
                self.right_semidrag = True
            if not self.right_down:
                self.right_semidrag = False

        if not self.display.zoom_is_allowed():
            if self.middle_down and not self.middle_dragging and (new_px != old_px or new_py != self.py):
                self.middle_semidrag = True
            if not self.middle_down:
                self.middle_semidrag = False
        # In reporting with press_event etc., 1=left, 2=right, 3=middle
        if not new_buttons[1]:  # < Ignore changes in the left button state while the right button is down!
            b = new_buttons[0]
            if b != left_down:
                if b:
                    if not self.buttons[0]:  #< Releasing the other button of a chord doesn't "press" the left
                        self.mouse.push_event(press_event(1, self.mouse))
                    else:
                        b = False
                elif self.left_dragging:
                    self.mouse.push_event(drop_event(1, self.mouse))
                    self.left_dragging = False
                elif self.left_semidrag:
                    self.mouse.push_event(release_event(1, self.mouse))
                elif self.left_down:
                    self.mouse.push_event(click_event(1, self.mouse))

            if b and self.left_down and (new_px != old_px or new_py != self.py) and not self.left_dragging:
                self.mouse.push_event(drag_event(1, self.mouse))
                self.left_dragging = True

            self.left_down = b
        # < Ignore changes in the left button state while the right button is down!
        if not self.display.spin_is_allowed() and not new_buttons[0]:
            b = new_buttons[1]

            if b != self.right_down:
                if b:
                    if not self.buttons[1]:  #< Releasing the other button of a chord doesn't "press" the right
                        self.mouse.push_event(press_event(2, self.mouse))
                    else:
                        b = False
                elif self.right_dragging:
                    self.mouse.push_event(drop_event(2, self.mouse))
                    self.right_dragging = False
                elif self.right_semidrag:
                    self.mouse.push_event(release_event(2, self.mouse))
                elif self.right_down:
                    self.mouse.push_event(click_event(2, self.mouse))

            if b and self.right_down and (new_px != old_px or new_py != py) and not self.right_dragging:
                self.mouse.push_event(drag_event(2, self.mouse))
                self.right_dragging = True

            self.right_down = b
        if not self.display.zoom_is_allowed():
            b = (new_buttons[0] and new_buttons[1])

            if b != self.middle_down:
                if b:
                    if not (buttons[0] and buttons[1]):
                        self.mouse.push_event(press_event(3, self.mouse))
                    else:
                        b = False
                elif self.middle_dragging:
                    self.mouse.push_event(drop_event(3, self.mouse))
                    self.middle_dragging = False
                elif self.middle_semidrag:
                    self.mouse.push_event(release_event(3, self.mouse))
                elif self.middle_down:
                    self.mouse.push_event(click_event(3, self.mouse))

            if b and self.middle_down and (new_px != old_px or new_py != self.py) and not self.middle_dragging:
                self.mouse.push_event(drag_event(3, self.mouse))
                self.middle_dragging = True

            self.middle_down = b

        self.px = new_px
        self.py = new_py

        for b in range(0, 2):
            self.buttons[b] = new_buttons[b]
