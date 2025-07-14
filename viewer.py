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
    if __name__ == "__main__":
        viewer = Viewer()
        viewer.main_loop()