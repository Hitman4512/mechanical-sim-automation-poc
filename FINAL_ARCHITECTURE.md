# FINAL_ARCHITECTURE.md

**Version:** 1.0
**Status:** 🔒 LOCKED
**Locked Date:** June 19, 2026
**Author:** Siddhartha Aryan (C133967)

---

## 0. Document Control — Read This First

This file is the **single source of truth** for the AI-Driven Mechanical 3D Simulation Automation POC. It exists so that any LLM session (or human) picking up this project — regardless of how much time has passed — can execute against one unchanging plan instead of re-deciding settled questions, drifting, or hallucinating details.

**Rules for using this file:**
1. Every architectural decision in this document is FINAL. Do not propose alternatives, "improvements," or reinterpretations unless the user explicitly says "update FINAL_ARCHITECTURE.md."
2. If something in `project_progress.md` (the daily-state-tracking companion file) seems to contradict this file, **this file wins** — flag the contradiction to the user, don't silently resolve it.
3. If a detail needed for implementation is genuinely missing from this file, ask the user — don't invent it and don't retroactively edit this file without explicit permission.
4. This file describes the **target architecture**, not necessarily what has been built yet. For "where are we right now," read `project_progress.md`.

---

## 1. Project Identity

**Name:** AI-Driven Mechanical 3D Simulation Automation — Local POC
**One-line goal:** Convert a paired CAD model + procedural PDF into a fully rendered 4K mechanical simulation video, via a deterministic local pipeline that calls the Claude API exactly twice.
**Canonical test case:** `UR10.fbx` + `UR10.pdf` (UR10 robot, camera movement / procedural instructions).
**Distribution:** Runs 100% locally, but the codebase (Section 6.1 — excluding runtime data in Section 6.2) is structured for publication as an open-source framework on GitHub. A third party must be able to reproduce the environment using only `requirements.txt` and `.env.example`.

---

## 2. Core Principle — The Iron Rule (Non-Negotiable)

> **Claude API is called exactly 2 times per pipeline run. No loops. No re-invocations on failure.**

