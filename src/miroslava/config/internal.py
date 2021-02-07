"""Miroslava system-wide constants."""

import getpass
import pathlib
import sys

# Operating system details
# This variable offers only the name of the host operating system
# which is sufficient enough for handling an alternate control flow
# depending upon different operating systems.
OS = sys.platform

# Flag to conditionally check if the host operating system is Windows.
IS_WINDOWS = OS == "win32"

# Current logged user
# This variable offers the name of the currently logged user. Kindly
# note that it does not consider other login accounts. The behaviour
# may be unexpected for Guest User accounts.
SESSION_USER = getpass.getuser()

# Operating system filesystem seperator
# This variable helps building of operating system agnostic file paths.
PATH_SEP = pathlib.os.sep

# Canonical path
# This is the base or the root path by default where all the
# cache/data/logs/models would be stored. The `CANONICAL_PATH` can
# be overridden via `SOME_FUTURE_OBJECT`.
CANONICAL_PATH = pathlib.Path().home()

# Datetime formats
# Default datetime format for almost datetime related activities. This
# format is the most common and is default for almost all cases.
STANDARD_DATETIME_FMT = "%Y-%m-%d %H:%M:%S"  # 2020-04-11 22:17:00

# Datetime format to use while logging events. This format offers more
# clarity and avoids confusion between date and month (e.g. 05-04-2004).
LOGGING_DATETIME_FMT = "%b %d, %Y %H:%M:%S"  # Apr 11, 2020 22:17:00

# Time zone specifications
# If True, Miroslava will use naive local time zone.
USE_LOCAL_TIME_ZONE = False

# By default, Miroslava uses `UTC` time zone for handling all datetime
# events. Although the behaviour can be easily overridden by changing
# the status of `USE_LOCAL_TIME_ZONE` flag.
TIME_ZONE = "UTC"

# Logging formats
# This format intends to provide a detailed overview for logged events.
LOGGING_MSG_FMT = (
    "%(asctime)s.%(msecs)03d %(levelname)8s %(process)8d "
    "[%(threadName)16s] %(pathname)30s:%(lineno)d - %(message)s"
)

# Format to use while an exception is raised.
LOGGING_EXC_FMT = "{}: {} {} line {}"

# Regular Expressions
# Expression to check the `%Z` (timezone parameter).
TIME_ZONE_RE = r"(?:(?<=\%Z) | (?=\%Z))"

# Expression to find the logging attribute padding length.
LOGGING_ATTR_RE = r"\%\(\b{}\b\)(\d*)[d-s]"  # %(levelname)8s
