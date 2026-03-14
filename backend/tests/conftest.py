"""Shared fixtures for tests."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure backend/ is on sys.path so imports like `from config import ...` work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Settings, get_settings
from schemas.circuit_spec import CircuitSpec, Component, Net, NetSegment
from schemas.api import ERCResult


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    """Clear the lru_cache on get_settings between tests."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
def tmp_storage(tmp_path):
    """Patch settings to use a temp directory for storage, return the path."""
    with patch.dict(os.environ, {
        "STORAGE_PATH": str(tmp_path),
        "ANTHROPIC_API_KEY": "test-key",
    }):
        get_settings.cache_clear()
        yield tmp_path
    get_settings.cache_clear()


@pytest.fixture()
def sample_spec() -> CircuitSpec:
    """A minimal valid CircuitSpec for tests."""
    return CircuitSpec(
        components=[
            Component(ref="R1", value="10k", footprint="Resistor_SMD:R_0805_2012Metric"),
            Component(ref="C1", value="100nF", footprint="Capacitor_SMD:C_0805_2012Metric"),
        ],
        nets=[
            Net(name="VCC", connections=[
                NetSegment(ref="R1", pin="1"),
                NetSegment(ref="C1", pin="1"),
            ]),
            Net(name="GND", connections=[
                NetSegment(ref="R1", pin="2"),
                NetSegment(ref="C1", pin="2"),
            ]),
        ],
    )


@pytest.fixture()
def sample_spec_dict(sample_spec) -> dict:
    """sample_spec as a dict (like LLM JSON output)."""
    return sample_spec.model_dump()


@pytest.fixture()
def sample_erc_result() -> ERCResult:
    return ERCResult(passed=True, messages=[], summary="ERC passed.")
