"""Minimal spec schema for sandbox (no backend dependency)."""

from pydantic import BaseModel, Field


class Component(BaseModel):
    ref: str
    value: str
    footprint: str = "Resistor_SMD:R_0805_2012Metric"


class NetSegment(BaseModel):
    ref: str
    pin: str


class Net(BaseModel):
    name: str
    connections: list[NetSegment] = Field(default_factory=list)


class CircuitSpec(BaseModel):
    components: list[Component] = Field(default_factory=list)
    nets: list[Net] = Field(default_factory=list)
