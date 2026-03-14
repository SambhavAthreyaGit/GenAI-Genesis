"""Tests for schemas: circuit_spec and api models."""

import pytest
from pydantic import ValidationError

from schemas.circuit_spec import CircuitSpec, Component, Net, NetSegment
from schemas.api import GenerateRequest, GenerateResponse, ERCResult, ProjectResponse


class TestComponent:
    def test_create_with_defaults(self):
        c = Component(ref="R1", value="10k")
        assert c.ref == "R1"
        assert c.value == "10k"
        assert c.footprint == "Resistor_SMD:R_0805_2012Metric"

    def test_create_with_footprint(self):
        c = Component(ref="U1", value="LM7805", footprint="Package_TO_SOT_THT:TO-220-3_Vertical")
        assert c.footprint == "Package_TO_SOT_THT:TO-220-3_Vertical"

    def test_missing_ref_raises(self):
        with pytest.raises(ValidationError):
            Component(value="10k")

    def test_missing_value_raises(self):
        with pytest.raises(ValidationError):
            Component(ref="R1")


class TestNetSegment:
    def test_create(self):
        s = NetSegment(ref="R1", pin="1")
        assert s.ref == "R1"
        assert s.pin == "1"

    def test_missing_pin_raises(self):
        with pytest.raises(ValidationError):
            NetSegment(ref="R1")


class TestNet:
    def test_create_empty_connections(self):
        n = Net(name="VCC")
        assert n.name == "VCC"
        assert n.connections == []

    def test_create_with_connections(self):
        n = Net(name="GND", connections=[NetSegment(ref="R1", pin="2")])
        assert len(n.connections) == 1


class TestCircuitSpec:
    def test_empty_spec(self):
        s = CircuitSpec()
        assert s.components == []
        assert s.nets == []

    def test_roundtrip_json(self, sample_spec):
        data = sample_spec.model_dump()
        rebuilt = CircuitSpec.model_validate(data)
        assert rebuilt == sample_spec

    def test_from_dict(self, sample_spec_dict):
        spec = CircuitSpec.model_validate(sample_spec_dict)
        assert len(spec.components) == 2
        assert len(spec.nets) == 2


class TestGenerateRequest:
    def test_valid(self):
        r = GenerateRequest(prompt="Simple LED circuit")
        assert r.prompt == "Simple LED circuit"
        assert r.run_erc is True

    def test_empty_prompt_fails(self):
        with pytest.raises(ValidationError):
            GenerateRequest(prompt="")

    def test_run_erc_false(self):
        r = GenerateRequest(prompt="test", run_erc=False)
        assert r.run_erc is False


class TestERCResult:
    def test_passed(self):
        e = ERCResult(passed=True, messages=[], summary="OK")
        assert e.passed is True

    def test_failed_with_messages(self):
        e = ERCResult(passed=False, messages=["Pin 1 unconnected"], summary="ERC failed")
        assert not e.passed
        assert len(e.messages) == 1

    def test_summary_optional(self):
        e = ERCResult(passed=True)
        assert e.summary is None


class TestGenerateResponse:
    def test_create(self):
        r = GenerateResponse(
            project_id="abc-123",
            schematic_url="/files/abc-123/schematic.kicad_sch",
            pcb_url="/files/abc-123/board.kicad_pcb",
        )
        assert r.status == "completed"
        assert r.erc_result is None


class TestProjectResponse:
    def test_create(self):
        p = ProjectResponse(
            project_id="xyz",
            schematic_url="/files/xyz/schematic.kicad_sch",
            pcb_url="/files/xyz/board.kicad_pcb",
            status="completed",
        )
        assert p.prompt is None
        assert p.created_at is None
