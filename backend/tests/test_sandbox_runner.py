"""Tests for SandboxRunner (mocked Docker subprocess)."""

import asyncio
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from schemas.api import ERCResult
from schemas.circuit_spec import CircuitSpec, Component, Net, NetSegment
from services.sandbox_runner import SandboxRunner


@pytest.fixture()
def runner(tmp_storage):
    return SandboxRunner()


@pytest.fixture()
def simple_spec():
    return CircuitSpec(
        components=[Component(ref="R1", value="10k")],
        nets=[],
    )


class TestSandboxRunner:
    @pytest.mark.asyncio
    async def test_docker_not_found(self, runner, simple_spec):
        with patch("shutil.which", return_value=None):
            with pytest.raises(RuntimeError, match="Docker not found"):
                await runner.run(simple_spec)

    @pytest.mark.asyncio
    async def test_successful_run(self, runner, simple_spec, tmp_path):
        """Simulate a successful sandbox run by writing expected files."""

        async def fake_communicate():
            return b"OK", b""

        async def fake_exec(*args, **kwargs):
            # Write expected output files into the bind-mount dir
            # Find the -v arg to get the work dir
            cmd_list = list(args)
            for i, a in enumerate(cmd_list):
                if a == "-v" and i + 1 < len(cmd_list):
                    mount = cmd_list[i + 1]
                    host_path = mount.split(":")[0]
                    output = Path(host_path) / "output"
                    output.mkdir(parents=True, exist_ok=True)
                    (output / "schematic.kicad_sch").write_text("(kicad_sch)")
                    (output / "board.kicad_pcb").write_text("(kicad_pcb)")
                    erc = {"passed": True, "messages": [], "summary": "OK"}
                    (output / "erc_result.json").write_text(json.dumps(erc))
                    break
            proc = MagicMock()
            proc.communicate = AsyncMock(return_value=(b"OK", b""))
            proc.returncode = 0
            proc.kill = MagicMock()
            proc.wait = AsyncMock()
            return proc

        with patch("shutil.which", return_value="/usr/bin/docker"):
            with patch("asyncio.create_subprocess_exec", side_effect=fake_exec):
                sch, pcb, erc = await runner.run(simple_spec, run_erc=True)

        assert sch == b"(kicad_sch)"
        assert pcb == b"(kicad_pcb)"
        assert erc is not None
        assert erc.passed is True

    @pytest.mark.asyncio
    async def test_container_nonzero_exit(self, runner, simple_spec):
        async def fake_exec(*args, **kwargs):
            proc = MagicMock()
            proc.communicate = AsyncMock(return_value=(b"", b"some error"))
            proc.returncode = 1
            proc.kill = MagicMock()
            proc.wait = AsyncMock()
            return proc

        with patch("shutil.which", return_value="/usr/bin/docker"):
            with patch("asyncio.create_subprocess_exec", side_effect=fake_exec):
                with pytest.raises(RuntimeError, match="Sandbox failed"):
                    await runner.run(simple_spec)

    @pytest.mark.asyncio
    async def test_missing_schematic_output(self, runner, simple_spec):
        """Container succeeds but doesn't write schematic.kicad_sch."""
        async def fake_exec(*args, **kwargs):
            cmd_list = list(args)
            for i, a in enumerate(cmd_list):
                if a == "-v" and i + 1 < len(cmd_list):
                    mount = cmd_list[i + 1]
                    host_path = mount.split(":")[0]
                    output = Path(host_path) / "output"
                    output.mkdir(parents=True, exist_ok=True)
                    # Only write board, not schematic
                    (output / "board.kicad_pcb").write_text("(kicad_pcb)")
                    break
            proc = MagicMock()
            proc.communicate = AsyncMock(return_value=(b"OK", b""))
            proc.returncode = 0
            proc.kill = MagicMock()
            proc.wait = AsyncMock()
            return proc

        with patch("shutil.which", return_value="/usr/bin/docker"):
            with patch("asyncio.create_subprocess_exec", side_effect=fake_exec):
                with pytest.raises(RuntimeError, match="schematic"):
                    await runner.run(simple_spec)

    @pytest.mark.asyncio
    async def test_erc_not_requested(self, runner, simple_spec):
        async def fake_exec(*args, **kwargs):
            cmd_list = list(args)
            for i, a in enumerate(cmd_list):
                if a == "-v" and i + 1 < len(cmd_list):
                    mount = cmd_list[i + 1]
                    host_path = mount.split(":")[0]
                    output = Path(host_path) / "output"
                    output.mkdir(parents=True, exist_ok=True)
                    (output / "schematic.kicad_sch").write_text("sch")
                    (output / "board.kicad_pcb").write_text("pcb")
                    break
            proc = MagicMock()
            proc.communicate = AsyncMock(return_value=(b"OK", b""))
            proc.returncode = 0
            proc.kill = MagicMock()
            proc.wait = AsyncMock()
            return proc

        with patch("shutil.which", return_value="/usr/bin/docker"):
            with patch("asyncio.create_subprocess_exec", side_effect=fake_exec):
                sch, pcb, erc = await runner.run(simple_spec, run_erc=False)
        assert sch == b"sch"
        assert pcb == b"pcb"
        assert erc is None
