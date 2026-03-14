# GenAI-Genesis — Project Spec

## Overview

Web app: user describes a circuit/PCB in natural language → backend generates a KiCad schematic and placed-only PCB → user sees both in the browser (KiCanvas) and can run ERC. No autorouter; routing is left to the user in KiCad.

---

## User Flow

1. **Land on the app**  
   User opens the web app (Next.js frontend).

2. **Enter prompt**  
   User types a natural-language description in a text area (e.g. “Create a line follower PCB”, “Simple 5 V regulator with LED”).

3. **Generate**  
   User clicks **Generate** (or similar). Frontend sends the prompt to the backend.

4. **Backend pipeline**  
   - Backend calls **Anthropic API** with the prompt (+ system prompt / few-shot if needed).  
   - LLM returns a **structured spec** (e.g. JSON: components, refs, values, nets).  
   - Backend runs a **QA sandbox** (Ubuntu Docker with KiCad + Python):  
     - Python (e.g. **kiutils** or **kicad-sch-api**) turns the spec into **`.kicad_sch`**.  
     - Same process creates **`.kicad_pcb`** with footprints placed (simple placement, no router).  
     - Runs **ERC** in the sandbox (`kicad-cli sch erc`).  
   - Backend stores the generated files and returns **project id** and **file URLs** (and ERC result if run).

5. **View on the page**  
   Frontend loads the schematic and board URLs into **KiCanvas** (two viewers: schematic + PCB). User can pan/zoom and inspect both.

6. **Verification feedback**  
   If ERC was run, the UI shows **ERC passed** or **ERC failed** with a short summary (e.g. “Pin 5 of U1 unconnected”). Optional: “Regenerate” or “Fix” to re-run the pipeline which would update the prompt to redesign.

7. **Download (optional)**  
   User can **Download project** (schematic + PCB as a zip or KiCad project) to open in KiCad for routing and fabrication.

---

## Tech Stack

### Frontend

| Layer        | Choice        | Notes                                      |
|-------------|----------------|--------------------------------------------|
| Framework   | **Next.js**    | App router, API routes if needed           |
| UI          | **React**      | Components for prompt, viewers, status      |
| Styling     | **Tailwind CSS** | Layout, forms, buttons, responsive       |
| Viewer      | **KiCanvas**   | Embed for `.kicad_sch` and `.kicad_pcb`     |

- Single page or minimal routing: prompt → result view.  
- KiCanvas: `<kicanvas-embed src={schematicUrl} />` and same for board URL.

### Backend

| Layer        | Choice        | Notes                                      |
|-------------|----------------|--------------------------------------------|
| API         | **FastAPI**    | REST (e.g. `POST /generate`, `GET /projects/{id}`) |
| LLM         | **Anthropic API** | Claude for prompt → structured spec     |
| Spec → KiCad| **Python**     | Inside sandbox: kiutils and/or kicad-sch-api |
| Execution   | **QA sandbox** | Ubuntu Docker with KiCad CLI + Python deps |

- FastAPI receives prompt, calls Anthropic, then invokes the sandbox with the spec (and optional prompt for debugging).  
- Sandbox returns paths/artifacts; FastAPI stores files (e.g. local or S3-like) and returns URLs + ERC result.

### QA Sandbox (Docker)

| Item        | Choice        | Notes                                      |
|-------------|----------------|--------------------------------------------|
| Base image  | **Ubuntu**     | LTS                                        |
| KiCad       | **KiCad 7/8**  | Install `kicad-cli` (and deps) for ERC     |
| Python      | **3.10+**      | kiutils and/or kicad-sch-api               |
| Usage       | One-off run    | Backend runs container (or exec in a pool), passes spec in, reads generated files + ERC output out |

- Sandbox does **not** need a display; only CLI and file I/O.  
- Input: structured spec (JSON). Output: `.kicad_sch`, `.kicad_pcb`, and optional ERC report (stdout/stderr or file).

### LLM

| Item        | Choice        | Notes                                      |
|-------------|----------------|--------------------------------------------|
| Provider    | **Anthropic**  | Claude API                                 |
| Output      | **Structured** | JSON spec (components, nets); parse and validate in backend |

- System prompt: define the schema (e.g. component list with ref, value, footprint; net list with pin refs).  
- Response parsing: validate JSON, handle malformed output with retries or fallback.

### Storage

- **Generated files:** `.kicad_sch`, `.kicad_pcb` (and optionally ERC report). Store in filesystem or object store; expose via stable URLs (or signed URLs) for KiCanvas.  
- **Metadata:** Project id, prompt, timestamps, ERC status. FastAPI can keep in memory, SQLite, or Postgres depending on need.

---

## Pipeline (Backend + Sandbox)

```
User prompt
    → FastAPI
    → Anthropic API (prompt → structured spec JSON)
    → Validate / normalize spec
    → Invoke QA sandbox (Ubuntu Docker)
        → Python: spec → .kicad_sch (kiutils / kicad-sch-api)
        → Python: .kicad_sch → .kicad_pcb with placed footprints (kiutils), no router
        → kicad-cli sch erc project.kicad_sch (optional)
        → Output: .kicad_sch, .kicad_pcb, erc_result
    → FastAPI: store files, return URLs + ERC summary
    → Frontend: load URLs in KiCanvas, show ERC status
```

---

## What We’re Not Doing (Scope)

- No autorouter (no FreeRouting or other router).  
- No SPICE in MVP (can add later).  
- No vector DB in MVP.  
- No user auth in MVP (optional later).  
- Routing: user does it in KiCad after download.

---

## File Layout (Suggested)

```
GenAI-Genesis/
├── docs/
│   └── PROJECT_SPEC.md          # this file
├── frontend/                    # Next.js + React + Tailwind
│   ├── app/
│   │   ├── page.tsx             # main page: prompt + viewers
│   │   └── layout.tsx
│   └── ...
├── backend/                     # FastAPI
│   ├── main.py
│   ├── routes/
│   ├── services/                # anthropic, sandbox runner
│   └── ...
├── sandbox/                     # Docker + KiCad + Python
│   ├── Dockerfile               # Ubuntu + KiCad + kiutils
│   ├── runner.py                # entry: read spec, write .kicad_sch/.kicad_pcb, run ERC
│   └── requirements.txt
└── README.md
```

---

## Summary

- **User flow:** Prompt → Generate → View schematic + PCB in browser (KiCanvas) → See ERC result → Optional download.  
- **Tech:** Next.js (React, Tailwind), FastAPI, Anthropic API, Ubuntu Docker sandbox with KiCad + Python (kiutils), KiCanvas. No vector DB for MVP.  
- **Output:** Schematic + placed-only PCB; no router; ERC for “does the design work?” before fabrication.
