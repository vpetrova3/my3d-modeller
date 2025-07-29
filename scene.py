import sys
import numpy
from numpy.linalg import inv
from node import Sphere, Cube, SnowFigure


class Scene(object):
    PLACE_DEPTH = 15.0

    def __init__(self):
        self.node_list     = []
        self.selected_node = None

    # ------------------------------------------------------------------
    # public helpers
    # ------------------------------------------------------------------
    def add_node(self, n):
        self.node_list.append(n)

    def render(self):
        for n in self.node_list:
            n.render()

    # ------------------------------------------------------------------
    # selection & manipulation
    # ------------------------------------------------------------------
    def pick(self, origin, direction, modelview):
        if self.selected_node:
            self.selected_node.select(False)
            self.selected_node = None

        mindist, closest = sys.maxsize, None
        for n in self.node_list:
            hit, dist = n.pick(origin, direction, modelview)
            if hit and dist < mindist:
                mindist, closest = dist, n

        if closest:
            closest.select(True)
            closest.depth        = mindist
            closest.selected_loc = origin + direction * mindist
            self.selected_node   = closest

    def rotate_selected_color(self, forward):
        if self.selected_node:
            self.selected_node.rotate_color(forward)

    def scale_selected(self, up):
        if self.selected_node:
            self.selected_node.scale(up)

    def move_selected(self, origin, direction, inv_model):
        if not self.selected_node:
            return
        node  = self.selected_node
        depth = node.depth
        old   = node.selected_loc
        new   = origin + direction * depth

        delta = new - old
        delta = inv_model.dot(numpy.array([delta[0], delta[1], delta[2], 0]))
        node.translate(*delta[:3])
        node.selected_loc = new

    def place(self, shape, origin, direction, inv_model):
        new = {'sphere': Sphere, 'cube': Cube, 'figure': SnowFigure}[shape]()
        self.add_node(new)

        loc = origin + direction * self.PLACE_DEPTH
        loc = inv_model.dot(numpy.array([loc[0], loc[1], loc[2], 1]))
        new.translate(*loc[:3])
