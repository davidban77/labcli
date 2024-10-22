from typer.testing import CliRunner

from labcli.cli import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "LabCLI Application" in result.stdout
