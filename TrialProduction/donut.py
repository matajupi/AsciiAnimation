# interval when calculating theta
theta_spacing = 0.07
# interval when calculating phi
phi_spacing   = 0.02

R1 = 1
R2 = 2
K2 = 10
# Calculate K1 based on screen size: the maximum x-distance occurs
# roughly at the edge of the torus, which is at x=R1+R2, z=0.  we
# want that to be displaced 3/8ths of the width of the screen, which
# is 3/4th of the way from the center to the side of the screen.
# screen_width*3/8 = K1*(R1+R2)/(K2+0)
# screen_width*K2*3/(8*(R1+R2)) = K1
import shutil
import os
import numpy as np
screen_width  = shutil.get_terminal_size().columns
screen_height = shutil.get_terminal_size().lines
# K1 = screen_width*K2*3/(8*(R1+R2)) # Z dash
K1 = 20

def render(A, B):
    # precompute sines and cosines of A and B
    import math
    cosA = math.cos(A)
    sinA = math.sin(A)
    cosB = math.cos(B)
    sinB = math.sin(B)

    # terminal outputs
    output  = [[' ' for i in range(screen_height)] 
    for j in range(screen_width)]
    # zbuffers
    zbuffer = [[0 for i in range(screen_height)]
    for j in range(screen_width)]

    # theta goes around the cross-sectional circle of a torus
    theta = 0
    while theta < 2 * math.pi:
        # precompute sines and cosines of theta
        costheta = math.cos(theta)
        sintheta = math.sin(theta)
        
        phi = 0
        # phi goes around the center of revolution of a torus
        while phi < 2 * math.pi:
            # precompute sines and cosines of phi
            cosphi = math.cos(phi)
            sinphi = math.sin(phi)

            # the x, y coordinate of the circle, before revolving
            # factored out of the above equations
            # (R2, 0, 0) + (R1cos(theta), R1sin(theta), 0)
            circlex = R2 + R1 * costheta 
            circley = R1 * sintheta

            # final 3D (x, y, z) coordinate after rotations,
            # directly from our math above
            # x=(R2+R1cos(theta))*(cos(B)cos(phi)+sin(A)sin(B)sin(phi))
            # -R1cos(A)sin(B)sin(theta)
            # y=(R2+R1cos(theta))*(cos(phi)sin(B)-cos(B)sin(A)sin(phi))
            # +R1cos(A)cos(B)sin(theta)
            # z=cos(A)*(R2+R1cos(theta))sin(phi)+R1sin(A)sin(theta)
            x = circlex * (cosB * cosphi + sinA * sinB * sinphi)
            - circley * cosA * sinB
            y = circlex * (sinB * cosphi - sinA * cosB * sinphi)
            + circley * cosA * cosB
            # z = z + K2
            z = K2 + cosA * circlex * sinphi + circley * sinA
            # one over z
            ooz = 1 / z

            # x and y projection. note that y is negated here, because y
            # goes up in 3D space but down on 2D displays.
            # (x', y') = (K1x / K2 + z, k1y / K2 + z)
            # Since z = z + K2 above
            # K1 * x * (1 / z), K1 * y * (1 / z)
            # Set display place
            xp = int(screen_width / 2 + K1 * ooz * x)
            yp = int(screen_height / 2 - K1 * ooz * y)

            # calculate luminance. ugly, but correct.
            # L = cos(phi)cos(theta)sin(B)-cos(A)cos(theta)sin(phi)
            # -sin(A)sin(theta)+cos(B)(cos(A)sin(theta)-cos(theta)
            # sin(A)sin(phi))
            L = cosphi * costheta * sinB - cosA * costheta * sinphi
            - sinA * sintheta + cosB * (cosA * sintheta - costheta
            * sinA * sinphi)

            # L ranges from -sqrt(2) to +sqrt(2). If it's < 0, the
            # surface is pointing away from us, so we won't bother
            # trying to plot it.
            if L > 0:
                # test against the z-buffer. larger 1/z means the pixel
                # is closer to the viewr than what's already plotted.
                # hold the maximum value of 1/z for the z axis 
                # at all locations(x', y').
                if ooz > zbuffer[xp][yp]:
                    zbuffer[xp][yp] = ooz
                    luminance_index = int(L * 8)
                    # liminance_index is now in the range 0..11
                    # (8*sqrt(2) = 11.3)
                    # luminance and plot it in our output:
                    output[xp][yp] = ".,-~:;=!*#$@"[luminance_index]
            phi += phi_spacing
        theta += theta_spacing
    
    # now, dump output[] to the screen.
    # bring cursor to "home" location, in just about any currently-used
    # terminal emulation mode
    import sys

    sys.stdout.write("\x1b[H")
    for y in range(screen_height):
        for x in range(screen_width):
            sys.stdout.write(output[x][y])
        sys.stdout.write('\n')

import math
if __name__ == "__main__":
    a = 1
    b = 1
    while True:
        a_spacing = 0.07
        b_spacing = 0.03
        while a < 2 * math.pi:
            while b < 2 * math.pi:
                render(a, b)
                b += b_spacing
            a += a_spacing
        a = 1
        b = 1


