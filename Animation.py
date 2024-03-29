import math
import sys
import shutil
import os
import numpy as np
import abc

SCREEN_WIDTH = shutil.get_terminal_size().columns
SCREEN_HEIGHT = shutil.get_terminal_size().lines

MAX_RAD = 2 * math.pi

K1 = 30


class ThreeDimensionalObject(object, metaclass=abc.ABCMeta):
    """ 3Dオブジェクトを計算するクラス """

    @abc.abstractmethod
    def compute_frame(self, A, B):
        """ 最大2軸方向への計算が可能 """
        pass


class Donut(ThreeDimensionalObject):
    # Small circle radius
    R1 = 1
    # Big circle radius
    R2 = 2

    # Distance between screen and eye
    K2 = 5

    theta_spacing = 0.07
    phi_spacing = 0.02

    screen_notes = [[None for i in range(int(MAX_RAD * 100) + 1)]
                    for j in range(int(MAX_RAD * 100) + 1)]

    def compute_frame(self, A, B):
        """ A: X軸, B: Y軸 """
        note_a = int(A * 100)
        note_b = int(B * 100)
        if not (self.screen_notes[note_a][note_b] is None):
            return self.screen_notes[note_a][note_b]

        # zbuffer
        zbuffer = np.zeros((SCREEN_WIDTH, SCREEN_HEIGHT))
        # screen contents
        output = np.full((SCREEN_WIDTH, SCREEN_HEIGHT), ' ')

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
            circlex = self.R2 + self.R1 * costheta
            circley = self.R1 * sintheta

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
                zpos = z + self.K2

                # compute zpos ^ -1
                ooz = 1 / zpos

                # Compute xdash, ydash(scree上においての座標)
                xdash = round(K1 * x * ooz)
                ydash = round((K1 / 2) * y * ooz)

                # Compute x position, y position
                # xpos = (screen_width) / 2, ypos = (screen_height) / 2
                xpos = round((SCREEN_WIDTH) / 2) + xdash
                ypos = round((SCREEN_HEIGHT) / 2) - ydash

                # Compute luminance(L <= sqrt(2))
                L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta
                + cosB * (cosA * sintheta - costheta * sinA * sinphi)

                # Seek display character
                if L > 0 and ooz > zbuffer[xpos][ypos]:
                    zbuffer[xpos][ypos] = ooz
                    luminance_index = round(L * 8)
                    output[xpos][ypos] = ".,-~:;=!*#$@"[luminance_index]

                phi += self.phi_spacing
            theta += self.theta_spacing

        # Store result
        self.screen_notes[note_a][note_b] = output
        return output


class ASCIIAnimation:
    """ アニメーションを表示するクラス """
    A_spacing = 0
    B_spacing = 0
    clear_type = None
    obj = None

    def render_forever(self):
        A = 0
        B = 0

        while True:
            if A > MAX_RAD:
                A = 0
            if B > MAX_RAD:
                B = 0

            output = self.obj.compute_frame(A, B)
            self.render_frame(output)

            A += self.A_spacing
            B += self.B_spacing

    def render_frame(self, output):
        self.clear_type.clear()
        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                sys.stdout.write(output[x][y])
            sys.stdout.write(os.linesep)
        sys.stdout.flush()


class Main(ASCIIAnimation):
    """
    以下の二つの要素はそれぞれX軸、Z軸の回転速度を表します。
    0以上6.28以下で任意の値を設定できます。
    0を設定するとその軸の回転が止まります。
    """
    A_spacing = 0.04
    B_spacing = 0.04

    def start(self):
        self.process_arguments()
        self.render_forever()

    def process_arguments(self):
        args = sys.argv
        objtype = ""
        cleartype = ""
        if len(args) == 3:
            objtype = args[1]
            cleartype = args[2]
        else:
            objtype = "donut"
            cleartype = "win"

        obj = self.create_object(objtype)
        clear_type = self.create_clear_type(cleartype)

        if obj is None or clear_type is None:
            self.show_error_message()
            sys.exit(0)

        self.obj = obj
        self.clear_type = clear_type

    def create_object(self, objtype):
        if objtype == "donut":
            return Donut()
        return None

    def create_clear_type(self, cleartype):
        if cleartype == "escape":
            return EscapeCharacter.instance()
        elif cleartype == "win":
            return WinCommand.instance()
        elif cleartype == "linux":
            return LinuxUnixCommand.instance()
        return None

    def show_error_message(self):
        print("コマンドライン引数が無効です。")
        print("第一引数：オブジェクトのタイプ (donut)")
        print("第二引数：文字を削除する方法 (escape or win or linux)")


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
    Main().start()
