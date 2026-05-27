from typer.testing import CliRunner
from unittest.mock import patch
from aiq.cli.main import app

runner = CliRunner()


def test_group_list_calls_api():
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = []
        result = runner.invoke(app, ["group", "list"])
        assert result.exit_code == 0
        mock_get.assert_called_once()


def test_model_list_calls_api():
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = []
        result = runner.invoke(app, ["model", "list"])
        assert result.exit_code == 0
        mock_get.assert_called_once()


def test_agent_list_calls_api():
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = []
        result = runner.invoke(app, ["agent", "list"])
        assert result.exit_code == 0
        mock_get.assert_called_once()


def test_aiq_bare_calls_status():
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = []
        result = runner.invoke(app, [])
        assert result.exit_code == 0


def test_aiq_status_alias():
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = []
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0


def test_aiq_list_alias():
    with patch("httpx.get") as mock_get:
        mock_get.return_value.json.return_value = []
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