- Call #1 (Phase 2): Procedural PDF → Procedural JSON
- Call #2 (Phase 4): Procedural JSON + Object Manifest JSON → Simulation Execution JSON
- If output at any AI-dependent phase is invalid, the workflow **stops and logs the error**. It does **not** call Claude again to "fix" or retry.
- Prompts are improved **offline** (by editing the HTTP Request node's prompt/body) and redeployed for the *next* run — never patched live mid-run with extra calls.
- **Enforcement check:** the n8n workflow graph must contain **exactly two** nodes that call `api.anthropic.com`, and neither may have an incoming connection that originates from a downstream failure/retry path.

---

## 3. Scope Boundaries

### In Scope
- 100% local execution on a single Windows laptop.
- Manual trigger via n8n UI (no folder-watch automation).
- Local Blender (headless, Cycles) for CAD preprocessing, simulation, and rendering.
- Local n8n instance (installed via `npm`, not Docker).
- Exactly 2 Claude API calls per run.

### Explicitly Out of Scope (Decommissioned / Not Used)
- ❌ AWS S3, Lambda, IAM, EC2, CloudWatch — fully decommissioned. Old cloud architecture is **retired**, not paused.
- ❌ GitHub Codespaces hosting for n8n — n8n no longer runs remotely.
- ❌ Automated folder-watch triggers.
- ❌ Docker / containerization for n8n.
- ❌ WSL2 — pipeline runs natively on Windows (PowerShell/CMD only).
- ❌ Any third Claude API call, feedback loop, or retry-to-Claude mechanism.
- ❌ A/B testing, prompt evaluation platforms (Braintrust, PromptLab, Arize) — explicitly deferred to v2.

---

## 4. Tech Stack (Exact)

| Layer | Tool | Version / Notes |
|---|---|---|
| OS | Windows | Native, no WSL2 |
| Orchestration | n8n | Latest stable via `npm install n8n -g`, run locally on `localhost:5678` |
| AI | Claude API | Model string: `claude-sonnet-4-6` |
| 3D Engine | Blender | 4.x, headless mode (`--background`) |
| Render Engine | Cycles | GPU compute (OptiX), **not** Eevee — quality over speed |
| Scripting | Python | 3.x, for `validate_schema.py` (uses `jsonschema` library) and Blender Python API scripts |
| Video Assembly | FFmpeg | H.264 (libx264) encoding |
| Version Control | Git + GitHub | Local repo, pushed to GitHub |
| Data Exchange Format | JSON | All inter-phase data |
| GPU | RTX A4500 | 24GB VRAM, i9 12th gen laptop |

---

## 5. Local Environment Specification

- **Machine:** Single Windows laptop (i9 12th gen, RTX A4500 24GB VRAM). No remote compute.
- **Shell:** PowerShell or CMD for all script/process invocation. No bash, no WSL2.
- **n8n hosting:** Runs as a local Node.js process on the same machine as Blender — this is required because the `Execute Command` node spawns subprocesses on the host it runs on, and it must have direct access to the local GPU, local Blender install, and local filesystem.
- **Network:** No external network dependency except the two outbound HTTPS calls to `api.anthropic.com`. No webhook ingress required (manual trigger only).

---

## 6. Repository & Folder Structure

### 6.1 Git Repository (versioned, pushed to GitHub)

Lives at a path of the user's choosing (e.g. `C:\Users\<user>\projects\mechanical-sim-automation-poc\`). Contains code/config only — **no large binary runtime data**. This is the exact folder published to GitHub as the open-source framework; anyone cloning it should be able to reproduce the environment using only `requirements.txt` and `.env.example`.

```
mechanical-sim-automation-poc/
├── .env                          (gitignored — real secrets/paths)
├── .env.example                  (committed — template, no secrets)
├── requirements.txt              (committed — pinned Python dependencies)
├── .gitignore
├── README.md
├── FINAL_ARCHITECTURE.md
├── project_progress.md
├── n8n-workflows/
│   └── cad_simulation_pipeline.json   (exported n8n workflow, committed after every major change)
├── scripts/
│   ├── blender_preprocess.py     (Phase 3)
│   ├── blender_simulate_render.py (Phase 5 + 6)
│   └── validate_schema.py        (Phase 4.5)
├── schemas/
│   ├── procedural_json.schema.json
│   ├── object_manifest.schema.json
│   └── simulation_execution.schema.json
└── docs/
    └── AI_Simulation_POC_Revised_Local_Architecture.docx
```

### 6.2 Runtime Pipeline Data (NOT versioned — pure local working directory)

Path is set via `.env` variable `PIPELINE_ROOT`, default `C:\pipeline\`. This directory holds large/transient files and is **entirely separate from the git repo** (not nested inside it).

```
C:\pipeline\
├── inputs\
│   ├── cad\        ← .fbx / .usd / .usda / .usdc / .abc / .blend / .obj / .gltf / .glb
│   └── pdf\        ← procedural PDF documents
├── intermediates\
│   └── {jobId}\
│       ├── {jobId}-procedural.json
│       ├── {jobId}-object-manifest.json
│       ├── {jobId}-simulation-execution.json
│       ├── {jobId}-validation-error.log     (only if validation fails)
│       └── frames\
│           └── frame_0001.png ... frame_NNNN.png
├── outputs\
│   └── {jobId}.mp4
└── logs\
    └── {jobId}-report.json
```

---

## 7. Naming Conventions

- **`jobId` format:** `{baseName}_{YYYYMMDD_HHMMSS}` — e.g. `UR10_20260619_143000`. Generated once at Phase 1 and threaded through every downstream phase, filename, and log.
- **`baseName`:** filename without extension, used to pair CAD ↔ PDF. Comparison is **case-insensitive exact match** (e.g. `UR10.fbx` ↔ `ur10.pdf` is a valid pair; `UR10_v2.fbx` ↔ `UR10.pdf` is not).
- **Multiple-file rule:** If more than one CAD or PDF file exists in the input folders at once, the pipeline logs a warning and processes only the **alphabetically first valid matching pair**, ignoring the rest. (POC assumes one job at a time.)

---

## 8. Phase 0 — Environment & Project Setup

**Type:** One-time (re-run only if environment changes)

### 8.1 Software to Install (Windows, native)

| Software | Purpose | Install Method |
|---|---|---|
| Node.js (LTS) | Required to run n8n | Official Windows installer |
| n8n | Orchestration engine | `npm install n8n -g` |
| Python 3.x | Validation script + Blender API scripting support | Official Windows installer, ensure "Add to PATH" checked |
| Python packages (`requirements.txt`) | Phase 4.5 validation (`jsonschema`) | `pip install -r requirements.txt` |
| Blender 4.x | CAD preprocessing, simulation, rendering | Official Windows installer |
| FFmpeg | Video assembly | Download static build, add `bin\` to PATH |
| Git | Version control | Official Windows installer |
| GitHub CLI (optional) | Easier repo creation/push | `winget install GitHub.cli` |

### 8.2 Verification Checklist (run each command, confirm output)

```powershell
node -v
npm -v
n8n --version
python --version
pip show jsonschema
blender --version
ffmpeg -version
git --version
```

All must return valid version strings with no errors before proceeding to Phase 1 work.

### 8.3 Git & GitHub Initialization

```powershell
cd C:\Users\<user>\projects
mkdir mechanical-sim-automation-poc
cd mechanical-sim-automation-poc
git init
# create folder structure per Section 6.1
git add .
git commit -m "Day 0 - Project scaffold, local architecture initialized"
git branch -M main
git remote add origin https://github.com/<user>/mechanical-sim-automation-poc.git
git push -u origin main
```

### 8.4 `.gitignore` (must include)

```
.env
/pipeline/
node_modules/
*.log
__pycache__/
*.pyc
.n8n/
```

### 8.5 `requirements.txt` Template (committed — pinned Python dependencies)

```
jsonschema>=4.21.0
```

This covers every Python package needed **outside** Blender's bundled interpreter (the Blender scripts use Blender's own internal Python + `bpy`, not this file). A fresh clone of the open-source repo should only need `pip install -r requirements.txt` to satisfy Phase 4.5's validation dependency. Whenever a new Python dependency is introduced, it must be added here and committed — never assume a contributor has it installed system-wide.

### 8.6 `.env.example` Template (committed) / `.env` (gitignored, real values)

```bash
# Claude API
CLAUDE_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-sonnet-4-6

# Pipeline paths
PIPELINE_ROOT=C:\pipeline
BLENDER_EXE_PATH=C:\Program Files\Blender Foundation\Blender 4.x\blender.exe

# n8n
N8N_PORT=5678
N8N_HOST=localhost

# Render settings
RENDER_ENGINE=CYCLES
RENDER_DEVICE=OPTIX
RENDER_SAMPLES=512
RENDER_RESOLUTION_X=3840
RENDER_RESOLUTION_Y=2160
FRAME_RATE=24
```

`.env.example` is committed with placeholder values only (as shown above), so anyone forking the open-source repo can copy it to `.env` and fill in their own API key and local paths without any real secret ever touching version control.

### 8.7 `README.md` Required Sections

1. Project title + one-line description
2. Open-source framing: note that this repo is published as an open-source framework, with `FINAL_ARCHITECTURE.md` linked as the authoritative spec
3. Prerequisites (mirrors Section 8.1 of this file)
4. Setup instructions (mirrors Section 8.3–8.6, including `pip install -r requirements.txt` and copying `.env.example` → `.env`)
5. How to run a pipeline job (manual trigger steps)
6. Folder structure overview (mirrors Section 6)
7. Current status (one-line pointer to `project_progress.md`, not duplicated detail)

### 8.8 n8n Initial Configuration

- Install n8n locally: `npm install n8n -g`
- Launch: `n8n start` → accessible at `http://localhost:5678`
- Create new workflow: `CAD Simulation Pipeline (Local)`
- No webhook node needed — workflow begins with a **Manual Trigger** node.
- Export workflow JSON to `n8n-workflows/cad_simulation_pipeline.json` after every structural change, and commit.

### 8.9 Phase 0 Exit Criteria

- [ ] All Section 8.2 verification commands succeed
- [ ] Git repo initialized, pushed to GitHub, folder structure matches Section 6.1
- [ ] `requirements.txt` committed, `pip install -r requirements.txt` completes with no errors
- [ ] `.env` populated with real Claude API key and correct local paths (created by copying `.env.example`)
- [ ] `C:\pipeline\` folder tree created matching Section 6.2 (empty subfolders)
- [ ] n8n running locally at `localhost:5678`, empty workflow created
- [ ] Blender confirmed to launch headless: `blender --background --version` succeeds

---

## 9. Phase 1 — Input Acquisition & Pairing

**Type:** Manual trigger (LOCAL)

### 9.1 Trigger
User manually clicks "Execute Workflow" in the n8n UI after placing files in `C:\pipeline\inputs\cad\` and `C:\pipeline\inputs\pdf\`.

### 9.2 Pairing & Retry Logic (exact sequence)

1. **Manual Trigger** node fires.
2. **Code node — "Scan Input Folders"**: lists files in `inputs\cad\` and `inputs\pdf\`, extracts `baseName` for each (case-insensitive), attempts to find a matching pair per Section 7 naming rules.
3. **IF node — "Pair Found?"**
   - **TRUE branch** (pair found on first scan): generate `jobId`, proceed directly to Phase 2.
   - **FALSE branch** (no pair found): continue to step 4.
4. **Wait node**: pause exactly **30 seconds**.
5. **Code node — "Rescan Input Folders"**: re-run the same scan logic as step 2.
6. **IF node — "Pair Found on Retry?"**
   - **TRUE branch**: generate `jobId`, proceed to Phase 2.
   - **FALSE branch**: continue to step 7.
7. **Stop and Error node — "Log Pairing Failure"**: write an error entry (missing file(s), baseName, timestamp) to `C:\pipeline\logs\pairing-failure-{timestamp}.log`. Workflow halts cleanly. **No further retries.**

### 9.3 Rule
Exactly **one** automatic retry (after a single 30-second wait). If the pair still isn't found after that retry, the workflow stops and logs — it does not wait/retry indefinitely.

---

## 10. Phase 2 — Claude Call #1: Document Intelligence

**Type:** AI (CALL #1 of 2)

### 10.1 Node Flow
1. **Extract from File node**: reads the PDF from `inputs\pdf\{baseName}.pdf`, extracts raw text.
2. **HTTP Request node — "Claude Call 1"**: `POST https://api.anthropic.com/v1/messages`
   - Model: `claude-sonnet-4-6`
   - System/user prompt instructs Claude to return **only valid JSON, no markdown fences, no preamble**, matching the Procedural JSON schema (Section 10.3).
   - Input: extracted PDF text + jobId + schema definition embedded in the prompt.
3. **Code node — "Parse Claude Call 1 Response"**: strips any accidental markdown fencing, attempts `JSON.parse()`.
   - **Parse failure** → Stop and Error node, log to `intermediates\{jobId}\{jobId}-procedural-parse-error.log`. Workflow halts. **No retry to Claude** (this is a lightweight parse-only check, not the full schema gate — the full `jsonschema` gate is reserved for Phase 4.5 per the original design).
   - **Parse success** → continue.
4. **Write File node**: save parsed JSON to `intermediates\{jobId}\{jobId}-procedural.json`.

### 10.2 Example Request Shape
```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 4096,
  "messages": [
    { "role": "user", "content": "<system instructions + schema + extracted PDF text>" }
  ]
}
```

### 10.3 Procedural JSON Schema (output of Phase 2)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ProceduralJSON",
  "type": "object",
  "required": ["jobId", "sourceDocument", "steps"],
  "properties": {
    "jobId": { "type": "string" },
    "sourceDocument": { "type": "string" },
    "totalDurationSeconds": { "type": "number", "minimum": 0 },
    "steps": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["stepId", "order", "action", "targetObject", "motionParams", "durationSeconds"],
        "properties": {
          "stepId": { "type": "string" },
          "order": { "type": "integer", "minimum": 1 },
          "action": {
            "type": "string",
            "enum": ["move", "rotate", "grip", "release", "weld", "drill", "place", "wait", "approach", "retract"]
          },
          "targetObject": { "type": "string" },
          "toolInteraction": { "type": ["string", "null"] },
          "motionParams": {
            "type": "object",
            "properties": {
              "startPosition": { "type": ["array", "null"], "items": { "type": "number" }, "minItems": 3, "maxItems": 3 },
              "endPosition": { "type": ["array", "null"], "items": { "type": "number" }, "minItems": 3, "maxItems": 3 },
              "rotationDegrees": { "type": ["array", "null"], "items": { "type": "number" }, "minItems": 3, "maxItems": 3 },
              "speed": { "type": ["number", "null"] }
            }
          },
          "durationSeconds": { "type": "number", "exclusiveMinimum": 0 },
          "dependsOnStepId": { "type": ["string", "null"] }
        }
      }
    }
  }
}
```

---

## 11. Phase 3 — CAD Preprocessing (Local Blender)

**Type:** Automated (LOCAL BLENDER)

### 11.1 Node Flow
- **Execute Command node — "Run Blender Preprocess"**:
```powershell
"%BLENDER_EXE_PATH%" --background --python scripts\blender_preprocess.py -- ^
  --input "C:\pipeline\inputs\cad\{baseName}.{ext}" ^
  --output "C:\pipeline\intermediates\{jobId}\{jobId}-object-manifest.json"
