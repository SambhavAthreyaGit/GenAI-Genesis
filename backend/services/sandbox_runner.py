"""Run KiCad generation in Docker sandbox; return generated files and ERC result."""

import asyncio
import json
import shutil
import tempfile
from pathlib import Path

from config import get_settings
from schemas.api import ERCResult
from schemas.circuit_spec import CircuitSpec


class SandboxRunner:
    """Invoke sandbox Docker image with spec; collect .kicad_sch, .kicad_pcb, ERC result."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def run(
        self,
        spec: CircuitSpec,
        run_erc: bool = True,
    ) -> tuple[bytes, bytes, ERCResult | None]:
        """
        Run sandbox with validated spec. Returns (schematic_content, pcb_content, erc_result).
        Raises on timeout or container failure.
        """
        docker = shutil.which("docker")
        if not docker:
            raise RuntimeError("Docker not found in PATH")

        with tempfile.TemporaryDirectory(prefix="genai_sandbox_") as tmp:
            work = Path(tmp)
            input_dir = work / "input"
            output_dir = work / "output"
            input_dir.mkdir()
            output_dir.mkdir()

            spec_path = input_dir / "spec.json"
            spec_path.write_text(spec.model_dump_json(indent=2), encoding="utf-8")

            # Container contract: read /work/input/spec.json, write to /work/output/
            cmd = [
                "docker",
                "run",
                "--rm",
                "--network=none",
                "-v",
                f"{work}:/work:rw",
                "-e",
                f"RUN_ERC={'1' if run_erc else '0'}",
                self.settings.sandbox_image,
            ]
            timeout = self.settings.sandbox_timeout_seconds

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(work),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                raise RuntimeError(
                    f"Sandbox timed out after {timeout}s. KiCad generation may be too slow."
                ) from None

            if proc.returncode != 0:
                err = (stderr or b"").decode("utf-8", errors="replace")
                raise RuntimeError(f"Sandbox failed (exit {proc.returncode}): {err}")

            schematic_path = output_dir / "schematic.kicad_sch"
            pcb_path = output_dir / "board.kicad_pcb"
            if not schematic_path.exists():
                raise RuntimeError("Sandbox did not produce schematic.kicad_sch")
            if not pcb_path.exists():
                raise RuntimeError("Sandbox did not produce board.kicad_pcb")

            schematic_content = schematic_path.read_bytes()
            pcb_content = pcb_path.read_bytes()

            erc_result: ERCResult | None = None
            erc_path = output_dir / "erc_result.json"
            if erc_path.exists():
                try:
                    data = json.loads(erc_path.read_text(encoding="utf-8"))
                    erc_result = ERCResult.model_validate(data)
                except Exception:
                    erc_result = ERCResult(
                        passed=False,
                        messages=[f"Could not parse {erc_path}"],
                        summary="ERC result unreadable",
                    )
            elif run_erc:
                # Sandbox may have written ERC to stdout; we could parse it here
                erc_result = ERCResult(
                    passed=False,
                    messages=["ERC was requested but erc_result.json was not produced"],
                    summary="ERC result missing",
                )

            return schematic_content, pcb_content, erc_result
