"""Miroslava logger."""

import logging
import sys
from typing import IO, Dict, Optional, Tuple

from miroslava.config.internal import (
    LOGGER_DATETIME_FMT,
    LOGGER_EXC_FMT,
    LOGGER_MSG_FMT,
    PATH_SEP,
)
from miroslava.utils.common import Singleton, TTYPalette

# NOTE: Most of the docstring is referenced from the original logging
# module since this logger does not intent to change the behavior of
# the underlying implementation but rather adds some level of simplicity
# and flexibility that is required in most of the development cases.

_tty_levels = {
    logging.CRITICAL: TTYPalette.RED_1,
    logging.ERROR: TTYPalette.DARK_ORANGE,
    logging.WARNING: TTYPalette.YELLOW,
    logging.INFO: TTYPalette.GREEN_1,
    logging.DEBUG: TTYPalette.GREY_50,
    logging.NOTSET: TTYPalette.AQUA,
}

_tty_reset = TTYPalette.DEFAULT


class Formatter(logging.Formatter, metaclass=Singleton):
    """Formatter to convert the LogRecord to text.

    A Formatter need to know how the LogRecord is constructed. It is
    responsible for converting the LogRecord to (usually) a string which
    can be interpreted by either a human or an external system.

    This Formatter class allows uniform formatting across various
    logging levels using the message format provided to it. If None
    is provided, default template would be used.

    The Formatter can be initialized with a format string which makes
    use of knowledge of the LogRecord attributes and thus provides an
    extension for logging the records and traceback information in a
    graceful manner.

    The default formatting template is inspired by the `Spring Boot`
    framework.

    Args:
        log_fmt (str, optional): Logging message format.
            Defaults to `LOGGER_MSG_FMT`.
        date_fmt (str, optional): Logging datetime format. Defaults to
            `LOGGER_DATETIME_FMT`.

    Attributes:
        default_fmt (bool): Whether default format is used or not.
        log_fmt (str): Logging message format.
            Defaults to `LOGGER_MSG_FMT`.
        date_fmt (str): Logging datetime format. Defaults to
            `LOGGER_DATETIME_FMT`.

    See Also:
        logging.Formatter:
            Logging formatter class from standard library.
        miroslava.config.internals:
            Module which holds all the constants used in the Formatter.
        miroslava.utils.common.Singleton:
            A thread-safe implementation of Singleton design pattern.

    """

    def __init__(
        self,
        log_fmt: Optional[str] = None,
        date_fmt: Optional[str] = None,
    ) -> None:
        self.default_fmt = False
        if not log_fmt:
            log_fmt = LOGGER_MSG_FMT
            self.default_fmt = True
        if not date_fmt:
            date_fmt = LOGGER_DATETIME_FMT
        self.log_fmt = log_fmt
        self.date_fmt = date_fmt

    def formatException(self, ei: Tuple) -> str:
        """Format and return the specified exception information
        as a string.

        Please note that this implementation does not work directly.
        The standard `logging.Formatter()` is needed for creating the
        `str` format of the logged record which adds unnecessary `\n`
        characters to the output which needs to be skipped.

        Args:
            ei (_SysExcInfoType): Exception message to log.
                _SysExcInfoType = Tuple(type, BaseException, TracebackType)

        Returns:
            str: Formatted exception string without `\n` characters.

        """
        exc_cls, exc_msg, exc_tbk = ei
        exc_fnc = exc_tbk.tb_frame.f_code.co_name
        exc_obj = "on" if exc_fnc == "<module>" else f"in {exc_fnc}() on"
        exc_tbk = exc_obj, exc_tbk.tb_lineno
        return LOGGER_EXC_FMT.format(exc_cls.__name__, exc_msg, *exc_tbk)

    def formatPath(self, path: str, fnc: str, limit: int = 27) -> str:
        """Format path with module-like structure.

        This formatting function ensures that the `pathname` attribute
        follows the standard pattern similar to that of `Spring Boot`
        framework.

        If the `Logger` is called from a module, the absolute path of
        the module would be considered and if triggered via the shell or
        the interpreter (stdin), `shell` would be returned.

        Args:
            path (str): Pathname of the logged event.
            fnc (str): Function (callable instance) of the logged event.

        Returns:
            str: Formatted pathname value.

        """
        if path == "<stdin>":
            return "shell"
        path = path[path[0] == PATH_SEP : -3].replace(PATH_SEP, ".")
        if fnc != "<module>":
            path += f".{fnc}()"
        if len(path) > limit:  # maximum limit
            path = "..." + path[-limit:]
        return path

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified record as text.

        If there is exception information, it is formatted using the
        `formatException()` and replaced with the original message.

        Args:
            record (LogRecord): Instance of an event being logged.

        Returns:
            str: Formatted log output.

        """
        if self.default_fmt:
            record.caller = self.formatPath(record.pathname, record.funcName)
        if record.exc_info:
            record.msg = self.formatException(record.exc_info)
            record.exc_info = record.exc_text = None
        return logging.Formatter(self.log_fmt, self.date_fmt).format(record)


class StreamHandler(logging.StreamHandler, metaclass=Singleton):
    """Add colors to the TTY interface.

    A handler class which writes logging records, color formatted, to
    a stream. Note that this class does not close the stream, as
    sys.stdout or sys.stderr may be used.

    Args:
        stream (IO): IO stream. Defaults to sys.stdout.
        only_level (bool): Whether to colorize only the levels.
            Defaults to True.
        **kwargs: Keyword list of log attrs and colors.

    Attributes:
        only_level (bool): Whether to colorize only the levels.
            Defaults to True.
        **kwargs: Keyword list of log attrs and colors.

    Returns:
        str: Color formatted log output.

    See Also:
        logging.StreamHandler:
            Logging handler class from standard library.
        miroslava.utils.common.Singleton:
            A thread-safe implementation of Singleton design pattern.
        miroslava.config.common.TTYPalette:
            Class which provides color codes for a TTY interface.

    """

    def __init__(
        self,
        stream: Optional[IO[str]] = sys.stdout,
        *,
        only_level: bool = True,
        **kwargs: Dict[str, str],
    ) -> None:
        self.only_level = only_level
        self.kwargs = {k: getattr(TTYPalette, v) for k, v in kwargs.items()}
        super().__init__(stream=stream)

    def format(self, record: logging.LogRecord) -> str:
        """Format the attrs with colors.

        Args:
            record (LogRecord): Instance of an event being logged.

        Returns:
            str: Color formatted log output.

        """
        out = logging.StreamHandler.format(self, record)
        if self.only_level:
            out = out.replace(
                record.levelname,
                _tty_levels[record.levelno] + record.levelname + _tty_reset,
            )
            return out
        for key, value in self.kwargs.items():
            if hasattr(record, key):
                attr = str(getattr(record, key))
                out = out.replace(attr, value + attr + _tty_reset)
        return out
