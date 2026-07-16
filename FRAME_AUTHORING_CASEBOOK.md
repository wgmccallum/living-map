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
  KEPT at the time, flagged borderline (the 8.EE.6 connection is the punchline, not
  strictly load-bearing) — CUT 2026-07-16 once the slope chain carried the load; see
  C11 for the adjudication. LF-100's description deliberately avoids "using a slope
  triangle" (would violate C1).
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
- **Challenged and KEPT (2026-07-16):** LF-100→081-a. Objection: one could
  "formulate slope without ever having computed it." Ruling: real but esoteric —
  the strict test's "other than in edge cases" clause covers it; 081-a's argument
  forms rise/run between pairs of points, which IS LF-100's performance embedded.
  Atomic-skill-inside stands. (The same session cut 094→081-a, leaving LF-100 as
  081-a's only in-frame prerequisite — the similarity prerequisite docks from a
  future Geometry frame, see C10.)

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
- Interim policy: roots = "prerequisites outside frame." Current justified roots
  (updated by C14, 2026-07-16): 084-d, 088-b/c, 089-b, 090-a/b/c/d, 093-e, LF-100.
- Docking-site update (C14): the entry point from 6.RP/7.RP.1 is now the identify-k
  family {090-a/b/c/d} — the natural heirs of deleted LF-087 — plus 089-b; the decide
  family is a diagnostic layer just downstream of entry, not the doorway itself.
- Placeholder precedent: LF-084-b (straight-line justification deferred to Geometry).
  The open question whether 081-a is the same territory was RESOLVED 2026-07-16:
  081-a stays a real KC. The placeholder test is "is the performance developed and
  assessed within this frame?" — 081-a is the first half of 8.EE.6, done by grade-8
  students (similarity precedes slope triangles in IM's sequence); 084-b's converse
  (the solution set of y = mx + b is a line) genuinely is not. Sharing similar-
  triangles territory means both DOCK into a future Geometry frame, not that both
  are placeholders. Refinement: docking points can attach to NON-ROOT KCs too —
  081-a has in-frame prerequisite LF-100 while its similarity prerequisite is
  outside-frame (a C6 mentions-without-prerequisite where the missing KC belongs to
  another frame).
- **Backup:** `bak_delete087_rename_20260706_170511`.

## C11 — Borderline flags currently open

All three flags resolved 2026-07-16; none currently open.

- ~~088-a→090-d~~ RESOLVED by reversal (C14).
- ~~090-d→093-d~~ RESOLVED: Bill confirmed the edge (strengthened by C14 — 090-d is
  a root carrying the applying family directly; solving rate problems genuinely needs
  extraction of the constant). Flag cleared, edge confirmed.
- ~~091→081-b~~ RESOLVED by cut (backup `bak_cut_091_081b_20260716_065255`).
  Fails the strict counterfactual: 081-b's derivation needs slope constancy (fed by
  081-a) and the point (0,0), not the ability to write PR equations — 091 is neither
  ingredient nor special case of the argument. The "8.EE.6 punchline" (PR equations
  ARE line equations) that justified keeping it lives properly in the bridge
  principle 099, which 091 already feeds; the edge was curricular adjacency (the
  sentence order of 8.EE.6). 081-b keeps the derivation chain 081-a→081-b→081-c;
  091 keeps out-edge →099. Frame 60 KCs / 87 edges, validates all-4.

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
- **Evidence:** all four staging sessions (including the abandoned ones, whose content
  survives nowhere else) are preserved in
  `archive/archive_deleted_sandbox_linear-functions-trial_20260624.db` — see
  [archive/README.md](archive/README.md).

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

## C14 — Classification-before-extraction; decide → identify overturned (Standards §4)

