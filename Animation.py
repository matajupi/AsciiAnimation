import math
import sys
import shutil
import os
import numpy as np
import abc
import random
from collections import namedtuple

# Reference site https://www.a1k0n.net/2011/07/20/donut-math.html

SCREEN_WIDTH  = shutil.get_terminal_size().columns
SCREEN_HEIGHT = shutil.get_terminal_size().lines

MAX_RAD = 2 * math.pi

class ThreeDimensionalObject(object, metaclass=abc.ABCMeta):
    """ 3D Object """
    # Distance between object and eye
    # If you want to change size, you can update this value
    K2 = 5

    # X, Y, Z軸の回転角度を保持
    Xrad = 0.0
    Yrad = 0.0
    Zrad = 0.0

    # X, Y, Z軸の位置を保持
    Xpos = 0.0
    Ypos = 0.0
    Zpos = 0.0

    # 所属するCanvas
    canvas = None
    # 計算結果を保持する

    @abc.abstractmethod
    def next_frame(self):
        pass

    @abc.abstractmethod
    def has_next(self):
        pass

class Donut1(ThreeDimensionalObject):
    Xspacing = None
    Zspacing = None

    theta_spacing = 0.07
    phi_spacing   = 0.02

    R1 = 1
    R2 = 2

    storage = [[[] for i in range(int(MAX_RAD * 100) + 1)]
              for j in range(int(MAX_RAD * 100) + 1)]

    def __init__(self, xspa, zspa):
        self.Xspacing = xspa
        self.Zspacing = zspa
        self.Xpos = SCREEN_WIDTH / 2
        self.Ypos = SCREEN_HEIGHT / 2

    def next_frame(self):
        if self.Xrad > MAX_RAD:
            self.Xrad = 0
        if self.Zrad > MAX_RAD:
            self.Zrad = 0

        xnum = int(self.Xrad * 100)
        znum = int(self.Zrad * 100)

        if not(self.storage[xnum][znum]):
            points = self.compute_frame()
            self.storage[xnum][znum] = points

        val = self.storage[xnum][znum]

        for v in val:
            self.canvas.set_output(v[0], v[1])

        self.Xrad += self.Xspacing
        self.Zrad += self.Zspacing

    def has_next(self):
        return True

    def compute_frame(self):
        points = []

        # precompute
        sinX = math.sin(self.Xrad)
        cosX = math.cos(self.Xrad)
        sinZ = math.sin(self.Zrad)
        cosZ = math.cos(self.Zrad)

        theta = 0
        while theta <= MAX_RAD:
            # precompute
            sintheta = math.sin(theta)
            costheta = math.cos(theta)
            circlex = self.R2 + self.R1 * costheta
            circley = self.R1 * sintheta

            phi = 0
            while phi <= MAX_RAD:
                #precompute
                sinphi = math.sin(phi)
                cosphi = math.cos(phi)

                # compute x, y, z
                # formular from https://www.a1k0n.net/2011/07/20/donut-math.html
                x = circlex * (cosZ * cosphi + sinX * sinZ * sinphi) - circley * cosX * sinZ
                y = circlex * (cosphi * sinZ - cosZ * sinX * sinphi) + circley * cosX * cosZ
                z = cosX * circlex * sinphi + circley * sinX

                # compute z position
                z += self.K2

                # compute z ^ -1
                ooz = 1 / z

                # compute x dash, y dash
                xdash = round(self.canvas.K1 * x * ooz)
                ydash = round((self.canvas.K1 / 2) * y * ooz)

                # compute x position, y position
                xpos = round(self.Xpos) + xdash
                ypos = round(self.Ypos) - ydash

                # compute luminance (L <= sqrt(2))
                L = cosphi * costheta * sinZ - cosX * costheta * sinphi - sinX * sintheta 
                + cosZ * (cosX * sintheta - costheta * sinX * sinphi)

                points.append(((xpos, ypos, z), L))

                phi += self.phi_spacing
            theta += self.theta_spacing

        return points


class ASCIIAnimationCanvas(object, metaclass=abc.ABCMeta):
    """ 3Dオブジェクトが所属する仮想空間 """
    # Distance between screen and eye
    K1 = 30
    objects = []
    display = None

    @abc.abstractmethod
    def start(self):
        pass

    def set_output(self, point, luminance):
        x = point[0]
        y = point[1]
        z = point[2]
        ooz = 1 / z
        if luminance > 0:
            if ooz > self.zbuffer[x][y]:
                self.zbuffer[x][y] = ooz
                luminance_index = round(luminance * 8)
                self.output[x][y] = ".,-~:;=!*#$@"[luminance_index]

    def animation(self):
        is_continue = True
        while is_continue:
            self.zbuffer = np.zeros((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.output = np.full((SCREEN_WIDTH, SCREEN_HEIGHT), ' ')
            is_continue = self.change_frame()
            self.display.render_frame()

    def change_frame(self):
        flag = False
        for o in self.objects:
            flag = flag or o.has_next
            if o.has_next:
                o.next_frame()
        return flag


class CustomCanvas(ASCIIAnimationCanvas):
    def start(self):
        """ 実質メインエントリーポイント """
        self.display = Terminal()
        self.display.canvas = self
        self.display.clear_type = WinCommand.instance()
        d = Donut1(0.04, 0)
        d.canvas = self
        self.objects.append(d)
        self.animation()

   

class Display(object, metaclass=abc.ABCMeta):
    """ 3Dオブジェクトを描画するための抽象クラス """
    canvas = None

    @abc.abstractmethod
    def render_frame(self):
        pass

class Terminal(Display):
    """ ターミナル上で3Dオブジェクトを描画するためのクラス """
    clear_type = None

    def render_frame(self):
        self.clear()
        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                sys.stdout.write(self.canvas.output[x][y])
            sys.stdout.write(os.linesep)
        sys.stdout.flush()

    def clear(self):
        self.clear_type.clear()

class ClearType(object, metaclass=abc.ABCMeta):
    """ ターミナルに書かれた文字を削除する方法を表すクラス """
    @abc.abstractmethod
    def clear(self):
        pass

# Singleton
class EscapeCharacter(ClearType):
    _instance = None
    def __init__(self):
        raise RuntimeError("This class is singleton. Please use instance() class method.")
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def clear(self):
        sys.stdout.write("\x1b[H")
        sys.stdout.flush()

# Singleton
class WinCommand(ClearType):
    _instance = None
    def __init__(self):
        raise RuntimeError("This class is singleton. Please use instance() class method.")
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def clear(self):
        os.system("cls")

# Singleton
class LinuxUnixCommand(ClearType):
    _instance = None
    def __init__(self):
        raise RuntimeError("This class is singleton. Please use instance() class method.")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def clear(self):
        os.system("clear")

if __name__ == "__main__":
    CustomCanvas().start()
