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
        init_primitives()

    # ------------------------------------------------------------------
    # GLUT / OpenGL init
    # ------------------------------------------------------------------
    def init_interface(self):
        glutInit()
        glutInitWindowSize(640, 480)
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutCreateWindow(b"3D Modeller")
        glutDisplayFunc(self.render)

    def init_opengl(self):
        self.modelView       = numpy.identity(4)
        self.inverseModelView = numpy.identity(4)

        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHT0)

        glLightfv(GL_LIGHT0, GL_POSITION, GLfloat_4(0, 0, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, GLfloat_3(0, 0, -1))
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.4, 0.4, 0.4, 0)

    def init_scene(self):
        self.scene = Scene()
        self.create_sample_scene()

    def create_sample_scene(self):
        c = Cube();   c.translate( 2, 0,  2); c.color_index = 2; self.scene.add_node(c)
        s = Sphere(); s.translate(-2, 0,  2); s.color_index = 3; self.scene.add_node(s)
        f = SnowFigure(); f.translate(-2, 0, -2);             self.scene.add_node(f)

    def init_interaction(self):
        self.interaction = Interaction()
        self.interaction.register_callback('pick',         self.pick)
        self.interaction.register_callback('move',         self.move)
        self.interaction.register_callback('place',        self.place)
        self.interaction.register_callback('rotate_color', self.rotate_color)
        self.interaction.register_callback('scale',        self.scale)

    # ------------------------------------------------------------------
    # main loop
    # ------------------------------------------------------------------
    def main_loop(self):
        glutMainLoop()

    # ------------------------------------------------------------------
    # view helpers
    # ------------------------------------------------------------------
    def init_view(self):
        w, h = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        aspect = float(w) / float(h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glViewport(0, 0, w, h)
        gluPerspective(70, aspect, 0.1, 1000.0)
        glTranslated(0, 0, -15)

    def render(self):
        self.init_view()

        glEnable(GL_LIGHTING)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        tx, ty, tz, _ = self.interaction.translation
        glTranslated(tx, ty, tz)
        glMultMatrixf(self.interaction.trackball.matrix)

        mv = numpy.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        self.modelView        = mv.T
        self.inverseModelView = inv(mv.T)

        self.scene.render()

        glDisable(GL_LIGHTING)
        glCallList(G_OBJ_PLANE)
        glPopMatrix()
        glFlush()

    # ------------------------------------------------------------------
    # interaction callbacks
    # ------------------------------------------------------------------
    def get_ray(self, x, y):
        self.init_view()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        start = numpy.array(gluUnProject(x, y, 0.001))
        end   = numpy.array(gluUnProject(x, y, 0.999))
        dir   = (end - start); dir /= norm(dir)
        return start, dir

    def pick(self, x, y):
        start, dir = self.get_ray(x, y)
        self.scene.pick(start, dir, self.modelView)

    def move(self, x, y):
        start, dir = self.get_ray(x, y)
        self.scene.move_selected(start, dir, self.inverseModelView)

    def place(self, shape, x, y):
        start, dir = self.get_ray(x, y)
        self.scene.place(shape, start, dir, self.inverseModelView)

    def rotate_color(self, forward):
        self.scene.rotate_selected_color(forward)

    def scale(self, up):
        self.scene.scale_selected(up)


if __name__ == '__main__':
    Viewer().main_loop()