- **Finding (2026-07-16, Bill's smell):** none of the decide KCs seemed a strict
  prerequisite for its identify sibling — "for tables, first you identify the constant
  of proportionality from a table; this skill helps you detect tables that are not
  proportional." Diagnosis: the four decide→identify edges (088-a→090-d "kept" in C3,
  089-a→090-a, 089-b→090-b, 089-c→090-c) were the last remnants of the C3
  concept-proxy pattern — "must know *what* proportionality is first" wearing a
  classification costume — and this document's own §4 had blessed decide → identify
  as a legitimate pattern.
- **Counterfactual per representation:** table — reading k off a given proportional
  table needs one row and one division, no classification needed; reverse is strong
  (deciding *is* extracting the candidate constant across rows and checking
  constancy). Verbal — extracting "$3 per pound" is near-6.RP; judging whether a
  context is proportional is the harder conceptual act done by recognizing a constant
  rate exists. Equation — reading the coefficient in explicit y = kx is the atom;
  deciding extends it to arbitrary forms. Graph — INDEPENDENT both ways: the decide
  criterion (straight line through origin) never touches k.
- **Resolution (Bill adjudicated):** reversed three (090-d→088-a, 090-a→089-a,
  090-c→089-c); the graph pair separated — 089-b→090-b cut with no replacement.
  Frame 60 KCs / 88 edges, validates all-4. Connectivity forced reversal over pure
  deletion for the three: those decide KCs had no other edges.
- **Consequences:** identify family {090-a/b/c/d} became roots (the docking site for
  a future Ratios & Rates frame — closer kin to deleted LF-087 than the decide family
  ever was); 088-a, 089-a, 089-c became sinks (classification as terminal
  diagnostic) — completing 088-a's demotion arc from universal ancestor (C3) to zero
  out-edges; schema "Recognizing Proportional Relationships" redescribed (no longer
  "THE entry point"). Closes C11's first flag; strengthens 090-d→093-d.
- **Rule:** decide/classify KCs are built on their identify/extract atoms, not the
  reverse; a decide → identify edge is usually a concept-proxy in disguise. When the
  classification criterion doesn't involve the parameter at all, the pair is
  independent — cut, don't reverse. (Standards §4 anti-pattern added; the former
  "decide → identify → use/compare" legitimate pattern rewritten.)
- **Backup:** `bak_decide_identify_reversal_20260716_064029`. NOTE: taken with plain
  `cp` before the WAL rule was surfaced — verified complete after the fact
  (integrity ok, 205 edges, old edges present). Future scripts: `sqlite3 .backup`.

## C15 — Bridge content hiding in the wrong schema; the lone-mention diagnostic (Standards §4, §5)

- **Smell (Bill, 2026-07-16):** examining 094→081-a — "to interpret the unit rate as
  a slope, you need to know what the slope is. Is slope mentioned anywhere else in
  the proportional relationships schema?"
- **Diagnostic:** it wasn't — 094 was the ONLY slope mention in any PR leaf; every
  other mention was LF-side. A concept mentioned by exactly one KC in a schema,
  while a sibling schema owns the concept, marks that KC as misplaced bridge
  content. 094's long description is 8.EE.5 language sitting in a 7.RP leaf.
- **Resolution:** cut 094→081-a (unit-rate-as-slope is not prerequisite to the
  similar-triangles argument — the dependency runs the other way); added LF-100→094
  (to equate the unit rate with the slope you must know what the slope of a line
  is); moved 094 to linear-function-properties beside 099 — bridge KCs live on the
  general side, with the special-case side feeding them (090-b→094 retained).
- **Rule:** a KC that imports a concept its schema never otherwise mentions is
  probably bridge content; place it in the schema that owns the concept, fed by
  both sides of the bridge. Backups: `bak_cut_094_081a_20260716_071301`,
  `bak_094_bridge_20260716_072649`.
- **Infra lesson discovered here:** the server's in-memory NetworkX graph is loaded
  at startup and NOT updated by direct-sqlite edits — the API validate endpoint
  produced phantom violations against stale wiring (and had been silently
  validating stale wiring since 2026-07-06). After direct sqlite work, validate
  OFFLINE (build GraphStore from the DB, call frame_engine.validate_frame) and
  restart the server. See CLAUDE.md.

