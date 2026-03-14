"""Tests for sandbox/runner.py (the script that runs inside Docker)."""

import json
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Set WORK env to a temp dir before importing runner (it reads WORK at module level)
_SANDBOX_TMP = tempfile.mkdtemp(prefix="sandbox_test_work_")
os.environ.setdefault("WORK", _SANDBOX_TMP)

# Add sandbox/ to path so we can import runner
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "sandbox"))

import runner as sandbox_runner


class TestLibIdForRef:
    @pytest.mark.parametrize("ref,expected", [
        ("R1", "Device:R"),
        ("R100", "Device:R"),
        ("C1", "Device:C"),
        ("L1", "Device:L"),
        ("D1", "Device:D"),
        ("Q1", "Device:Q_NPN_BCE"),
        ("U1", "Device:Opamp"),
        ("IC2", "Device:Opamp"),
        ("X1", "Device:R"),  # fallback
    ])
    def test_mapping(self, ref, expected):
        assert sandbox_runner.lib_id_for_ref(ref) == expected


class TestGenerateSchematicSexpr:
    def test_minimal_spec(self):
        spec = {
            "components": [{"ref": "R1", "value": "10k", "footprint": "Resistor_SMD:R_0805_2012Metric"}],
            "nets": [],
        }
        result = sandbox_runner.generate_schematic_sexpr(spec)
        assert "(kicad_sch" in result
        assert "R1" in result
        assert "10k" in result
        assert "(lib_symbols" in result
        assert result.strip().endswith(")")

    def test_multiple_components(self):
        spec = {
            "components": [
                {"ref": "R1", "value": "10k"},
                {"ref": "C1", "value": "100nF"},
                {"ref": "U1", "value": "LM7805"},
            ],
            "nets": [],
        }
        result = sandbox_runner.generate_schematic_sexpr(spec)
        assert "R1" in result
        assert "C1" in result
        assert "U1" in result

    def test_with_nets(self):
        spec = {
            "components": [
                {"ref": "R1", "value": "10k"},
                {"ref": "C1", "value": "100nF"},
            ],
            "nets": [
                {"name": "VCC", "connections": [{"ref": "R1", "pin": "1"}, {"ref": "C1", "pin": "1"}]},
            ],
        }
        result = sandbox_runner.generate_schematic_sexpr(spec)
        assert "(wire" in result

    def test_empty_components(self):
        spec = {"components": [], "nets": []}
        result = sandbox_runner.generate_schematic_sexpr(spec)
        assert "(kicad_sch" in result
        assert "(lib_symbols" in result

    def test_deduplicates_lib_symbols(self):
        spec = {
            "components": [
                {"ref": "R1", "value": "10k"},
                {"ref": "R2", "value": "20k"},
            ],
            "nets": [],
        }
        result = sandbox_runner.generate_schematic_sexpr(spec)
        # Device:R should only appear once in lib_symbols
        assert result.count('(symbol "Device:R"') == 1


class TestGeneratePcbSexpr:
    def test_minimal_spec(self):
        spec = {
            "components": [{"ref": "R1", "value": "10k", "footprint": "Resistor_SMD:R_0805_2012Metric"}],
            "nets": [],
        }
        result = sandbox_runner.generate_pcb_sexpr(spec)
        assert "(kicad_pcb" in result
        assert "R1" in result
        assert "F.Cu" in result

    def test_multiple_components_placed(self):
        spec = {
            "components": [
                {"ref": "R1", "value": "10k"},
                {"ref": "C1", "value": "100nF"},
            ],
            "nets": [],
        }
        result = sandbox_runner.generate_pcb_sexpr(spec)
        assert "R1" in result
        assert "C1" in result
        # Each component placed as a footprint
        assert result.count("(footprint") == 2

    def test_empty_spec(self):
        spec = {"components": [], "nets": []}
        result = sandbox_runner.generate_pcb_sexpr(spec)
        assert "(kicad_pcb" in result
        assert "(footprint" not in result


class TestRunErc:
    def test_kicad_cli_not_found(self):
        with patch("shutil.which", return_value=None):
            passed, msgs = sandbox_runner.run_erc(Path("/tmp/fake.kicad_sch"))
        assert passed is False
        assert "kicad-cli not found" in msgs


class TestMain:
    def test_missing_spec_exits(self, tmp_path):
        with patch.object(sandbox_runner, "SPEC_PATH", tmp_path / "nope.json"), \
             patch.object(sandbox_runner, "OUTPUT_DIR", tmp_path / "output"), \
             pytest.raises(SystemExit) as exc_info:
            sandbox_runner.main()
        assert exc_info.value.code == 1

    def test_full_run(self, tmp_path):
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        spec = {
            "components": [{"ref": "R1", "value": "10k"}],
            "nets": [],
        }
        spec_path = input_dir / "spec.json"
        spec_path.write_text(json.dumps(spec))

        with patch.object(sandbox_runner, "SPEC_PATH", spec_path), \
             patch.object(sandbox_runner, "OUTPUT_DIR", output_dir), \
             patch.object(sandbox_runner, "RUN_ERC", False):
            sandbox_runner.main()

        assert (output_dir / "schematic.kicad_sch").exists()
        assert (output_dir / "board.kicad_pcb").exists()
        assert (output_dir / "erc_result.json").exists()

        erc = json.loads((output_dir / "erc_result.json").read_text())
        assert erc["passed"] is True
        assert erc["summary"] == "ERC passed."

        sch = (output_dir / "schematic.kicad_sch").read_text()
        assert "(kicad_sch" in sch
        assert "R1" in sch

        pcb = (output_dir / "board.kicad_pcb").read_text()
        assert "(kicad_pcb" in pcb
