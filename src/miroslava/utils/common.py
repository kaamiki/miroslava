"""Collection of common utilities."""

import os
from threading import Lock

from miroslava.config import colors
from miroslava.config.internal import IS_WINDOWS

__all__ = ["Singleton", "TTYPalette", "tty_colors"]


class Singleton(type):
    """A `thread-safe` implementation of Singleton design pattern.

    Singleton is a creational design pattern, which ensures that only
    a single object of its kind exist and provides a single point of
    access to it for any other code.

    The below is a `thread-safe` implementation of the Singleton design
    pattern. This will let the users instantiate the derived class
    multiple times and still would refer to the same object.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        instances (dict): Instances of class that have initialise.
        lock (Lock): Thread lock object.

    Examples:
        >>> class SomeClass(metaclass=Singleton):
        ...     pass
        ...
        >>> x1 = SomeClass()
        >>> x2 = SomeClass()
        >>> x1
        <__main__.SomeClass object at 0x7f3f2d7db820>
        >>> x2
        <__main__.SomeClass object at 0x7f3f2d7db820>
        >>> x1 is x2
        True
        >>>

    References:
        [1] See https://stackoverflow.com/q/6760685 for more ways for
            implementing singletons in code.
        [2] See https://refactoring.guru/design-patterns/singleton/python/example
            for better understanding of the below implementation.

    """

    instances = {}
    lock = Lock()

    def __call__(cls, *args, **kwargs):
        """Callable singleton instance."""
        with cls.lock:
            if cls not in cls.instances:
                cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]


tty_color_check = lambda x: x.isupper() and x.startswith("TTY")
tty_colors = (color for color in dir(colors) if tty_color_check(color))


class TTYPalette(object):
    """Color palette for TTY.

    The class provides about 200+ color unique color options to use
    from on a TTY interface.

    Reference:
        [1] See https://stackoverflow.com/a/64222858/14316408 for
            rendering colors on Windows TTY (both Powershell and CMD)

    See Also:
        miroslava.config.colors:
            Module which contains all the available colors for TTY.

    """

    if IS_WINDOWS:
        os.system("color")
    for tty_color in tty_colors:
        locals()[tty_color[10:]] = getattr(colors, tty_color)
    del tty_color
