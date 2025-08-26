"""
primitive.py — OpenGL display lists for basic shapes & grid.

We pre-build tiny display lists so actual node rendering can be a single
glCallList(...) per primitive. This keeps per-frame code simple and small.
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy  # (not strictly required here, but often useful)

# Display-list IDs (arbitrary unique integers)
G_OBJ_CUBE   = 1
G_OBJ_SPHERE = 2
G_OBJ_PLANE  = 3

def GLfloat_3(x, y, z):   return (GLfloat * 3)(x, y, z)
def GLfloat_4(x, y, z, w): return (GLfloat * 4)(x, y, z, w)

def init_primitives():
    """Create display lists for cube, sphere, and a ground-plane grid."""
    # ---- cube ---------------------------------------------------------
    glNewList(G_OBJ_CUBE, GL_COMPILE)
    glutSolidCube(1.0)          # centered at origin, side length 1.0
    glEndList()

    # ---- sphere -------------------------------------------------------
    glNewList(G_OBJ_SPHERE, GL_COMPILE)
    glutSolidSphere(0.5, 16, 16) # radius 0.5 to match unit-size AABB nicely
    glEndList()

    # ---- ground plane grid -------------------------------------------
    glNewList(G_OBJ_PLANE, GL_COMPILE)
    size, step = 20, 1
    glBegin(GL_LINES)
    for i in range(-size, size + 1, step):
        glVertex3f(i, 0, -size); glVertex3f(i, 0,  size)
        glVertex3f(-size, 0, i); glVertex3f( size, 0, i)
    glEnd()
    glEndList()
