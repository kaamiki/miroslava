from miroslava.utils import Singleton, TTYPalette


class TestSingletonClass(metaclass=Singleton):
    pass


def test_singleton():
    x1 = TestSingletonClass()
    x2 = TestSingletonClass()
    assert x1 is x2
    assert x1 == x2


def test_ttypalette():
    orange = TTYPalette.ORANGE_1
    plum = TTYPalette.PLUM_1
    assert orange == "\u001b[38;5;214m"
    assert plum == "\u001b[38;5;219m"
