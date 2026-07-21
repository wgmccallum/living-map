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
- **Addendum (2026-07-21):** the two edges this entry *added* on the rationale
  "interpreting points needs graph-reading, not graph-making" (089-b→092-a/b) were
  themselves proxies — for out-of-frame graph literacy — and were cut in C18.

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
  (updated by C14 2026-07-16, C18 and C19 2026-07-21, C24 2026-07-21): 084-d,
  085-e/i/k/l, 088-b/c, 089-b, 090-a/b/c/d, 092-a/b, 093-e, LF-100, LF-103. The
  policy now extends to islands — see Standards §4 and C18.
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

## C18 — Islands are legal when docked; the marked-vs-determined counterfactual; missing-frame signature (Standards §4 roots and islands policy)

- **Discovery (2026-07-21, AI smell pass #1):** the committed frame was DISCONNECTED —
  island {LF-089-b (decide proportional from graph), LF-092-a/b (explain point (x,y) /
  point (0,0) on a PR graph), LF-096-a/b (LF analogs)} — created 2026-07-16 when C14
  cut 089-b→090-b, the island's only bridge. Unnoticed because `validate_frame` checks
  only convexity/closure/acyclicity/laminarity; it has never checked connectedness
  (despite CLAUDE.md listing it). All "verified connected" claims since 07-16 were
  offline component checks or stale.
- **Proposed in-frame fix REJECTED (Bill):** 085-i (determine initial value from
  graph) → 096-b (explain the intercept point in context) looked like
  mentions-without-prerequisite (096-b's description says "identify the point where
  the line crosses the y-axis"). **Marked-vs-determined counterfactual:** given a
  graph with the intercept *marked*, a student interprets it without ever determining
  it — interpretation needs graph-reading, not parameter extraction. Recurring
  pattern: a description that mentions locating/identifying a feature does not
  implicate the determine-KC if the feature could be given.
- **Diagnosis (Bill):** the island is the symptom of a MISSING FRAME — coordinate
  plane and graphs of covarying quantities (≈5.G.1-2, 6.NS.8, 6.EE.9; 8.F.5
  qualitative graphs, absent from this frame entirely, belongs there too; working
  name "Coordinate Plane & Covarying Quantities"). Internal confirmation: the island
  is exactly the set of graph KCs with NO parameter content (straightness, meaning of
  points), while every graph KC touching k/m/b (090-b, 085-h/i, 094, LF-100, 102,
  095-a, 085-o, 088-c) is anchored to the main component *through* its parameter
  content. Clincher: 092-c (the point (1, r)) is the one point-interpretation KC
  that was connected — precisely the one whose content is the unit rate. Deleted
  `coordinate-plane-v1` (never developed; 69 KCs preserved in
  `living_map.db.bak_predelete_cop_20260702`) is raw material for that frame.
- **Resolution (Bill approved all three, 2026-07-21):** (1) Standards §4 extended:
  connectedness is a MAP-level property; an island is legal iff its roots are
  justified docking points; disconnection is a diagnostic (missing edges vs missing
  frame); validation reports components rather than gating on connectedness.
  (2) 089-b→092-a/b CUT — C4 addendum: those edges were added as stand-ins for
  graph-reading ("interpreting points needs graph-reading, not graph-making") and
  fail the same counterfactual as 085-i→096-b. 092-a/b become docking roots;
  **089-b becomes the frame's first deliberately isolated KC** (docking root + C14
  terminal diagnostic, degree 0). (3) Docking surface recorded in the three boundary
  schemas' descriptions (interpreting-proportional-relationships,
  representing-and-interpreting-linear-functions, unit-rates-and-recognition); full
  receiving surface for the future frame: 089-b, 092-a/b/c, 096-a/b, 088-c, 090-b,
  085-h/i/o, 095-a, LF-100, 102, 084-g.
