"""
interaction.py — Translates OS input (GLUT) into app-level events.

- Handles mouse buttons/motion, keyboard, and arrow keys.
- Exposes a small callback bus: 'pick', 'move', 'place', 'rotate_color', 'scale'.
- Also maintains an orbital trackball (right-drag) and scene translation.

Viewer registers handlers here; Scene doesn't need to know about GLUT.
"""

from collections import defaultdict
from OpenGL.GLUT import (
    glutGet, glutMouseFunc, glutMotionFunc, glutKeyboardFunc, glutSpecialFunc,
    glutPostRedisplay, GLUT_WINDOW_WIDTH, GLUT_WINDOW_HEIGHT,
    GLUT_LEFT_BUTTON, GLUT_RIGHT_BUTTON, GLUT_MIDDLE_BUTTON,
    GLUT_DOWN, GLUT_KEY_UP, GLUT_KEY_DOWN, GLUT_KEY_LEFT, GLUT_KEY_RIGHT
)
import trackball


class Interaction(object):
    def __init__(self):
        self.pressed      = None                 # which mouse button is down
        self.trackball    = trackball.Trackball(theta=-25, distance=15)
        self.translation  = [0, 0, 0, 0]         # x,y,z shift of the whole scene
        self.mouse_loc    = None                 # last mouse position (x,y)
        self.callbacks    = defaultdict(list)    # event -> [handlers]
        self.register()

    # -------- GLUT registration ---------------------------------------
    def register(self):
        glutMouseFunc(self.handle_mouse_button)
        glutMotionFunc(self.handle_mouse_move)
        glutKeyboardFunc(self.handle_keystroke)
        glutSpecialFunc(self.handle_keystroke)

    # -------- app-level helper API ------------------------------------
    def translate(self, x, y, z):
        """Move the whole scene (camera-fixed approach)."""
        self.translation[0] += x
        self.translation[1] += y
        self.translation[2] += z

    def register_callback(self, name, func):
        """Viewer uses this to hook scene operations to events."""
        self.callbacks[name].append(func)

    def trigger(self, name, *args, **kw):
        """Dispatch app-level event to all registered listeners."""
        for cb in self.callbacks[name]:
            cb(*args, **kw)

    # -------- low-level event handlers --------------------------------
    def handle_mouse_button(self, button, mode, x, y):
        """Mouse press/release handler."""
        w, h = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y    = h - y                      # convert to OpenGL-style origin (bottom-left)
        self.mouse_loc = (x, y)

        if mode == GLUT_DOWN:
            self.pressed = button
            if button == GLUT_LEFT_BUTTON:
                self.trigger('pick', x, y)               # select node under cursor
            elif button == 3:                             # wheel up → zoom in
                self.translate(0, 0, 1.0)
            elif button == 4:                             # wheel down → zoom out
                self.translate(0, 0, -1.0)
        else:
            self.pressed = None
        glutPostRedisplay()

    def handle_mouse_move(self, x, scr_y):
        """Mouse move while dragging: rotate, move selection, or pan."""
        w, h = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y    = h - scr_y
        if self.pressed is not None:
            dx, dy = x - self.mouse_loc[0], y - self.mouse_loc[1]
            if self.pressed == GLUT_RIGHT_BUTTON and self.trackball:
                # Orbit around origin (camera rotation)
                self.trackball.drag_to(self.mouse_loc[0], self.mouse_loc[1], dx, dy)
            elif self.pressed == GLUT_LEFT_BUTTON:
                # Move selected node to follow the cursor's ray
                self.trigger('move', x, y)
            elif self.pressed == GLUT_MIDDLE_BUTTON:
                # Pan the whole scene parallel to the screen
                self.translate(dx / 60.0, dy / 60.0, 0)
            glutPostRedisplay()
        self.mouse_loc = (x, y)

    def handle_keystroke(self, key, x, scr_y):
        """Keyboard (ASCII + special keys)."""
        # Convert to OpenGL coords for consistency (not strictly needed here)
        w, h = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        y    = h - scr_y

        # Place primitives
        if   key == b's' or key == 's': self.trigger('place', 'sphere', x, y)
        elif key == b'c' or key == 'c': self.trigger('place', 'cube',   x, y)

        # Scale selected node (up/down arrows)
        elif key == GLUT_KEY_UP      : self.trigger('scale', up=True)
        elif key == GLUT_KEY_DOWN    : self.trigger('scale', up=False)

        # Cycle color (left/right arrows)
        elif key == GLUT_KEY_LEFT    : self.trigger('rotate_color', forward=True)
        elif key == GLUT_KEY_RIGHT   : self.trigger('rotate_color', forward=False)

        glutPostRedisplay()
