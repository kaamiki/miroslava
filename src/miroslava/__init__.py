import os.path as _os
import os

from .config.internal import LOGGER_PATH, ROOT_PATH

if not _os.exists(ROOT_PATH):
    os.mkdir(ROOT_PATH)

for path in (LOGGER_PATH,):
    os.makedirs(path, exist_ok=True)
