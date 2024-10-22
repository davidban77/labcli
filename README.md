[![Open the Example in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/davidban77/labcli?quickstart=1&devcontainer_path=.devcontainer%2Fexample%2Fdevcontainer.json)
# LabCLI

LabCLI is a command line interface for managing lab environments. It is designed to be used as is or imported into other scripts or CLI applications.

## Installation

To get started you can install the package from PyPI.

```bash
pip install labcli
```

## Usage

To get started you can use the `labcli` command:

```bash
labcli --help
```

It comes with builtin commands to manage [containerlab](https://containerlab.dev/) and [docker compose](https://docs.docker.com/compose/) environments.

```bash
labcli containerlab --help
labcli docker --help
```

### Example

To see it in action, this repository comes with an `example` directory that contains a `docker-compose.yml` file and a `containerlab` directory. These have been created to demonstrate how to use `labcli` to manage lab environments.

To start the `containerlab` environment:

```bash
labcli containerlab start --topology example/containerlab/lab.clab.yml
```

To start the `docker compose` environment:

```bash
labcli docker start --compose example/docker-compose.yml
```

> Note: You can also use the `--help` flag to get more information about the commands and their options. For example, with the `--profile` argument you can spin up a docker compose environment for a specific profile of services applied to it:
>
> ```bash
> labcli docker start --compose example/docker-compose.yml --profile collector
> ```
>
> This will start the `docker-compose.yml` environment with the `collector` profile.

## Open in GitHub Codespaces

You can open this repository in GitHub Codespaces by clicking on the badge at the top of this README. This will open a new Codespace with the repository and the development environment already set up.

This will give you a feel of the `labcli` in action and how it can be used to manage lab environments.

## Development

To install the development environment you need to have [uv](https://docs.astral.sh/uv) installed.

```bash
git clone https://github.com/davidban77/labcli.git
cd labcli
uv sync
```

This will create a virtual environment and install the required dependencies.