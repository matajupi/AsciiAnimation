import math
import sys
import shutil
import os
import numpy as np
import abc
import random
from collections import namedtuple

SCREEN_WIDTH  = shutil.get_terminal_size().columns
SCREEN_HEIGHT = shutil.get_terminal_size().lines

MAX_RAD = 2 * math.pi

ThreeDimensionalPoint = namedtuple("ThreeDimensionalPoint", ["x", "y", "z"])

class ResultStorage:
    """ 一度計算した計算結果を保持するクラス """
    storage = {}
    def has(self, key):
        return key in self.storage

    def get(self, key):
        return self.storage[key]

    def store(self, key, value):
        self.storage[key] = value


class ThreeDimensionalObject(object, metaclass=abc.ABCMeta):
    """ 3D Object """
    # (theta, phi) : (ThreeDimensionalPoint)
    # X, Y, Z軸の回転角度を保持
    X = 0.0
    Y = 0.0
    Z = 0.0
    object_storage = ResultStorage()
    animator = None
    
    def set_animator(self, animator):
        self.animator = animator

    @abc.abstractmethod
    def get_object(self):
        pass

    @abc.abstractmethod
    def compute_luminance(self, point):
        pass

class Donut(ThreeDimensionalObject):
    """ 3D Donut Object """
    R1 = 1
    R2 = 2
    theta_spacing = 0.07
    phi_spacing   = 0.02
    is_computed = False

    def get_object(self):
        if not(self.is_computed):
            self.compute_object()
            is_computed = True
        return [k for k in self.object_storage]

    def compute_object(self):
        theta = 0
        while theta <= MAX_RAD:
            sintheta = math.sin(theta)
            costheta = math.cos(theta)
            circlex = R2 + R1 * costheta
            circley = R1 * sintheta

            phi = 0
            while phi <= MAX_RAD:
                sinphi = math.sin(phi)
                cosphi = math.cos(phi)

                x = circlex * cosphi
                y = circley
                z = -circlex * sinphi
                pos = ThreeDimensionalPoint(x, y, z)
                self.object_storage.store(pos, (theta, phi))

                phi += self.phi_spacing
            theta += self.theta_spacing

    def compute_luminance(self, point, sinA, cosA, sinB, cosB):
        if not(self.object_storage.has(point)):
            raise Exception("ObjectStorage!!")
        pair = self.object_storage.get(point)
        theta = pair[0]
        phi = pair[1]
        sintheta = math.sin(theta)
        costheta = math.cos(theta)
        sinphi = math.sin(phi)
        cosphi = math.cos(phi)
        L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta + cosB * (cosA * sintheta - costheta * sinA * sinphi)
        return L

class Cube(ThreeDimensionalObject):
    """ 3D Cube Object"""
    def get_object(self):
        # TODO: Compute cube frame
        pass

    def compute_object(self):
        pass

    def compute_luminance(self, point):
        pass

class ThreeDimensionalAnimator:
    """ 3Dオブジェクトが所属する仮想空間であり動かすためのAnimator """
    light_point = ThreeDimensionalPoint(0, 1, -1)
    # (A, B) : [*[*char]]
    screen_storage = ResultStorage()
    obj = None
    K1 = 30
    K2 = 5
    A = 0.0
    B = 0.0
    A_spacing = 0.04
    B_spacing = 0.04

    def __init__(self, display, a_spacing=0.04, b_spacing=0.04, K1=30, k2=5):
        self.A_spacing = a_spacing
        self.B_spacing = b_spacing
        self.K1 = K1
        self.K2 = K2

    def set_object(self, obj):
        self.obj = obj
        self.obj.set_animator(self)

    def execute_forever(self):
        # TODO: Compute rotation and draw using Display class
        # write program when spacing < 0
        pass

class Display(object, metaclass=abc.ABCMeta):
    """ 3Dオブジェクトを描画するための抽象クラス """
    @abc.abstractmethod
    def render_frame(self, frame):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

class Terminal(Display):
    """ ターミナル上で3Dオブジェクトを描画するためのクラス """
    clear_type = None

    def set_clear_type(self, clt):
        self.clear_type = clt

    def render_frame(self, frame):
        # TODO: Render processing
        pass

    def clear(self):
        clear_type.clear()

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

class AsciiAnimation(Terminal):
    """ AsciiAnimationアプリケーション """
    def start(self):
        """ アプリ開始時に呼ばれる """
        self.show_start_message()
        a_sp = self.listen_to_spacing("x")
        b_sp = self.listen_to_spacing("y")
        self.clear_type = self.listen_to_clear_type()
        print(a_sp)
        print(b_sp)
        input()
        sys.exit(0)
        animator = ThreeDimensionalAnimator(self, a_sp, b_sp)
        obj = Donut()
        animator.set_object(obj)

    def show_start_message(self):
        print("ASCII Animation !!")

    def listen_to_spacing(self, axis):
        print(f"{axis}軸の回転角度N({MAX_RAD} >= N >= 0)")
        print(f"デフォルト(0.04)に設定したい場合-1を入力。")
        print(f"{axis}軸の回転を止めたい場合0を入力。")
        while True:
            vs = input(f"{axis}軸 >> ")
            try:
                vf = float(vs)
                if vf == -1:
                    return 0.04
                if vf < 0 or vf > MAX_RAD:
                    raise Exception()
                return vf
            except:
                print("入力値が不正です。")

    def listen_to_clear_type(self):
        print(f"ターミナル上の文字を削除するための方法。")
        print(f"エスケープ文字: escape | Windowsコマンド: win | Linux or Unixコマンド: linux")
        print("エスケープ文字を選択した場合多少動きがなめらかになりますがターミナルによっては使用できません。")
        while True:
            clts = input("タイプ >> ")
            if clts == "escape":
                return EscapeCharacter.instance
            elif clts == "win":
                return WinCommand.instance
            elif clts == "linux":
                return LinuxUnixCommand.instance
            else:
                print("入力値が不正です。")

if __name__ == "__main__":
    AsciiAnimation().start()
    input()
