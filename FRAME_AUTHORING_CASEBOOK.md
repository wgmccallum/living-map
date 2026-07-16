# Frame Authoring Casebook

**Audience: AI auditors and provenance readers.** This file records the concrete cases
behind each principle in [FRAME_AUTHORING_STANDARDS.md](FRAME_AUTHORING_STANDARDS.md),
with full KC identifiers, dates, evidence, and resolutions. Human readers should start
with the standards document; this one assumes access to the Linear Functions frame
(`linear-functions`, committed 2026-07-02) and is deliberately dense.

Format per entry: **principle exercised → finding → evidence → resolution → date/backup.**
When running an audit pass, check candidate findings against these precedents: the
evidence patterns here are the calibration set.

---

## C1 — Method restrictions in KC descriptions (Standards §3)

- **Finding:** LF-088-a's long description restricted demonstration method ("without
  relying on a table or graph"). Adjudication (Bill, 2026-07-06): never restrict HOW a
  student demonstrates a KC; differentiate by input representation only. Wanting a
  method restriction signals a badly written or overbroad KC.
- **Follow-up sweep:** 29 long descriptions cleaned same day — prescribed procedures
  (LF-090-a/b/d "by calculating y/x…", LF-085-m "first find rate then work backwards",
  LF-093-a "set up using part = percent × whole"), two-step construct recipes
  (LF-085-a/n/o/p), show-your-work demands, and compare-KCs' "determine each rate"
  (LF-001-c/d/e, LF-097-a/b/c → "determine which is greater + justify").
- **Kept deliberately (not violations):** definitional parentheticals, product criteria
  (LF-088-b/c), justification requirements, worked-example clauses (LF-085-b/c/d/e,
  LF-092-*, LF-094), derivation KCs LF-081-a/b/c (argument IS content), LF-099's
  initial-value-0 check (IS the content).
- **Backup:** `bak_method_cleanup_20260706_171118`.

## C2 — Task-form restrictions are the same disease (Standards §3)

- **Finding:** LF-093-d required a problem to combine unit rates AND proportional
  relationships (a task-form conjunction). Adjudicated 2026-07-06: task-form
  restriction = method restriction.
- **Resolution:** rewritten "Solve multistep problems involving proportional
  relationships"; single-step sibling LF-093-e created.
- **Backup:** `bak_093d_restructure_20260706_165209`.

## C3 — Concept-proxy KC / degree outlier (Standards §3, §4; detector: degree outlier)

- **Finding:** LF-088-a (decide proportional from verbal) had 8 outgoing edges — it was
  proxying "understands proportionality," which is not a KC-level claim.
- **Resolution (2026-07-06):** cut proxy out-edges to LF-084-d, 088-b, 088-c, 091,
  093-a/b/c/d; kept only 088-a→090-d (flagged borderline). Descendant count fell
  53→25. Concept-level understanding lives at schema level.
- **Consequence:** LF-084-d, 088-b, 088-c became roots — honest (real prerequisites are
  outside-frame). See C10.
- **Backup:** `bak_088a_audit_20260706_163320`.

## C4 — Production→interpretation proxy edges; family-asymmetry evidence (Standards §4; detectors: family asymmetry)

- **Smell (Bill, 2026-07-13):** "not sure 088-b/c are strictly prerequisite" to
  identifying constants of proportionality and comparing proportional relationships.
- **Decisive internal evidence:** LF-090-c (identify k from equations) had only
  LF-089-c as prerequisite — no "write equations" (LF-091) edge — while the table and
  graph siblings LF-090-a/b each carried an extra production edge (088-b, 088-c) on
  top of their 089 edge. Same family, inconsistent treatment = the production edges
  were proxies for representation familiarity.
