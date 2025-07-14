# my3d-modeller
My own 3D modeller built in Python with OpenGL

Notes Taken (as I'm completing the project):
  - OpenGL: graphical application programming interface, which is the standard API for developing graphics applications across platforms. It has two variant: Legacy OpenGL and Modern OpenGL. We will use Legacy OpenGL as it allows us to have the standard linear algebra knowledge required, making the project more readabe and keeping the code size small. 
  - Rendering happens through polygons defined by vertices and normals. So we should specify an object's 4 vertices and the normal of the side.
  - We are using GLUT, bundled with OpenGL, to create the operating system windows and to register any user infterface callcbacks. It's sufficient for the scope of the project.
  - To manage the GLUT and OpenGL settup, we create the Viewer class, and using a single instance of it. It manages window creation and rendering, and it contains the program's main loop. init_interface creates the window that the modeller will be rendered into and specifies the function when the design needs to be rendered.
  - init_opengl sets up the OpenGL state needed for the project. Sets the matrices, enables backface culling, register the light that illuminates the scene, tells OpenGL we'd like color on the objects.
  - init_scene is for the Scene objects, and it places initial nodes to get the user started. init_interaction registers callbacks for user interaction.
  - After initializing the Viewer class, we call glutMainLoop, which transfers program execution to GLUT (a function that never returns). SO callbacks registered on GLUT events will be called when those events occur.
  - Coordinate space: it's an origin point and a set of 3 basis vectors: our know x, y, z axes. Any point in 3 dimensions can be represented as an offset in the x,y,z directions from origin point. The same point has different representations in different coordinate spaces. So any 3D point can be represented in any 3D coordinate space.
  - We will use vectors (difference between 2 x,y,z points) as we will transfrom matrices. In computer graphics, it's convenient to use multiple coordinate spaces for different types of points. Transformation matrices convert points from one coordinate space to another. And to convert a vector v from one coordinate space to another, we multiply by a transformation Matrix M:v' = Mv.
  - So drawing
