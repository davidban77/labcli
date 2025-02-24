import os

import pulumi
import pulumi.automation as auto
import pulumi_digitalocean as do
import typer

app = typer.Typer()

# Ensure your DigitalOcean token is available.
DO_TOKEN = os.getenv("DIGITALOCEAN_TOKEN", "")
if not DO_TOKEN:
    typer.echo("Please set the DIGITALOCEAN_TOKEN environment variable.")
    raise SystemExit(1)


def pulumi_program():
    user_data = """#!/bin/bash
set -e
apt-get update -y
apt-get upgrade -y
apt-get install -y docker.io git
systemctl start docker
systemctl enable docker
git clone https://github.com/yourusername/yourdockerapp.git /opt/yourdockerapp
cd /opt/yourdockerapp
docker build -t yourdockerapp .
docker run -d -p 80:80 yourdockerapp
"""
    droplet = do.Droplet(
        "my-droplet",
        image="ubuntu-20-04-x64",  # Or use "ubuntu-22-04-x64" if desired.
        region=do.Region.LON1,  # Change to your preferred region.
        size="s-1vcpu-1gb",  # Adjust droplet size if needed.
        ssh_keys=["your-ssh-key-id"],  # Replace with your actual SSH key ID(s).
        user_data=user_data,
    )
    pulumi.export("droplet_ip", droplet.ipv4_address)


def get_stack():
    stack_name = "dev"
    project_name = "digitalocean-droplet"
    try:
        stack = auto.create_or_select_stack(stack_name=stack_name, project_name=project_name, program=pulumi_program)
    except Exception as e:
        typer.echo(f"Error creating/selecting stack: {e}")
        raise e
    # Pass the DigitalOcean token to Pulumi.
    stack.set_config("digitalocean:token", auto.ConfigValue(value=DO_TOKEN))
    return stack


@app.command()
def boot():
    """
    Boot up (create) the droplet using Pulumi.
    """
    stack = get_stack()
    typer.echo("Starting droplet creation (pulumi up)...")
    up_res = stack.up(on_output=print)
    droplet_ip = up_res.outputs.get("droplet_ip")
    if droplet_ip:
        typer.echo(f"Droplet created with IP: {droplet_ip.value}")
    else:
        typer.echo("Droplet creation completed, but no IP was exported.")


@app.command("list")
def list_droplet(name: str = typer.Option(None, help="Name of the droplet to list details for")):
    """
    List details for droplets. If a name is provided, shows details for that droplet.
    Otherwise, lists all droplets.
    """
    if name:
        try:
            droplet = do.get_droplet(name=name)
            typer.echo("-----")
            typer.echo(f"ID: {droplet.id}")
            typer.echo(f"Name: {droplet.name}")
            typer.echo(f"IP: {droplet.ipv4_address}")
            typer.echo(f"Region: {droplet.region}")
            typer.echo(f"Size: {droplet.size}")
        except Exception as e:
            typer.echo(f"No droplet found with name '{name}'. Error: {e}")
    else:
        try:
            droplets = do.get_droplets()
            if not droplets.droplets:
                typer.echo("No droplets found.")
                return
            for droplet in droplets.droplets:
                typer.echo("-----")
                typer.echo(f"ID: {droplet.id}")
                typer.echo(f"Name: {droplet.name}")
                typer.echo(f"IP: {droplet.ipv4_address}")
                typer.echo(f"Region: {droplet.region}")
                typer.echo(f"Size: {droplet.size}")
        except Exception as e:
            typer.echo(f"Error listing droplets: {e}")


@app.command()
def update():
    """
    Update the droplet configuration using Pulumi.

    Re-running pulumi up will compare your current state with the desired state
    (as defined in your pulumi program) and make any necessary changes.
    """
    stack = get_stack()
    typer.echo("Updating droplet configuration (pulumi up)...")
    up_res = stack.up(on_output=print)
    droplet_ip = up_res.outputs.get("droplet_ip")
    if droplet_ip:
        typer.echo(f"Droplet updated. Current IP: {droplet_ip.value}")
    else:
        typer.echo("Update completed, but no IP was exported.")


@app.command()
def destroy():
    """
    Destroy the droplet using Pulumi.
    """
    stack = get_stack()
    typer.echo("Destroying the droplet (pulumi destroy)...")
    stack.destroy(on_output=print)
    typer.echo("Droplet destroyed.")


if __name__ == "__main__":
    app()