- **Resolution (11 cut / 9 added):** cut 088-b→{090-a, 001-d, 001-e},
  088-c→{090-b, 001-c, 001-d, 092-a/b/c}, 091→{001-c, 001-e}. Added
  090-b+090-c→001-c, 090-a+090-b→001-d, 090-a+090-c→001-e, 089-b→092-a/b,
  090-b→092-c (the point (1, r) is specifically about the unit rate). Kept
  088-b→095-b and 088-c→095-a: genuine production→production special-case-first.
- **Result:** decide → identify-k → compare chain uniform across all four input
  representations.
- **Backup:** `bak_088bc_proxy_edges_20260713_105002`.

## C5 — Production→interpretation in the modeling cycle (Standards §4)

- **Finding (2026-07-13 audit):** LF-085-a (construct model from verbal) fed
  LF-085-b/c (interpret rate / initial value in context) and LF-098 (use a model to
  solve problems). All three targets' long descriptions begin "Given a linear function
  that models a real-world situation…" — interpreting/using a GIVEN model does not
  require constructing one.
- **Resolution:** cut 085-a→{085-b, 085-c, 098}; added 085-j→085-b, 085-k→085-c
  (locate m and b in the equation before interpreting them), 085-b→098 and 085-c→098
  (using a model requires interpreting its parts). Side benefit: un-sank 085-b/c.
- **Backup:** `bak_edge_audit_20260713_145559`.

## C6 — Long edge → missing intermediates; mentions-without-prerequisite (Standards §4 expansion test; detectors: long edges, disconnected subchains)

- **Smell (Bill, 2026-07-13):** 091→081-b "feels like there should be intermediate KCs."
- **Evidence:** LF-081-b's long description says the student uses "the definition of
  slope," but its only prerequisite was LF-091 (write y = kx), which contains no slope.
  Meanwhile the slope-machinery chain 090-b→094→081-a dead-ended into placeholder
  084-b — two chains that plainly should touch, didn't.
- **Resolution:** added 081-a→081-b (constant slope via similar triangles is the
  engine of the derivation) + NEW KC **LF-100** "Compute the slope of a line from two
  points on it" (Skill, slope-and-linear-equations leaf, root — coordinate-plane and
  similarity prerequisites outside frame), LF-100→081-a. Geometric slope-of-a-LINE was
  missing entirely: 085-h/l are function-rate KCs, and the 081 family works on bare
  lines (IM Grade 8 ordering: slope triangles precede linear functions). 091→081-b
  KEPT, flagged borderline (the 8.EE.6 connection is the punchline, not strictly
  load-bearing). LF-100's description deliberately avoids "using a slope triangle"
  (would violate C1).
- **Backup:** `bak_edge_audit_20260713_145559`.

## C7 — Parallel-structure gap (Standards §4; detector: parallel-structure gaps)

- **Finding (2026-07-13 audit):** special-case-before-general PR→LF edge families
  existed for compare (001-c/d/e→097-a/b/c), represent (088-b/c→095-b/a),
  interpret-points (092-a/b→096-a/b), and the bridge principle (091, 084-a→099) —
  but NOT for the determine-rate family, even though k IS the rate of change in the
  special case.
- **Resolution:** added 090-a→085-f, 090-b→085-h, 090-c→085-j, 090-d→085-d.
  Initial-value KCs correctly have no PR analog (initial value is 0 there).
- **Rule:** when a special→general family exists, it must be complete.

## C8 — Atomic-skill-inside; smaller symmetry fixes (Standards §4)

- 085-l (rate from two points) → 085-f (from table) existed; graph analog 085-l→085-h
  was missing (read two points off the graph, compute). Added 2026-07-13.
- 093-e (one-step PR solving) is the atomic skill inside percent/markup/interest
  problems: added 093-e→093-a/b/c.
- 084-d→084-c added: explaining WHY an example is non-linear appeals to the defining
  features, not just the y = mx + b form.
- **Declined as too weak:** 092-c→094 (the (1, r) point as precursor to
  unit-rate-as-slope — plausible but fails strict counterfactual).

