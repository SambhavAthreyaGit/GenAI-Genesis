"""Tests for SpecValidator."""

import pytest

from schemas.circuit_spec import CircuitSpec, Component, Net, NetSegment
from services.spec_validator import SpecValidator, SpecValidationError, _default_footprint


class TestSpecValidator:
    def setup_method(self):
        self.validator = SpecValidator()

    def test_valid_spec(self, sample_spec):
        result = self.validator.validate(sample_spec)
        assert isinstance(result, CircuitSpec)
        assert len(result.components) == 2
        assert len(result.nets) == 2

    def test_empty_components_raises(self):
        spec = CircuitSpec(components=[], nets=[])
        with pytest.raises(SpecValidationError, match="At least one component"):
            self.validator.validate(spec)

    def test_duplicate_ref_raises(self):
        spec = CircuitSpec(
            components=[
                Component(ref="R1", value="10k"),
                Component(ref="R1", value="20k"),
            ],
            nets=[],
        )
        with pytest.raises(SpecValidationError, match="Duplicate component ref"):
            self.validator.validate(spec)

    def test_missing_ref_raises(self):
        spec = CircuitSpec(
            components=[Component(ref="", value="10k")],
            nets=[],
        )
        with pytest.raises(SpecValidationError, match="must have ref and value"):
            self.validator.validate(spec)

    def test_missing_value_raises(self):
        spec = CircuitSpec(
            components=[Component(ref="R1", value="")],
            nets=[],
        )
        with pytest.raises(SpecValidationError, match="must have ref and value"):
            self.validator.validate(spec)

    def test_net_unknown_ref_raises(self):
        spec = CircuitSpec(
            components=[Component(ref="R1", value="10k")],
            nets=[Net(name="VCC", connections=[NetSegment(ref="R2", pin="1")])],
        )
        with pytest.raises(SpecValidationError, match="unknown component ref"):
            self.validator.validate(spec)

    def test_net_empty_pin_raises(self):
        spec = CircuitSpec(
            components=[Component(ref="R1", value="10k")],
            nets=[Net(name="VCC", connections=[NetSegment(ref="R1", pin="")])],
        )
        with pytest.raises(SpecValidationError, match="empty pin"):
            self.validator.validate(spec)

    def test_normalizes_whitespace(self):
        spec = CircuitSpec(
            components=[Component(ref="  R1 ", value=" 10k ", footprint=" Resistor_SMD:R_0805_2012Metric ")],
            nets=[Net(name=" VCC ", connections=[NetSegment(ref=" R1 ", pin=" 1 ")])],
        )
        result = self.validator.validate(spec)
        assert result.components[0].ref == "R1"
        assert result.components[0].value == "10k"
        assert result.components[0].footprint == "Resistor_SMD:R_0805_2012Metric"
        assert result.nets[0].name == "VCC"
        assert result.nets[0].connections[0].ref == "R1"
        assert result.nets[0].connections[0].pin == "1"

    def test_normalizes_empty_net_name(self):
        spec = CircuitSpec(
            components=[Component(ref="R1", value="10k")],
            nets=[Net(name="", connections=[])],
        )
        result = self.validator.validate(spec)
        assert result.nets[0].name == "UnnamedNet"

    def test_spec_with_no_nets(self):
        spec = CircuitSpec(
            components=[Component(ref="R1", value="10k")],
            nets=[],
        )
        result = self.validator.validate(spec)
        assert len(result.nets) == 0

    def test_multiple_components_different_refs(self):
        spec = CircuitSpec(
            components=[
                Component(ref="R1", value="10k"),
                Component(ref="C1", value="100nF"),
                Component(ref="U1", value="LM7805"),
            ],
            nets=[],
        )
        result = self.validator.validate(spec)
        assert len(result.components) == 3


class TestDefaultFootprint:
    @pytest.mark.parametrize("ref,expected_substr", [
        ("R1", "Resistor_SMD"),
        ("C1", "Capacitor_SMD"),
        ("L1", "Inductor_SMD"),
        ("D1", "SOT-23"),
        ("Q1", "TO-92"),
        ("U1", "DIP-8"),
        ("IC1", "DIP-8"),
        ("J1", "PinHeader"),
        ("P1", "PinHeader"),
        ("X1", "Resistor_SMD"),  # fallback
    ])
    def test_default_footprint(self, ref, expected_substr):
        fp = _default_footprint(ref)
        assert expected_substr in fp
