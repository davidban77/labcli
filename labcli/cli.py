""" LabCLI Application. """
import typer

import labcli.utils.containerlab_utils as containerlab_utils
import labcli.utils.docker_utils as docker_utils
from labcli.base import console
from labcli.version import __version__, banner

app = typer.Typer(
    help=f"{banner()}[b blue] LabCLI Application[/b blue]",
    add_completion=True,
    rich_markup_mode="rich",
)

app.add_typer(containerlab_utils.app, name="containerlab")
app.add_typer(docker_utils.app, name="docker")


def version_callback(value: bool):
    """Print the version of the application."""
    if value:
        console.print(f"LabCLI v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show the version and exit."
    ),
):
    """LabCLI Application."""
    pass