```

### 11.2 `blender_preprocess.py` Responsibilities
- Import CAD file (supports: `.fbx`, `.usd`, `.usda`, `.usdc`, `.abc`, `.blend`, `.obj`, `.gltf`, `.glb`).
- Mesh conversion / unit normalization (target units: meters).
- Hierarchy reconstruction (parent/child mesh relationships).
- Collision mesh generation per object.
- Serialize results to Object Manifest JSON.

### 11.3 Object Manifest JSON Schema (output of Phase 3)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ObjectManifestJSON",
  "type": "object",
  "required": ["jobId", "sourceFile", "units", "meshes"],
  "properties": {
    "jobId": { "type": "string" },
    "sourceFile": { "type": "string" },
    "units": { "type": "string", "enum": ["meters", "millimeters", "centimeters"] },
    "meshes": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["name", "boundingBox", "pivot", "parent"],
        "properties": {
          "name": { "type": "string" },
          "boundingBox": {
            "type": "object",
            "required": ["min", "max"],
            "properties": {
              "min": { "type": "array", "items": { "type": "number" }, "minItems": 3, "maxItems": 3 },
              "max": { "type": "array", "items": { "type": "number" }, "minItems": 3, "maxItems": 3 }
            }
          },
          "pivot": { "type": "array", "items": { "type": "number" }, "minItems": 3, "maxItems": 3 },
          "parent": { "type": ["string", "null"] },
          "children": { "type": "array", "items": { "type": "string" } },
          "vertexCount": { "type": ["integer", "null"] },
          "hasCollisionMesh": { "type": "boolean" }
        }
      }
    }
  }
}
```

