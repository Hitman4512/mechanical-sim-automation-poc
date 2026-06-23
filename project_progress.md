# Project Progress — AI-Driven Mechanical 3D Simulation Automation (Local POC)

**Last Updated:** June 23, 2026
**Current Phase:** Phase 3 — Blender Preprocess (not yet built)

---

## Latest Entry — June 23, 2026

**What happened — Phase 2 COMPLETE ✅**

Full node sequence built and tested:
`generate jobID → Create Job Folder → Extract from File (PDF) → Claude Call 1 → Parse Claude Call 1 Response → Prepare Procedural JSON Binary → Write Procedural JSON`

**Key decisions & discoveries:**
- **PDF strategy:** Option B — Read File(s) From Disk node reads PDF as binary (`pdfBinary` field), sent as base64 `document` block directly to Claude API. No text extraction step.
- **Create Job Folder:** `cmd /c mkdir "{{ $('generate jobID').first().json.intermediatesDir }}"` — uses `intermediatesDir` field from `generate jobID` output. Expression mode required.
- **Claude Call 1:** HTTP Request node, POST `https://api.anthropic.com/v1/messages`, model `claude-sonnet-4-6`, `max_tokens: 4096`. Headers: `x-api-key` (Expression, `$env.CLAUDE_API_KEY`), `anthropic-version: 2023-06-01`, `content-type: application/json`. Body in Expression mode.
- **API key:** Not yet received — deferred. `$env.CLAUDE_API_KEY` configured but not populated. Non-blocking.
- **Mock node:** Claude Call 1 replaced with mock Code node returning hardcoded valid Procedural JSON for testing. Swap back to HTTP Request when API key arrives.
- **Write pattern:** Write File to Disk node lacks File Content option — workaround: `Prepare Procedural JSON Binary` Code node converts JSON to base64 binary, feeds into `Write Procedural JSON` (Write File to Disk) via `Input Binary Field: data`.
- **Execute Command expression mode:** Must explicitly toggle Command field to Expression mode — defaults to Fixed, causing literal `{{ }}` folder names.
- **`intermediatesDir`** field output by `generate jobID` contains full path `C:\pipeline\intermediates\{jobId}` — use this instead of manual concatenation.

**All Phase 2 nodes tested and passing ✅**

**Open items:** Claude Call 1 is currently the mock Code node. Swap to HTTP Request when API key is available.

**Next planned step (from `FINAL_ARCHITECTURE.md` Section 11):** Phase 3 — `Run Blender Preprocess` Execute Command node + `blender_preprocess.py` script. Decision pending: build script now or mock and continue node graph first.

---

## Previous Entry — June 22, 2026 (compressed)

Phase 1 COMPLETE. Pairing/retry logic built and tested. Nodes: Manual Trigger → List Input Files → Scan Input Folders → pair check (IF) → Wait 30s → List Input Files1 → Scan Input Folders1 → retry pair check (IF) → [log pair failure] / [generate jobID]. All test cases pass.

---

## Previous Entry — June 22, 2026 (compressed)

Phase 0 COMPLETE. All tools verified: Node.js v24.14.0, n8n 2.26.7, Python 3.12.5, jsonschema 4.26.0, FFmpeg 8.1.1, Git 2.45.2, Blender 4.5.10 LTS. Repo pushed to GitHub (commit `d04b7cd`). `C:\pipeline\` runtime tree created.

---

## Previous Entry — June 19, 2026 (compressed)

Architecture pivot finalized. `FINAL_ARCHITECTURE.md` locked. Old cloud architecture fully decommissioned.
