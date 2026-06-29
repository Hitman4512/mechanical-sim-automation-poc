# Project Progress — AI-Driven Mechanical 3D Simulation Automation (Local POC)

**Last Updated:** June 26, 2026
**Current Phase:** Demo Asset Overnight Render — pipeline fully complete, queued for 720-frame run

---

## Latest Entry — June 26, 2026

**What happened — Phases 5, 6, 7, 8 COMPLETE ✅ | Full pipeline end-to-end validated ✅ | Demo asset prepared ✅**

### Phases 5 + 6 — Blender Simulation + Render (combined)

Per architecture design, Phases 5 and 6 run inside a single Blender invocation (`blender_simulate_render.py`). One Execute Command node covers both.

**Nodes added (in order):**
- `Build Blender Simulate Command` (Code) — TRUE branch of `Validation Pass check`. Constructs full CLI string. Key fix: `cadFile` from `generate jobID` is filename only (`automation_test.obj`), not full path — extension extracted via `cadFileRaw.split('.').pop()` for multi-format support
- `Run Blender Simulation + Render` (Execute Command) — `{{ $json.blenderSimCmd }}`

**Script written:** `scripts/blender_simulate_render.py`
- Handles Phase 5 (keyframe application, constraints, camera setup) + Phase 6 (Cycles render, OptiX, 4K PNG sequence) in one script
- Key functions: `import_cad()` (multi-format), `apply_keyframes()`, `apply_constraints()`, `setup_camera()` (lookAt via mathutils quaternion), `add_default_lighting()` (3-point sun), `configure_render()` (Cycles + OptiX fallback chain → CUDA → CPU), `setup_materials()` (Principled BSDF per-object)
- Scale keyframe support added: `kf.get("scale")` → `obj.scale` + `keyframe_insert("scale")`
- Output: `C:\pipeline\intermediates\{jobId}\frames\frame_0000.png` … `frame_NNNN.png`

**Test run:** `automation_test.obj` (TestCube), 10 frames, 4K Cycles. All 11 frames rendered successfully (`frame_0000.png` → `frame_0010.png`). Node green. ✅

### Phase 7 — FFmpeg Video Assembly

**Nodes added:**
- `Build FFmpeg Command` (Code) — constructs ffmpeg CLI string (`libx264, crf 18, slow preset, yuv420p`)
- `Assemble Video` (Execute Command) — `{{ $json.ffmpegCmd }}`

Output: `C:\pipeline\outputs\{jobId}.mp4`. Verified working with 10-frame test (0.4s video). ✅

### Phase 8 — Completion Report

**Nodes added:**
- `Build Completion Report` (Code) — assembles report JSON (jobId, status, endTime, claudeCallCount: 2, outputVideoPath)
- `Prepare Report Binary` (Code) — converts to base64
- `Write Completion Report` (Write File to Disk) — `C:\pipeline\logs\{jobId}-report.json`

Report confirmed written to `C:\pipeline\logs\`. ✅

---

### Demo Asset — Prepared for Overnight Render

**Demo asset designed:** `demo_pyramid.obj` (multi-part) + `demo_pyramid.pdf` (13-step procedure)

**OBJ objects:** `TriPyramid`, `SqPyramid`, `Label1`, `Label2`, `Label3`, `Label4`

**Animation sequence (720 frames = 30s @ 24fps):**

| Frames | Action |
|---|---|
| 0–72 | Camera zoom-in from (0,−10,3) → (0,−6,2) |
| 72–240 | TriPyramid 6DOF motion (translate ±0.5 X/Y/Z, rotate ±30° X/Y/Z), returns to origin |
| 240–312 | Transition: TriPyramid scale 1→0, SqPyramid scale 0→1 |
| 312–432 | Label1–4 appear sequentially (scale 0→1 at frames 360, 390, 412, 432) |
| 432–552 | SqPyramid + Labels rotate 360° anti-clockwise around Z axis |
| 552–600 | Camera moves position 1 → position 2 (45° elevation) |
| 600–720 | Camera orbits pyramid 3× CCW (41 keyframes, 3-frame intervals, 27°/step) |

**Mock `Claude Call 2` updated:** full 720-frame JSON with `scale` keyframes for transition + label appearance + orbit keyframes generated via loop (41 points, smooth orbit)

**`blender_simulate_render.py` updated:** scale keyframe support + `setup_materials()` (Principled BSDF per-object: TriPyramid silver, SqPyramid gold, Labels red/green/blue/yellow)

**Pending (overnight):**
- Place `demo_pyramid.obj` → `C:\pipeline\inputs\cad\`
- Place `demo_pyramid.pdf` → `C:\pipeline\inputs\pdf\`
- Remove `automation_test.*` from inputs
- Run workflow → estimated 15–24 hours on RTX A4500 Laptop GPU

**Active mocks (unchanged — swap when API key arrives):**
- `Claude Call 1` — mock Code node; real HTTP Request node `Claude Call #1` configured but disconnected
- `Claude Call 2` — mock Code node (updated to 720-frame demo JSON); real HTTP Request node `Claude Call #2` configured but disconnected

**Next planned step:**
Swap mock Claude Call 1 and Claude Call 2 Code nodes → real HTTP Request nodes once Anthropic API key arrives. Populate `.env` with `CLAUDE_API_KEY`. Run full end-to-end pipeline with real Claude API calls.

---

## Previous Entry — June 24, 2026 (compressed)

Phase 4 COMPLETE. `Read Object Manifest → Build Phase 4 Prompt → Claude Call 2 (mock) → Parse → Prepare Binary → Write Simulation Execution JSON → Build Validation Command → Run Schema Validation → Validation Pass check → Validation Failed (FALSE branch)`. Schema validation passes. Key fix: double `{{ }}\{{ }}` expression breaks Write/Read File nodes — always use single concatenated expression.

---

## Previous Entry — June 23, 2026 (compressed)

Phase 3 COMPLETE. `Build Blender Command` + `Run Blender Preprocess` nodes. `blender_preprocess.py` written and verified. Object Manifest JSON passes schema. Key learning: Execute Command with embedded double-quotes in expressions fails — pre-build CLI string in Code node, reference as `{{ $json.blenderCmd }}`.

---

## Previous Entry — June 23, 2026 (compressed)

Phase 2 COMPLETE. `generate jobID → Create Job Folder → Extract from File (PDF) → Claude Call 1 → Parse Claude Call 1 Response → Prepare Procedural JSON Binary → Write Procedural JSON`. PDF sent as base64 document block. Write pattern: binary Code node → Write File to Disk.

---

## Previous Entry — June 22, 2026 (compressed)

Phase 1 COMPLETE. Pairing/retry logic built and tested. All test cases pass.

---

## Previous Entry — June 22, 2026 (compressed)

Phase 0 COMPLETE. All tools verified. Repo pushed to GitHub. `C:\pipeline\` runtime tree created.

---

## Previous Entry — June 19, 2026 (compressed)

Architecture pivot finalized. `FINAL_ARCHITECTURE.md` locked. Old cloud architecture fully decommissioned.