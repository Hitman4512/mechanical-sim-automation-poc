# AI-Driven Mechanical 3D Simulation Automation — Local POC

> Convert a paired CAD model + procedural PDF into a fully rendered 4K mechanical simulation video via a deterministic local pipeline that calls the Claude API exactly **twice**.

**Author:** Siddhartha Aryan · 23FE10CDS00194 · MUJ  
**Status:** Phase 8 Complete — Demo render validated ✅  
**Repo:** `SiddharthaAryan-2003/animation_and_rendering_automation-n8n`

---

## What This Does

This pipeline takes two inputs — a CAD model (`.obj`, `.fbx`, `.glb`, etc.) and a procedural PDF document describing mechanical operations — and produces a fully rendered 4K animation video showing the mechanical procedure being executed in 3D.

The entire process is orchestrated by n8n, runs 100% locally on a Windows machine with an NVIDIA GPU, and uses the Claude API for exactly two AI inference calls per run. Everything else — CAD preprocessing, keyframe application, rendering, and video assembly — is deterministic and local.

---

## The Iron Rule

> **Claude API is called exactly 2 times per pipeline run. No loops. No re-invocations on failure.**

- **Call \#1 (Phase 2):** Procedural PDF → Procedural JSON (assembly steps, motion params, timing)
- **Call \#2 (Phase 4):** Procedural JSON + Object Manifest → Simulation Execution JSON (keyframes, camera paths, constraints)

If AI output is invalid at any phase, the workflow stops and logs the error. The prompt is improved offline and redeployed for the next run. Never patched live.

---

## Tech Stack

| Layer | Tool | Version |
|---|---|---|
| OS | Windows (native, no WSL2) | — |
| Orchestration | n8n | 2.26.7 (npm) |
| AI | Claude API | `claude-sonnet-4-6` |
| 3D Engine | Blender (headless) | 4.5.10 LTS |
| Render Engine | Cycles + OptiX | GPU compute |
| Scripting | Python | 3.12.5 |
| JSON Validation | jsonschema | 4.26.0 |
| Video Assembly | FFmpeg | 8.1.1 |
| GPU | NVIDIA RTX A4500 | 24GB VRAM |

---

## Repository Structure

```
mechanical-sim-automation-poc/
├── .env.example                        ← Copy to .env, fill in your values
├── requirements.txt                    ← Python dependencies
├── FINAL_ARCHITECTURE.md               ← Authoritative technical spec (locked)
├── project_progress.md                 ← Day-by-day build log
├── n8n-workflows/
│   └── cad_simulation_pipeline.json    ← Import this into n8n
├── scripts/
│   ├── blender_preprocess.py           ← Phase 3: CAD → Object Manifest JSON
│   ├── blender_simulate_render.py      ← Phase 5+6: Keyframes + Cycles render
│   └── validate_schema.py             ← Phase 4.5: JSON schema gate
├── schemas/
│   ├── procedural_json.schema.json
│   ├── object_manifest.schema.json
│   └── simulation_execution.schema.json
└── docs/
    └── AI_Simulation_POC_Revised_Local_Architecture.docx
```

**Runtime data** (inputs, intermediates, outputs, logs) lives at `C:\pipeline\` — not versioned.

---

## Prerequisites

Install all of the following on a Windows machine with an NVIDIA GPU:

- **Node.js LTS** — [nodejs.org](https://nodejs.org)
- **n8n** — `npm install n8n -g`
- **Python 3.x** — [python.org](https://python.org) (check "Add to PATH")
- **Blender 4.5 LTS** — [blender.org](https://blender.org) *(do not use Blender 5.x — breaking API changes)*
- **FFmpeg** — download static build, add `bin\` to PATH
- **Git** — [git-scm.com](https://git-scm.com)
- **NVIDIA GPU with OptiX support** — RTX series recommended

Verify all installs:
```powershell
node -v && n8n --version && python --version && blender --version && ffmpeg -version && git --version
```

---

## Setup

### 1. Clone the repo
```powershell
git clone https://github.com/SiddharthaAryan-2003/animation_and_rendering_automation-n8n.git
cd animation_and_rendering_automation-n8n
```

### 2. Install Python dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure environment
```powershell
copy .env.example .env
```
Edit `.env` and fill in:
```
CLAUDE_API_KEY=sk-ant-your-key-here
PIPELINE_ROOT=C:\pipeline
BLENDER_EXE_PATH=C:\Program Files\Blender Foundation\Blender 4.5\blender.exe
```

### 4. Create the runtime folder tree
```powershell
mkdir C:\pipeline\inputs\cad
mkdir C:\pipeline\inputs\pdf
mkdir C:\pipeline\intermediates
mkdir C:\pipeline\outputs
mkdir C:\pipeline\logs
```

### 5. Import the n8n workflow
- Start n8n: `n8n start`
- Open `http://localhost:5678`
- Import `n8n-workflows/cad_simulation_pipeline.json`
- Add your `CLAUDE_API_KEY` to n8n's environment variables

