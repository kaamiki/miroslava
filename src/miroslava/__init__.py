"""Miroslava: A simple sandbox environment."""

try:
    from ._about import __version__
except ImportError:
    __version__ = "0.0.0"

from _miroslava import palette
from _miroslava.track import BaseProtocol
from _miroslava.utils import FileHandler
from _miroslava.utils import Formatter
from _miroslava.utils import Handler
from _miroslava.utils import Logger
from _miroslava.utils import MiroslavaError
from _miroslava.utils import RotatingFileHandler
from _miroslava.utils import SingletonMeta
from _miroslava.utils import StreamHandler
from _miroslava.utils import StreamHandlerHinter
from _miroslava.utils import TimedRotatingFileHandler
from _miroslava.utils import TTYPalette
from _miroslava.utils import create_logger
from _miroslava.utils import get_logger
from _miroslava.utils import stderr
from _miroslava.utils import stdout

__all__ = [
    "palette",
    "BaseProtocol",
    "FileHandler",
    "Formatter",
    "Handler",
    "Logger",
    "MiroslavaError",
    "RotatingFileHandler",
    "SingletonMeta",
    "StreamHandler",
    "StreamHandlerHinter",
    "TimedRotatingFileHandler",
    "TTYPalette",
    "create_logger",
    "get_logger",
    "stderr",
    "stdout",
]
