import math
import sys
import shutil
import os
import numpy as np

SCREEN_WIDTH  = shutil.get_terminal_size().columns
SCREEN_HEIGHT = shutil.get_terminal_size().lines

MAX_RAD = math.pi * 2

theta_spacing = 0.07
phi_spacing   = 0.02

# Small circle radius
R1 = 1
# Big circle radius
R2 = 2

# Distance between object and eye
K2 = 5
# Distance between screen and eye
K1 = 30

screen_notes = [[None for i in range(int(MAX_RAD * 100) + 1)]
                    for j in range(int(MAX_RAD * 100) + 1)]

"""
以下の二つの要素はそれぞれX軸、Z軸の回転速度を表します。
0以上6.28以下で任意の値を設定できます。
0を設定するとその軸の回転が止まります。
"""
A_spacing = 0.04
B_spacing = 0.04

""" 
画面上の文字列を削除する方法の指定
escape: エスケープ文字により削除します（推奨）。ターミナルによっては使用できないものもあります。
win: Windowsコマンドにより削除します。
linux: LinuxもしくはUnixコマンドにより削除します。
"""
clear_type = "escape"

def render_forever():
    A = 0
    B = 0
    
    while True:
        if A > MAX_RAD:
            A = 0
        if B > MAX_RAD:
            B = 0
        output = compute_frame(A, B)
        render_frame(output)
        A += A_spacing
        B += B_spacing

def render_frame(output):
    if clear_type == "escape":
        sys.stdout.write("\x1b[H")
    elif clear_type == "win":
        os.system('cls')
    elif clear_type == "linux":
        os.system('clear')
    
    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            sys.stdout.write(output[x][y])
        sys.stdout.write(os.linesep)
    sys.stdout.flush()

def compute_frame(A, B):
    note_a = int(A * 100)
    note_b = int(B * 100)
    if not(screen_notes[note_a][note_b] is None):
        return screen_notes[note_a][note_b]
    
    # zbuffer
    zbuffer = np.zeros((SCREEN_WIDTH, SCREEN_HEIGHT))
    # screen contents
    output  = np.full((SCREEN_WIDTH, SCREEN_HEIGHT), ' ')

    # Precompute
    sinA = math.sin(A)
    cosA = math.cos(A)
    sinB = math.sin(B)
    cosB = math.cos(B)

    theta = 0
    while theta <= MAX_RAD:
        # Precompute
        sintheta = math.sin(theta)
        costheta = math.cos(theta)
        circlex = R2 + R1 * costheta
        circley = R1 * sintheta

        phi = 0
        while phi <= MAX_RAD:
            # Precompute
            sinphi = math.sin(phi)
            cosphi = math.cos(phi)

            # Compute x, y, z
            x = circlex * (cosB * cosphi + sinA * sinB * sinphi) - circley * cosA * sinB
            y = circlex * (cosphi * sinB - cosB * sinA * sinphi) + circley * cosA * cosB
            z = cosA * circlex * sinphi + circley * sinA

            # Compute z position
            zpos = z + K2

            # compute zpos ^ -1
            ooz = 1 / zpos

            # Compute xdash, ydash(scree上においての座標)
            xdash = round(K1 * x * ooz)
            ydash = round((K1 / 2) * y * ooz)

            # Compute x position, y position
            # xpos = (screen_width) / 2, ypos = (screen_height) / 2
            xpos = round((SCREEN_WIDTH)  / 2) + xdash
            ypos = round((SCREEN_HEIGHT) / 2) - ydash

            # Compute luminance(L <= sqrt(2))
            L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta 
            + cosB * (cosA * sintheta - costheta * sinA * sinphi)

            # Seek display character
            if L > 0 and ooz > zbuffer[xpos][ypos]:
                zbuffer[xpos][ypos] = ooz
                luminance_index = round(L * 8)
                output[xpos][ypos] = ".,-~:;=!*#$@"[luminance_index]

            phi += phi_spacing
        theta += theta_spacing

    # Store result
    screen_notes[note_a][note_b] = output
    return output

if __name__ == "__main__":
    render_forever()