---

## Running a Job

1. Place your CAD file in `C:\pipeline\inputs\cad\` (e.g. `part.obj`)
2. Place the matching PDF in `C:\pipeline\inputs\pdf\` (e.g. `part.pdf`) — filenames must match (case-insensitive)
3. Open n8n at `http://localhost:5678`
4. Click **Execute Workflow** on `CAD Simulation Pipeline (Local)`
5. Output video appears at `C:\pipeline\outputs\{jobId}.mp4`

---

## Pipeline Phases

| Phase | Type | Description |
|---|---|---|
| 0 | Setup | Environment install, repo scaffold |
| 1 | Manual | Input pairing: CAD ↔ PDF by filename, 1 retry |
| 2 | **AI Call \#1** | PDF → Procedural JSON via Claude |
| 3 | Local | Blender headless: CAD → Object Manifest JSON |
| 4 | **AI Call \#2** | Procedural JSON + Manifest → Simulation Execution JSON via Claude |
| 4.5 | Local | JSON schema validation gate (stop on failure) |
| 5+6 | Local | Blender: apply keyframes + Cycles render → PNG sequence |
| 7 | Local | FFmpeg: PNG sequence → MP4 (H.264, CRF 18) |
| 8 | Local | Completion report written to `C:\pipeline\logs\` |

---

## Supported CAD Formats

`.obj` · `.fbx` · `.glb` · `.gltf` · `.blend` · `.abc` · `.usd` · `.usda` · `.usdc`

---

## Render Settings (Default)

| Setting | Value |
|---|---|
| Engine | Cycles |
| Device | OptiX (NVIDIA GPU) |
| Resolution | 3840 × 2160 (4K) |
| Frame Rate | 24 fps |
| Samples | 512 |
| Output Format | PNG 16-bit → H.264 MP4 |

---

## Known n8n Constraints (v2.26.7)

If you extend or modify the workflow, be aware of these confirmed quirks:

- `fs`, `path`, `child_process` are **blocked** in Code nodes — use Execute Command nodes for filesystem ops
- Code node mode must be **"Run Once for All Items"** — upstream data access with `.first()` fails in per-item mode
- Execute Command nodes **cannot** resolve `{{ }}` expressions with embedded double-quotes — pre-build CLI strings in a preceding Code node
- Write/Read File nodes: use a **single concatenated expression** for paths — two separate `{{ }}` blocks with a literal `\` between them breaks the parser
- For long-running processes (Blender renders): redirect stdout to a log file and echo a short sentinel string — n8n's Execute Command stdout buffer overflows on verbose output

---

## Cost Per Video

| Component | Cost |
|---|---|
| Claude Call \#1 | ₹10–₹40 |
| Claude Call \#2 | ₹40–₹100 |
| Rendering (local GPU) | ₹0 |
| **Total** | **₹50–₹140** |

---

## Architecture Reference

See [`FINAL_ARCHITECTURE.md`](./FINAL_ARCHITECTURE.md) for the complete locked specification — schemas, node graph, naming conventions, error handling standards, and change control rules.

---

## Future Scope

- Swap mock Claude Call nodes → real HTTP Request nodes (pending API key)
- Real UR10 robot CAD + PDF end-to-end run
- AWS cloud migration for production scale (S3 + Lambda + EC2 GPU)
- Prompt A/B testing with Braintrust once Iron Rule is relaxed for v2
- Automated folder-watch trigger to replace manual n8n UI trigger

---

## License

MIT — open-source framework, structured for third-party reproduction. See `requirements.txt` and `.env.example` to get started.