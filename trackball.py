"""
Virtual trackball helper (borrowed from Glumpy).

Typical use:

    tb = Trackball(theta=-25, distance=15)

    @window.event
    def on_mouse_drag(x, y, dx, dy, button, modifiers):
        tb.drag_to(x, y, dx, dy)

    # in your render:
    glMultMatrixf(tb.matrix)

You can also set `theta` (rotation round X) and `phi` (rotation round Z)
directly.


# Notes for this project:
# - The class exposes .matrix (4x4 rotation) that viewer multiplies into MV.
# - Interaction.drag_to(...) calls Trackball.drag_to(...) to update rotation.
"""

import math
import OpenGL.GL as gl
from OpenGL.GL import GLfloat

# ----- small vector helpers -------------------------------------------------
def _v_add(v1, v2):  return [v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2]]
def _v_sub(v1, v2):  return [v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2]]
def _v_mul(v, s):    return [v[0]*s, v[1]*s, v[2]*s]
def _v_dot(v1, v2):  return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
def _v_cross(v1, v2):
    return [(v1[1]*v2[2]) - (v1[2]*v2[1]),
            (v1[2]*v2[0]) - (v1[0]*v2[2]),
            (v1[0]*v2[1]) - (v1[1]*v2[0])]
def _v_length(v):    return math.sqrt(_v_dot(v, v))
def _v_normalize(v):
    try:  return _v_mul(v, 1.0 / _v_length(v))
    except ZeroDivisionError: return v

# ----- quaternion helpers (for robust rotation accumulation) ----------------
def _q_add(q1, q2):
    t1 = _v_mul(q1, q2[3])
    t2 = _v_mul(q2, q1[3])
    t3 = _v_cross(q2, q1)
    tf = _v_add(t1, _v_add(t2, t3))
    tf.append(q1[3]*q2[3] - _v_dot(q1, q2))
    return tf
def _q_mul(q, s):        return [q[0]*s, q[1]*s, q[2]*s, q[3]*s]
def _q_dot(q1, q2):      return (q1[0]*q2[0] + q1[1]*q2[1] +
                                 q1[2]*q2[2] + q1[3]*q2[3])
def _q_length(q):        return math.sqrt(_q_dot(q, q))
def _q_normalize(q):
    try:  return _q_mul(q, 1.0 / _q_length(q))
    except ZeroDivisionError: return q
def _q_from_axis_angle(v, phi):
    q = _v_mul(_v_normalize(v), math.sin(phi/2.0))
    q.append(math.cos(phi/2.0))
    return q
def _q_rotmatrix(q):
    """Convert quaternion to column-major 4x4 rotation matrix array."""
    m = [0.0]*16
    m[ 0] = 1 - 2*(q[1]*q[1] + q[2]*q[2])
    m[ 1] =     2*(q[0]*q[1] - q[2]*q[3])
    m[ 2] =     2*(q[2]*q[0] + q[1]*q[3])
    m[ 5] = 1 - 2*(q[2]*q[2] + q[0]*q[0])
    m[ 6] =     2*(q[1]*q[2] - q[0]*q[3])
    m[ 8] =     2*(q[2]*q[0] - q[1]*q[3])
    m[ 9] =     2*(q[1]*q[2] + q[0]*q[3])
    m[10] = 1 - 2*(q[1]*q[1] + q[0]*q[0])
    m[15] = 1.0
    return m

class Trackball(object):
    """Virtual trackball for intuitive 3D rotation; expose .matrix to GL."""

    def __init__(self, *, theta=0, phi=0, zoom=1, distance=3):
        self._rotation = [0, 0, 0, 1]  # quaternion (x,y,z,w)
        self._count    = 0
        self._matrix   = None
        self._RENORMCOUNT  = 97        # periodically renormalize quaternion
        self._TRACKBALLSIZE = .8

        self.zoom     = zoom
        self.distance = distance
        self._x = self._y = 0.0

        self._set_orientation(theta, phi)

    # ---- called by Interaction on right-drag -------------------------
    def drag_to(self, x, y, dx, dy):
        """
        Update rotation based on mouse drag from (x,y) by (dx,dy).
        We map screen coords to virtual sphere, compute an axis & angle,
        then accumulate into the current quaternion.
        """
        vp = gl.glGetIntegerv(gl.GL_VIEWPORT)
        w, h = float(vp[2]), float(vp[3])
        x  =  (2*x  - w) / w
        y  =  (2*y  - h) / h
        dx = (2*dx) / w
        dy = (2*dy) / h

        q = self._rotate(x, y, dx, dy)
        self._rotation = _q_add(q, self._rotation)

        self._count += 1
        if self._count > self._RENORMCOUNT:
            self._rotation = _q_normalize(self._rotation)
            self._count = 0

        self._matrix = (GLfloat * 16)(*_q_rotmatrix(self._rotation))

    # (zoom_to and pan_to exist for completeness; not used directly here)
    def zoom_to(self, _, __, ___, dy):
        h = float(gl.glGetIntegerv(gl.GL_VIEWPORT)[3])
        self.zoom -= 5 * dy / h

    def pan_to(self, _, __, dx, dy):
        self._x += dx * 0.1
        self._y += dy * 0.1

    # ---- properties ---------------------------------------------------
    @property
    def matrix(self):  return self._matrix

    # ---- internal helpers ---------------------------------------------
    def _set_orientation(self, theta, phi):
        """Seed orientation from Euler-ish angles (X then Z)."""
        angle = math.radians(theta)
        xrot  = [math.sin(angle/2), 0, 0, math.cos(angle/2)]
        angle = math.radians(phi)
        zrot  = [0, 0, math.sin(angle/2), math.cos(angle/2)]
        self._rotation = _q_add(xrot, zrot)
        self._matrix   = (GLfloat * 16)(*_q_rotmatrix(self._rotation))

    def _project(self, r, x, y):
        """Project 2D screen point onto a virtual sphere of radius r."""
        d = math.hypot(x, y)
        if d < r * 0.70710678:     # inside sphere
            return math.sqrt(r*r - d*d)
        t = r / 1.41421356         # on hyperbolic sheet
        return t*t / d

    def _rotate(self, x, y, dx, dy):
        if not dx and not dy:
            return [0, 0, 0, 1]
        last = [x, y, self._project(self._TRACKBALLSIZE, x, y)]
        new  = [x+dx, y+dy,
                self._project(self._TRACKBALLSIZE, x+dx, y+dy)]
        axis = _v_cross(new, last)
        t    = _v_length(_v_sub(last, new)) / (2*self._TRACKBALLSIZE)
        t    = max(-1, min(1, t))
        return _q_from_axis_angle(axis, 2*math.asin(t))