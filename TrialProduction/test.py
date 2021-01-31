import random
class A:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

class B(A):
    @classmethod
    def instance(cls):
        return super.instance()

    def say_hello(self):
        print("Hello")


a = A.instance()
print(type(a))
b = B.instance()
print(type(b))
b.say_hello()
