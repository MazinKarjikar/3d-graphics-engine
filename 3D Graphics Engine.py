"""
This program is used to display objects - described by their vertices in 3D space - on a 2D computer screen. 
My motivation to make this project is to use my knowledge of linear algebra along with my interest of video games
to make a programming project that would challenge me. This project also allows me to develop in Python and get
some experience with object oriented programming. 
"""
import math
import copy
import pygame as pg

pg.init()


# Let's define a Vector...
class Vector:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def toString(self):
        print(self.x, self.y, self.z)


# ...as well as a Triangle.
class Triangle:
    def __init__(self, v1: Vector, v2: Vector, v3: Vector):
        self.pts = [v1, v2, v3]

    def toString(self):
        for vec in self.pts:
            vec.toString()


# Let's also define any object as a mesh of triangles. Triangles are the simplest 2D object, and are the building block.
class Mesh:
    def __init__(self, tris: list):
        self.tris = tris


def main():
    # Colors to be preset since we are using pygame.
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # Initializing the screen
    screen = pg.display.set_mode()
    WIDTH, HEIGHT = screen.get_size()
    print(WIDTH, HEIGHT)
    # WIDTH = 1800
    # HEIGHT = 1000
    size = (WIDTH, HEIGHT)
    pi = 3.14159
    dudVec = Vector(1, 1, 1)

    fAspectRatio = float(HEIGHT) / float(WIDTH)
    fNear = 0.1
    fFar = 1000.0
    fFov = 90.0
    fFovRad = 1.0 / (math.tan(fFov * 0.5 / 180.0 * pi))
    start_time = pg.time.get_ticks()

    # This is the projection matrix for objects we want to put in our field of view.
    # We will consider our x, y, and z boundaries as +- 1. Normalizing our axes will help a lot with projection.
    # To normalize, our x coordinate will be multiplied by the aspect ratio. We will also divide x and y by z -
    # the farther away the objects are, the less they should seem to move on the screen for an equivalent change in x or y coordinates.
    # Normalizing z requires simulating the screen being a cross section of the person's FOV (who is viewing the screen). The math accounting
    # for this is included in fFar and fNear.
    # Lastly, the FOV increasing means the x and y coordinate changes should also be smaller.
    PROJECTION_MATRIX = [[0.0] * 4 for _ in range(4)]
    PROJECTION_MATRIX[0][0] = fAspectRatio * fFovRad
    PROJECTION_MATRIX[1][1] = fFovRad
    PROJECTION_MATRIX[2][2] = fFar / (fFar - fNear)
    PROJECTION_MATRIX[3][2] = (-fFar * fNear) / (fFar - fNear)
    PROJECTION_MATRIX[2][3] = 1.0
    PROJECTION_MATRIX[3][3] = 0.0
    # print(PROJECTION_MATRIX)

    # Since we will be doing a lot of Matrix Multiplication, let's define a function for it.
    def matrixMultVector(i: Vector, o: Vector, mat):
        o.x = i.x * mat[0][0] + i.y * mat[1][0] + i.z * mat[2][0] + mat[3][0]
        o.y = i.x * mat[0][1] + i.y * mat[1][1] + i.z * mat[2][1] + mat[3][1]
        o.z = i.x * mat[0][2] + i.y * mat[1][2] + i.z * mat[2][2] + mat[3][2]
        w = i.x * mat[0][3] + i.y * mat[1][3] + i.z * mat[2][3] + mat[3][3]

        if w != 0:
            o.x /= w
            o.y /= w
            o.z /= w

    # Screen update speed
    clock = pg.time.Clock()

    # Initializing a cube made up of 12 triangles, each consisting of two.
    # I am creating a convention of listing the vertices in clockwise order.
    # I will also be using standard Rubix Cube notation to notate which face of the cube I am referring to.
    meshCube = Mesh(
        # F (Front)
        [
            Triangle(Vector(0, 0, 0), Vector(0, 1, 0), Vector(1, 1, 0)),
            Triangle(Vector(0, 0, 0), Vector(1, 1, 0), Vector(1, 0, 0)),
            # R (Right)
            Triangle(Vector(1, 0, 0), Vector(1, 1, 0), Vector(1, 1, 1)),
            Triangle(Vector(1, 0, 0), Vector(1, 1, 1), Vector(1, 0, 1)),
            # B (Back)
            Triangle(Vector(1, 0, 1), Vector(1, 1, 1), Vector(0, 1, 1)),
            Triangle(Vector(1, 0, 1), Vector(0, 1, 1), Vector(0, 0, 1)),
            # L (Left)
            Triangle(Vector(0, 0, 1), Vector(0, 1, 1), Vector(0, 1, 0)),
            Triangle(Vector(0, 0, 1), Vector(0, 1, 0), Vector(0, 0, 0)),
            # U (Up)
            Triangle(Vector(0, 1, 0), Vector(0, 1, 1), Vector(1, 1, 1)),
            Triangle(Vector(0, 1, 0), Vector(1, 1, 1), Vector(1, 1, 0)),
            # D (Down)
            Triangle(Vector(1, 0, 1), Vector(0, 0, 1), Vector(0, 0, 0)),
            Triangle(Vector(1, 0, 1), Vector(0, 0, 0), Vector(1, 0, 0)),
        ]
    )

    # Switch for the drawing loop
    done = False

    # ------- Main Program Loop -------
    while not done:
        # --- Main Event Loop ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        # START OF CODE FOR CALCULATE/DRAW
        screen.fill(BLACK)
        curr_time = pg.time.get_ticks()
        fTheta = (curr_time - start_time) / 1000.0

        # ROTATION MATRICES

        # Rotation Z
        matRotZ = [[0] * 4 for _ in range(4)]
        matRotZ[0][0] = math.cos(fTheta)
        matRotZ[0][1] = math.sin(fTheta)
        matRotZ[1][0] = -math.sin(fTheta)
        matRotZ[1][1] = math.cos(fTheta)
        matRotZ[2][2] = 1
        matRotZ[3][3] = 1

        # Rotation X
        matRotX = [[0] * 4 for _ in range(4)]
        matRotX[0][0] = 1
        matRotX[1][1] = math.cos(fTheta * 0.5)
        matRotX[1][2] = math.sin(fTheta * 0.5)
        matRotX[2][1] = -math.sin(fTheta * 0.5)
        matRotX[2][2] = math.cos(fTheta * 0.5)
        matRotX[3][3] = 1

        # Create a new triangle which holds the coordinates of our triangles in the mesh, but projected.
        for tri in meshCube.tris:
            TEMPLATE = Triangle(Vector(0, 0, 0), Vector(0, 0, 0), Vector(0, 0, 0))
            triRotatedZ = copy.deepcopy(TEMPLATE)
            triRotatedZX = copy.deepcopy(TEMPLATE)
            triOnScreen = copy.deepcopy(TEMPLATE)

            matrixMultVector(tri.pts[0], triRotatedZ.pts[0], matRotZ)
            matrixMultVector(tri.pts[1], triRotatedZ.pts[1], matRotZ)
            matrixMultVector(tri.pts[2], triRotatedZ.pts[2], matRotZ)

            matrixMultVector(triRotatedZ.pts[0], triRotatedZX.pts[0], matRotX)
            matrixMultVector(triRotatedZ.pts[1], triRotatedZX.pts[1], matRotX)
            matrixMultVector(triRotatedZ.pts[2], triRotatedZX.pts[2], matRotX)

            triTranslate = copy.deepcopy(triRotatedZX)
            triTranslate.pts[0].z = triRotatedZX.pts[0].z + 3.0
            triTranslate.pts[1].z = triRotatedZX.pts[1].z + 3.0
            triTranslate.pts[2].z = triRotatedZX.pts[2].z + 3.0

            matrixMultVector(triTranslate.pts[0], triOnScreen.pts[0], PROJECTION_MATRIX)
            matrixMultVector(triTranslate.pts[1], triOnScreen.pts[1], PROJECTION_MATRIX)
            matrixMultVector(triTranslate.pts[2], triOnScreen.pts[2], PROJECTION_MATRIX)

            # Scale them properly - right now they are values between 0 and 1 since we normalized them.
            triOnScreen.pts[0].x += 1.0
            triOnScreen.pts[0].y += 1.0
            triOnScreen.pts[1].x += 1.0
            triOnScreen.pts[1].y += 1.0
            triOnScreen.pts[2].x += 1.0
            triOnScreen.pts[2].y += 1.0

            triOnScreen.pts[0].x *= 0.5 * float(WIDTH)
            triOnScreen.pts[0].y *= 0.5 * float(HEIGHT)
            triOnScreen.pts[1].x *= 0.5 * float(WIDTH)
            triOnScreen.pts[1].y *= 0.5 * float(HEIGHT)
            triOnScreen.pts[2].x *= 0.5 * float(WIDTH)
            triOnScreen.pts[2].y *= 0.5 * float(HEIGHT)

            x0 = triOnScreen.pts[0].x
            x1 = triOnScreen.pts[1].x
            x2 = triOnScreen.pts[2].x
            y0 = triOnScreen.pts[0].y
            y1 = triOnScreen.pts[1].y
            y2 = triOnScreen.pts[2].y

            pg.draw.polygon(screen, WHITE, [(x0, y0), (x1, y1), (x2, y2)], 1)

        pg.display.flip()
        # Setting FPS
        clock.tick(60)

    pg.quit()


main()
