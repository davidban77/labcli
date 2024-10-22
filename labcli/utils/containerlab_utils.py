""" Containerlab management related commands. """

import subprocess
from pathlib import Path

import typer
from typing_extensions import Annotated

from labcli.base import console, run_cmd

app = typer.Typer(help="Containerlab management related commands.", rich_markup_mode="rich")


@app.command(rich_help_panel="Containerlab Management", name="deploy")
def containerlab_deploy(
    sudo: Annotated[bool, typer.Option(help="Use sudo to run containerlab")] = True,
    topology: Annotated[
        Path,
        typer.Argument(
            help="Path to the topology file",
            exists=True,
            file_okay=True,
            readable=True,
        ),
    ] = Path("./containerlab/lab.clab.yaml"),
) -> subprocess.CompletedProcess | None:
    """Deploy a containerlab topology.

    [u]Example:[/u]
        [i]labcli containerlab deploy ./containerlab/lab.clab.yaml[/i]
    """
    console.log("Deploying containerlab topology", style="info")
    console.log(f"Topology file: [orange1 i]{topology}", style="info")
    exec_cmd = f"containerlab deploy -t {topology}"
    if sudo:
        exec_cmd = f"sudo {exec_cmd}"
    run_cmd(exec_cmd, task_name="Deploying containerlab topology")


@app.command(rich_help_panel="Containerlab Management", name="destroy")
def containerlab_destroy(
    sudo: Annotated[bool, typer.Option(help="Use sudo to run containerlab")] = True,
    topology: Annotated[
        Path,
        typer.Argument(
            help="Path to the topology file",
            exists=True,
            file_okay=True,
            readable=True,
        ),
    ] = Path("./containerlab/lab.clab.yaml"),
):
    """Destroy a containerlab topology.

    [u]Example:[/u]
        [i]labcli containerlab destroy ./containerlab/lab.clab.yaml[/i]
    """
    console.log("Deploying containerlab topology", style="info")
    console.log(f"Topology file: [orange1 i]{topology}", style="info")
    exec_cmd = f"containerlab destroy -t {topology} --cleanup"
    if sudo:
        exec_cmd = f"sudo {exec_cmd}"
    run_cmd(exec_cmd, task_name="Destroying containerlab topology")


@app.command(rich_help_panel="Containerlab Management", name="inspect")
def containerlab_inspect(
    sudo: Annotated[bool, typer.Option(help="Use sudo to run containerlab")] = True,
    topology: Annotated[
        Path,
        typer.Argument(
            help="Path to the topology file",
            exists=True,
            file_okay=True,
            readable=True,
        ),
    ] = Path("./containerlab/lab.clab.yaml"),
):
    """Inspect a containerlab topology.

    [u]Example:[/u]
        [i]labcli containerlab show ./containerlab/lab.clab.yaml[/i]
    """
    console.log("Showing containerlab topology", style="info")
    console.log(f"Topology file: [orange1 i]{topology}", style="info")
    exec_cmd = f"containerlab inspect -t {topology}"
    if sudo:
        exec_cmd = f"sudo {exec_cmd}"
    run_cmd(exec_cmd, task_name="Inspect containerlab topology")