### 11.4 Runtime Expectation
2–5 minutes, depending on model complexity.

---

## 12. Phase 4 — Claude Call #2: Simulation Schema Generation

**Type:** AI (CALL #2 of 2 — final Claude call in the pipeline)

### 12.1 Node Flow
1. **Read File node(s)**: load `{jobId}-procedural.json` and `{jobId}-object-manifest.json`.
2. **Code node — "Build Phase 4 Prompt"**: combines both JSON payloads + schema definition into a single prompt.
3. **HTTP Request node — "Claude Call 2"**: `POST https://api.anthropic.com/v1/messages`, model `claude-sonnet-4-6`. Instructs Claude to perform semantic object matching (Procedural step `targetObject` names ↔ Object Manifest `meshes[].name`) and emit the full Simulation Execution JSON, JSON-only output.
4. **Code node — "Parse Claude Call 2 Response"**: strip fencing, `JSON.parse()`. Parse failure → Stop and Error, log, halt (no retry).
5. **Write File node**: save to `intermediates\{jobId}\{jobId}-simulation-execution.json`.

### 12.2 Simulation Execution JSON Schema (output of Phase 4)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SimulationExecutionJSON",
  "type": "object",
  "required": ["jobId", "frameRate", "totalFrames", "objects", "cameraPath"],
  "properties": {
    "jobId": { "type": "string" },
    "frameRate": { "type": "integer", "enum": [24, 25, 30] },
    "totalFrames": { "type": "integer", "minimum": 1 },
    "objects": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["meshName", "keyframes"],
        "properties": {
          "meshName": { "type": "string" },
          "keyframes": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "required": ["frame", "position", "rotation"],
              "properties": {
                "frame": { "type": "integer", "minimum": 0 },
                "position": { "type": "array", "items": { "type": "number" }, "minItems": 3, "maxItems": 3 },
                "rotation": { "type": "array", "items": { "type": "number" }, "minItems": 3, "maxItems": 3 },
                "interpolation": { "type": "string", "enum": ["LINEAR", "BEZIER", "CONSTANT"] }
              }
            }
          },
          "constraints": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["type", "targetMesh"],
              "properties": {
                "type": { "type": "string", "enum": ["parent", "track_to", "limit_location", "limit_rotation", "child_of"] },
                "targetMesh": { "type": "string" },
                "params": { "type": "object" }
              }
            }
          }
        }
      }
    },
    "cameraPath": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["frame", "position", "lookAt"],
        "properties": {
          "frame": { "type": "integer", "minimum": 0 },
          "position": { "type": "array", "items": { "type": "number" }, "minItems": 3, "maxItems": 3 },
          "lookAt": { "type": "array", "items": { "type": "number" }, "minItems": 3, "maxItems": 3 },
          "fov": { "type": ["number", "null"] }
        }
      }
    },
    "timingOffsets": { "type": "object" }
  }
}
```

### 12.3 Critical Rule
This is Claude's **final** call in the pipeline. After Phase 4, **zero** further AI involvement of any kind, for the rest of the run.

---

## 13. Phase 4.5 — JSON Validation Gate (MANDATORY)

**Type:** Automated (LOCAL VALIDATION LAYER)

### 13.1 Node Flow
- **Execute Command node — "Run Schema Validation"**:
```powershell
python scripts\validate_schema.py ^
  --input "C:\pipeline\intermediates\{jobId}\{jobId}-simulation-execution.json" ^
  --schema "schemas\simulation_execution.schema.json" ^
  --errorlog "C:\pipeline\intermediates\{jobId}\{jobId}-validation-error.log"