## C16 — The wiring-differential test for representation splits (Standards §3)

- **Question:** when does the differentiate-by-input-representation principle (§3)
  demand a split, and when is a generic multi-representation KC honest? Adjudicated
  2026-07-16 on the two open granularity questions, with opposite outcomes.
- **093-e KEPT GENERIC** ("solve for unknown values in a PR", stimulus: context,
  table, graph, or equation): all four would-be variants have out-of-frame
  prerequisites (equation evaluation, graph reading, equivalent ratios) — four
  identical roots — and the applying KCs are all contextual, so they'd hang off one
  variant leaving the rest as disconnected root-sinks. No differential wiring, no
  split. Also: a from-graph variant would shadow point-interpretation (092-a), and
  a from-equation variant is below the frame's floor.
- **091 SPLIT** (write y = kx; backup `bak_091_split_20260716_081857`): its four
  in-edges 090-a/b/c/d→091 were each individually FALSE as conjunctive claims (a
  student who has never seen a PR graph still writes y=kx from a table). Narrowed
  091 to verbal (085-a precedent: keep ID and edges, 090-d→091, →099), minted
  **LF-101** (from a table, 090-a→101) and **LF-102** (from a graph, 090-b→102)
  per §9 accession numbering, with split provenance annotations as the interim
  lineage log (C13). 090-c→091 cut outright — there is no equation-input variant
  of writing an equation.
- **C7 completeness dividend:** the construct family (085-a/n/o/p) had NO PR
  feeders; the split supplied the missing special-case-first family: 091→085-a,
  101→085-n, 102→085-o. 085-p (two points) correctly has no analog.
- **Rule (now Standards §3):** split by representation only when the variants would
  be wired differently; a bundled KC with representation-specific in-edges is a
  conjunctive overclaim — split it; identically-wired variants are complexity
  without information — keep generic. Earlier instances, same test avant la
  lettre: 085-a split (each variant had its own determine-m/b feeder pair), 087
  rewritten generic instead of split (variants shared all wiring).
- Frame after both: 62 KCs / 89 edges, validates all-4 offline.

## C17 — Mathematical vs cognitive vs pedagogical meaning of an edge (Standards §4 preamble)

- **Question (Bill, 2026-07-16, longstanding):** an edge seems to carry both a
  mathematical and a pedagogical meaning, and the two can contradict — e.g., it is a
  perfectly valid pedagogical move to run opposite to the logical direction, telling
  the story from the end and going back to see how you got there.
- **Resolution:** three relations live on the same nodes and get only one arrow
  type between them. Edges are the COGNITIVE relation (strict counterfactual).
  Mathematical dependency is housed as derivation KCs when the argument is itself
  content (081-a/b/c) or as placeholders when deferred cross-frame (084-b). The
  pedagogical sequence is a walk over the frame, not part of it, and is constrained
  only in its MASTERY order — the encounter/mastery distinction: punchline-first
  storytelling sequences encounters, and encountering a phenomenon is not
  performing a KC.
- **Same-day evidence of the conflation:** 091→081-b cut (story structure
  masquerading as prerequisite — "the 8.EE.6 punchline"); the decide→identify
  family (7.RP.2a/2b document order imported as dependency); 084-b (pedagogy
  legitimately running against MATHEMATICAL order — assume the fact, justify in
  Geometry — with the placeholder as the receipt).
- **Consequence:** pedagogy cannot contradict a correct edge, only refute a wrong
  one — a curriculum that reliably produces mastery of B before A falsifies A→B.
  Teaching-order experience joins task generation (§8.2) as an edge-falsification
  instrument.
- **Deliberately not in the frame:** the walk itself. If collaborators later need
  curriculum narratives, they should be an overlay (an ordered path of encounters,
  validated by "assess only after in-edges are banked") — never additional edges.
  The §8.1 curriculum-walk stress test already checks graph/walk consistency.

---

*Add entries in the same format. Every substantive change to the standards document
should cite its entry here.*
