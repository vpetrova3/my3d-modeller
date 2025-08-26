"""
aabb.py — Axis-Aligned Bounding Box (AABB) support + simple wireframe draw.

Purpose:
- Each Node owns an AABB that approximates its occupied space.
- We use fast ray–AABB intersection to implement picking (object selection).

Notes:
- Boxes live in a node's local/model space, but the ray comes in view/world
  space. We pass a transform matrix that maps the box into the ray's space.
"""

import numpy
from OpenGL.GL import (
    glMatrixMode, glPushMatrix, glPopMatrix,
    glTranslated, glPolygonMode, glCallList,
    GL_MODELVIEW, GL_LINE, GL_FILL, GL_FRONT_AND_BACK
)
from primitive import G_OBJ_CUBE

EPSILON = 1e-6  # small tolerance to avoid divide-by-zero / precision issues


class AABB(object):
    def __init__(self, centre, size):
        """
        centre: (x,y,z) of box center in the node's local space
        size:   half-extent in each axis (so total width = 2*size)
        """
        self.centre = numpy.array(centre, dtype=float)
        self.size   = numpy.array(size,   dtype=float)

    def scale(self, s):
        """Uniformly scale the box when the node scales."""
        self.size *= s

    def ray_hit(self, origin, direction, model):
        """
        Test if a ray hits this box.

        origin, direction: 3D ray in *the same space* as `model`.
        model: 4x4 matrix that maps from this box's local space (AABB space)
               into the ray's space (typically current model-view).

        Approach:
        - Convert OBB (box under transform) test into three "slab" tests along
          the transformed box axes. Keep a running [t_min, t_max] interval of
          valid ray distances. If the interval collapses, there's no hit.
        - Return (True, distance) for the closest hit along the ray.
        """
        minimum = self.centre - self.size
        maximum = self.centre + self.size

        t_min, t_max = 0.0, 1e6
        obb_pos = model[:3, 3]             # box center in ray space
        delta   = obb_pos - origin

        for i in range(3):                  # test each axis of the (oriented) box
            axis = model[i, :3]             # the i-th local axis under transform
            e    = numpy.dot(axis, delta)
            f    = numpy.dot(direction, axis)

            if abs(f) > EPSILON:            # regular case: compute t for each slab
                t1 = (e + minimum[i]) / f
                t2 = (e + maximum[i]) / f
                if t1 > t2:
                    t1, t2 = t2, t1
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                if t_max < t_min:           # interval collapsed → miss
                    return False, 0.0
            else:
                # Ray is parallel to this slab: reject if origin not between faces
                if -e + minimum[i] > EPSILON or -e + maximum[i] < -EPSILON:
                    return False, 0.0
        return True, t_min

    def render(self):
        """Draw a unit cube at the AABB center (wireframe) — purely visual aid."""
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslated(*self.centre)
        glCallList(G_OBJ_CUBE)              # unit cube display list (size=1)
        glPopMatrix()
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
