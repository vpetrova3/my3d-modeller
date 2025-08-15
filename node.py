import random
import numpy
from numpy.linalg import inv, norm
from OpenGL.GL import (
    glPushMatrix, glPopMatrix, glCallList, glMultMatrixf, glColor3f,
    glMaterialfv, GL_FRONT, GL_EMISSION
)
import color
from aabb import AABB
from primitive import G_OBJ_CUBE, G_OBJ_SPHERE


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def scaling(s):
    m = numpy.identity(4)
    m[0, 0], m[1, 1], m[2, 2] = s
    return m


def translation(t):
    m = numpy.identity(4)
    m[0, 3], m[1, 3], m[2, 3] = t
    return m


# ----------------------------------------------------------------------
# abstract Node
# ----------------------------------------------------------------------
class Node(object):
    def __init__(self):
        self.color_index       = random.randint(color.MIN_COLOR, color.MAX_COLOR)
        self.aabb              = AABB([0, 0, 0], [0.5, 0.5, 0.5])
        self.translation_matrix = numpy.identity(4)
        self.scaling_matrix     = numpy.identity(4)
        self.selected           = False

    # ------ rendering --------------------------------------------------
    def render(self):
        glPushMatrix()
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

    def render_self(self):                      # implemented by subclasses
        raise NotImplementedError

    # ------ transforms -------------------------------------------------
    def translate(self, dx, dy, dz):
        self.translation_matrix = numpy.dot(self.translation_matrix,
                                            translation([dx, dy, dz]))

    def scale(self, up=True):
        s = 1.1 if up else 0.9
        self.scaling_matrix = numpy.dot(self.scaling_matrix, scaling([s, s, s]))
        self.aabb.scale(s)

    # ------ selection helpers -----------------------------------------
    def pick(self, origin, direction, modelview):
        transform = numpy.dot(
            numpy.dot(modelview, self.translation_matrix),
            inv(self.scaling_matrix)
        )
        return self.aabb.ray_hit(origin, direction, transform)

    def select(self, state=None):
        self.selected = (not self.selected) if state is None else state

    def rotate_color(self, forward=True):
        self.color_index += 1 if forward else -1
        if self.color_index > color.MAX_COLOR:
            self.color_index = color.MIN_COLOR
        if self.color_index < color.MIN_COLOR:
            self.color_index = color.MAX_COLOR


# ----------------------------------------------------------------------
# primitives
# ----------------------------------------------------------------------
class Primitive(Node):
    call_list = None

    def render_self(self):
        glCallList(self.call_list)


class Cube(Primitive):
    call_list = G_OBJ_CUBE


class Sphere(Primitive):
    call_list = G_OBJ_SPHERE


# ----------------------------------------------------------------------
# compound example – the snowman
# ----------------------------------------------------------------------
class HierarchicalNode(Node):
    def __init__(self):
        super(HierarchicalNode, self).__init__()
        self.children = []

    def render_self(self):
        for c in self.children:
            c.render()


class SnowFigure(HierarchicalNode):
    def __init__(self):
        super(SnowFigure, self).__init__()
        self.children = [Sphere(), Sphere(), Sphere()]

        self.children[0].translate(0, -0.6, 0)
        self.children[1].translate(0,  0.1, 0)
        self.children[2].translate(0,  0.75, 0)

        self.children[1].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.8, 0.8, 0.8]))
        self.children[2].scaling_matrix = numpy.dot(
            self.scaling_matrix, scaling([0.7, 0.7, 0.7]))

        for c in self.children:
            c.color_index = color.MIN_COLOR

        self.aabb = AABB([0, 0, 0], [0.5, 1.1, 0.5])