```
- `validate_schema.py` uses Python's `jsonschema` library, exits with code `0` on valid, non-zero on invalid (writing details to the error log).

### 13.2 IF node — "Validation Passed?"
- **TRUE** (exit code 0): proceed to Phase 5.
- **FALSE** (non-zero exit): **Stop and Error node** — workflow halts cleanly, error already logged. **Invalid JSON is never sent back to Claude.** Prompt must be improved offline (edit the Phase 4 HTTP Request node's prompt) and redeployed for the *next* run.

### 13.3 What Gets Checked
- Valid JSON structure (already implicit from Phase 4 parse step)
- All required keys present per `simulation_execution.schema.json`
- Sensible numeric ranges: non-negative frame numbers, `frameRate` in `{24,25,30}`, `totalFrames ≥ 1`, 3-element position/rotation arrays

---

## 14. Phase 5 — Blender Simulation Execution

**Type:** Automated (LOCAL BLENDER)

### 14.1 Node Flow
- **Execute Command node — "Run Blender Simulation"**:
```powershell
"%BLENDER_EXE_PATH%" --background --python scripts\blender_simulate_render.py -- ^
  --cad "C:\pipeline\inputs\cad\{baseName}.{ext}" ^
  --simjson "C:\pipeline\intermediates\{jobId}\{jobId}-simulation-execution.json" ^
  --manifest "C:\pipeline\intermediates\{jobId}\{jobId}-object-manifest.json" ^
  --outdir "C:\pipeline\intermediates\{jobId}\frames"
