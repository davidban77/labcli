""" Base functionalities for LabCLI. """

import os
import shlex
import subprocess  # nosec
from pathlib import Path
from typing import Any, Optional

from dotenv import dotenv_values, load_dotenv
from rich.console import Console
from rich.theme import Theme

load_dotenv(verbose=True, override=True, dotenv_path=Path("./.env"))
ENVVARS = {**dotenv_values(".env"), **dotenv_values(".setup.env"), **os.environ}

custom_theme = Theme({"info": "cyan", "warning": "bold magenta", "error": "bold red", "good": "bold green"})

console = Console(color_system="truecolor", log_path=False, record=True, theme=custom_theme, force_terminal=True)


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).

    Args:
        val (str): String representation of truth.

    Returns:
        bool: True or False
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


def is_truthy(arg: Any) -> bool:
    """Convert "truthy" strings into Booleans.

    Examples:
    ```python
        >>> is_truthy('yes')
        True
    ```

    Args:
        arg (Any): Any value to be converted to boolean.

    Returns:
        bool

    Raises:
        ValueError: If the value is not a valid truthy value
    """
    if isinstance(arg, bool):
        return arg
    if arg is None:
        return False
    return bool(strtobool(arg))


def run_cmd(
    exec_cmd: str,
    envvars: dict[str, Any] = ENVVARS,
    cwd: Optional[str] = None,
    timeout: Optional[int] = None,
    shell: bool = False,
    capture_output: bool = False,
    task_name: str = "",
) -> subprocess.CompletedProcess:
    """Run a command and return the result.

    Args:
        exec_cmd (str): Command to execute
        envvars (dict, optional): Environment variables. Defaults to ENVVARS.
        cwd (str, optional): Working directory. Defaults to None.
        timeout (int, optional): Timeout in seconds. Defaults to None.
        shell (bool, optional): Run the command in a shell. Defaults to False.
        capture_output (bool, optional): Capture stdout and stderr. Defaults to True.
        task_name (str, optional): Name of the task. Defaults to "".

    Returns:
        subprocess.CompletedProcess: Result of the command
    """
    console.log(f"Running command: [orange1 i]{exec_cmd}", style="info")
    result = subprocess.run(
        shlex.split(exec_cmd),
        env=envvars,
        cwd=cwd,
        timeout=timeout,
        shell=shell,  # nosec
        capture_output=capture_output,
        text=True,
        check=False,
    )
    task_name = task_name if task_name else exec_cmd

    if not capture_output:
        console.print()
        if result.returncode == 0:
            console.rule(f"[green]Successfully ran: [b i]{task_name}", style="good")
        else:
            console.rule(f"[red]Issues encountered running: [b i]{task_name}", style="warning")
        console.print()

    return result
