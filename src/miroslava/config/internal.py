"""Miroslava system-wide constants"""

import getpass
import pathlib
import sys

# Operating system details
# This is needed for designing and handling different control flows
# for different operating systems.
OS = sys.platform

# Current logged user
USR = getpass.getuser()

# Operating system filesystem seperator
# `/` for *nix based and `\\` for Windows operating systems.
SEP = pathlib.os.sep
