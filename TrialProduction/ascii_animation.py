import math
import sys
import shutil
import os
import numpy as np
import abc

MAX_RAD = math.pi * 2

class SurfacePoint:
    """ Surface X, Y, Z coordinates """
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class ThreeDimensionalObject(object, metaclass=abc.ABCMeta):
    """ 3D object """
    @abc.abstractmethod
    def get_obj(self):
        pass

class Donut(ThreeDimensionalObject):
    theta_spacing = 0.07
    phi_spacing   = 0.02

    # Radius of a small circle
    R1 = 1
    # Radius of a big circle
    R2 = 2

    # Save what you calculated once
    cache = []

    def get_obj(self):
        if self.cache:
            return self.cache

        theta = 0
        while theta <= MAX_RAD:
            sintheta = math.sin(theta)
            costheta = math.cos(theta)
            circlex = self.R2 + self.R1 * costheta
            circley = self.R1 * sintheta

            phi = 0
            while phi <= MAX_RAD:
                sinphi = math.sin(phi)
                cosphi = math.cos(phi)
                x = circlex * cosphi
                y = circley
                z = -circlex * sinphi
                self.cache.append(SurfacePoint(x, y, z))
                phi += self.phi_spacing
            theta += self.theta_spacing

        return self.cache

class Cube(ThreeDimensionalObject):
    cache = []

    def get_obj(self):
        if self.cache:
            return self.cache

class RenderingApparatus:
    screen_width  = shutil.get_terminal_size().columns
    screen_height = shutil.get_terminal_size().lines

    # Distance between object and screen
    K2 = 5
    # Distance between object and eye
    K1 = 30

    # Save screen for each radians
    output_cache = np.zeros((int(MAX_RAD * 100), int(MAX_RAD * 100)))

    def __init__(self, obj, A_spacing, B_spacing):
        self.obj = obj
        self.A_spacing = A_spacing
        self.B_spacing = B_spacing

    def render_forever(self):
        A = 0
        B = 0
        while True:
            output = self.compute_frame(A, B)
            self.render_frame(output)
            A += self.A_spacing
            B += self.B_spacing
            if A > MAX_RAD:
                A = 0
            if B > MAX_RAD:
                B = 0

    def compute_frame(self, A, B):
        poA = int(A * 100)
        poB = int(B * 100)
        if self.output_cache[poA][poB]:
            return self.output_cache[poA][poB]

        zbuffer = np.zeros((self.screen_width, self.screen_height))
        output  = np.full((self.screen_width, self.screen_height), ' ')

        # Precompute
        sinA = math.sin(A)
        sinB = math.sin(B)
        cosA = math.cos(A)
        cosB = math.cos(B)

        obj_points = self.obj.get_obj()

        for point in obj_points:
            # Compute X Y Z
            x = point.x * cosB - point.y * sinB
            y = point.x * cosA * sinB + point.y * cosA * cosB - point.z * sinA
            z = point.x * sinA * sinB + point.y * sinA * cosB + point.z * cosA

            # Add K2 and compute z position
            z += self.K2

            # Compute z ^ -1
            ooz = 1 / z
            # Compute x dash, y dash on screen
            xdash = round(self.K1 * x * ooz)
            ydash = round((self.K1 / 2) * y * ooz)

            # Compute x position and y position
            xpos = round((self.screen_width) / 2) + xdash
            ypos = round((self.screen_height) / 2) - ydash

            # Compute luminace (max = sqrt(2))
            L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta + cosB * (cosA * sintheta - costheta * sinA * sinphi)

            # Put a display character on output
            is_x_range_valid = self.screen_width > xpos and xpos >= 0
            is_y_range_valid = self.screen_height > ypos and ypos >= 0
            if L > 0 and is_x_range_valid and is_y_range_valid:
                if ooz > zbuffer[xpos][ypos]:
                    zbuffer[xpos][ypos] = ooz
                    luminance_index = round(L * 8)
                    output[xpos][ypos] = ".,-~:;=!*#$@"[luminance_index]

        self.output_cache[poA][poB] = output
        return self.output_cache[poA][poB]

    def render_frame(output):
        os.system('cls')
        for y in range(self.screen_height):
            for x in range(self.screen_width):
                sys.stdout.write(output[x, y])
            sys.stdout.write('\n')
        sys.stdout.flush()

if __name__ == "__main__":
    obj = None
    a_spacing = 0.04
    b_spacing = 0.02
    while True:
        t = input("Type >> ")
        if t == "cube":
            obj = Cube()
            break
        elif t == "donut":
            obj = Donut()
            break
        else:
            continue

    apparatus = RenderingApparatus(obj, a_spacing, b_spacing)
    apparatus.render_forever()
