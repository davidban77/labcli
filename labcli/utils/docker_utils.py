""" Docker management related commands. """

import subprocess
from enum import Enum
from pathlib import Path
from typing import Any

import typer
from typing_extensions import Annotated

from labcli.base import ENVVARS, console, is_truthy, run_cmd

app = typer.Typer(help="Docker management related commands.", rich_markup_mode="rich")


class DockerNetworkAction(Enum):
    """Docker network action."""

    CONNECT = "connect"
    CREATE = "create"
    DISCONNECT = "disconnect"
    INSPECT = "inspect"
    LIST = "ls"
    PRUNE = "prune"
    REMOVE = "rm"


def docker_compose_cmd(
    compose_action: str,
    docker_compose_file: Path,
    profiles: list[str] = [],
    services: list[str] = [],
    verbose: int = 0,
    extra_options: str = "",
    command: str = "",
    project_name: str | None = None,
) -> str:
    """Create docker-compose command to execute.

    Args:
        compose_action (str): Docker Compose action to run.
        docker_compose_file (Path): Docker compose file.
        profiles (List[str], optional): List of profiles to use. Defaults to [].
        services (List[str], optional): List of specifics container to action. Defaults to [].
        verbose (int, optional): Verbosity. Defaults to 0.
        extra_options (str, optional): Extra docker compose flags to pass to the command line. Defaults to "".
        command (str, optional): Command to execute in docker compose. Defaults to "".
        project_name (str, optional): Project name. Defaults to None.

    Returns:
        str: Docker compose command
    """
    if is_truthy(ENVVARS.get("DOCKER_COMPOSE_WITH_HASH", None)):
        exec_cmd = f"docker-compose -f {docker_compose_file}"
    else:
        exec_cmd = f"docker compose -f {docker_compose_file}"

    if project_name:
        exec_cmd += f" --project-name {project_name}"

    for profile in profiles:
        exec_cmd += f" --profile {profile}"

    if verbose:
        exec_cmd += " --verbose"
    exec_cmd += f" {compose_action}"

    if extra_options:
        exec_cmd += f" {extra_options}"
    if services:
        exec_cmd += f" {' '.join(services)}"
    if command:
        exec_cmd += f" {command}"

    return exec_cmd


def run_docker_compose_cmd(
    compose_file: Path,
    action: str,
    project_name: str | None = None,
    profiles: list[str] = [],
    services: list[str] = [],
    verbose: int = 0,
    command: str = "",
    extra_options: str = "",
    envvars: dict[str, Any] = ENVVARS,
    timeout: int | None = None,
    shell: bool = False,
    capture_output: bool = False,
    task_name: str = "",
) -> subprocess.CompletedProcess:
    """Run a docker compose command.

    Args:
        compose_file (str): Docker compose file.
        action (str): Docker compose action. Example 'up'
        project_name (str, optional): Project name. Defaults to None.
        profiles (list[str], optional): List of profiles defined in the docker compose. Defaults to [].
        services (list[str], optional): List of services defined in the docker compose. Defaults to [].
        verbose (int, optional): Execute verbose command. Defaults to 0.
        command (str, optional): Docker compose command to send on action `exec`. Defaults to "".
        extra_options (str, optional): Extra options to pass over docker compose command. Defaults to "".
        envvars (dict, optional): Environment variables. Defaults to ENVVARS.
        timeout (int, optional): Timeout in seconds. Defaults to None.
        shell (bool, optional): Run the command in a shell. Defaults to False.
        capture_output (bool, optional): Capture stdout and stderr. Defaults to True.
        task_name (str, optional): Name of the task passed. Defaults to "".

    Returns:
        subprocess.CompletedProcess: Result of the command run
    """
    if not compose_file.exists():
        console.log(f"File not found: [orange1 i]{compose_file}", style="error")
        raise typer.Exit(1)

    exec_cmd = docker_compose_cmd(
        action,
        docker_compose_file=compose_file,
        profiles=profiles,
        services=services,
        command=command,
        verbose=verbose,
        extra_options=extra_options,
        project_name=project_name,
    )
    return run_cmd(
        exec_cmd=exec_cmd,
        envvars=envvars,
        timeout=timeout,
        shell=shell,
        capture_output=capture_output,
        task_name=f"{task_name}",
    )


