"""
viewer.py — Entry point. Owns the window, GL state, Scene, and Interaction.

Flow:
- init_interface(): create GLUT window & register the draw callback.
- init_opengl():    configure lights, depth, and default matrices.
- init_scene():     create Scene and seed some starter nodes.
- init_interaction(): wire Interaction events to Scene operations.
- render():         per-frame: set projection, build ModelView from trackball
                    + translation, render Scene & the ground grid.

Run:
    python viewer.py
"""

import numpy
from numpy.linalg import inv, norm
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import color
from primitive import *
from interaction import Interaction
from scene import Scene
from node import Sphere, Cube, SnowFigure


class Viewer(object):
    def __init__(self):
        self.init_interface()
        self.init_opengl()
        self.init_scene()
        self.init_interaction()
        init_primitives()  # build display lists

    # ---------------------- GLUT / OpenGL init -------------------------
    def init_interface(self):
        glutInit()
        glutInitWindowSize(640, 480)
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutCreateWindow(b"3D Modeller")
        glutDisplayFunc(self.render)  # draw callback

    def init_opengl(self):
        # Keep copies of ModelView and its inverse to convert between spaces
        self.modelView        = numpy.identity(4)
        self.inverseModelView = numpy.identity(4)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)

        # Basic headlight
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(0, 0, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, GLfloat_3(0, 0, -1))

        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.4, 0.4, 0.4, 0)

    def init_scene(self):
        self.scene = Scene()
        self.create_sample_scene()

    def create_sample_scene(self):
        """Drop a cube, a sphere, and a snow figure so there's something to see."""
        c = Cube();   c.translate( 2, 0,  2); c.color_index = 2; self.scene.add_node(c)
        s = Sphere(); s.translate(-2, 0,  2); s.color_index = 3; self.scene.add_node(s)
        f = SnowFigure(); f.translate(-2, 0, -2);             self.scene.add_node(f)

    def init_interaction(self):
        """Wire UI events to scene operations."""
        self.interaction = Interaction()
        self.interaction.register_callback('pick',         self.pick)
        self.interaction.register_callback('move',         self.move)
        self.interaction.register_callback('place',        self.place)
        self.interaction.register_callback('rotate_color', self.rotate_color)
        self.interaction.register_callback('scale',        self.scale)

    # --------------------------- main loop -----------------------------
    def main_loop(self):
        glutMainLoop()

    # -------------------------- view helpers ---------------------------
    def init_view(self):
        """(Re)build projection matrix for the current window size."""
        w, h = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        aspect = float(w) / float(h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0, 0, w, h)
        gluPerspective(70, aspect, 0.1, 1000.0)  # <- single place we set perspective
        glTranslated(0, 0, -15)                  # pull the whole scene "back"

    def render(self):
        """One frame: set matrices, draw the scene, then the grid."""
        self.init_view()

        glEnable(GL_LIGHTING)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Camera/scene motion from Interaction:
        tx, ty, tz, _ = self.interaction.translation
        glTranslated(tx, ty, tz)
        glMultMatrixf(self.interaction.trackball.matrix)

        # Cache MV and its inverse for ray generation & space conversion
        mv = numpy.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        self.modelView        = mv.T
        self.inverseModelView = inv(mv.T)

        # Draw all nodes (with lighting)
        self.scene.render()

        # Draw ground plane without lighting for contrast
        glDisable(GL_LIGHTING)
        glCallList(G_OBJ_PLANE)
        glPopMatrix()
        glFlush()

    # ---------------------- interaction callbacks ---------------------
    def get_ray(self, x, y):
        """
        Convert 2D mouse coords into a 3D ray (camera space), by unprojecting
        near & far points and normalizing the direction.
        """
        self.init_view()               # ensure projection matches current size
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        start = numpy.array(gluUnProject(x, y, 0.001))
        end   = numpy.array(gluUnProject(x, y, 0.999))
        direction = end - start
        direction = direction / norm(direction)
        return start, direction

    def pick(self, x, y):
        start, direction = self.get_ray(x, y)
        self.scene.pick(start, direction, self.modelView)

    def move(self, x, y):
        start, direction = self.get_ray(x, y)
        self.scene.move_selected(start, direction, self.inverseModelView)

    def place(self, shape, x, y):
        start, direction = self.get_ray(x, y)
        self.scene.place(shape, start, direction, self.inverseModelView)

    def rotate_color(self, forward):
        self.scene.rotate_selected_color(forward)

    def scale(self, up):
        self.scene.scale_selected(up)


if __name__ == '__main__':
    Viewer().main_loop()