```

### 14.2 `blender_simulate_render.py` Responsibilities (Simulation portion)
- Re-import CAD model into a fresh Blender scene.
- Apply keyframes per object from `objects[].keyframes` (position, rotation, interpolation mode).
- Apply constraints per `objects[].constraints` (parent, track_to, limit_location, limit_rotation, child_of).
- Apply camera path from `cameraPath` (position, lookAt, fov per frame).
- Validate collisions where applicable.
- If JSON references a mesh name not found in the scene, or describes a physically impossible sequence (e.g. constraint cycle), Blender fails predictably and the script writes a clear error to the script's own stderr/log — caught by n8n's Execute Command error handling, which halts the workflow.

### 14.3 Runtime Expectation
5–15 minutes, depending on complexity.

---

## 15. Phase 6 — Rendering

**Type:** Automated (LOCAL GPU)

**Priority for this POC: accuracy and quality over speed.**

### 15.1 Render Settings (locked defaults, all overridable via `.env`)

| Setting | Value |
|---|---|
| Render Engine | Cycles |
| Device | GPU — OptiX (RTX A4500) |
| Resolution | 3840 × 2160 (4K UHD), always |
| Frame Rate | 24 fps |
| Samples | 512 |
| Adaptive Sampling | Enabled, noise threshold 0.01 |
| Denoiser | OptiX denoiser |
| Color Management | AgX (Blender 4.x default) |
| Output Format | PNG, 16-bit color depth, RGBA |
| Output Path | `C:\pipeline\intermediates\{jobId}\frames\frame_%04d.png` |

### 15.2 Runtime Expectation
Per original docx estimate: simple scenes 20–40 min, complex scenes 60–120 min at 4K with Cycles. Since quality is prioritized over speed for this POC, no fallback to 1080p or Eevee is applied automatically — if a run is too slow, that's a manual decision for the user to make per-run, not an automatic pipeline behavior.

---

## 16. Phase 7 — Video Assembly

**Type:** Automated (LOCAL)

### 16.1 Node Flow
- **Execute Command node — "Assemble Video"**:
```powershell
ffmpeg -framerate 24 -i "C:\pipeline\intermediates\{jobId}\frames\frame_%04d.png" ^
  -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow ^
  "C:\pipeline\outputs\{jobId}.mp4"
