"""Miroslava logger."""

import logging
import os
import re
from typing import Optional, Tuple

from miroslava.config.internal import (
    LOGGING_ATTR_RE,
    LOGGING_DATETIME_FMT,
    LOGGING_EXC_FMT,
    LOGGING_MSG_FMT,
    PATH_SEP,
)
from miroslava.utils.common import Singleton

__all__ = ["Formatter"]

# NOTE: Most of the docstring is referenced from the original
# logging module as we are not changing the behavior of the
# underlying implementation but rather adding some level of
# simplicity, scalability and flexibility that is required in
# most of the development cases.


class Formatter(logging.Formatter, metaclass=Singleton):
    """Formatter to convert a LogRecord to text.

    A Formatter need to know how a LogRecord is constructed. They are
    responsible for converting a LogRecord to (usually) a string which
    can be interpreted by either a human or an external system.

    This Formatter class allows uniform formatting across various
    logging levels using the formatting string provided to it. If None
    is provided, default template would be used.

    The Formatter can be initialized with a format string which makes
    use of knowledge of the LogRecord attributes and thus provides an
    extension for logging the records and traceback information in a
    graceful manner.

    The default formatting template is inspired by the `SprintBoot`
    framework.

    Args:
        fmt (str, optional): Logging format. Defaults to `LOGGING_MSG_FMT`.
        datefmt (str, optional): Logging datetime format. Defaults to
            `LOGGING_DATETIME_FMT`.
        traceback (bool): Whether to format log messages with traceback.
            Defaults to False.

    Attributes:
        fmt (str): Logging format. Defaults to `LOGGING_MSG_FMT`.
        datefmt (str): Logging datetime format. Defaults to
            `LOGGING_DATETIME_FMT`.
        traceback (bool): Whether to format log messages with traceback.
            Defaults to False.
        limit (int): Limit the length of pathname attribute.

    See Also:
        logging.Formatter:
            Logging formatter class from standard library.
        miroslava.config.internals:
            Module which holds all the constants i.e. all the logging
            formats, regex used and fs path separator.
        miroslava.utils.common.Singleton:
            A thread-safe implementation of Singleton design pattern.

    """

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        traceback: bool = False,
    ) -> None:
        if not fmt:
            fmt = LOGGING_MSG_FMT
        if not datefmt:
            datefmt = LOGGING_DATETIME_FMT
        self.fmt = fmt
        self.datefmt = datefmt
        self.traceback = traceback
        self.limit = re.findall(LOGGING_ATTR_RE.format("pathname"), self.fmt)
        self.limit = int(self.limit[0]) - 3

    def formatException(self, ei: Tuple) -> str:
        """Format and return the specified exception information
        as a string.

        Please note that this implementation does not work directly.
        The standard `logging.Formatter()` is needed for creating the
        `str` format of the logged record. This adds unnecessary `\n`
        characters to the output which needs to be skipped.

        Args:
            ei (_SysExcInfoType): Exception message to log.
                _SysExcInfoType = Tuple(type, BaseException, TracebackType)

        Returns:
            str: Formatted exception string.

        """
        exc_cls, exc_msg, exc_tbk = ei
        exc_fnc = exc_tbk.tb_frame.f_code.co_name
        exc_obj = "on" if exc_fnc == "<module>" else f"in {exc_fnc}() on"
        exc_tbk = exc_obj, exc_tbk.tb_lineno
        return LOGGING_EXC_FMT.format(exc_cls.__name__, exc_msg, *exc_tbk)

    def formatPath(self, path: str) -> str:
        """Format path with module-like structure.

        This formatting function ensures that the `pathname` attribute
        follows the standard pattern similar to that of `SprintBoot`
        framework.

        If the `Logger` is called from a module, the absolute path of
        the module would be considered and if triggered via the shell or
        the interpreter (stdin), `shell` would be returned.

        Args:
            path (str): Pathname of the log event.

        Returns:
            str: Formatted pathname value.

        """
        if path == "<stdin>":
            return "shell"
        path = path[:-3].replace(os.path.abspath(os.curdir), "")
        path = path[path[0] == PATH_SEP :].replace(PATH_SEP, ".")
        if len(path) > self.limit:
            path = "..." + path[-self.limit :]
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
        record.pathname = self.formatPath(record.pathname)
        if record.funcName != "<module>" and record.pathname != "shell":
            record.pathname += f".{record.funcName}()"
        out = logging.Formatter(self.fmt, self.datefmt).format(record)
        if not self.traceback:
            if record.exc_text:
                out, *_ = out.replace(
                    str(record.exc_info[1]),
                    self.formatException(record.exc_info),
                ).partition("Traceback")
        return out.strip("\n")
