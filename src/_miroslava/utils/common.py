"""Common: Collection of commonly used tools and attributes."""

import os
from threading import Lock
from typing import Any
from typing import Dict

from _miroslava import palette

__all__ = ["SingletonMeta", "TTYPalette"]


class SingletonMeta(type):
    """Thread-safe implementation of singleton design pattern.

    It ensures only a ``single instance`` of the class is available
    at runtime. See singletons_ in python and their implementations_.

    .. code-block:: python

        class Foo(metaclass=SingletonMeta):

            def __init__(self):
                pass

    .. _singletons: https://refactoring.guru/design-patterns/singleton/python/example
    .. _implementations: https://stackoverflow.com/q/6760685

    """

    instances: Dict["SingletonMeta", type] = {}
    lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> type:
        """Callable singleton instance."""
        with cls.lock:
            if cls not in cls.instances:
                cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]


class TTYPalette(object):
    """Color palette for TTY.

    This provides more than **200** unique color options to use on a
    TTY interface. See how ANSI escapes work on `Windows TTY`_ shell.

    .. _Windows TTY: https://stackoverflow.com/a/64222858/14316408

    """

    colors = (
        color
        for color in dir(palette)
        if color.isupper() and color.startswith("TTY")
    )

    if os.name == "nt":
        os.system("color")
    for color in colors:
        locals()[color[10:]] = getattr(palette, color)
    del color
