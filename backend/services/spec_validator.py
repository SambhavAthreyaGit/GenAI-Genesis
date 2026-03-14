"""Validate and normalize LLM output before sending to sandbox."""

from schemas.circuit_spec import CircuitSpec, Component, Net, NetSegment


class SpecValidationError(ValueError):
    """Raised when spec validation fails."""

    pass


class SpecValidator:
    """Validates and normalizes a CircuitSpec for the sandbox."""

    def validate(self, spec: CircuitSpec) -> CircuitSpec:
        """
        Validate required fields, ref uniqueness, net references; normalize.
        Returns validated/normalized spec. Raises SpecValidationError on failure.
        """
        if not spec.components:
            raise SpecValidationError("At least one component is required")

        refs = set()
        for c in spec.components:
            ref = (c.ref or "").strip()
            val = (c.value or "").strip()
            if not ref or not val:
                raise SpecValidationError(f"Component must have ref and value: {c}")
            if ref in refs:
                raise SpecValidationError(f"Duplicate component ref: {ref}")
            refs.add(ref)

        for net in spec.nets:
            for seg in net.connections:
                seg_ref = (seg.ref or "").strip()
                seg_pin = (str(seg.pin) if seg.pin else "").strip()
                if seg_ref not in refs:
                    raise SpecValidationError(
                        f"Net '{net.name}' references unknown component ref: {seg_ref}"
                    )
                if not seg_pin:
                    raise SpecValidationError(
                        f"Net '{net.name}' has connection with empty pin for ref {seg_ref}"
                    )

        # Normalize: ensure footprint has a default when empty
        components = []
        for c in spec.components:
            footprint = c.footprint.strip() if c.footprint else _default_footprint(c.ref)
            components.append(
                Component(ref=c.ref.strip(), value=c.value.strip(), footprint=footprint)
            )

        nets = []
        for n in spec.nets:
            name = (n.name or "").strip() or "UnnamedNet"
            connections = [
                NetSegment(ref=s.ref.strip(), pin=str(s.pin).strip())
                for s in n.connections
            ]
            nets.append(Net(name=name, connections=connections))

        return CircuitSpec(components=components, nets=nets)


def _default_footprint(ref: str) -> str:
    """Return a sensible default footprint based on ref prefix."""
    r = ref.upper()
    if r.startswith("R"):
        return "Resistor_SMD:R_0805_2012Metric"
    if r.startswith("C"):
        return "Capacitor_SMD:C_0805_2012Metric"
    if r.startswith("L"):
        return "Inductor_SMD:L_0805_2012Metric"
    if r.startswith("D"):
        return "Package_TO_SOT_SMD:SOT-23"
    if r.startswith("Q"):
        return "Package_TO_SOT_THT:TO-92_Inline"
    if r.startswith("U") or r.startswith("IC"):
        return "Package_DIP:DIP-8_W7.62mm"
    if r.startswith("J") or r.startswith("P"):
        return "Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical"
    return "Resistor_SMD:R_0805_2012Metric"
