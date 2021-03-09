import pytest
from miroslava.utils import Singleton
from miroslava.utils import TTYPalette


class TestSingletonClass(metaclass=Singleton):
    pass


def test_singleton() -> None:
    x1 = TestSingletonClass()
    x2 = TestSingletonClass()
    assert x1 is x2
    assert x1 == x2


@pytest.mark.parametrize(
    ("color", "code"),
    (
        ("GOLD_1", "\u001b[38;5;220m"),
        ("ORANGE_1", "\u001b[38;5;214m"),
        ("PLUM_1", "\u001b[38;5;219m"),
    ),
)
def test_ttypalette(color: str, code: str) -> None:
    assert getattr(TTYPalette, color) == code
