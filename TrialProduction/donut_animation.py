import math
import sys
import shutil
import os
import numpy as np
import abc

SCREEN_WIDTH  = shutil.get_terminal_size().columns
SCREEN_HEIGHT = shutil.get_terminal_size().lines

MAX_RAD = 2 * math.pi

class ResultStorage:
    storage = {}
    def has(key):
        return key in self.storage

    def get(key):
        return self.storage[key]

    def store(key, value):
        self.storage[key] = value

class ThreeDimensionalObject(object, metaclass=abc.ABCMeta):
    def execute_forever(self, display):
        self.display = display

    @abc.abstractmethod
    def compute_frame(self):
        pass

class DonutObject(ThreeDimensionalObject):
    R1 = 1
    R2 = 2

    # Distance between object and eye
    K1 = 30
    # Distance between object and screen
    K2 = 5

    phi_spacing   = 0.07
    theta_spacing = 0.02

    a_spacing = 0
    b_spacing = 0

    memo_length = int(MAX_RAD * 100 + 1)

    # Trigonometric memo
    phi_memo    = [() for i in range(memo_length)]
    theta_memo  = [() for i in range(memo_length)]
    a_memo      = [() for i in range(memo_length)]
    b_memo      = [() for i in range(memo_length)]
    
    # Screen memo
    screen_memo = [
            [np.zeros((0)) for i in range(memo_length)]
            for j in range(memo_length)]

    def execute_forever(self, display):
        super().execute_forever(display)
        
    def compute_frame(self, A, B):
        pos_a = int(A * 100)
        pox_b = int(B * 100)
        if len(self.screen_memo[a][b]) != 0:
            return self.screen_memo[a][b]

        zbuffer = np.zeros((SCREEN_WIDTH, SCREEN_HEIGHT))
        output  = np.full((CREEN_WIDTH, SCREEN_HEIGHT), ' ')

        # Precompute
        pos_a = int(A * 100)
        pos_b = int(B * 100)
        if len(self.a_memo[pos_a]) == 0:
            self.a_memo[pos_a] = (math.sin(A), math.cos(A))
        if len(self.b_memo[pos_b]) == 0:
            self.b_memo[pos_b] = (math.sin(B), math.cos(B))
        memo = self.a_memo[pos_a]
        sinA = memo[0]
        cosA = memo[1]
        memo = self.b_memo[pos_b]
        sinB = memo[0]
        cosB = memo[1]

        theta = 0
        while theta <= MAX_RAD:
            # Precompute
            pos_theta = int(theta * 100)
            if len(theta_memo[pos_theta]) == 0:
                self.theta_memo[pos_theta] = (math.sin(theta), math.cos(theta))
            memo = self.theta_memo[pos_theta]
            sintheta = memo[0]
            costheta = memo[1]
            circlex = self.R2 + self.R1 * costheta
            circley = self.R1 * sintheta

            phi = 0
            while phi <= MAX_RAD:
                # Precompute
                pos_phi = int(phi * 100)
                if len(phi_memo[pos_phi]) == 0:
                    self.phi_memo[pos_phi] = (math.sin(phi), math.cos(phi))
                memo = self.phi_memo[pos_phi]
                sinphi = memo[0]
                cosphi = memo[1]

                # Compute x, y, z
                x = circlex * (cosB * cosphi + sinA * sinB * sinphi) - circley * cosA * sinB
                y = circlex * (cosphi * sinB - cosB * sinA * sinphi) + circley * cosA * cosB
                z = cosA * circlex * sinphi + circley * sinA

                # Add K2 and compute z position
                z += self.K2

                # Compute Z ^ -1
                ooz = 1 / z

                # Compute x dash, y dash
                xdash = round(self.K1 * x * ooz)
                ydash = round((self.K1 / 2) * y * ooz)

                # Compute x position and y position
                xpos = round(screen_width / 2) + xdash
                ypos = round(screen_height / 2) + ydash

                # Compute luminace (max = sqrt(2))
                L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta + cosB * (cosA * sintheta - costheta * sinA * sinphi)

                # Seek display character
                is_range_valid = screen_width >= xpos and xpos >= 0 and screen_height >= ypos and ypos >= 0
                if L > 0 and is_range_valid:
                    if ooz > zbuffer[xpos][ypos]:
                        zbuffer[xpos][ypos] = ooz
                        luminance_index = round(L * 8)
                        output[xpos][ypos] = ".,-~:;=!*#$@"[luminance_index]
                phi += self.phi_spacing
            theta += theta_spacing

class Display:
    @abc.abstractmethod
    def render_frame(self, frame):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

class CommandLineDisplay(Display):
    def render_frame(self, frame):
        pass

if __name__ == "__main__":
    pass
