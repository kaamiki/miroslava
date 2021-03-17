"""Logging: Control and capture logs."""

import logging
import logging.handlers
import os
import sys
from datetime import timedelta
from types import TracebackType
from typing import IO
from typing import Any
from typing import MutableMapping
from typing import Optional
from typing import Tuple
from typing import Union

from _miroslava.utils.common import TTYPalette

__all__ = [
    "FileHandler",
    "Formatter",
    "Handler",
    "Logger",
    "RotatingFileHandler",
    "StreamHandler",
    "StreamHandlerHinter",
    "TimedRotatingFileHandler",
    "create_logger",
    "get_logger",
    "stderr",
    "stdout",
]

SysExcInfoType = Tuple[type, BaseException, Optional[TracebackType]]
TupleOfNone = Tuple[None, ...]

logging._levelToName = {
    60: "TRACE",
    50: "FATAL",
    40: "ERROR",
    30: "WARN",
    20: "INFO",
    10: "DEBUG",
    0: "NOTSET",
}

BASIC_FORMAT = (
    "%(asctime)s %(color)s%(levelname)s%(reset)s [%(threadName)s] "
    "%(caller)s:%(lineno)d : %(message)s"
)
EVENT_FORMAT = "%b %d, %y %H:%M:%S"


class Formatter(logging.Formatter):
    """Formatter to convert the LogRecord to colored text.

    This class allows uniform formatting across all the logging levels
    using the log format provided to it. If None is provided, default
    log format is used.

    The class adds colors using log levels.

    :param fmt: Log message format, defaults to None.
    :param datefmt: Log datetime format, defaults to None.
    :var level_style: Dictionary of log levels and associated colors.
    :var reset_style: Color code which resets all styling on TTY.
    :var use_default: Whether to use default format for logging.

    .. note::

        Coloring of the logs currently depends upon the logging level.

    .. seealso::

        :py:meth:`logging.Formatter.format()` and
        :py:meth:`logging.Formatter.formatException` of the logging
        module from python standard library for better understanding.

    .. versionadded:: 1.1.0

        - Support for :py:attr:`record.color` and :py:attr:`record.reset`
          attributes which control the coloring of record components
          using the new :py:meth:`colorize` and :py:meth:`decolorize`
          methods.

        - Support for handling ``lambda`` functions in records.

    """

    level_style = {
        60: TTYPalette.DARK_VIOLET,  # type: ignore[attr-defined]
        50: TTYPalette.RED_1,  # type: ignore[attr-defined]
        40: TTYPalette.ORANGE_RED_1,  # type: ignore[attr-defined]
        30: TTYPalette.YELLOW_3,  # type: ignore[attr-defined]
        20: TTYPalette.GREEN_3,  # type: ignore[attr-defined]
        10: TTYPalette.GREY_50,  # type: ignore[attr-defined]
        0: TTYPalette.AQUA,  # type: ignore[attr-defined]
    }
    reset_style = TTYPalette.DEFAULT  # type: ignore[attr-defined]
    use_default = False

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
    ) -> None:
        """Initialize the formatter."""

        if not fmt:
            fmt = BASIC_FORMAT
            self.use_default = True
        if not datefmt:
            datefmt = EVENT_FORMAT
        self.fmt = fmt
        self.datefmt = datefmt

    def colorize(self, record: logging.LogRecord) -> None:
        """Add colors to the logging levels by manipulating record.

        :param record: Instance of the logged event.

        .. note::

            This behavior only works on the TTY interfaces.

        """

        if getattr(record, "isatty", False):
            record.color = self.level_style[record.levelno]  # type: ignore
            record.reset = self.reset_style  # type: ignore
        else:
            record.color = record.reset = ""  # type: ignore

    def decolorize(self, record: logging.LogRecord) -> None:
        """Remove ``color`` and ``reset`` attributes from a record.

        :param record: Instance of the logged event.

        """

        del record.color  # type: ignore
        del record.reset  # type: ignore

    def formatException(self, ei: Union[SysExcInfoType, TupleOfNone]) -> str:
        r"""Format exception information as text.

        :param ei: Information about the caught exception.
        :return: Formatted exception information string.

        .. note::

            This implementation does not work directly. The standard
            :py:class:`logging.Formatter` is required. It creates an
            output string with **\\n** which need to be skipped.

        """

        func = "<module>"
        lineno = 0
        klass, msg, tback = ei
        if tback:
            func = tback.tb_frame.f_code.co_name
            lineno = tback.tb_lineno
        func = "on" if func == "<module>" else f"in {func}() on"
        return f"{klass.__name__}: {msg} {func} line {lineno}"  # type: ignore

    def format_path(self, path: str, func: str) -> str:
        r"""Format ``record.pathname`` with a module-like structure.

        This ensures that the ``record.pathname`` attribute is formatted much
        like from the logs from **Spring Boot** framework.

        :param path: Pathname of the module which is logging the event.
        :param func: Callable instance which is logging the event.
        :return: *Spring Boot-esque* formatted path.

        .. note::

            If called from a module, the base path of the module would
            be used else **shell** would be returned for the interpreter
            *(stdin)* based input.

        """

        if path == "<stdin>":
            return "shell"
        sep = "site-packages" if "site-packages" in path else os.getcwd()
        path = path.split(sep)[-1].replace(os.path.sep, ".")[
            path[0] != "." : -3
        ]
        if func != "<module>":
            path += f".{func}"
        return path

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as text.

        If any exception is caught then, it is formatted using the
        :py:meth:`formatException` and replaced with the original
        message.

        :param record: Instance of the logged event.
        :return: Captured and formatted output log string.

        """

        if self.use_default or "caller" in self.fmt:
            if record.funcName == "<lambda>":
                record.funcName = "lambda"
            record.caller = self.format_path(  # type: ignore[attr-defined]
                record.pathname, record.funcName
            )
        if record.exc_info:
            record.msg = self.formatException(record.exc_info)
            record.exc_info = record.exc_text = None
        self.colorize(record)
        text = logging.Formatter(self.fmt, self.datefmt).format(record)
        self.decolorize(record)
        return text


class Handler(object):
    """Handler instance which dispatches logging events to streams.

    This is the base handler class which acts as a placeholder to define
    the handler interface. This class can optionally use a formatter
    class to format records as desired.

    :param handler: Handler instance which will output to a stream.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to use for formatting record,
        defaults to :py:class:`Formatter`.

    .. versionadded:: 1.1.0

    """

    def __init__(
        self,
        handler: logging.Handler,
        level: Optional[Union[int, str]] = None,
        formatter: logging.Formatter = Formatter,  # type: ignore[assignment]
    ) -> None:
        """Initialize the handler."""

        self.handler = handler
        self.handler.setFormatter(formatter)
        if level:
            self.handler.setLevel(level)

    def add_handler(self, logger: logging.Logger) -> None:
        """Add handler to the logger object.

        :param logger: Instance of the logging channel.

        """

        logger.addHandler(self.handler)


class FileHandler(Handler):
    """Handler instance which writes logging records to disk files.

    :param filename: Absolute path of the output log file.
    :param mode: Mode in which the file needs to be opened, defaults
        to append.
    :param encoding: Platform-dependent encoding for the file, defaults
        to None.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to use for formatting record,
        defaults to :py:class:`Formatter`.

    .. seealso::

        :py:class:`logging.FileHandler` from the python standard
        library and :py:class:`Handler`.

    .. versionadded:: 1.1.0

    """

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        encoding: Optional[str] = None,
        level: Optional[Union[int, str]] = None,
        formatter: logging.Formatter = Formatter,  # type: ignore[assignment]
    ) -> None:
        """Open the file and use it as the stream for logging."""

        handler = logging.FileHandler(filename, mode, encoding)
        super().__init__(handler, level, formatter)


class RotatingFileHandler(Handler):
    """Handler instance for logging to a set of files, which switches
    from one file to next when the current file reaches a certain size.

    By default, the file grows indefinitely. You can specifiy particular
    values to allow the file to rollover at a pre-determined size.

    :param filename: Absolute path of the output log file.
    :param mode: Mode in which the file needs to be opened, defaults
        to append.
    :param max_bytes: Maximum size in bytes after which the rollover
        should happen, defaults to 10 MB.
    :param backups: Maximum files to retain after rollover, defaults
        to 5.
    :param encoding: Platform-dependent encoding for the file, defaults
        to None.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to use for formatting record,
        defaults to :py:class:`Formatter`.

    .. note::

        Rollover occurs whenever the current log file is nearly
        ``max_bytes`` in size. If the ``backups`` >= 1, the system will
        successively create new files with same pathname as the base
        file, but with extensions ".1", ".2", etc. appended to it. For
        example, with a ``backups`` of 5 and a base file name of
        "mira.log", "mira.log.1", "mira.log.2", ... through to
        "mira.log.5". The file being written to is always "mira.log" -
        when it gets filled up, it is closed and renamed to "mira.log.1"
        and if files "mira.log.1", "mira.log.2" etc. exists, then they
        are renamed to "mira.log.2", "mira.log.3", etc. respectively.

        If ``max_bytes`` is zero, rollover never occurs.

    .. seealso::

        :py:class:`logging.RotatingFileHandler` from the python standard
        library and :py:class:`Handler`.

    .. versionadded:: 1.1.0

    """

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        max_bytes: int = 10000000,
        backups: int = 5,
        encoding: Optional[str] = None,
        level: Optional[Union[int, str]] = None,
        formatter: logging.Formatter = Formatter,  # type: ignore[assignment]
    ) -> None:
        """Open the file and use it as the stream for logging."""

        handler = logging.handlers.RotatingFileHandler(
            filename, mode, max_bytes, backups, encoding
        )
        super().__init__(handler, level, formatter)

    def do_rollover(self) -> Any:
        """Do a rollover when current log file is nearly in size."""

        return self.handler.doRollover()  # type: ignore


class TimedRotatingFileHandler(Handler):
    """Handler instance for logging to a set of files, which switches
    from one file to next at certain timed intervals.

    :param filename: Absolute path of the output log file.
    :param when: Interval of when the rollover should happen, defaults
        to S.
    :param interval: Interval count of the rollover, defaults to 1 day.
    :param backups: Maximum files to retain after rollover, defaults
        to 5.
    :param encoding: Platform-dependent encoding for the file, defaults
        to None.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to use for formatting record,
        defaults to :py:class:`Formatter`.

    .. note::

        If ``backups`` > 0, when rollover is done, no more than
        ``backups`` files are kept, the oldest ones are deleted.

    .. seealso::

        :py:class:`logging.TimedRotatingFileHandler` from the python
        standard library and :py:class:`Handler`.

    .. versionadded:: 1.1.0

    """

    def __init__(
        self,
        filename: str,
        when: str = "S",
        interval: Union[int, float, timedelta] = timedelta(days=1),
        backups: int = 5,
        encoding: Optional[str] = None,
        level: Optional[Union[int, str]] = None,
        formatter: logging.Formatter = Formatter,  # type: ignore[assignment]
    ) -> None:
        """Open the file and use it as the stream for logging."""

        handler = logging.handlers.TimedRotatingFileHandler(
            filename, when, self.to_seconds(interval), backups, encoding
        )
        super().__init__(handler, level, formatter)

    def do_rollover(self) -> Any:
        """Do a rollover when current log file is approaching the
        interval.

        :returns: Handler with rollover to perform.

        """

        return self.handler.doRollover()  # type: ignore

    @staticmethod
    def to_seconds(interval: Union[int, float, timedelta]) -> int:
        """Convert the time delta into seconds.

        :param interval: Interval timestamp to convert.
        :returns: Interval in seconds.

        """

        if isinstance(interval, (int, float)):
            interval = timedelta(seconds=interval)
        return int(interval.total_seconds())


class StreamHandlerHinter(logging.StreamHandler):
    """StreamHandler instance which hints if the output stream is a
    TTY.

    .. seealso::

        :py:meth:`logging.StreamHandler.format` from the python standard
        library.

    .. versionadded:: 1.1.0

    """

    def format(self, record: logging.LogRecord) -> str:
        """Add hint if the specified stream is a TTY.

        :param record: Instance of the logged event.
        :return: Formatted string for the output stream.

        """

        if hasattr(self.stream, "isatty"):
            try:
                record.isatty = self.stream.isatty()  # type: ignore
            except ValueError:
                record.isatty = False  # type: ignore
        else:
            record.isatty = False  # type: ignore
        strict = super().format(record)
        del record.isatty  # type: ignore
        return strict


class StreamHandler(Handler):
    """Handler class which writes logging records, appropriately
    formatted to a stream.

    :param stream: IO stream, defaults to sys.stderr.
    :param level: Logging level of the logged event, defaults to None.
    :param formatter: Formatter instance to use for formatting record,
        defaults to :py:class:`Formatter`.

    .. note::

        This class does not close the stream, as ``sys.stdout`` or
        ``sys.stderr`` may be used.

    .. versionchanged:: 1.1.0

    """

    def __init__(
        self,
        stream: Optional[IO[str]] = sys.stderr,
        level: Optional[Union[int, str]] = None,
        formatter: logging.Formatter = Formatter,  # type: ignore[assignment]
    ) -> None:
        """Initialize the stream handler."""

        super().__init__(StreamHandlerHinter(stream), level, formatter)


stderr = StreamHandler()
stdout = StreamHandler(sys.stdout)


class Logger(logging.LoggerAdapter):
    """Logger instance to represent a logging channel.

    This instance uses a ``LoggerAdapter`` which makes it easier to
    specify contextual information in logging output.

    .. seealso::

        :py:class:`logging.LoggerAdapter` for the changes in the
        implementation of :py:meth:`process` method.

    .. versionchanged:: 1.1.0

    """

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> Tuple[Any, MutableMapping[str, Any]]:
        """Process the logging message and the keyword arguments passed
        to in to a logging call to insert contextual information.

        You can either manipute the message itself, the keyword
        arguments or both. Return the message and modified kwargs to
        suit your needs.

        :param msg: Logged message.
        :param kwargs: Keyword arguments with contextual information.
        :returns: Tuple of message and modified kwargs.

        """

        extra = self.extra.copy()  # type: ignore[attr-defined]
        if "extra" in kwargs:
            extra.update(kwargs.pop("extra"))  # type: ignore[attr-defined]
        for name in kwargs.keys():
            if name == "exc_info":
                continue
            extra[name] = kwargs.pop(name)
        kwargs["extra"] = extra
        return msg, kwargs

    def debug(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``DEBUG`` severity level."""

        self.logger._log(10, msg, args, **kwargs)

    def info(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``INFO`` severity level."""

        self.logger._log(20, msg, args, **kwargs)

    def warning(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``WARNING`` severity level."""

        self.logger._log(30, msg, args, **kwargs)

    def error(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``ERROR`` severity level."""

        self.logger._log(40, msg, args, **kwargs)

    def critical(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``CRITICAL`` severity level."""

        self.logger._log(50, msg, args, **kwargs)

    def exception(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        """Log message with ``CRITICAL`` severity level."""

        self.logger._log(60, msg, args, True, **kwargs)

    fatal = critical
    warn = warning


def get_logger(name: Optional[str] = None, **kwargs: Any) -> Logger:
    """Return a logger with the specified name.

    :param name: Logging channel name, defaults to None.
    :returns: Logger instance.

    .. seealso::

        :py:func:`logging.getLogger` from the python standard library.

    """

    return Logger(logging.getLogger(name), kwargs)


def create_logger(**kwargs: Any) -> Logger:
    """Create logger for logging system.

    The default behavior is to create a ``RotatingFileHandler`` and
    ``StreamHandler`` which writes to a output log file and sys.stderr
    respectively and then set level for logging events to the handlers.

    :returns: Logger instance.

    .. note::

        This implementation is based on :py:func:`logging.basicConfig`.

    """

    root = logging.getLogger(None)
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        handler.close()
    if len(root.handlers) == 0:
        level = kwargs.get("level", logging.INFO)
        root.setLevel(level)
        format = kwargs.get("format", None)
        datefmt = kwargs.get("datefmt", None)
        formatter = Formatter(format, datefmt)
        handlers = kwargs.get("handlers", None)
        if handlers is None:
            handlers = []
            stream = kwargs.get("stream", None)
            handlers.append(StreamHandler(stream, level, formatter))
            filename = kwargs.get("filename", None)
            filemode = kwargs.get("filemode", "a")
            if filename:
                handlers.append(
                    RotatingFileHandler(
                        filename, filemode, level=level, formatter=formatter
                    )
                )
        for handler in handlers:  # type: ignore[assignment]
            handler.add_handler(root)  # type: ignore[attr-defined]
        capture_warnings = kwargs.get("capture_warnings", True)
        logging.captureWarnings(capture_warnings)
    name = kwargs.get("name", None)
    return get_logger(name, **kwargs)