@app.command(rich_help_panel="Docker Image Management", name="build")
def docker_build(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to build")] = None,
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Build necessary container images.

    [u]Example:[/u]

    To build all services in default docker-compose file:
        [i]labcli docker build[/i]

    To build a specific services:
        [i]labcli docker build --compose ./other/docker-compose.yml telegraf-01 telegraf-02[/i]
    """
    console.log(f"Building service(s): [orange1 i]{services if services else 'all'}", style="info")
    run_docker_compose_cmd(
        action="build",
        profiles=profiles if profiles else [],
        compose_file=compose_file,
        services=services if services else [],
        verbose=verbose,
        task_name="build stack",
    )


@app.command(rich_help_panel="Docker Image Management", name="pull")
def docker_pull(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to pull")] = None,
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Pull container images.

    [u]Example:[/u]

    To pull all services in default docker-compose file:
        [i]labcli docker pull[/i]

    To pull a specific services:
        [i]labcli docker pull --compose ./other/docker-compose.yml telegraf-01 telegraf-02[/i]
    """
    console.log(f"Pulling service(s): [orange1 i]{services if services else 'all'}", style="info")
    run_docker_compose_cmd(
        action="pull",
        compose_file=compose_file,
        profiles=profiles if profiles else [],
        services=services if services else [],
        verbose=verbose,
        task_name="pull stack",
    )


@app.command(rich_help_panel="Docker Stack Management", name="exec")
def docker_exec(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to run an exec command")] = None,
    command: Annotated[str, typer.Argument(help="Command to execute")] = "bash",
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Execute a command in a container.

    [u]Example:[/u]

    To execute a command in a service:
        [i]labcli docker exec telegraf-01 bash[/i]

        To execute a command in a service and verbose mode:
        [i]labcli docker exec telegraf-01 bash --verbose[/i]
    """
    console.log(f"Executing command in service: [orange1 i]{services}", style="info")
    run_docker_compose_cmd(
        action="exec",
        compose_file=compose_file,
        profiles=profiles if profiles else [],
        services=services if services else [],
        command=command,
        verbose=verbose,
        task_name="exec command",
    )


@app.command(rich_help_panel="Docker Stack Management", name="debug")
def docker_debug(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to start in debug mode")] = None,
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Start docker compose in debug mode.

    [u]Example:[/u]

    To start all services in debug mode:
        [i]labcli docker debug[/i]

    To start a specific service in debug mode:
        [i]labcli docker debug telegraf-01[/i]
    """
    console.log(f"Starting in debug mode service(s): [orange1 i]{services if services else 'all'}", style="info")
    run_docker_compose_cmd(
        action="up",
        compose_file=compose_file,
        profiles=profiles if profiles else [],
        services=services if services else [],
        verbose=verbose,
        extra_options="--remove-orphans",
        task_name="debug stack",
    )


@app.command(rich_help_panel="Docker Stack Management", name="start")
def docker_start(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to start")] = None,
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Start services.

    [u]Example:[/u]

    To start all services in dev profile:
        [i]labcli docker start --profile dev[/i]

    To start a specific service:
        [i]labcli docker start telegraf-01 telegraf-02[/i]
    """
    console.log(f"Starting service(s): [orange1 i]{services if services else 'all'}", style="info")
    run_docker_compose_cmd(
        action="up",
        compose_file=compose_file,
        profiles=profiles if profiles else [],
        services=services if services else [],
        verbose=verbose,
        extra_options="-d --remove-orphans",
        task_name="start stack",
    )


@app.command(rich_help_panel="Docker Stack Management", name="stop")
def docker_stop(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to stop")] = None,
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Stop services.

    [u]Example:[/u]

    To stop all services for a production profile:
        [i]labcli docker stop --profile production[/i]

    To stop a specific service:
        [i]labcli docker stop telegraf-01 telegraf-02[/i]
    """
    console.log(f"Stopping service(s): [orange1 i]{services if services else 'all'}", style="info")
    run_docker_compose_cmd(
        action="stop",
        compose_file=compose_file,
        profiles=profiles if profiles else [],
        services=services if services else [],
        verbose=verbose,
        task_name="stop stack",
    )


@app.command(rich_help_panel="Docker Stack Management", name="restart")
def docker_restart(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to restart")] = None,
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Restart services.

    [u]Example:[/u]

    To restart all services in the batteries-included profile:
        [i]labcli docker restart --profile batteries-included[/i]

    To restart a specific service:
        [i]labcli docker restart telegraf-01 telegraf-02[/i]
    """
    console.log(f"Restarting service(s): [orange1 i]{services if services else 'all'}", style="info")
    run_docker_compose_cmd(
        action="restart",
        compose_file=compose_file,
        profiles=profiles if profiles else [],
        services=services if services else [],
        verbose=verbose,
        task_name="restart stack",
    )


@app.command(rich_help_panel="Docker Stack Management", name="logs")
def docker_logs(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to show logs from")] = None,
    follow: Annotated[bool, typer.Option("-f", "--follow", help="Follow logs")] = False,
    tail: int | None = typer.Option(None, "-t", "--tail", help="Number of lines to show"),
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Show logs for containers.

    [u]Example:[/u]

    To show logs for all services:
        [i]labcli docker logs[/i]

    To show logs for a specific service in dev profile:
        [i]labcli docker logs telegraf-01 --profile dev[/i]

    To show logs for a specific service and follow the logs and tail 10 lines:
        [i]labcli docker logs telegraf-01 --follow --tail 10[/i]
    """
    console.log(f"Showing logs for service(s): [orange1 i]{services if services else 'all'}", style="info")
    options = ""
    if follow:
        options += "-f "
    if tail:
        options += f"--tail={tail}"
    run_docker_compose_cmd(
        action="logs",
        compose_file=compose_file,
        profiles=profiles if profiles else [],
        services=services if services else [],
        extra_options=options,
        verbose=verbose,
        task_name="show logs",
    )


@app.command(rich_help_panel="Docker Stack Management", name="ps")
def docker_ps(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to show status")] = None,
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Show containers.

    [u]Example:[/u]

    To show all services:
        [i]labcli docker ps[/i]

    To show a specific service:
        [i]labcli docker ps telegraf-01[/i]
    """
    console.log(f"Showing containers for service(s): [orange1 i]{services if services else 'all'}", style="info")
    run_docker_compose_cmd(
        action="ps",
        compose_file=compose_file,
        profiles=profiles if profiles else [],
        services=services if services else [],
        verbose=verbose,
        extra_options="--all",
        task_name="show containers",
    )


@app.command(rich_help_panel="Docker Stack Management", name="destroy")
def docker_destroy(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to destroy")] = None,
    volumes: Annotated[bool, typer.Option(help="Remove volumes")] = False,
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Destroy services and resources.

    [u]Example:[/u]

    To destroy all services for a batteries-included profile:
        [i]labcli docker destroy --profile batteries-included[/i]

    To destroy a specific service:
        [i]labcli docker destroy telegraf-01[/i]

    To destroy a specific service and remove volumes:
        [i]labcli docker destroy prometheus --volumes[/i]

    To destroy all services and remove volumes:
        [i]labcli docker destroy --volumes[/i]
    """
    console.log(f"Destroying service(s): [orange1 i]{services if services else 'all'}", style="info")
    run_docker_compose_cmd(
        action="down",
        compose_file=compose_file,
        profiles=profiles if profiles else [],
        services=services if services else [],
        verbose=verbose,
        extra_options="--volumes --remove-orphans" if volumes else "--remove-orphans",
        task_name="destroy stack",
    )


@app.command(rich_help_panel="Docker Stack Management", name="rm")
def docker_rm(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to remove")] = None,
    volumes: Annotated[bool, typer.Option(help="Remove volumes")] = False,
    force: Annotated[bool, typer.Option(help="Force removal of containers")] = False,
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Remove services.

    [u]Example:[/u]

    To remove all services:
        [i]netobs docker rm --scenario batteries-included[/i]

    To remove a specific service:
        [i]netobs docker rm telegraf-01 --scenario batteries-included[/i]

    To remove a specific service and remove volumes:
        [i]netobs docker rm telegraf-01 --volumes --scenario batteries-included[/i]

    To remove all services and remove volumes:
        [i]netobs docker rm --volumes --scenario batteries-included[/i]

    To remove all services and force removal of containers:
        [i]netobs docker rm --force --scenario batteries-included[/i]

    To force removal of a specific service and remove volumes:
        [i]netobs docker rm telegraf-01 --volumes --force --scenario batteries-included[/i]
    """
    console.log(f"Removing service(s): [orange1 i]{services if services else 'all'}", style="info")
    extra_options = "--stop "
    if force:
        extra_options += "--force "
    if volumes:
        extra_options += "--volumes "
    run_docker_compose_cmd(
        action="rm",
        compose_file=compose_file,
        profiles=profiles if profiles else [],
        services=services if services else [],
        verbose=verbose,
        extra_options=extra_options,
        task_name="remove containers",
    )


@app.command(rich_help_panel="Docker Stack Management", name="update")
def docker_update(
    compose_file: Annotated[
        Path, typer.Option("--compose", "-c", help="Docker Compose file.", exists=True, file_okay=True, readable=True)
    ] = Path("./docker-compose.yml"),
    profiles: Annotated[
        list[str] | None,
        typer.Option("--profile", "-p", help="Docker Compose profile", case_sensitive=False),
    ] = None,
    services: Annotated[list[str] | None, typer.Argument(help="Service(s) to update")] = None,
    volumes: Annotated[bool, typer.Option(help="Remove volumes")] = False,
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
):
    """Update services.

    [u]Example:[/u]

    To update all services:
        [i]labcli docker update[/i]

    To update a specific service:
        [i]labcli docker update telegraf-01 telegraf-02[/i]
    """
    console.log(f"Updating service(s): [orange1 i]{services if services else 'all'}", style="info")

    # Delete the containers
    drms = docker_rm(
        compose_file=compose_file, profiles=profiles, services=services, verbose=verbose, force=True, volumes=volumes
    )

    # Start them back if the removal was successful
    if drms is not None and drms.returncode == 0:
        docker_start(compose_file=compose_file, profiles=profiles, services=services, verbose=verbose)
        console.log(f"Service(s) updated: [orange1 i]{services if services else 'all'}", style="info")
    else:
        console.log(f"Service(s) update failed: [orange1 i]{services if services else 'all'}", style="error")


@app.command(rich_help_panel="Docker Network Management", name="network")
def docker_network(
    action: Annotated[
        DockerNetworkAction,
        typer.Argument(..., help="Action to perform", case_sensitive=False),
    ],
    name: Annotated[str, typer.Option("-n", "--name", help="Network name")] = "labcli",
    driver: Annotated[str, typer.Option(help="Network driver")] = "bridge",
    subnet: Annotated[str, typer.Option(help="Network subnet")] = "198.51.100.0/24",
    verbose: Annotated[bool, typer.Option(help="Verbose mode")] = False,
) -> subprocess.CompletedProcess | None:
    """Manage docker network.

    [u]Example:[/u]

    To create a network:
        [i]labcli docker network create --name labcli --driver bridge --subnet

    To list all networks:
        [i]labcli docker network ls[/i]
    """
    console.log(f"Network {action.value}: [orange1 i]{name}", style="info")
    exec_cmd = f"docker network {action.value}"
    if driver and action.value == "create":
        exec_cmd += f" --driver={driver} "
    if subnet and action.value == "create":
        exec_cmd += f" --subnet={subnet}"
    if action.value != "ls" and action.value != "prune":
        exec_cmd += f" {name}"
    run_cmd(
        exec_cmd=exec_cmd,
        task_name=f"network {action.value}",
    )
