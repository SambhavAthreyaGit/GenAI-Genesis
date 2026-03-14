"""LLM service: natural-language prompt -> structured JSON spec via Anthropic."""

import json
import re

from anthropic import Anthropic

from config import get_settings
from schemas.circuit_spec import CircuitSpec

SYSTEM_PROMPT = """You are a circuit design assistant. Given a natural language description of a circuit or PCB, you output a structured JSON spec that can be used to generate a KiCad schematic and PCB.

Output ONLY valid JSON, no markdown or explanation. The JSON must have this shape:
{
  "components": [
    { "ref": "R1", "value": "10k", "footprint": "Resistor_SMD:R_0805_2012Metric" },
    { "ref": "C1", "value": "100nF", "footprint": "Capacitor_SMD:C_0805_2012Metric" },
    { "ref": "U1", "value": "LM7805", "footprint": "Package_TO_SOT_THT:TO-220-3_Vertical" }
  ],
  "nets": [
    { "name": "VCC", "connections": [{"ref": "U1", "pin": "1"}, {"ref": "C1", "pin": "1"}] },
    { "name": "GND", "connections": [{"ref": "U1", "pin": "2"}, {"ref": "C1", "pin": "2"}] }
  ]
}

Rules:
- ref: reference designator (R1, C1, U1, J1, etc.). Must be unique.
- value: component value or part number (e.g. "10k", "100nF", "LM7805").
- footprint: KiCad footprint in Library:Name form. Use standard library names like Resistor_SMD:R_0805_2012Metric, Capacitor_SMD:C_0805_2012Metric, Package_TO_SOT_THT:TO-220-3_Vertical when unsure.
- nets: list of nets. Each net has "name" and "connections" (list of {"ref": "<component ref>", "pin": "<pin number or name>"}).
- Every pin that should be connected must appear in exactly one net (except power symbols which can be in a net by name like VCC or GND).
"""


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Anthropic | None = None

    def _get_client(self) -> Anthropic:
        if self._client is None:
            if not self.settings.anthropic_api_key:
                raise ValueError("ANTHROPIC_API_KEY is not set")
            self._client = Anthropic(api_key=self.settings.anthropic_api_key)
        return self._client

    def get_spec(self, prompt: str) -> CircuitSpec:
        """Call Anthropic with prompt; parse and return CircuitSpec. Raises on API or parse errors."""
        client = self._get_client()
        response = client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text if response.content else ""
        # Strip markdown code block if present
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```\s*$", "", text)
        data = json.loads(text)
        return CircuitSpec.model_validate(data)
