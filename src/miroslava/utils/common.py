"""Collection of common utilities."""

import os
from threading import Lock
from typing import Any
from typing import Dict

from miroslava.config import colors
from miroslava.config.internal import WINDOWS_OS

__all__ = ["Singleton", "TTYPalette", "tty_colors"]


class Singleton(type):
    r"""Thread-safe implementation of singleton design pattern.

    It ensures only a ``single instance`` of the class is available
    at runtime. See singletons_ in python and their implementations_.

    To incorporate Singleton in a class, use it like a ``metaclass``.

    .. code-block:: python

        class Foo(metaclass=Singleton):

            def __init__(self):
                pass

    .. _singletons: https://refactoring.guru/design-patterns/singleton/python/example
    .. _implementations: https://stackoverflow.com/q/6760685

    """

    instances: Dict["Singleton", type] = {}
    lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> type:
        """Callable singleton instance."""
        with cls.lock:
            if cls not in cls.instances:
                cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]


tty_color_check = lambda x: x.isupper() and x.startswith("TTY")
tty_colors = (color for color in dir(colors) if tty_color_check(color))


class TTYPalette(object):
    r"""Color palette for TTY.

    This provides more than **200** unique color options to use on a
    TTY interface. See how ANSI escapes work on `Windows TTY`_ shell.

    .. _Windows TTY: https://stackoverflow.com/a/64222858/14316408

    """

    if WINDOWS_OS:
        os.system("color")
    for tty_color in tty_colors:
        locals()[tty_color[10:]] = getattr(colors, tty_color)
    del tty_color
