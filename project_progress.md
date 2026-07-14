# Project Progress — AI-Driven Mechanical 3D Simulation Automation (Local POC)

**Last Updated:** July 7, 2026
**Current Phase:** Awaiting real Claude API key | Render time benchmarks collected across resolutions | Ready to queue full demo render at chosen resolution/samples

---

## Latest Entry — July 7, 2026

**What happened — Render time benchmarking across resolutions**

Tested render time per frame at three resolution/sample combos (hardcoded values, no Claude calls — see July 6 entry):

| Resolution | Samples | Time/frame |
|---|---|---|
| 540p | 128 | 15 sec |
| 1080p | 128 | 20 sec |
| 4K | 456 | 60 sec |

**Reading this:** 4K at 456 samples costs 4x the per-frame time of 540p, but that's a mix of two variables (resolution jump + almost 4x the samples). Not a clean apples-to-apples test — if you want to isolate whether resolution or sample count is the bigger cost driver, next test should hold samples constant across resolutions.

**Next planned step:** Decide target resolution/samples for the real demo render based on total time budget (frame count × time/frame), then swap mock Claude Call 1 + 2 → real HTTP Request nodes once API key arrives.

---

## Previous Entry — July 6, 2026 (compressed)

Switched Claude Call 1 + 2 nodes to hardcoded JSON values temporarily (no live API calls) to unblock testing. Cleared several bugs. First test video rendered at 540p, 32 samples. Fixed a rotation logic bug (root cause unconfirmed — resolved with Claude's help, not independently diagnosed).

---

## Previous Entry — July 3, 2026 (compressed)

Schema files fixed: `object_manifest.schema.json` and `procedural_json.schema.json` populated (were empty), `simulation_execution.schema.json` got missing `constraints` block added. All 3 committed to repo.

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