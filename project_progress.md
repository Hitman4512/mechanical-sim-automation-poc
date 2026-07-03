# Project Progress — AI-Driven Mechanical 3D Simulation Automation (Local POC)

**Last Updated:** July 3, 2026
**Current Phase:** Awaiting real Claude API key | All schemas fixed | Demo render ready to queue

---

## Latest Entry — July 3, 2026

**What happened — Schema files fixed ✅**

- `schemas/object_manifest.schema.json` — was empty, now populated (FINAL_ARCHITECTURE.md Section 11.3)
- `schemas/procedural_json.schema.json` — was empty, now populated (FINAL_ARCHITECTURE.md Section 10.3)
- `schemas/simulation_execution.schema.json` — missing `constraints` block added (FINAL_ARCHITECTURE.md Section 12.2)
- All 3 schema files committed to repo

**Next planned step:** Swap mock Claude Call 1 + 2 → real HTTP Request nodes once API key arrives. Populate `.env` with `CLAUDE_API_KEY`.

---

## Previous Entry — June 29, 2026 (compressed)

Demo render (`demo_pyramid_20260626_173318`) complete. 721 frames rendered. stdout maxBuffer overflow on `Run Blender Simulation + Render` fixed: redirect Blender stdout/stderr to log file, echo only `RENDER_DONE` / `PREPROCESS_DONE` sentinel strings. 6 manually deleted frames caused numbering gap — fixed with Python renumber script (715 contiguous frames). FFmpeg run manually → MP4 confirmed at `C:\pipeline\outputs\`. 

---

## Previous Entry — June 26, 2026 (compressed)

Phases 5+6+7+8 COMPLETE. `blender_simulate_render.py` written (keyframes, constraints, camera, materials, Cycles/OptiX). 10-frame test passed. FFmpeg assembly working. Completion report writing to `C:\pipeline\logs\`. Demo asset prepared: `demo_pyramid.obj` (TriPyramid, SqPyramid, Label1-4) + `demo_pyramid.pdf` (13-step procedure, 720 frames, 30s). Mock `Claude Call 2` updated to 720-frame JSON with scale keyframes + orbit camera loop.

---

## Previous Entry — June 24, 2026 (compressed)

Phase 4 COMPLETE. Schema validation passes. Key fix: double `{{ }}\{{ }}` expression breaks Write/Read File nodes — always use single concatenated expression.

---

## Previous Entry — June 23, 2026 (compressed)

Phase 3 COMPLETE. `blender_preprocess.py` written and verified. Key learning: pre-build CLI string in Code node, reference as `{{ $json.blenderCmd }}`.

---

## Previous Entry — June 23, 2026 (compressed)

Phase 2 COMPLETE. PDF sent as base64 document block. Write pattern: binary Code node → Write File to Disk.

---

## Previous Entry — June 22, 2026 (compressed)

Phase 1 COMPLETE. Pairing/retry logic built and tested.

---

## Previous Entry — June 22, 2026 (compressed)

Phase 0 COMPLETE. All tools verified. Repo pushed to GitHub. `C:\pipeline\` runtime tree created.

---

## Previous Entry — June 19, 2026 (compressed)

Architecture pivot finalized. `FINAL_ARCHITECTURE.md` locked. Old cloud architecture fully decommissioned.