```
- `-crf 18` = visually near-lossless quality. `-preset slow` = prioritizes compression quality over encode speed, consistent with the "quality over speed" directive for this phase.

### 16.2 Runtime Expectation
2–5 minutes.

---

## 17. Phase 8 — Delivery

**Type:** Automated (LOCAL)

### 17.1 Node Flow
- **Code node — "Build Completion Report"**: assembles a JSON summary of the run.
- **Write File node**: saves to `C:\pipeline\logs\{jobId}-report.json`.
- Final video already resides at `C:\pipeline\outputs\{jobId}.mp4` — no further file movement needed (no cloud upload).
- Workflow marked complete in n8n.

### 17.2 Completion Report JSON Shape
```json
{
  "jobId": "string",
  "status": "success | failed",
  "startTime": "ISO8601 timestamp",
  "endTime": "ISO8601 timestamp",
  "phaseDurations": {
    "phase1": "seconds", "phase2": "seconds", "phase3": "seconds",
    "phase4": "seconds", "phase4_5": "seconds", "phase5": "seconds",
    "phase6": "seconds", "phase7": "seconds"
  },
  "claudeCallCount": 2,
  "outputVideoPath": "string",
  "errorLog": "string | null"
}
```

---

## 18. n8n Workflow — Canonical Node Graph

| # | Node Name | Type | Key Config | On Success → |
|---|---|---|---|---|
| 1 | Manual Trigger | Manual Trigger | — | 2 |
| 2 | Scan Input Folders | Code | Lists `inputs\cad\`, `inputs\pdf\`, extracts baseNames | 3 |
| 3 | Pair Found? | IF | Checks for baseName match | TRUE→6, FALSE→4 |
| 4 | Wait 30s | Wait | 30 seconds | 5 |
| 5 | Rescan Input Folders | Code | Same logic as node 2 | → IF: Pair Found on Retry? (TRUE→6, FALSE→ Stop/Error: Log Pairing Failure) |
| 6 | Generate jobId | Code | `{baseName}_{YYYYMMDD_HHMMSS}` | 7 |
| 7 | Extract from File (PDF) | Extract from File | Reads PDF text | 8 |
| 8 | Claude Call 1 | HTTP Request | POST to `api.anthropic.com/v1/messages`, model `claude-sonnet-4-6` | 9 |
| 9 | Parse Claude Call 1 Response | Code | `JSON.parse()`, strip fencing | Pass→10, Fail→Stop/Error |
| 10 | Write Procedural JSON | Write File | `{jobId}-procedural.json` | 11 |
| 11 | Run Blender Preprocess | Execute Command | `blender --background --python blender_preprocess.py` | 12 |
| 12 | Read Object Manifest | Read File | `{jobId}-object-manifest.json` | 13 |
| 13 | Build Phase 4 Prompt | Code | Combines Procedural JSON + Object Manifest JSON | 14 |
| 14 | Claude Call 2 | HTTP Request | POST to `api.anthropic.com/v1/messages`, model `claude-sonnet-4-6` | 15 |
| 15 | Parse Claude Call 2 Response | Code | `JSON.parse()`, strip fencing | Pass→16, Fail→Stop/Error |
| 16 | Write Simulation Execution JSON | Write File | `{jobId}-simulation-execution.json` | 17 |
| 17 | Run Schema Validation | Execute Command | `python validate_schema.py` | 18 |
| 18 | Validation Passed? | IF | Checks exit code | TRUE→19, FALSE→Stop/Error |
| 19 | Run Blender Simulation + Render | Execute Command | `blender --background --python blender_simulate_render.py` | 20 |
| 20 | Assemble Video | Execute Command | `ffmpeg ...` → MP4 | 21 |
| 21 | Build Completion Report | Code | Assembles report JSON | 22 |
| 22 | Write Completion Report | Write File | `{jobId}-report.json` | END |

**Iron Rule check on this graph:** nodes 8 and 14 are the only two calls to the Claude API. No edge in this graph routes from any failure path back into node 8 or 14.

---

## 19. Error Handling & Logging Standards

- Every failure point uses n8n's **Stop and Error** node — the workflow halts cleanly, it does not continue silently or retry the AI layer.
- All error logs are written to `C:\pipeline\intermediates\{jobId}\` (for in-run failures) or `C:\pipeline\logs\` (for pre-jobId failures like pairing).
- Log file naming: `{jobId}-{phase}-error.log` (e.g. `UR10_20260619_143000-validation-error.log`).
- **No phase may silently swallow an error and proceed with default/placeholder data.**
- The only permitted automatic retry in the entire pipeline is the single 30-second pairing retry in Phase 1 (Section 9.2). No other phase retries automatically.

---

## 20. Claude API Call Specification

- **Model (both calls):** `claude-sonnet-4-6`
- **Endpoint:** `https://api.anthropic.com/v1/messages`
- **Auth:** `CLAUDE_API_KEY` from `.env`, passed as header, never hardcoded in workflow JSON.
- **Output contract (both calls):** Claude must return **raw JSON only** — system prompt explicitly instructs no markdown code fences, no commentary, no preamble — to keep the downstream `Code node` parse step simple and deterministic.
- **Total calls per run:** exactly 2 (Section 2, Section 18).

---

## 21. Success Criteria (POC)

| # | Criterion | Acceptance Bar |
|---|---|---|
| 1 | One clean CAD model processed end-to-end | Any CAD file with a supported extension (Section 4) + correctly paired PDF, no manual intervention required |
| 2 | Procedural PDF parsed to valid JSON | ≥8 of 10 test runs produce valid Procedural JSON |
| 3 | Simulation JSON maps procedural steps to mesh names correctly | ≥6 of 10 test runs, plausible keyframe timing |
| 4 | Blender renders video with correct motion | Parts move in correct sequence, 4K |
| 5 | Manual trigger via n8n UI works reliably | No setup required after initial Phase 0 config |
| 6 | Iron Rule held throughout | Exactly 2 Claude calls per run, verified via node graph (Section 18) |

---

## 22. Change Control

This document is **locked**. It may only be modified when the user explicitly instructs an update (e.g. "update FINAL_ARCHITECTURE.md to..."). Any LLM session working on this project must treat every section above as fixed ground truth unless told otherwise — including by a prior session's summary, which is not itself authorization to change this file.
