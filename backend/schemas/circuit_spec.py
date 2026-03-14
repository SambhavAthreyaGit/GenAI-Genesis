"""Shared circuit spec schema for LLM output, validator, and sandbox."""

from pydantic import BaseModel, Field


class Component(BaseModel):
    """A component in the circuit (e.g. resistor, IC, connector)."""

    ref: str = Field(..., description="Reference designator, e.g. R1, U1, C1")
    value: str = Field(..., description="Value or part number, e.g. 10k, LM7805")
    footprint: str = Field(
        default="Resistor_SMD:R_0805_2012Metric",
        description="KiCad footprint library:name, e.g. Resistor_SMD:R_0805_2012Metric",
    )


class NetSegment(BaseModel):
    """A single connection in a net: component ref and pin number."""

    ref: str = Field(..., description="Component reference, e.g. R1")
    pin: str = Field(..., description="Pin number or name, e.g. 1, VCC")


class Net(BaseModel):
    """A net: named net with list of connected pins."""

    name: str = Field(..., description="Net name, e.g. VCC, GND, Net_R1_1")
    connections: list[NetSegment] = Field(
        default_factory=list,
        description="List of ref+pin that are connected on this net",
    )


class CircuitSpec(BaseModel):
    """Structured spec: components and nets. Used by LLM, validator, and sandbox."""

    components: list[Component] = Field(
        default_factory=list,
        description="List of components with ref, value, footprint",
    )
    nets: list[Net] = Field(
        default_factory=list,
        description="List of nets with name and connections (ref, pin)",
    )
