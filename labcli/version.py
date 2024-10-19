""" LabCLI version module """

import importlib.metadata

from labcli.base import console

__version__ = importlib.metadata.version("labcli")


def banner():
    console.print(
        r"""
[blue]
  _       _          _ _
 | |     | |        | (_)
 | | __ _| |__   ___| |_
 | |/ _` | '_ \ / __| | |
 | | (_| | |_) | (__| | |
 |_|\__,_|_.__/ \___|_|_| [bold]v{0}[/bold]
[/blue]
        """.format(
            __version__
        )
    )
    return "==> LabCLI v{0}".format(__version__)