- **Frame after:** 62 KCs / 87 edges; components 57 + 2 + 2 + 1, every component's
  roots justified; justified roots list now 084-d, 088-b/c, 089-b, 090-a/b/c/d,
  092-a/b, 093-e, LF-100. Validates all-4 offline and via live API (graph reloaded
  via POST /api/reload). Stale "unit rate as slope (8.EE.5)" clause also removed
  from the interpreting-PR leaf description (remnant of 094's C15 move).
- **Backup:** `living_map.db.bak_islands_policy_20260721_062651`.

## C19 — C14 re-audit of the LF half; a schema-quotient cycle as evidence of a mis-schemed family (Standards §4, §5)

- **Finding (2026-07-21, AI smell pass #1, Q2):** the LF decide→identify lattice —
  084-e/f/g/h (decide whether a verbal/table/graph/equation relationship is linear)
  each feeding their extraction siblings 085-d..k (determine rate / initial value
  from that representation), 8 edges, plus 084-d (defining features) → 085-l
  (compute rate from two values) — was the same classification-before-extraction
  anti-pattern C14 overturned on the PR side. The 2026-07-13 audit had "verified the
  lattice clean," but that predated C14: **when a principle lands, the re-audit
  (§10) must sweep BOTH halves of the frame**, and this one hadn't.
- **Change set (Bill approved):** mirror C14 per representation. REVERSED the three
  rate pairs — 085-d→084-e (verbal: deciding linearity is recognizing a constant
  rate; extracting it is the atom), 085-f→084-f (table: deciding IS computing
  differences and checking constancy), 085-j→084-h (equation: reading m in explicit
  form is the atom; deciding linearity of arbitrary forms extends it). CUT the graph
  pair 084-g→085-h with no replacement (straightness never touches the rate value —
  independent both ways, the 089-b/090-b precedent). CUT the four initial-value
  edges 084-e→085-e, 084-f→085-g, 084-g→085-i, 084-h→085-k (the linearity criterion
  never involves the initial value). CUT 084-d→085-l (Δy/Δx is arithmetic, not an
  application of the linearity principle).
- **First application ROLLED BACK:** the reversals created a schema-quotient 2-cycle
  linear-function-modeling ↔ linear-function-properties (frame_acyclicity/F3
  violation): reversals ran modeling→properties while 084-a (interpret y = mx + b)
  → 085-a (construct from verbal) — the only properties→modeling edge — ran back.
  The KC graph stayed acyclic; only the quotient broke. C14 never hit this because
  the PR decide family already lived in its own leaf. Inverse transaction applied,
  DB verified edge-identical to backup.
- **Resolution (option C, Bill approved over A: pure cuts, and B: cut 084-a→085-a):**
  the cycle is *evidence the diagnostic family was mis-schemed* — a terminal
  diagnostic layer hiding inside the concept schema, the inverse flavor of C15's
  bridge-content-in-the-wrong-schema. NEW LEAF `recognizing-linear-relationships`
  ("Recognizing Linear Relationships", 8.F.3) created under the frame root, exactly
  parallel to `unit-rates-and-recognition` on the PR side; 084-e/f/g/h moved there
  (4 KCs, min-3 satisfied, trivially convex — four sinks, no edges among them);
  then the full edge set applied. Quotient now properties→modeling,
  properties→recognizing, modeling→recognizing — acyclic.
- **Consequences:** decide-linear family = terminal diagnostic sinks (completing the
  frame-wide symmetry with C14: both recognizing leaves are diagnostic layers built
  on extraction); NEW ROOTS 085-e (initial value from verbal — context-reading is
  prior knowledge; no PR analog per C7), 085-i (from graph — C18 docking surface),
  085-k (from equation — 6.EE/7.EE prior knowledge), 085-l (rate from two values —
  rational-number arithmetic; sibling atom of LF-100). Justified-roots list updated
  in C10. Frame: 62 KCs / 81 edges / 15 schemas, all four checks valid offline and
  via live API (POST /api/reload). Option B was rejected partly because it would
  foreclose ever fixing the 084-a→construct-family asymmetry symmetrically
  (084-a→085-a is separately under scrutiny — smell-pass Q3 and weak findings).
- **Rules:** (1) a landed principle triggers a whole-frame re-audit, not a
  neighborhood one; (2) a schema-quotient cycle exposed by correcting edge
  directions marks a mis-schemed family — move the family rather than sacrifice
  correct edges (now Standards §5).
- **Backups:** `bak_lf_decide_identify_20260721_063251` (first attempt, rolled
  back), `bak_recognizing_linear_leaf_20260721_064133` (applied change set).

## C20 — The 084-a neighborhood: derivations gate nothing; evaluation-suffices cuts; a KC suspected of being a schema (Standards §3, §4/C17)

- **Finding (2026-07-21, AI smell pass #1, Q3):** 084-a (interpret y = mx + b as
  defining a linear function) had exactly one in-edge — 081-c (derive y = mx + b) —
  so the whole derivation chain LF-100→081-a→081-b→081-c gated 8 downstream KCs
  including constructing models and graphing from equations. C17 in its purest form:
  8.F.3 and 8.EE.6 are mastered independently in every framework; whole populations
  master form-interpretation without ever mastering the derivation. Pedagogy
  falsifies the edge.
- **Resolution (Bill adjudicated):** (1) CUT 081-c→084-a; ADDED 084-d→084-a
  (identifying the roles of m and b IS invoking the defining features; passes the
  mentions test; intra-schema). The derivation strand LF-100→081-a→081-b→081-c
  (plus 081-a→084-b) is now self-contained and terminal — derivation KCs house
  mathematical dependency as content and gate nothing practical.
  (2) CUT 084-a→095-a/b (**evaluation-suffices test**: a correct table is repeated
  substitution and a correct graph follows from plotting two evaluated points —
  expression evaluation is 6.EE prior knowledge, plotting docks from the C18
  coordinate frame; form-interpretation is not required, and requiring the
  plot-intercept-use-rate method would violate C1). Both keep their production
  special-case feeders (088-b/c).
  (3) CUT 084-a→085-a, adjudicated *against* the family-completeness alternative
  (adding 084-a→085-n/o/p): **Bill's diagnosis is that 084-a is more in the nature
  of a SCHEMA than a KC** — "interpret the form as defining a linear function" is
  concept-level understanding, which §3 houses at schema level. Cut provisionally
  in anticipation of resolving that. OPEN QUESTION recorded on LF-084-a
  (annotation): demote to a literal performance, absorb into the
  linear-function-properties schema description, or split into assessable atoms.
- **Consequences:** frame 62 KCs / 78 edges; 084-a now in {084-d}, out {084-b,
  084-c, 084-h, 099} — degree outlier resolved. TWO NEW LEGAL ISLANDS split off:
  {088-b→095-b} (make tables, PR→LF) and {088-c→095-a} (make graphs, PR→LF), whose
  only tie to the main component had been 084-a's cut out-edges. Consistent with
  C18 (roots 088-b/c already justified docking points) and with the C4/C5 lesson
  that production KCs are rarely prerequisite to anything: production strands
  naturally form docking-anchored islands. Frame components now 53+2+2+2+2+1;
  validates all-4 offline and via live API.
- **Rule candidates:** the evaluation-suffices test (an edge into a
  production-from-equation KC fails if substitution alone yields a correct
  product); production strands forming islands is expected structure, not defect.
  The 084-a KC-vs-schema question stays OPEN — first entry in that category since
  the C10 placeholder test.
- **Backup:** `bak_084a_neighborhood_20260721_072320`.

## C21 — Completing the problem-solving PR→LF family; an example is not a prerequisite (Standards §4; detectors: parallel-structure gaps, family asymmetry)

- **Finding (2026-07-21, AI smell pass #1, Q5):** the special-case-before-general
  PR→LF families were complete everywhere (compare, represent, interpret-points,
  determine-rate, construct) EXCEPT problem-solving: 098 (use a linear model to
  solve problems) had no edge from 093-e (solve for unknown values in a PR — 098's
  performance in the b = 0 special case). Instead it had 093-c (simple interest) →
  098, added 2026-07-02 on the observation that an interest balance is itself
  linear.
- **Adjudication (Bill approved):** ADDED 093-e→098 (C7 completeness; the strict
  counterfactual is near-airtight — solving y = mx + b for an unknown without being
  able to do it in y = kx has no non-edge-case instances). CUT 093-c→098: linearity
  of interest balances makes interest an *example* of a linear model, not a
  prerequisite for using one — C17's curricular-story-as-edge in miniature. The
  asymmetry was the tell: no reason interest alone, among 093-a/b/c/d, would feed
  098.
- **Consequences:** 093-c a sink — all four applying-PR KCs now uniformly terminal
  contextual performances; 098 in-edges {085-b, 085-c, 093-e} (interpret the
  parts + the special-case atom). Frame stays 62 KCs / 78 edges (swap), components
  53+2+2+2+2+1, validates all-4 offline and live. All five questions from AI smell
  pass #1 are now resolved or explicitly deferred (Q4 → the 084-a open question).
- **Backup:** `bak_q5_098_feeders_20260721_073923`.

## C22 — The atoms-already-exist test: a KC dissolved into a schema description (Standards §3, §5)

- **Finding (2026-07-21, resolving the open question recorded in C20):** LF-084-a
  ("Interpret y = mx + b as defining a linear function", the frame's ONLY
  Definition-type KC) was suspected by Bill of being a schema in disguise. The
  decisive evidence: **every assessable atom in its long description already existed
  as a KC in the frame** — "identifying m as the rate of change" = LF-085-j
  near-verbatim; "identifying b as the y-intercept (initial value)" = LF-085-k;
  "explain that it defines a linear function" = LF-084-h (whose decide-from-equation
  criterion is *defined* as equivalence to y = mx + b) plus LF-084-d's closing
  clause ("…so that the output can be expressed as y = mx + b"). Task-generation
  falsification (§8.2): no task assesses 084-a without being a 085-j/k, 084-h, or
  084-d task. So of the three candidate resolutions, **demote-to-performance and
  split-into-atoms both collapse into minting duplicates** — absorption was the only
  non-degenerate dissolution. This is C3's mirror: 088-a proxied "understands
  proportionality" (PR side); 084-a proxied "understands the y = mx + b form" (LF
  side), and on both sides the concept-level content ends up in schema descriptions.
  Corroborating: 084-a's out-edges were already nearly all redundant (084-c kept
  084-d; 084-h kept 084-d and 085-j; placeholder 084-b kept 081-a) — only
  084-a→099 did real work.
- **Resolution (Bill adjudicated: absorb):** LF-084-a DELETED; its concept-level
  content absorbed into the `linear-function-properties` schema description (which
  now names the form-interpretation explicitly and points to the assessable atoms);
  heir edge **084-d→099** added (mentions test: 099's description is written
  entirely in 084-d's defining-features vocabulary); the other 4 edges cut with no
  replacement. Provenance annotation on the schema = interim lineage log (C16
  style); the resolved open_question annotation survives the KC row's deletion as
  a historical record.
- **Consequences:** frame **61 KCs / 74 edges / 15 schemas**, components
  52+2+2+2+2+1 (main component one smaller; island structure unchanged); roots
  exactly the previously justified list; no Definition-type KC remains in the frame
  (the frame's working definition is 084-d, a Principle — which is why 084-a was
  redundant even *as* a definition). Validates all-4 offline and via live API
  (POST /api/reload). **Q4 (091→099) deliberately deferred again** per Bill — to be
  adjudicated now that 099's in-edges are {084-d, 091}; its open_question
  annotation updated.
- **Rule (added to §3):** the **atoms-already-exist test** — when adjudicating a
  suspected concept-KC, enumerate the assessable atoms in its description; if each
  already exists as a KC in the frame, the KC is a schema description trapped in a
  KC. Absorb it into the schema description; do not demote (mints a duplicate) or
  split (mints several).
- **Backup:** `bak_084a_absorb_20260721_121304`.

## C23 — Terminology attaches to its object: unit rate vs constant of proportionality (Standards §3)

- **Finding (2026-07-21, Bill's smell):** LF-001-c/d/e (Comparing Proportional
  Relationships, 8.EE.5) said "compare the unit rates" — but a unit rate is
  attached to a ratio, and what the compare family actually compares is the
  parameter of each *relationship*. Internal evidence: the family's feeders
  (090-a/b/c/d) already say "identify the constant of proportionality," and the LF
  mirror family (097-a/b/c) says "rate of change" — 001's "unit rates" was the
  inconsistency. An initial global-replace proposal was **rejected by Bill**, and
  the refinement became the principle: LF-092-c (the point (1, r), 7.RP.2d) is
  *genuinely* about the unit rate — the point's entire significance is the per-one
  reading made visible on the graph — and LF-094 (8.EE.5) keeps "unit rate as the
  slope" because slope is itself a per-one reading (rise per 1 of run), so the
  identification is between two per-one quantities; "constant of proportionality =
  slope" would flatten the bridge and lose the forward generalization to
  rate-of-change-as-slope on the LF side (where no constant of proportionality
  exists to appeal to).
- **Resolution (Bill adjudicated; backup `bak_terminology_c23_20260721_150411`):**
  (1) 001-c/d/e shorts + longs: "unit rates" → "constants of proportionality"
  (001-c keeps its steepness clause). (2) Comparing-PR schema description likewise.
  (3) 092-c long description tightened: "the unit rate **or** constant of
  proportionality" (loose synonymy) → "the unit rate — **which equals** the
  relationship's constant of proportionality" (teaches the relation); the (1, k)
  rewrite was considered and rejected. (4) Root PR schema description was stale
  ("including unit rates" predated LF-087's deletion, which moved unit-rate
  computation out of the frame) → now names the constant of proportionality and
  its graph interpretation. 094 unchanged. Remaining "unit rate" mentions in the
  frame: exactly 092-c and 094, both deliberate.
- **Rule (added to §3):** attach terminology to its object — unit rate ↔ per-one
  value of a ratio/reading; constant of proportionality ↔ parameter of a
  proportional relationship; rate of change/slope ↔ linear functions and graphs.
  Equalities between terms are bridge-KC content, never loose synonymy. Classify
  each occurrence by its object; never search-and-replace terminology globally.
- **Consequences:** description-only change set — frame stays at 61 KCs / 74 edges /
  15 schemas (post-C22); validates all-4. Rationale annotations on 001-c/d/e and
  092-c; provenance annotations on both schema descriptions.
- **Open thread (Bill, pinned):** the distinction suggests possible missing
  finer-grain KCs about the three concepts *as objects* and the identifications
  between them — the frame currently has only two bridge KCs (092-c, 094) covering
  parts of the triangle. Recorded as a frame-level open_question annotation on
  `linear-functions`; to be discussed before any KCs are minted. **RESOLVED same
  day — see C24** (which also corrects this entry's bridge count: 099's clause was
  already the triangle's third side).
- **Q4 closed (same day, backup `bak_q4_cut_091_099_20260721_151019`):** 091→099
  CUT per Bill — no cognitive prerequisite; the edge was C16-split residue
  conjunctively claiming the bridge principle requires the *verbal-specific*
  write-y=kx skill. 099's in-edges now {084-d} (the C22 heir edge); 091 keeps
  091→085-a. Frame 61 KCs / 73 edges / 15 schemas, components 52+2+2+2+2+1,
  validates all-4 offline and live. All smell-pass-1 questions are now fully
  resolved; the frame's sole open question is the C23 three-concept thread above.

## C24 — The three-concept thread resolved: triangle inventory, two minted bridges, and the no-define-KCs ruling (Standards §3; closes C23's open thread)

- **Analysis (2026-07-21, AI smell pass #2 follow-on; Bill adjudicated D1–D5 one at
  a time):** inventory of the unit rate / constant of proportionality /
  rate-of-change(slope) triangle found **all three identifications already present**
  — 092-c (unit rate = k, graph exhibit), 094 (unit rate = slope), and 099's
  k-= -rate-of-change clause — correcting C23's "only two bridges" count. The real
  gaps were two missing *coverage* KCs and one boundary item, found by running C7
  special→general completeness over the bridge/interpretation layer.
- **D1 — minted LF-103** "Interpret the constant of proportionality in terms of the
  situation it models" (interpreting-proportional-relationships leaf, now 4 KCs).
  Gap evidence: 085-b (interpret rate of change in context) had special-case PR
  feeders for every other family but none here — the identify family's "state with
  units" is extraction, not interpretation, and 092-c covers only the graphical
  exhibit. Out-edge 103→085-b completes the C7 family. Deliberately a **root**
  (context-reading prior knowledge, like 085-e): by the marked-vs-determined
  counterfactual (C18) the constant arrives identified; the C5-style 090-d feeder
  was considered and not taken. Backup `bak_c23_mint_103_20260721_154243`.
- **D2 — minted LF-104** "Interpret the rate of change as the slope of the graph of
  a linear function" (linear-function-properties leaf, now 6 KCs) — the "forward
  generalization to rate-of-change-as-slope" that C23 itself invoked to justify
  keeping "unit rate" in 094, which did not exist as a KC (the identification was
  carried only by 085-h's "(slope)" parenthetical and one clause of 099). Wiring
  mirrors 094: in-edges {094 (special-case-before-general, un-sinks 094),
  085-h (embedded extraction atom, C8 reasoning mirroring 090-b→094)}; no direct
  LF-100 edge (the C15 know-what-slope-is requirement arrives transitively via
  094); sink like the other bridges. Backup `bak_c23_mint_104_20260721_154602`.
- **D3 — deferred** the representation-independent unit-rate = k bridge to the
  future Ratios & Rates frame (C18 missing-frame playbook): its unit-rate half
  belongs to the frame LF-087 was exiled to (C10), and a straddling KC would repeat
  087's boundary problem. Recorded as expected docking content in
  representing-proportional-relationships' boundary note; this frame carries only
  the graph-anchored exhibit (092-c). Backup `bak_c23_d3_boundary_20260721_154728`.
- **D4 — 099's grain confirmed:** the identification stays a clause of the bridge
  principle. Its two atoms (PR ⊂ linear-with-b-0; k = m under that inclusion) are
  not task-separable — splitting would mint a §8.2 task-indistinguishable
  duplicate — and the atoms-already-exist test does not dissolve it (085-j/090-c
  extract the two numbers separately, but the identification exists nowhere else).
  Rationale annotation on 099.
- **D5 — negative ruling on concepts-as-objects (the rule):** a concept-as-object
  question resolves *structurally, never lexically* — identifications between terms
  are bridge-KC content, meanings are schema-description content, and neither
  "define X" nor "distinguish the terms" is an assessable performance ("define X"
  is the C12 flat-parser fingerprint and the §3 concept-proxy smell; the frame
  deliberately has no Definition-type KC — its working definition 084-d is a
  Principle stating a performance). Added to Standards §3.
- **Consequences:** frame **63 KCs / 76 edges / 15 schemas**, components
  54+2+2+2+2+1 (both mints in the main component); justified roots = the C10 list
  **plus LF-103** (17 total). Frame-level open_question RESOLVED (resolution
  recorded as a frame rationale annotation); leaf descriptions updated
  (interpreting-PR now names 103; properties' bridge list now 094/099/104).
  Validates all-4 offline after each change set. Earlier the same day, smell pass
  #2's five description-level findings were applied (099 sentence-2 cut, 093-d
  "prior KCs" reword, 098 parenthetical cut, 001-d steepness clause, docking notes
  on the four root-holding schemas C18 missed — backups `bak_p2q1..p2q5_*`); no new
  principle emerged from that pass, so it has no casebook entry of its own.
- **Backups:** `bak_c23_mint_103_20260721_154243`, `bak_c23_mint_104_20260721_154602`,
  `bak_c23_d3_boundary_20260721_154728`, `bak_c23_d5_closeout_20260721_155421`.

---

*Add entries in the same format. Every substantive change to the standards document
should cite its entry here.*
