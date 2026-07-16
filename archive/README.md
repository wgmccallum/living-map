# Archive

Historical snapshots preserved as evidence. Files here are read-only records —
nothing in the app reads them.

## archive_deleted_sandbox_linear-functions-trial_20260624.db

Complete snapshot of the `linear-functions-trial` sandbox, taken when the sandbox
was deleted on 2026-06-24. This is the primary evidence behind casebook entry
**C12 — Ingestion precedents** ([FRAME_AUTHORING_CASEBOOK.md](../FRAME_AUTHORING_CASEBOOK.md)).

Contents:

- **Base graph as of June 2026**: 137 KCs / 130 edges (counting-numbers-v1 and
  coordinate-plane-v1 frames), from before the linear functions frame was committed.
- **All four linear functions staging sessions** (281 staged KCs, 251 staged edges,
  34 staged schemas in total):
  - `linear-functions-2026-05-26` — bottom-up attempt from the Aug 25 workbook;
    abandoned (42 KCs / 47 edges / 0 schemas — the "why bottom-up stalls" example).
  - `lf-prototype2-reconciled` — direct import of the reconciled Prototype 2
    workbook, bypassing AI steps; 86 prerequisites inferred by concept adjacency,
    review-only.
  - `linear-functions-2026-05-31` — workbook-aware import of the Nov 2025 file;
    13 colliding KC IDs renumbered to LFN-340..364; no edges (Antecedents empty).
  - `linear-functions-2026-06-03` — the chosen top-down build from CCSS standards
    files (8.EE.5–6, 8.F.1–5, 7.RP.1–3); this became the committed frame.

The abandoned sessions' actual content survives only in this file. To inspect,
copy it elsewhere first (SQLite may need write access to the directory for
temp files): `sqlite3 <copy>.db "SELECT * FROM staging_sessions;"`