## C9 — Schema splits vs convexity; leaf organization (Standards §5)

- A represent-only leaf split was rejected (2026-07-02) because 090-*→091 edges made
  it non-convex — leaves are family-based but only when convexity allows.
- Min-3 rule: a KC stays in a neighboring leaf until a planned split makes a new leaf
  viable (093 stayed in interpreting until its stage-5 split).
- Oversize leaf (modeling, 17 KCs) subdivided into determining-rate-and-initial-value
  + constructing-linear-function-models.

## C10 — Roots policy / frame boundary (Standards §4 roots; detector: unjustified roots)

- LF-087 (compute unit rates) deleted 2026-07-06: unit-rate computation belongs to a
  future Ratios & Rates frame. Schema renamed "Recognizing Proportional Relationships"
  = the 4-KC decide family {088-a, 089-a/b/c}, redescribed as THE entry point / docking
  site from 6.RP/7.RP.1 prior knowledge.
- Interim policy: roots = "prerequisites outside frame." Current justified roots:
  084-d, 088-a/b/c, 089-a/b/c, 093-e, LF-100.
- Placeholder precedent: LF-084-b (straight-line justification deferred to Geometry);
  open question whether 081-a is the same territory.
- **Backup:** `bak_delete087_rename_20260706_170511`.

## C11 — Borderline flags currently open

- 088-a→090-d (survives C3, flagged).
- 090-d→093-d (flagged 2026-07-06).
- 091→081-b (flagged in C6).

## C12 — Ingestion precedents (Standards §2)

- **Top-down beat bottom-up:** session `linear-functions-2026-06-03` (from CCSS,
  schemas free) chosen over bottom-up `linear-functions-2026-05-26` (42 KCs / 47
  edges / **0 schemas** — kept at status 'abandoned' as the illustration of why
  bottom-up stalls).
- **Flat-parser failure fingerprint:** row-per-chunk `parse_xlsx` on the Aug-25
  multi-sheet workbook flattened a 20-row Schemas sheet into "define X" KCs → 55 KCs,
  0 schemas. Any multi-sheet relational workbook needs a structure-aware importer.
- **Curricular-sequence hazard:** Prototype-2 ingest inferred 86 candidate prereqs by
  concept-adjacency rule — imported as review-only, never committed as-is.

## C13 — Identifiers are birth records, not addresses (Standards §9)

- **Place-value breakdown:** CNM schema IDs encoded hierarchy by place value
  (`CNM-8300` → `CNM-5300`, `CNM-5100` → `CNM-5010`); the scheme needed the escape
  hatch `CNM-825-30` when structure shifted, and the LF frame never adopted it —
  hierarchy-encoding IDs do not survive revision, because the ID is a second copy of
  the hierarchy and the copies drift.
- **Birthplace precedent:** `LF-084-b` (straight-line justification, deferred to
  Geometry, see C10) keeps its LF ID despite belonging to another frame's territory —
  the prefix records where the KC was minted, not where it lives.
- **Suffix-lineage hazard:** letter suffixes work as minting mnemonics (`LF-084-a..h`)
  but break as lineage records after two generations of splits; lineage belongs in a
  log, not the ID.
- **Decision (2026-07-16):** accession numbers `<domain>-<seq>` are the standard; IDs
  are immutable birth records; merges/splits retire-and-mint with a lineage log; CNM
  IDs grandfathered as opaque handles; §2 item 5 relaxed to within-document keys.
- **Human factors (same date):** IDs are working-memory handles, not names — useful
  mid-discussion, forgotten by the next day. Hence the §9 convention: durable
  documents pair an ID with its short description generously (first mention and
  whenever it hasn't appeared in a while), and the app's search bar is the canonical
  dereference (matches on ID and description).
- **Pending:** lineage log implementation (table + retire/mint workflow in the app).

---

*Add entries in the same format. Every substantive change to the standards document
should cite its entry here.*
