import pytest
from pathlib import Path


@pytest.fixture
def aiq_home(monkeypatch, tmp_path):
    """Redirects ~/.aiq to a temp dir for test isolation."""
    monkeypatch.setenv("AIQ_HOME", str(tmp_path))
    return tmp_path
