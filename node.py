"""
node.py — Scene graph building blocks.

Key ideas:
- Node is an abstract base defining the interface (render, transform, pick, etc.).
- Primitive subclasses (Cube, Sphere) draw themselves via OpenGL call lists.
- HierarchicalNode composes children → Composite pattern (e.g., SnowFigure).
"""

import random
import numpy
from numpy.linalg import inv
from OpenGL.GL import (
    glPushMatrix, glPopMatrix, glCallList, glMultMatrixf, glColor3f,
    glMaterialfv, GL_FRONT, GL_EMISSION
)
import color
from aabb import AABB
from primitive import G_OBJ_CUBE, G_OBJ_SPHERE


# ---------- tiny transform constructors (column-major-friendly) -------------
def scaling(s):
    """Return a 4x4 uniform/non-uniform scale matrix from (sx, sy, sz)."""
    m = numpy.identity(4, dtype=float)
    m[0, 0], m[1, 1], m[2, 2] = s
    return m

def translation(t):
    """Return a 4x4 translation matrix from (tx, ty, tz)."""
    m = numpy.identity(4, dtype=float)
    m[0, 3], m[1, 3], m[2, 3] = t
    return m


# ------------------------------- Node (abstract) ----------------------------
class Node(object):
    def __init__(self):
        # Random initial color, unit AABB, and identity transforms
        self.color_index        = random.randint(color.MIN_COLOR, color.MAX_COLOR)
        self.aabb               = AABB([0, 0, 0], [0.5, 0.5, 0.5])
        self.translation_matrix = numpy.identity(4, dtype=float)
        self.scaling_matrix     = numpy.identity(4, dtype=float)
        self.selected           = False    # drives highlight in render()

    def render(self):
        """
        - Push current ModelView.
        - Apply this node's translation and scale.
        - Set color (and a little emission if selected).
        - Call subclass's render_self() to actually draw geometry.
        - Pop ModelView.
        """
        glPushMatrix()
        # OpenGL expects column-major floats; numpy uses row-major.
        # The original code transposes translation, but not scaling; this works
        # because scaling_matrix is already constructed to match how OpenGL reads it.
        glMultMatrixf(numpy.transpose(self.translation_matrix))
        glMultMatrixf(self.scaling_matrix)

        r, g, b = color.COLORS[self.color_index]
        glColor3f(r, g, b)
        if self.selected:
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.3, 0.3, 0.3])

        self.render_self()

        if self.selected:
            glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0])
        glPopMatrix()

    def render_self(self):
        """Abstract: subclasses must draw their actual geometry."""
        raise NotImplementedError

    # -------- transforms ------------------------------------------------------
    def translate(self, dx, dy, dz):
        """Post-multiply a translation (moves in the node's current local space)."""
        self.translation_matrix = numpy.dot(self.translation_matrix,
                                            translation([dx, dy, dz]))

    def scale(self, up=True):
        """Uniformly scale node and its AABB for visual consistency."""
        s = 1.1 if up else 0.9
        self.scaling_matrix = numpy.dot(self.scaling_matrix, scaling([s, s, s]))
        self.aabb.scale(s)

    # -------- picking helpers -------------------------------------------------
    def pick(self, origin, direction, modelview):
        """
        Ray test vs. this node's AABB (approximate). We need to account
        for the node's transforms: M = MV * T * inv(S), so the unit AABB
        matches the on-screen scaled+translated geometry.
        """
        transform = numpy.dot(
            numpy.dot(modelview, self.translation_matrix),
            inv(self.scaling_matrix)
        )
        return self.aabb.ray_hit(origin, direction, transform)

    def select(self, state=None):
        """Toggle or set selected state (drives highlight)."""
        self.selected = (not self.selected) if state is None else state

    def rotate_color(self, forward=True):
        """Cycle through palette (left/right arrows)."""
        self.color_index += 1 if forward else -1
        if self.color_index > color.MAX_COLOR:
            self.color_index = color.MIN_COLOR
        if self.color_index < color.MIN_COLOR:
            self.color_index = color.MAX_COLOR


# ------------------------------ Primitive nodes -----------------------------
class Primitive(Node):
    """Base for simple shapes tied to an OpenGL display list."""
    call_list = None
    def render_self(self):
        glCallList(self.call_list)

class Cube(Primitive):
    call_list = G_OBJ_CUBE

class Sphere(Primitive):
    call_list = G_OBJ_SPHERE


# ---------------------------- Hierarchical example --------------------------
class HierarchicalNode(Node):
    """Composite node that renders a list of children with its transform."""
    def __init__(self):
        super(HierarchicalNode, self).__init__()
        self.children = []

    def render_self(self):
        for c in self.children:
            c.render()

class SnowFigure(HierarchicalNode):
    """A simple 'snowman': three stacked spheres with decreasing radii."""
    def __init__(self):
        super(SnowFigure, self).__init__()
        self.children = [Sphere(), Sphere(), Sphere()]

        # Position child spheres along Y; scale top two a bit smaller
        self.children[0].translate(0, -0.6, 0)
        self.children[1].translate(0,  0.1, 0)
        self.children[2].translate(0,  0.75, 0)

        self.children[1].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.8, 0.8, 0.8]))
        self.children[2].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.7, 0.7, 0.7]))

        # Make the snowman white initially
        for c in self.children:
            c.color_index = color.MIN_COLOR

        # Taller AABB to enclose the whole stack
        self.aabb = AABB([0, 0, 0], [0.5, 1.1, 0.5])
