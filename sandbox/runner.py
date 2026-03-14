#!/usr/bin/env python3
"""
Sandbox entry: read spec from /work/input/spec.json, write schematic and board to /work/output/.
Run kicad-cli sch erc and write erc_result.json.
"""

import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

# Sandbox paths (backend mounts work dir at /work)
WORK = Path(os.environ.get("WORK", "/work"))
INPUT_DIR = WORK / "input"
OUTPUT_DIR = WORK / "output"
SPEC_PATH = INPUT_DIR / "spec.json"
RUN_ERC = os.environ.get("RUN_ERC", "1") == "1"


def lib_id_for_ref(ref: str) -> str:
    """Map component ref prefix to KiCad symbol lib_id."""
    r = (ref or "R").upper()
    if r.startswith("R"):
        return "Device:R"
    if r.startswith("C"):
        return "Device:C"
    if r.startswith("L"):
        return "Device:L"
    if r.startswith("D"):
        return "Device:D"
    if r.startswith("Q"):
        return "Device:Q_NPN_BCE"
    if r.startswith("U") or r.startswith("IC"):
        return "Device:Opamp"
    return "Device:R"


def generate_schematic_sexpr(spec: dict) -> str:
    """Generate minimal valid .kicad_sch s-expression from spec."""
    version = "20230121"
    gen = "genai-genesis-sandbox"
    root_uuid = str(uuid.uuid4())
    parts = [
        "(kicad_sch",
        f'  (version {version})',
        f'  (generator "{gen}")',
        f'  (uuid "{root_uuid}")',
        "  (paper \"A4\")",
        "  (title_block",
        "    (title \"\") (date \"\") (rev \"\") (company \"\")",
        "  )",
        "  (lib_symbols",
    ]
    # Define one symbol per unique lib_id (minimal two-pin symbol for ERC)
    seen_libs: set[str] = set()
    for comp in spec.get("components", []):
        lib_id = lib_id_for_ref(comp.get("ref", "R"))
        if lib_id in seen_libs:
            continue
        seen_libs.add(lib_id)
        # KiCad 6 lib_symbols: (symbol "LibId" ...) with internal symbol and pins
        sym_name = lib_id.replace(":", "_")
        pin1_uuid = str(uuid.uuid4())
        pin2_uuid = str(uuid.uuid4())
        parts.append(f'    (symbol "{lib_id}" (in_bom yes) (on_board yes)')
        parts.append('      (property "Reference" "" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))')
        parts.append('      (property "Value" "" (at 0 2.54 0) (effects (font (size 1.27 1.27))))')
        parts.append(f'      (symbol "{sym_name}_0_1"')
        parts.append(f'        (pin "1" input (at 0 0 0) (length 0) (uuid "{pin1_uuid}"))')
        parts.append(f'        (pin "2" output (at 0 2.54 0) (length 0) (uuid "{pin2_uuid}"))')
        parts.append("      )")
        parts.append("    )")
    parts.append("  )")

    # Symbol instances: place each component
    step = 25.4  # 1 inch
    for i, comp in enumerate(spec.get("components", [])):
        ref = comp.get("ref", f"R{i+1}")
        value = comp.get("value", "")
        lib_id = lib_id_for_ref(ref)
        sym_inst_uuid = str(uuid.uuid4())
        x, y = 50.8 + (i % 4) * step, 25.4 + (i // 4) * step
        parts.append("  (symbol")
        parts.append(f'    (lib_id "{lib_id}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)')
        parts.append(f'    (uuid "{sym_inst_uuid}")')
        parts.append(f'    (property "Reference" "{ref}" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))')
        parts.append(f'    (property "Value" "{value}" (at 0 2.54 0) (effects (font (size 1.27 1.27))))')
        parts.append('    (instances')
        parts.append(f'      (project "genesis" (path "/{root_uuid}") (reference "{ref}") (unit 1))')
        parts.append("    )")
        parts.append("  )")

    # Wires: connect nets (simplified: one wire per net between first two pins)
    wire_uuid = 0
    for net in spec.get("nets", []):
        conns = net.get("connections", [])
        if len(conns) < 2:
            continue
        # Place a wire between two pins (we use fixed positions for MVP)
        ref_to_xy = {}
        for j, c in enumerate(spec.get("components", [])):
            rx = 50.8 + (j % 4) * step
            ry = 25.4 + (j // 4) * step
            ref_to_xy[c.get("ref")] = (rx, ry)
        try:
            (x1, y1), (x2, y2) = ref_to_xy[conns[0]["ref"]], ref_to_xy[conns[1]["ref"]]
            mid_y = (y1 + y2) / 2
            parts.append("  (wire")
            parts.append(f"    (pts (xy {x1} {y1}) (xy {x1} {mid_y}) (xy {x2} {mid_y}) (xy {x2} {y2}))")
            parts.append(f'    (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}")')
            parts.append("  )")
        except KeyError:
            pass

    parts.append("  (path")
    parts.append(f'    "/" (page "1")')
    parts.append("  )")
    parts.append(")")
    return "\n".join(parts)


def generate_pcb_sexpr(spec: dict) -> str:
    """Generate minimal valid .kicad_pcb with placed footprints (no routing)."""
    version = "20240108"
    gen = "genai-genesis-sandbox"
    parts = [
        "(kicad_pcb",
        f"  (version {version})",
        f'  (generator "{gen}")',
        "  (general)",
        "  (paper A4)",
        "  (layers",
        "    (0 \"F.Cu\" signal)",
        "    (31 \"B.Cu\" signal)",
        "    (32 \"B.Adhes\" user \"B.Adhesive\")",
        "    (33 \"F.Adhes\" user \"F.Adhesive\")",
        "    (34 \"B.Paste\" user)",
        "    (35 \"F.Paste\" user)",
        "    (36 \"B.SilkS\" user \"B.Silkscreen\")",
        "    (37 \"F.SilkS\" user \"F.Silkscreen\")",
        "    (38 \"B.Mask\" user)",
        "    (39 \"F.Mask\" user)",
        "  )",
    ]
    # Place one footprint per component in a grid
    step_mm = 10.0
    for i, comp in enumerate(spec.get("components", [])):
        ref = comp.get("ref", f"R{i+1}")
        fp = comp.get("footprint", "Resistor_SMD:R_0805_2012Metric")
        x_mm = 50 + (i % 6) * step_mm
        y_mm = 50 + (i // 6) * step_mm
        fp_uuid = str(uuid.uuid4())
        parts.append("  (footprint")
        parts.append(f'    (type smd) (library_id "{fp}") (at {x_mm} {y_mm}) (layer "F.Cu")')
        parts.append(f'    (tstamp {fp_uuid[:8]}) (uuid "{fp_uuid}")')
        parts.append(f'    (property "Reference" "{ref}" (at 0 -1.27 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))) (uuid "{uuid.uuid4()}"))')
        parts.append(f'    (property "Value" "{comp.get("value", "")}" (at 0 1.27 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))) (uuid "{uuid.uuid4()}"))')
        parts.append("  )")
    parts.append(")")
    return "\n".join(parts)


def run_erc(schematic_path: Path) -> tuple[bool, list[str]]:
    """Run kicad-cli sch erc; return (passed, list of message strings)."""
    cli = shutil.which("kicad-cli")
    if not cli:
        return False, ["kicad-cli not found"]
    try:
        result = subprocess.run(
            [cli, "sch", "erc", str(schematic_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        lines = [s for s in (out + "\n" + err).split("\n") if s.strip()]
        passed = result.returncode == 0
        return passed, lines
    except subprocess.TimeoutExpired:
        return False, ["ERC timed out"]
    except Exception as e:
        return False, [str(e)]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not SPEC_PATH.exists():
        print("ERROR: spec.json not found", file=sys.stderr)
        sys.exit(1)
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))

    schematic_path = OUTPUT_DIR / "schematic.kicad_sch"
    board_path = OUTPUT_DIR / "board.kicad_pcb"
    schematic_path.write_text(generate_schematic_sexpr(spec), encoding="utf-8")
    board_path.write_text(generate_pcb_sexpr(spec), encoding="utf-8")

    erc_passed = True
    erc_messages: list[str] = []
    if RUN_ERC:
        erc_passed, erc_messages = run_erc(schematic_path)

    summary = "ERC passed." if erc_passed else ("ERC failed: " + "; ".join(erc_messages[:5]))
    erc_result = {
        "passed": erc_passed,
        "messages": erc_messages,
        "summary": summary,
    }
    (OUTPUT_DIR / "erc_result.json").write_text(
        json.dumps(erc_result, indent=2),
        encoding="utf-8",
    )
    print("OK: schematic and board written to output/")


if __name__ == "__main__":
    main()
