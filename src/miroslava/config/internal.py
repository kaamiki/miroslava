"""Collection of constants that traverse throughout the package."""

import getpass
import os.path as _os
import sys

OS = sys.platform
WINDOWS_OS = OS == "win32"
LOGGED_USER = getpass.getuser()

LOGS = "logs"

PATH_SEP = _os.sep
HOME_PATH = _os.expanduser("~")
ROOT_PATH = _os.join(HOME_PATH, "miroslava")

DEFAULT_DATETIME_FMT = "%Y-%m-%d %H:%M:%S"
LOGGER_DATETIME_FMT = "%b %d, %Y %H:%M:%S"

USE_LOCAL_TZONE = False
TZONE = "UTC"

LOGGER_MSG_FMT = (
    "%(asctime)s.%(msecs)03d %(levelname)8s %(process)8d "
    "[%(threadName)16s] %(pathname)30s:%(lineno)d - %(message)s"
)
LOGGER_EXC_FMT = "{}: {} {} line {}"

TZONE_RE = r"(?:(?<=\%Z) | (?=\%Z))"
LOGGER_ATTR_RE = r"\%\(\b{}\b\)(\d*)[d-s]"
