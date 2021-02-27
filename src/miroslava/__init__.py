import os
import os.path as _os

from .config.internal import LOGGER_PATH, ROOT_PATH

if not _os.exists(ROOT_PATH):
    os.mkdir(ROOT_PATH)

_paths = (LOGGER_PATH,)

for _path in _paths:
    os.makedirs(_path, exist_ok=True)
