import math
import sys
import shutil
import os
import numpy as np

screen_width  = shutil.get_terminal_size().columns
screen_height = shutil.get_terminal_size().lines

theta_spacing = 0.07 # default 0.07
phi_spacing   = 0.02 # default 0.02

R1 = 1
R2 = 2

# Distance between object and eye
K2 = 5
# Distance between screen and eye
K1 = 30 # default 30

max_rad = 2 * math.pi

screen_cache = [[np.zeros((0)) for i in range(int(max_rad * 100) + 1)] for j in range(int(max_rad * 100) + 1)]

is_exsits_cache = False

phi_cache = [() for i in range(int(max_rad * 100 + 1))]
theta_cache = [() for i in range(int(max_rad * 100 + 1))]
a_cache = [() for i in range(int(max_rad * 100 + 1))]
b_cache = [() for i in range(int(max_rad * 100 + 1))]

def render_frame(A, B):
    """
    Render the donut
    A: Rotate x axis rad
    B: Rotate z axis rad
    """
    if len(screen_cache[int(A * 100)][int(B * 100)]) != 0:
        output = screen_cache[int(A * 100)][int (B * 100)]
        os.system('cls')
        for y in range(screen_height):
            for x in range(screen_width):
                sys.stdout.write(output[x][y])
            sys.stdout.write('\n')
        sys.stdout.flush()
        return

    zbuffer = np.zeros((screen_width, screen_height))
    output  = np.full((screen_width, screen_height), ' ')
    
    # precompute
    if len(a_cache[int(A * 100)]) == 0:
        cache = (math.sin(A), math.cos(A))
        a_cache[int(A * 100)] = cache
    cache = a_cache[int(A * 100)]
    sinA = cache[0]
    cosA = cache[1]
    if len(b_cache[int(B * 100)]) == 0:
        cache = (math.sin(B), math.cos(B))
        b_cache[int(B * 100)] = cache
    cache = b_cache[int(B * 100)]
    sinB = cache[0]
    cosB = cache[1]

    global is_exsits_cache
    theta = 0
    while theta <= max_rad:
        # precompute
        if not(is_exsits_cache):
            cache = (math.sin(theta), math.cos(theta))
            theta_cache[int(theta * 100)] = cache
        cache = theta_cache[int(theta * 100)]
        sintheta = cache[0]
        costheta = cache[1]
        circlex = R2 + R1 * costheta
        circley = R1 * sintheta

        phi = 0
        while phi <= max_rad:
            # precompute
            if not(is_exsits_cache):
                cache = (math.sin(phi), math.cos(phi))
                phi_cache[int(phi * 100)] = cache
            cache = phi_cache[int(phi * 100)]
            sinphi = cache[0]
            cosphi = cache[1]

            # debug compute donut
            # dx = circlex * cosphi
            # dy = circley
            # dz = -circlex * sinphi

            # debug compute x, y, z
            # x = dx * cosB - dy * sinB
            # y = dx * cosA * sinB + dy * cosA * cosB - dz * sinA
            # z = dx * sinA * sinB + dy * sinA * cosB + dz * cosA

            # compute x, y, z
            x = circlex * (cosB * cosphi + sinA * sinB * sinphi) - circley * cosA * sinB
            y = circlex * (cosphi * sinB - cosB * sinA * sinphi) + circley * cosA * cosB
            z = cosA * circlex * sinphi + circley * sinA

            # add K2 and compute z position
            z += K2

            # compute z ^ -1
            ooz = 1 / z

            # compute x dash, y dash
            xdash = round(K1 * x * ooz)
            ydash = round((K1 / 2) * y * ooz)

            # xpos = (screen_width) / 2, ypos = (screen_height) / 2
            # compute x position and y position
            xpos = round((screen_width)  / 2) + xdash
            ypos = round((screen_height) / 2) - ydash

            # compute luminance (max = sqrt(2))
            L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta + cosB * (cosA * sintheta - costheta * sinA * sinphi)

            # seek display character
            if L > 0 and not(xpos > screen_width or ypos > screen_height or xpos < 0 or ypos < 0):
                if xpos > screen_width or ypos > screen_height:
                    pass
                elif ooz > zbuffer[xpos][ypos]:
                    zbuffer[xpos][ypos] = ooz
                    luminance_index = round(L * 8)
                    output[xpos][ypos] = ".,-~:;=!*#$@"[luminance_index]
            phi += phi_spacing
        theta += theta_spacing

    is_exsits_cache = True
    # os.system('cls')
    sys.stdout.write("\x1b[H")
    for y in range(screen_height):
        for x in range(screen_width):
            sys.stdout.write(output[x][y])
        sys.stdout.write('\n')
    sys.stdout.flush()
    screen_cache[int(A * 100)][int(B * 100)] = output

if __name__ == "__main__":
    A = 0
    B = 0
    A_spacing = 0.04 # default 0.04
    B_spacing = 0.04 # default 0.02
    while True:
        if A > max_rad:
            A = 0
        if B > max_rad:
            B = 0
        render_frame(A, B)
        A += A_spacing
        B += B_spacing
