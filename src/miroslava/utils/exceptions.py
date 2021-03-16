"""Exceptions: Collection of all the exceptions raised by Miroslava."""

import os
import sys
import textwrap
from typing import Any


class MiroslavaError(Exception):
    """Base exception class for all exceptions raised by Miroslava.

    The ``valid`` argument ensures that the exceptions are raised
    explicitly by the authors. This guarantees that all the known
    corner cases in the framework are handled properly or patched
    nonetheless.

    :var msg: Message to display while raising the exception.

    """

    msg = ""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the exception."""

        super().__init__(self.msg)
        for name, value in kwargs.items():
            setattr(self, name, value)
        if not kwargs.pop("valid", True):
            sys.stderr.write("\n\n" + self.report_bug() + "\n\n")

    def __str__(self) -> str:
        """Return formatted string with valid arguments."""

        return self.msg.format(**vars(self))

    def report_bug(self) -> str:
        """Return bug reporting warning message.

        :return: Formatted message string with bug report warning.

        """

        width = os.get_terminal_size().columns
        title = "YIKES! There's a bug!".center(width, "-")
        title += (
            "If you are seeing this, then there is something wrong with "
            "Miroslava. Please report this issue here: 'https://github.com/"
            "kaamiki/miroslava/issues/new' so that we can fix it at the "
            "earliest. It would be a great help if you provide the steps, "
            "traceback information or even a code sample for reproducing this "
            "bug while submitting an issue."
        )
        return textwrap.fill(title, width)
