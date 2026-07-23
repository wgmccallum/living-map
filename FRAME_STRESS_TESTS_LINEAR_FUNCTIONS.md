# Stress-Test Results — Frame `linear-functions`

Per Standards §8, results are recorded here with the frame. A frame that has passed
§7 and §8 is release-ready.

Frame state under test: **63 KCs / 76 edges / 15 schemas**, published 2026-07-21
(third publish), components 54+2+2+2+2+1, 17 justified roots, no open questions.
Frame state after the §8.1 adjudications (casebook C25): **66 KCs / 82 edges /
15 schemas**, components 57+2+2+2+2+1, 18 justified roots (+LF-106); validates
all-4 offline + live. UNPUBLISHED relative to the 2026-07-21 publish.

| Test | Status | Date |
|---|---|---|
| §8.1 Curriculum walk | **PASSED — all six adjudication items resolved by Bill same day** (A1 mint LF-105; A2 mint LF-106/107; A3, A4, A6 recorded; A5 keep + corrected evidence) | 2026-07-22 |
| §8.2 Task generation | **PASSED — 60/60 Skills yield tasks; no duplicates (F1 kept+sharpened); 82-edge falsification: 1 cut (G1: 084-d→084-g), G2 resolved by stating the given (casebook C26, Standards §3 addendum)** | 2026-07-22 |
| §8.3 Mathematical audit | **PASSED — fresh-reader (no-context) audit; verdict "no wrong conception of the mathematics"; 2 findings dissolved vs C17/C23; six items H1–H6 all resolved by Bill same day (2 rewordings, 1 cut, 2 grain-decreasing mints+rewires, 1 note relocation); casebook C27** | 2026-07-22 |
| §8.4 Pedagogical audit | **PASSED — fresh-reader audit; findings dissolved against the record or resolved by Bill same day (P1 keep+defend; P2 frame-relative demands rubric, full re-tag; P3 easy-instance rungs 113/114/115; P4 record-no-mint; P5 mint 116; P6 trim); one item reopened and parked (110–112 presentation bundling); casebook C28** | 2026-07-23 |

---

## §8.1 Curriculum walk — IM 6–8 Math v.IV, Grades 7–8 (2026-07-22)

**Curriculum**: Illustrative Mathematics 6–8 v.IV, English pathway, from the
authenticated Content-API snapshot of 2026-07-20 (`~/Documents/Substack/IM-audit/cache/`).
**Units walked** (81 lessons): G7 U2 *Introducing Proportional Relationships* (15),
G7 U4 *Proportional Relationships and Percentages* (16), G8 U2 *Dilations, Similarity,
and Introducing Slope* (13), G8 U3 *Linear Relationships* (15), G8 U5 *Functions and
Volume* (22).
**Method**: mapping unit = the teacher-facing lesson goals (`ancillary_content.goals`);
coverage claims for weakly-goal-touched KCs were verified against the units'
362 practice problems and 118 G8U3/U5 activity bodies (keyword scan). Cool-downs not
systematically swept.

### Headline results

1. **Sequence: PASS.** The IM teaching order is extendable to a linear extension of
   the frame's partial order. No edge is falsified by teaching order (C17
   instrument). Two concurrencies noted (§ Order analysis), zero violations.
2. **Goal coverage: PASS with 6 adjudication items.** Every lesson goal maps to KCs,
   to recorded out-of-scope territory, or to one of items A1–A6 below.
3. **KC coverage: all 63 original KCs touched** (corrected 2026-07-22 after the A5
   deep dig — initial scans missed unit assessments). Weakest two: LF-085-m
   (unit-assessment only, never a lesson goal) and LF-085-p (given-intercept
   special case only; general position deferred to IM Geometry U6). See A5.
4. Six prior design decisions are independently **confirmed** by the curriculum
   (§ Validations), including both C14 reversals, the C19 re-schematization, and
   both C24 mints.

### Lesson-by-lesson map

Verdicts: **M** = maps to listed KCs; **OOS** = out of scope by design (destination
recorded); **A#** = adjudication item.

#### G7 Unit 2 — Introducing Proportional Relationships

| L | Title | Verdict | KCs / destination |
|---|---|---|---|
| 1 | One of These Things Is Not Like the Others | OOS | 6.RP equivalent-ratios review → Ratios & Rates frame (docking) |
| 2 | Introducing PR with Tables | M | 093-e (missing values); 088-b (table structure, completion form); "constant of proportionality" terminology → schema level (C24/D5) |
| 3 | More about Constant of Proportionality | M | 090-a; 103 (interpret k, constant speed) |
| 4 | PR and Equations | M | 101, 091 (generate y=kx); 093-e; the k-in-the-x=1-row reading = table-form per-one value → D3-deferred to Ratios & Rates (as designed) |
| 5 | Two Equations for Each Relationship | M | **LF-105** (minted 2026-07-22, A1 resolved) |
| 6 | Writing Equations to Represent Relationships | M | 091; 103 (interpret parts); 093-e/093-d (use equation to solve) |
| 7 | Comparing Relationships with Tables | M | 089-a; 090-a |
| 8 | Comparing Relationships with Equations | M | 089-c; 090-c |
| 9 | Solving Problems about PR | M | 088-a (decide it makes sense); 091; 093-d |
| 10 | Introducing Graphs of PR | M | 088-c; 089-b (line-through-origin criterion) |
| 11 | Interpreting Graphs of PR | M | 088-c (graph from one point + origin); 090-b; 092-a/b/c |
| 12 | Using Graphs to Compare Relationships | M | **LF-106** (minted 2026-07-22, A2 resolved); partial 090-b |
| 13 | Two Graphs for Each Relationship | M + A1 | 102 (equation from a point on graph); cross-representation coordination; axis-reversal → reciprocal thread (A1) |
| 14 | Four Representations | M | 090-a/b/c/d (unfamiliar context, units); 088-a + invent proportional/nonproportional examples |
| 15 | Using Water Efficiently | M | 088-a; 093-d (capstone; modeling practice itself OOS) |

#### G7 Unit 4 — Proportional Relationships and Percentages

| L | Title | Verdict | KCs / destination |
|---|---|---|---|
| 1 | Lots of Flags | OOS | scaled copies (G7U1 / Geometry) |
| 2 | Ratios and Rates with Fractions | OOS | 7.RP.1 fractional unit rates → Ratios & Rates docking site (deleted LF-087 territory, exactly as designed) |
| 3 | Revisiting PR | M | 090-a; 091; 093-e; 103 — fractional k handled by the generic KCs (no fractional variants needed; deliberate) |
| 4 | More than That, Less than That | OOS | 7.EE.2 expression structure → Expressions frame; precursor to 093-b |
| 5 | Say It with Decimals | OOS | 7.NS.2.d decimal expansions → Number System |
| 6–8 | Increasing and Decreasing / One Hundred Percent / Percent Inc-Dec with Equations | M | 093-b (both directions: new-from-original L6, original-from-new L8; L7's double-number-line is method scaffolding the frame rightly doesn't prescribe) |
| 9 | Part of a Percent | M | 093-a/b (fractional percentages; place-value reasoning OOS) |
| 10 | Tax and Tip | M | 093-a |
| 11 | Percentage Contexts | M | 093-a; 093-c (interest context) |
| 12 | Solving Multi-step Percentage Problems | M | 093-d |
| 13–15 | Measurement Error / Percent Error / Changes on the Earth | M | 093-b |
| 16 | Posing Percentage Problems | M | 093-b/d (problem-posing = modeling practice, OOS) |

#### G8 Unit 2 — Dilations, Similarity, and Introducing Slope

| L | Title | Verdict | KCs / destination |
|---|---|---|---|
| 1–9 | dilations, similarity, similar triangles | OOS | → future Geometry frame. This is precisely the prior knowledge LF-100 and 081-a's root status presumes — docking evidence, see Validations |
| 10 | Meet Slope | M | LF-100 (slope = vertical/horizontal change from two points, via slope triangles); 081-a (all slope triangles on a line are similar) |
| 11 | Writing Equations for Lines | M | 081-b (point on line ⟺ quotient equation; y=mx machinery) |
| 12 | Using Equations for Lines | M | 081-b/081-c (equations via similar triangles; point-satisfies-equation) |
| 13 | The Shadow Knows | OOS | similarity application; touch of 093-d |

#### G8 Unit 3 — Linear Relationships

| L | Title | Verdict | KCs / destination |
|---|---|---|---|
| 1 | Understanding Proportional Relationships | M | 090-c; 088-c; 091/102; 094 (activities explicitly connect unit-rate reasoning and similar-triangle equations) |
| 2 | Graphs of PR | M + OOS | 094 (partial); axis scaling → Coordinate Plane & Covarying Quantities (C18 docking evidence) |
| 3 | Representing PR | M + OOS | 088-c; 102; scale choice → COP&CQ |
| 4 | Comparing PR | M | **001-c/d/e — direct hit** (multiple representations, 8.EE.5) |
| 5 | Introduction to Linear Relationships | M | 099; 084-d (informal); 085-h/i; 104 |
| 6 | More Linear Relationships | M | 104; 096-b (positive vertical intercept); 085-h/i |
| 7 | Representations of Linear Relationships | M | LF-100 (slope from coordinates, generalized); 085-l; 085-o/085-a; 085-b/c; 081-c (derivation) |
| 8 | Translating to y=mx+b | M + A2 | 085-j/k; 095-a; 081-c (translation view); same-rate-different-b graph compare → A2 |
| 9 | Slopes Don't Have to Be Positive | M | negative m covered by the generic KCs (no positivity restriction anywhere — confirmed deliberate) |
| 10 | Calculating Slope | M | LF-100; 085-l |
| 11 | Line Designs | M/OOS | 095-a-adjacent graphing craft → COP&CQ |
| 12 | Equations of All Kinds of Lines | M + **A3** | 095-a/b (create graph/equation/table); x=a and y=b lines — no KC |
| 13 | Solutions to Linear Equations | **A4**/OOS | Ax+By=C, solution sets → Linear Equations & Systems frame |
| 14 | More Solutions to Linear Equations | OOS | → Linear Equations & Systems |
| 15 | Using Linear Relations to Solve Problems | M | 098; 096-a/b; 085-b/c |

#### G8 Unit 5 — Functions and Volume

| L | Title | Verdict | KCs / destination |
|---|---|---|---|
| 1–2 | Inputs and Outputs / Introduction to Functions | OOS + **A6** | 8.F.1 general function concept — destination frame unrecorded |
| 3 | Equations for Functions | OOS | evaluation atom (output for given input) — subsumed per C20 evaluation-suffices; 8.F.1 concept OOS (A6) |
| 4 | Tables, Equations, and Graphs of Functions | OOS + M | is-a-function-from-graph OOS (A6); activity touch of 084-g (spot the nonlinear graph) |
| 5–6 | More/Even More Graphs of Functions | OOS | 8.F.5 qualitative graphs → Coordinate Plane & Covarying Quantities (exactly as recorded in C18) |
| 7 | Connecting Representations of Functions | M (weak) | 097-a/b/c prep (8.F.2 tagged; goals are about representations generally) |
| 8 | Linear Functions | M | 084-d; the "any LF is y=mx+b with m=rate, b=initial value" comprehension goal = the **absorbed 084-a content at schema level** (C22 validated); 085-h/i; 104; 097 (tanks activity compares rate+initial value); 099 |
| 9 | Linear Models | M/OOS | 098 (partial); 084-e/f (decide-if-linear from data); fit/goodness-of-fit → statistics/modeling, OOS |
| 10 | Piecewise Linear Functions | OOS | piecewise → beyond frame by design |
| 11 | Filling Containers | M/OOS | 096-a; rate comparison (104); piecewise OOS |
| 12–16 | volume of cylinders/cones/spheres | OOS | 8.G.C → Geometry/Measurement frame |
| 17 | Scaling One Dimension | M | 084-e/g (justify linear); 096-a; 099 (activity: "linear because it is proportional") |
| 18 | Scaling Two Dimensions | M | **084-c (nonlinear examples — direct hit)**; 084-g |
| 19–22 | spheres, capstone | OOS | volume; 084-c touch at L22 (interpret nonlinear volume functions) |

### Order analysis (edge falsification by teaching order, C17)

Checked every frame edge whose endpoints both appear in the walked units against the
curriculum's mastery order. **No violations.** Notable confirmations and the two
concurrencies:

- **C14 identify→decide, confirmed in all three wired representations**: k-from-table
  (G7U2 L2–3) precedes decide-from-table (L7); k-from-equation (L4–6) precedes
  decide-from-equation (L8); k-from-verbal (L3/L6) precedes decide-from-verbal (L9).
- **The graph pair runs the OTHER way in IM** — decide-from-graph (L10) *precedes*
  identify-k-from-graph (L11). This is legal only because C14 cut 089-b→090-b and
  C18 left 089-b isolated. Had the pre-C14 edge 089-b→090-b survived, IM's order
  would have been consistent with it — but the C14 *reversal* direction
  (090-b→089-b) would have been **falsified by teaching order**. The cut (neither
  direction) is exactly what the curriculum supports: IM's L10 line-through-origin
  work never touches k. Strong empirical support for C14's asymmetric treatment of
  the graph pair.
- **C19 (rate-extraction before decide-linear)**: rates develop in G8U3, the
  decide-linear performances consolidate in G8U5 L9/L17–18. Consistent.
- **LF-100→094 (added 2026-07-16)**: slope (G8U2 L10–12) precedes
  unit-rate-as-slope (G8U3 L1–2). Consistent; the add is supported.
- Concurrency 1: **LF-100 and 081-a** develop together inside G8U2 L10 (compute and
  justify in the same lesson), with slope-from-coordinates fluency landing later
  (U3 L7/L10). No mastery-order conflict; noted because the edge's direction is
  invisible at lesson grain.
- Concurrency 2: **084-d and 099** develop together at G8U3 L5 (the
  proportional-vs-nonproportional contrast), with 084-d's crisp statement arriving
  at G8U5 L8. Encounter≠mastery (C17): both are mastered by U5 L8 and nothing
  requires 099 mastery earlier, so the edge stands — but this is the closest thing
  to a violation the walk produced. If §8.2 task work ever shows students deciding
  proportional-vs-linear without being able to state the defining features, revisit
  084-d→099.

### KC coverage (63 KCs)

**Untouched — none.** (Initial finding of 2 untouched KCs was corrected by the A5
deep dig: 085-m is assessed at unit-assessment level; 085-p appears in the
given-intercept special case, with general position deferred to IM Geometry U6.
See A5.)

**Touched at task/activity level but not goal level (7):** 097-a/b/c (8.F.2 tagged
on U5 L7–8; tanks activity + "two cars" practice problem), 084-e/f/g/h (U5 L4/9/17/18
activities), with 084-h the weakest (implicit in U3 L13 rearrangement to y=mx+b and
U5 L18 nonlinear equations).

**Touched but thin (3):** 088-b (tables are completed in G7U2 L2/L4, rarely created
from scratch — creation form appears only via G8U3 L12's multi-representation goal),
093-c (interest appears once as a context in G7U4 L11; CCSS 7.RP.3 names simple
interest explicitly), 095-b (single goal, G8U3 L12).

**Everything else: solidly touched**, including every KC minted or restructured in
the C14–C24 arc (see Validations).

### Validations (design decisions independently confirmed)

1. **C14 reversal + graph-pair cut** — see Order analysis. The strongest single
   result of the walk.
2. **C18 islands policy** — 089-b is taught (G7U2 L10), so isolation-in-frame ≠
   untaught; its content genuinely never touches k in IM either. 092-a/b are taught
   immediately after graphs are introduced with no in-frame prerequisite used —
   consistent with their docking-root status.
3. **C19** — decide-linear consolidates after rate extraction, across units.
4. **C22 (084-a absorbed)** — IM's own treatment of "any linear function is
   y=mx+b" is a *comprehend* goal (G8U5 L8), i.e. schema-level language, never a
   discrete assessable performance. The absorption matches the curriculum's grain.
5. **C24 mints both validated** — LF-103: explicit goals "interpret the constant of
   proportionality" (G7U2 L3, G7U4 L3) plus a practice problem asking for "the
   interpretation of the constant of proportionality." LF-104: goals at G8U3 L6–7
   and U5 L8. Both mints correspond to real curricular targets.
6. **084-b placeholder honesty (preview of §8.3)** — the deferred justification
   (slope triangles/similarity) is fully developed in G8U2 L6–12, i.e. the material
   the future Geometry-side frame will hold. The placeholder's deferral target
   exists in curricular reality.
7. **Root set** — every root's presumed prior knowledge is either taught earlier in
   IM (6.RP, G8U2 similarity) or belongs to the recorded missing frames. No root
   looked arbitrary against the curriculum.

### Adjudication items (A1–A6) — for Bill

- **A1 — Reciprocal constants (G7U2 L5, echoed in L13's axis-reversal). RESOLVED
  2026-07-22: Bill adjudicated MINT.** LF-105 "Write two equations for the same
  proportional relationship, y = kx and x = (1/k)y" — Skill, in
  representing-proportional-relationships, in-edge LF-091 (embedded atom, C8), sink;
  no representation split (C16). Docking sentence added to the schema description
  (reciprocal unit rates ← Ratios & Rates). Backup `bak_a1_mint_105_20260722_122058`;
  validated all-4 offline + live (reload used; 132 nodes/193 edges).
- **A2 — Same-representation comparison. RESOLVED 2026-07-22: Bill adjudicated MINT
  THE PAIR.** LF-106 "Compare the constants of proportionality of two proportional
  relationships graphed on the same axes" (Skill, Comparing PR leaf, ROOT —
  marked-vs-determined: steepness needs no extraction; graph-reading docks from
  COP&CQ; out-edges →001-c/d, →107). LF-107 "Compare the rates of change of two
  linear functions given as graphs on the same axes" (Skill, Comparing LF leaf; in
  {106} special-case-first; out →097-a/b). The 001-c/d "(which line is or would be
  steeper)" parentheticals now read as reformulations over an explicit atom (C8).
  Justified roots now 18 (+LF-106). Backup `bak_a2_mint_106_107_20260722_122804`;
  validated all-4 offline + live (reload; 134 nodes/198 edges).
- **A3 — Horizontal/vertical lines (G8U3 L12). RESOLVED 2026-07-22: Bill
  adjudicated RECORD, no mint.** Scope note appended to `slope-and-linear-equations`:
  x=a excluded as non-function → Linear Equations & Systems frame; y=b legal as the
  m=0 case. Description-only (no reload needed). Backup
  `bak_a3_vertical_lines_note_20260722_123335`.
- **A4 — Ax+By=C and solution sets (G8U3 L13–14). RESOLVED 2026-07-22: Bill
  adjudicated RECORD.** Frame-level editorial_note on `linear-functions` adds
  Linear Equations & Systems to the missing-frame ledger (downstream): feeding
  surface 081-c, 084-h, 085-j/k, 095-a/b; receiving content Ax+By=C, solution
  sets, x=a lines (per A3), 8.EE.8 systems. Annotation-only. Backup
  `bak_a4_leqs_ledger_20260722_123615`.
- **A5 — LF-085-m / LF-085-p. RESOLVED 2026-07-22: Bill adjudicated KEEP, no
  change — and the deeper dig (Bill's request, EdReports reasoning) CORRECTED the
  coverage claim.** Initial scans missed unit assessments and table-disguised
  items. Corrected evidence: **085-m IS assessed** — G8U5 Mid-Unit Assessment P7
  (vA and vB, 8.F.4): cost table with no x=0 row, "what is the one-time fee?"
  (two (x,y) values read from a table, per the standard's own wording). **085-p is
  touched only in the given-intercept special case** — U5 L8 practice P4 writes
  equations for lines through (0,b) and one other point; general-position
  two-point construction first appears in IM **Geometry U6** (point-slope, "It's
  All on the Line") — an IM placement choice, not a standards gap (Algebra 1
  checked too: absent). Rationale annotations recorded on both KCs. Backup
  `bak_a5_record_085mp_20260722_124215`. §8.2 carry-forward: generate 085-p's
  general-position task with care (no G8 curricular model to calibrate against);
  085-l vs LF-100 task-distinguishability already on the weak-finds list.
- **A6 — Where does 8.F.1 live? RESOLVED 2026-07-22: Bill adjudicated TWO
  INCARNATIONS.** The function concept brackets this frame: the informal/precursor
  incarnation (input/output rules, one-output-per-input over covarying quantities,
  6.EE.9 independent/dependent variables) joins **Coordinate Plane & Covarying
  Quantities** upstream; the formal incarnation (functions as objects, notation,
  domain/range — HS F-IF) is a **later formal Functions frame** downstream, for
  which this frame's linear functions are the chief example class. Frame-level
  editorial_note records both. Backup `bak_a6_functions_ledger_20260722_124701`.

**Metadata flag (mechanical):** LF-093-e has no kc_type annotation (the only KC
without one; plainly Skill). Fix with the next change set.

### Out-of-scope destinations touched by this walk (missing-frame ledger)

| Destination | Evidence from walk |
|---|---|
| Ratios & Rates (recorded, C14/C18/D3) | G7U2 L1, G7U4 L2; table-form per-one reading (D3) |
| Coordinate Plane & Covarying Quantities (recorded, C18) | G8U3 L2–3 axis scaling, L11 graphing craft; G8U5 L5–6 (8.F.5) |
| Geometry (similarity side; recorded via 081-a/084-b docking) | G8U2 L1–9; L13 |
| Linear Equations & Systems (**unrecorded** — A4) | G8U3 L12–14 |
| Functions-in-general (**unrecorded** — A6) | G8U5 L1–4 |
| Expressions (7.EE.2) | G7U4 L4, L8 (partial) |
| Number System (7.NS) | G7U4 L5 |
| Statistics/modeling practices | G7U2 L15, G7U4 L16, G8U5 L9–10 |

---

## §8.2 Task generation (2026-07-22)

Frame under test: 66 KCs / 82 edges / 15 schemas (post-§8.1 state). Tasks authored
fresh (not copied from IM) so they test the KC statements, not the curriculum.
Three checks per Standards §8.2: every Skill yields a task; task-indistinguishable
pairs are duplicates; edge falsification by task (Phase 2, below).

### Phase 1a — one task per KC

Conventions: each task respects the KC's input representation and prescribes no
method. Principles get explanation/derivation tasks (recorded for completeness —
the §8.2 mandate covers Skills).

**Recognizing Proportional Relationships (decide family — terminal diagnostics)**

| KC | Task |
|---|---|
| 088-a | A gym charges a $20 sign-up fee plus $30 per month. Is the total amount paid proportional to the number of months? Justify. |
| 089-a | The table shows (2, 7), (4, 14), (6, 21). Could this represent a proportional relationship? Justify. |
| 089-b | A graph shows a straight line through (0, 2) with positive slope. Does it show a proportional relationship? How do you know? |
| 089-c | Does y = 3(x + 2) represent a proportional relationship between x and y? Justify. |

**Representing Proportional Relationships**

| KC | Task |
|---|---|
| 088-b | Grape juice is mixed with 3 cups of concentrate for every 5 cups of water. Make a table showing three different batch sizes. |
| 088-c | Water flows into a tank at 2.5 liters per minute. Graph the relationship between time and volume. |
| 090-a | The table shows (4, 10), (6, 15), (10, 25). Identify the constant of proportionality. |
| 090-b | The graph of a proportional relationship passes through (4, 6). Identify the constant of proportionality. |
| 090-c | In y = 0.4x, identify the constant of proportionality. |
| 090-d | A bread recipe uses 2.5 cups of flour per batch. What is the constant of proportionality relating flour to batches? |
| 091 | Apples cost $1.80 per pound. Write an equation relating cost c to weight w. |
| 101 | Write an equation of the form y = kx for the relationship in the table (3, 7.5), (8, 20). |
| 102 | The graph of a proportional relationship passes through (5, 2). Write its equation. |
| 105 | Lin bikes at a steady speed, going 12 km in 45 minutes. Write two equations relating distance d and time t — one giving d in terms of t, one giving t in terms of d — and explain what each constant means. |

**Interpreting Proportional Relationships**

| KC | Task |
|---|---|
| 092-a | On the graph relating cups of oats (x) to grams of almonds (y) in a granola mix, what does the point (3, 90) mean? |
| 092-b | The graph of hours worked vs. pay passes through (0, 0). What does that point mean in this situation? |
| 092-c | On the graph of gasoline cost vs. gallons, what is the significance of the point (1, 3.20)? |
| 103 | The relationship between hours worked and pay is proportional with constant of proportionality 14.50. What does 14.50 mean in this situation? |

**Comparing Proportional Relationships**

| KC | Task |
|---|---|
| 001-c | Relationship A is graphed (a line through (2, 5)); relationship B is y = 2.2x. Which has the greater constant of proportionality? Justify. |
| 001-d | Relationship A is graphed (a line through (2, 5)); relationship B is the table (3, 8.1), (5, 13.5). Which has the greater constant of proportionality? Justify. |
| 001-e | Relationship A is y = 2.2x; relationship B is the table (3, 8.1), (5, 13.5). Which has the greater constant of proportionality? Justify. |
| 106 | Two lines on the same axes show the cost per pound of trail mix at two stores. Which store charges more per pound? Justify. |

**Applying Proportional Relationships**

| KC | Task |
|---|---|
| 093-e | Seven identical notebooks cost $16.10. How much do 12 cost? |
| 093-a | A jacket costs $65 before an 8% sales tax. What is the total cost? (variants: tip, markup, markdown, commission, fee) |
| 093-b | A town's population grew from 480 to 552. What is the percent increase? (variants: percent decrease, percent error) |
| 093-c | You deposit $800 at 4% simple interest per year. How much interest is earned in 3 years? |
| 093-d | A $120 item is discounted 25%, and then 8% tax is added to the discounted price. What is the final price? |

**Recognizing Linear Relationships (decide family — terminal diagnostics)**

| KC | Task |
|---|---|
| 084-e | A tank starts with 50 L of water and drains at 3 L per hour. Is the volume of water a linear function of time? Justify either way. |
| 084-f | The table shows (1, 4), (2, 7), (3, 10), (5, 16). Could this represent a linear relationship? Justify either way. |
| 084-g | [Graph shown: one straight line, one curve.] Which graphed relationship is linear? Justify either way. |
| 084-h | Is y = x(3 − x) linear? Is y = 3(x − 2)? Justify each. |

**Determining Rate of Change and Initial Value**

| KC | Task |
|---|---|
| 085-d | A plumber charges a $40 visit fee plus $55 per hour. What is the rate of change of the total charge with respect to hours? |
| 085-e | Same situation: what is the initial value? |
| 085-f | A linear relationship: (2, 130), (5, 205), (9, 305). What is the rate of change? |
| 085-g | Same table: what is the initial value? |
| 085-h | [Graph of a linear function shown.] What is the rate of change? |
| 085-i | [Same graph, intercept visible.] What is the initial value? |
| 085-j | For y = 12 − 2.5x, what is the rate of change? |
| 085-k | For y = 12 − 2.5x, what is the initial value? |
| 085-l | A linear function has the values (3, 11) and (7, 23). What is its rate of change? |
| 085-m | Same function: what is its initial value? |
| LF-100 | A line passes through (−2, 5) and (4, 8) in the coordinate plane. What is its slope? |

**Constructing and Using Linear Function Models**

| KC | Task |
|---|---|
| 085-a | A car rental costs $25 plus $0.30 per mile. Write a function giving the total cost. |
| 085-n | Write a linear function that fits the table (2, 130), (5, 205), (9, 305). |
| 085-o | Write the equation of the graphed line (intercept 40, passing through (4, 100)). |
| 085-p | A linear function has the values (3, 11) and (7, 23). Write the function. |
| 085-b | A plumber's charge is C = 40 + 55h. What does 55 mean in this situation? |
| 085-c | Same function: what does 40 mean in this situation? |
| 098 | A phone plan costs C = 20 + 0.10m dollars for m minutes. You budget $32 per month. How many minutes can you use? |

**Representing and Interpreting Linear Functions**

| KC | Task |
|---|---|
| 095-a | Graph y = −2x + 6. |
| 095-b | Make a table of at least four values for y = 3x − 5. |
| 096-a | On the graph of a laptop's battery percentage vs. hours of use, what does the point (2, 65) mean? |
| 096-b | On the same graph, what does the point (0, 100) mean? |

**Comparing Linear Functions**

| KC | Task |
|---|---|
| 097-a | Function A is graphed (rate visible from the line); function B is y = 2x + 9. Which has the greater rate of change? Justify. |
| 097-b | Function A is graphed; function B is the table (1, 14), (4, 29). Which has the greater rate of change? Justify. |
| 097-c | Function A is y = 2x + 9; function B is the table (1, 14), (4, 29). Which has the greater rate of change? Justify. |
| 107 | The volumes of water in two tanks are graphed on the same axes. Which tank is filling faster? Justify. |

**Linear Function Properties (bridges + examples)**

| KC | Task |
|---|---|
| 094 | The graph shows a runner's distance vs. time, a proportional relationship through (1, 6). Explain how the runner's speed (the unit rate) appears in the graph. |
| 104 | The graph shows a gym's total cost vs. months. Explain how the monthly rate of change appears in the graph. |
| 084-c | Give an example of a function that is not linear, and explain how you know it is not. |

**Principles (explanation/derivation tasks — outside the Skill mandate)**

| KC | Task |
|---|---|
| 081-a | Two slope triangles are drawn on the same line. Explain, using similar triangles, why they give the same slope. |
| 081-b | Using a slope triangle from (0, 0) to a point (x, y), derive the equation y = mx for a line through the origin with slope m. |
| 081-c | Derive the equation y = mx + b for the line with slope m and y-intercept b. |
| 084-b | **No in-frame task, BY DESIGN** — placeholder; the justification (why the graph is straight) is deferred to the Geometry frame (C8/C10 placeholder test: not developed or assessed in-frame). Recorded exemption, not a failure. |
| 084-d | State the two features that define a linear relationship. |
| 099 | y = 7x and y = 7x + 2 are both linear. Which one is also proportional, and what feature of proportional relationships makes the difference? |

**Result: every Skill KC yields a task — PASS (60/60, counting 093-e).** The one
task-less KC, 084-b, is a Principle and a recorded placeholder — doubly exempt.
Note in passing: 099's task naturally forces the initial-value concept, which
previews Phase 2's verdict on the watched edge 084-d→099.

### Phase 1b — task-indistinguishability (duplicate) sweep

Closest pairs examined, nearest first:

1. **085-l ↔ LF-100 — FLAG F1, the only unresolved pair** (carried from smell pass
   1's weak-finds list). The numeric work is identical: (23−11)/(7−3) vs
   (8−5)/(4−(−2)). Distinguishers: object and framing — LF-100 is the slope of a
   *line in the coordinate plane* (geometric object, derivation strand); 085-l is
   the rate of change of a *linear function* (functional object, modeling strand,
   typically in context). Wiring-differential argument for keeping both (C16
   logic): LF-100 anchors the derivation strand (→081-a, →094) and is a
   Coordinate-Plane docking root; 085-l anchors the modeling lattice (→085-f/h/m/p).
   A merge would fuse the geometric and modeling strands, straddle two schemas,
   and give one KC six out-edges across both. **RESOLVED 2026-07-22: Bill
   adjudicated KEEP BOTH + SHARPEN.** Both long descriptions now name their
   objects explicitly and cross-reference each other (085-l: function's rate of
   change in context; LF-100: slope of a line as a geometric figure). Rationale
   annotations on both KCs. Backup `bak_f1_sharpen_085l_100_20260722_144356`.
   Description-only change.
2. 090-a↔101, 090-b↔102, 090-d↔091 (extract k vs. write y=kx): distinguishable
   products (a number vs. an equation); C16 already wires them differently. PASS.
3. 092-c ↔ 090-b (the point (1, r) vs. identify k from graph): marked-vs-determined
   separates them — 092-c interprets a marked point, 090-b determines the constant.
   PASS.
4. Extract vs. interpret pairs (085-e/g/i/k/m ↔ 085-c; 085-d/f/h/j/l ↔ 085-b;
   090-d ↔ 103): a number vs. a meaning-statement. PASS across the board.
5. 106 ↔ 001-c/d and 107 ↔ 097-a/b (same-axes vs. cross-representation): stimuli
   differ structurally (one shared graph vs. two representations to coordinate).
   PASS — and the A2 mints did not create duplicates.
6. 094 ↔ 104 (unit rate vs. rate of change as slope): different objects per C23
   terminology-per-object. PASS. 094 ↔ 092-c likewise (slope link vs. point
   reading). PASS.
7. 093-e ↔ 093-d (single-step vs. multistep): task structure separates. PASS.
8. 089-b ↔ 084-g (through-origin vs. straightness criteria): different questions
   about the same stimulus type. PASS.
9. 105 ↔ 091 (two equations + reciprocal explanation vs. one equation): PASS.
10. 084-c ↔ 084-g/h (produce a non-example vs. classify a given): PASS.

**Result: no duplicates found; one sharpening flag (F1) for adjudication.**

### Phase 2 — edge falsification by task: pending

Plan: attempt, for each edge A→B in a stratified sample (all historically
flagged/watched edges, all C8 embedded-atom edges, all PR→LF special-case-first
edges, plus the remainder), a legitimate B-task solvable by a student who cannot
do A. Success falsifies the edge. Carry-forwards to test first: 084-d→099
(decide-without-state watch), 090-d→093-a/b/c/d (out-degree outlier), the A2 mint
edges 106→001-c/d and 107→097-a/b.

### Phase 2 — edge falsification by task (2026-07-22)

Method: for each edge A→B, attempt to construct a legitimate B-task solvable by a
student who cannot do A. If such a task exists within B's full task class, the
edge is falsified. Two structural arguments recur and are named here once:

- **Embedded-atom (EA):** every legitimate B-task contains an A-performance as a
  step (C8). No falsifying task can exist.
- **Task-subsumption (TS):** A's task class is a subset of B's task class (the
  special case *is* a B-task), so mastery of B includes mastery of A. This is the
  operational form of the special-case-first pattern (C7): a falsifying "B-without-
  A" student is impossible because some B-tasks simply ARE A-tasks.
- A third observation cuts the other way and produced this phase's flags: the
  **no-method-restriction principle can rescue or expose an edge.** An edge
  survives if every *method* for B routes through A (090-family into compares),
  but is exposed when B admits a legitimate method that never touches A
  (straightness-by-eye for 084-g; see G1).

**Verdicts: 78 of 82 HOLD. Zero edges falsified outright at the wiring level the
frame relies on; two flags (G1, G2) where the falsification instrument bites,
one recorded borderline (G3), one watch resolved positively.**

| Verdict class | Edges | Basis |
|---|---|---|
| EA — extraction inside equation-writing | 090-d→091, 090-a→101, 090-b→102, 091→105 | writing y=kx requires k; the pair requires y=kx |
| EA — extraction inside cross-rep compares | 090-b/c→001-c, 090-a/b→001-d, 090-a/c→001-e, 085-h/j→097-a, 085-f/h→097-b, 085-f/j→097-c | both constants/rates must be obtained, one per representation |
| EA — atoms inside determine/construct lattice | 085-l→085-f/h/m/p, 085-m→085-g/p, 085-f/g→085-n, 085-h/i→085-o, 085-d/e→085-a | rate/initial value are steps of the construction; b requires m |
| EA — extraction inside classification (C14) | 090-d→088-a, 090-a→089-a, 090-c→089-c | the yes-cases of deciding require exhibiting k; C14 confirmed operationally |
| EA — rate recognition inside decide-linear (C19) | 085-d→084-e, 085-f→084-f, 085-j→084-h | justify-either-way for verbal/table/equation stimuli requires engaging the rate |
| EA — derivation chain | LF-100→081-a, 081-a→081-b, 081-b→081-c | each derivation manipulates the previous object; LF-100→081-a per C15 adjudication |
| EA — bridge machinery | 090-b→094, LF-100→094 | unit-rate-as-slope needs k located on the graph and slope in hand |
| EA — features inside example/identification | 084-d→084-c, 084-d→099 | producing a non-example / naming the b=0 difference forces the feature vocabulary |
| TS — PR special case inside LF general | 091→085-a, 101→085-n, 102→085-o, 103→085-b, 092-a→096-a, 092-b→096-b, 088-b→095-b, 088-c→095-a, 090-a→085-f, 090-b→085-h, 090-c→085-j, 090-d→085-d, 001-c→097-a, 001-d→097-b, 001-e→097-c, 093-e→098, 106→107, 094→104 | the b=0 instance of the B-task class is literally an A-task |
| TS/EA — mint out-edges (A2) | 106→001-c/d, 107→097-a/b | a same-axes pair readable by extraction is inside the compare classes; and B-ability implies A-ability since 106/107 admit the extraction method too (no-method-restriction rescue) |
| EA — one-step solving inside applications | 093-e→093-a/b/c/d | reverse/find-original problems in each class are proportional solves |
| Holds with note (G3) | 090-d→093-a/b/c/d | forward percent problems convert percent language to a multiplier (an 090-d move); previously adjudicated 2026-07-06/16; borderline recorded, no action |
| Holds with note | 085-b/c→098, 084-d→084-e/f/h, 085-h→104 | see notes below |
| **FLAG G1** | **084-d→084-g** | see below |
| **FLAG G2** | **090-b→092-c** (and the interpret-family policy) | see below |
| By-design (placeholder) | 081-a→084-b | mathematical-support edge sanctioned by C17 for placeholders; not subject to task falsification |
| EA — interpret parts inside model use | 085-b/c→098 | formulating the question into the model requires knowing which part is which; pure equation-solving without interpretation is not mastery of the class |

**Watch resolved — 084-d→099 HOLDS.** The §8.1 concurrency watch asked whether
students could decide proportional-vs-linear without stating defining features.
The task test answers no: any legitimate 099 task ("which of y=7x, y=7x+2 is also
proportional, and why?") forces the initial-value concept — one of 084-d's two
features — into the justification. Decide-without-state did not materialize.

#### FLAG G1 — 084-d→084-g falsified; 084-g should mirror 089-b

Falsifying task: "Here are four graphs; decide for each whether the relationship
is linear, and justify." A student who justifies with "this one is a straight
line; this one curves" has produced a fully legitimate justification — 8.F.3
itself equates linear with straight-line graph — while being unable to state the
defining features (constant rate of change, initial value). Straightness
recognition is visual and self-contained; the graph member of the decide family,
unlike the verbal/table/equation members, never needs the rate concept.

The frame already half-knows this: C19 gave 084-e/f/h their rate-extraction
feeders (085-d/f/j) but deliberately gave 084-g none — the falsification now
removes its last in-edge. And the PR side sets the exact precedent: **089-b
(decide proportional from a graph, the through-origin criterion) is the frame's
deliberately isolated KC** — degree 0, docking root, terminal diagnostic (C14 cut
its extraction edge; C18 cut its proxy out-edges). 084-g is the same structure
one frame over: a visual criterion (straightness), a terminal diagnostic, with
graph-literacy prerequisites that live in Coordinate Plane & Covarying
Quantities.

**RESOLVED 2026-07-22: Bill adjudicated CUT.** Applied same day: frame 66 KCs /
81 edges, components 56+2+2+2+2+1+1, 084-g degree-0 (the frame's second
deliberately isolated KC, mirroring 089-b exactly), 19 roots. Rationale
annotation with docking justification on 084-g. Validates all-4 offline + live
(reload used; 134 nodes/197 edges). Backup `bak_g1_cut_084d_084g_20260722_145251`.

#### FLAG G2 — the interpret-family in-edge policy is inconsistent under marked-vs-determined

C24-D1 ruled that LF-103 (interpret k in context) takes **no** extraction feeder
because "the constant arrives identified" — interpreting never exercises
extraction. But three sibling interpretation KCs kept extraction feeders from the
2026-07-13 edge audit, which predates the D1 instrument (C19 rule: re-examining
under a landed principle is not relitigation):

- **090-b→092-c**: 092-c's task class is *definitionally marked* — the KC is
  "explain the significance of the point (1, r)"; every legitimate task presents
  the point. Determining k from an unmarked graph is never exercised. By D1's
  own logic this edge should not exist. Falsification framing: a student who can
  explain "the point (1, 3.20) shows the cost of one gallon — the constant of the
  relationship" while never having extracted k from a bare graph is cognitively
  coherent (the graph-point reading docks from COP&CQ, the per-one concept from
  Ratios & Rates). **Recommend cut**; 092-c becomes a root alongside its siblings
  092-a/b — the whole interpreting-PR leaf would then be uniformly docking roots
  {092-a, 092-b, 092-c, 103}, which is tidy and matches its boundary-schema note.
- **085-j→085-b and 085-k→085-c**: here the D1 logic does NOT apply, and the
  edges should stay. 085-b's task class is "interpret the rate of change of a
  linear function" — the rate is named but NOT exhibited; given C = 40 + 55h,
  interpreting "the rate of change" first requires locating it (the 085-j move).
  Unlike 092-c, the object must be found before it can be interpreted. The
  coherent line: **an interpretation KC takes an extraction feeder iff its task
  class presents the object unlocated** (085-b/c: yes; 092-c, 103: no — the point
  and the constant arrive exhibited).

**G2 RESOLVED 2026-07-22: Bill adjudicated KEEP ALL THREE + STATE THE GIVEN.**
The dispute was a description defect, not a wiring defect: 085-b/c narrowed to
"given by an equation" (their objects are named but arrive unlocated in the
given → the 085-j/k extraction feeders are cognitively real); 092-c's given was
already the graph (the point must be located on it → 090-b stands); 103's given
already includes the constant identified (D1 untouched). New Standards §3
principle "State the given"; casebook C26. Backup
`bak_g2_state_the_given_20260722_150724`. Description-only change.

#### Note G3 — 090-d→093-a/b/c/d (recorded, no action)

Forward percent problems ("increase 480 by 15%") require converting percent
language into a multiplicative constant — an 090-d-shaped move on percent
vocabulary; reverse problems require it more plainly. The edges hold, but they
hold through the percent-language reading of "identify the constant from a
verbal description," which is worth remembering when the Ratios & Rates frame
arrives (these four edges are where 093's outside-frame prerequisites will
partially re-dock). Previously adjudicated (088-a rewires 2026-07-06; 090-d→093-d
confirmed 2026-07-16); consistent with the out-degree-outlier review in smell
pass #2. No action.

---

## §8.3 Mathematical audit (2026-07-22)

Per Standards §8.3, run by a **fresh reader**: an AI instance with no authoring
context, given only a content dump (KC statements + types, the 81 edges with the
one-line cognitive-prerequisite semantics, schema descriptions) — no casebook, no
Standards, no annotations, no session history. Its full report is preserved
below verbatim, followed by the verification triage against the frame's records
(which the auditor deliberately could not see).

### Auditor's report (verbatim)

<details><summary>Full fresh-reader report</summary>

FINDINGS (abridged headers; full text in the session record):

1.1 LF-081-a→LF-084-b doubtful — the placeholder's deferred content is the
CONVERSE (solution set of y=mx+b is a line), which needs SAS-direction
similarity (proportional legs + right angle ⇒ collinear), not 081-a's
AA-direction argument (line ⇒ constant slope).

1.2 LF-088-b→LF-095-b, LF-088-c→LF-095-a doubtful — 088-b/c take a
contextual/verbal given, 095-a/b an equation given; neither subsumes the other;
"these edges encode grade order, not cognitive necessity." Also observes
085-j/k are not upstream of 095-a.

1.3 LF-090-d→LF-093-a/b/c doubtful, sharpest for 093-b — percent-change/error
can be mastered as fraction/decimal procedures without ever naming a constant
of proportionality from a verbal description; 090-d→093-d is fine.

2.1 LF-084-b is a sink but its fact ("graph is a line") is consumed by 084-g,
089-b, 088-c, 095-a, 099 — "neither upstream of its consumers nor explicitly
deferred for them."

2.2 LF-099 asserts "k is the rate of change (slope)" with only 084-d upstream —
no route to the slope claim (094/104 not upstream).

2.3 081-b/c prove only point-on-line ⇒ satisfies-equation; the converse is
084-b's content, "deferred but unrouted."

3.1 084-b's deferral is real and non-circular but UNDER-SPECIFIED — the note
says "similarity of slope triangles" as if the 081-a argument sufficed; the
Geometry frame owes specifically the SAS/converse tool, and "a Geometry author
could discharge the debt with AA only and leave the gap open."

3.2 The representation-independent "k = unit rate" bridge cannot live wholly in
a frame scoped to 6.RP/7.RP.1 — "constant of proportionality" is 7.RP.2 content
defined in THIS frame, so the deferred fact as placed depends on this map's
content (dependency inversion); its stated address is wrong.

4.1 Comparison family sign-ambiguity — "greater constant (steeper line)" is
false for negative constants; for rates −5 vs 2, algebraic and steepness
readings give different answers; two competent readers build different tasks.

4.2 084-d presents a one-condition criterion (constant rate) as a two-part
check ("constant rate of change AND initial value"); domain-restricted linear
contexts (no input 0) classify differently under the two readings.

4.3 085-j / 090-c: "identify the rate/constant as the coefficient of the
independent variable" is literally false for the non-solved forms the
statements admit (x + 2y = 6: coefficient 1, rate −1/2; 2y = 6x: coefficient 6,
k = 3). Needs "after rewriting in solved form."

Overall verdict: "This is a well-constructed map … The defects cluster in one
place: the logical infrastructure around 'the graph of a linear equation is a
line' … All are repairable by rewiring and rewording; none reflects a wrong
conception of the mathematics."

</details>

### Verification triage

**Dissolved against the record** (findings a fresh reader was expected to make,
answered by decisions it could not see):

- **2.1 (084-b sink / consumers unrouted)** — dissolves against C17: edges carry
  the COGNITIVE relation only; mathematical dependency lives in derivation KCs
  and placeholders and does not gate downstream KCs (this is precisely why C20
  cut 081-c→084-a: "derivations gate nothing practical"). Out-edges from the
  placeholder would cognitively gate a dozen KCs on a theorem no G8 student
  needs to hold. Method note for future §8.3 runs: the one-line edge semantics
  in the dump was not enough to convey C17 — a fresh-reader package should
  include the two-sentence cognitive-vs-mathematical distinction explicitly.
- **2.2 (099's "(slope)" clause unrouted)** — dissolves against C23/C24-D4: the
  parenthetical is the third terminology-triangle identification, deliberately
  carried by the bridge KC; cognitively, identifying k = m is parameter
  identification and does not require the graphical rate-as-slope KC (104).
- **1.1's edge-legality half** — the edge 081-a→084-b is a C17-sanctioned
  mathematical-support edge into a placeholder, not a cognitive claim; but the
  auditor's DIRECTIONAL point survives as H1 (below), because the placeholder's
  own text misstates which similarity tool is owed.

**Surviving items (H1–H6), adjudicated one at a time:**

- **H1 (from 1.1 + 2.3 + 3.1) — 084-b under-specifies the deferred tool.**
  Verified: the long says the justification "rests on similarity of slope
  triangles," which describes 081-a's direction (line ⇒ constant slope, AA).
  The deferred fact is the converse (points satisfying y = mx + b are
  collinear), which needs the SAS-direction construction. A Geometry-frame
  author reading today's note could discharge the debt with the wrong theorem.
  **RESOLVED 2026-07-22: Bill adjudicated REWORD, keep the support edge.**
  084-b's long and the boundary note now specify the converse (SAS direction:
  equal slopes → proportional legs + common right angle → similar → collinear)
  as the owed justification, distinct from the AA direction the frame develops,
  citing McCallum, "What makes a line straight?"
  (mathematicalmusings.substack.com/p/what-makes-a-line-straight), which proves
  both theorems. Backup `bak_h1_084b_converse_20260722_171807`. Description-only.
- **H2 (from 1.2) — 088-b/c→095-a/b fail once the givens are stated.** Verified
  against the longs: 088-b's given is "described in words or with specific
  values"; 088-c's given is unstated ("Given a proportional relationship");
  095-a/b's given is the equation. With a verbal given, the §8.2
  task-subsumption defense collapses (an equation-given task is not a special
  case of a verbal-given task), and the counterfactual student (plots from
  equations; cannot model a verbal context) is constructible. This is
  state-the-given (§3, C26) applied one day later to the last unexamined
  production edges. **RESOLVED 2026-07-22: Bill adjudicated a third way — fix by
  DECREASING GRAIN: parallel production KCs per given, at both levels.** Applied:
  088-b/c narrowed to words-given (state the given; both now degree-0 standalone
  diagnostics, docking-justified); **minted LF-108** (graph a PR given y = kx)
  and **LF-109** (table for a PR given y = kx), both ROOTS by evaluation-suffices
  (C20 — substitution needs no constant identified), COP&CQ plotting dock; edges
  088-c→095-a and 088-b→095-b CUT and replaced by same-given special-case-first
  edges **108→095-a, 109→095-b**. Not minted (wiring-differential fails,
  recorded): table-given variants at either level (plotting given pairs is
  COP&CQ content); LF-from-words (decomposes into 085-a + 095-a per the G2
  decomposition move; qualitative words-to-graph is COP&CQ's 8.F.5 strand).
  Frame: 68 KCs / 81 edges, components 56+2+2+2+2+1+1+1+1, 21 roots, four
  standalone diagnostics (084-g, 088-b, 088-c, 089-b); validates all-4 offline +
  live. Backup `bak_h2_production_split_20260722_174422`. Also noted: 095-a/b
  have no language-demand rows (same metadata-gap class as the 097 family).
- **H3 (from 1.3) — 090-d→093-b falsified; a/c borderline.** The percent-error
  class (|new − orig|/orig, and forward change via percent-of + add) never
  names a constant from a verbal description; the auditor independently landed
  on §8.2's G3 borderline and sharpened it to 093-b. **RESOLVED 2026-07-22: Bill
  adjudicated CUT 090-d→093-b only** (a/c/d kept — their percent/interest
  language genuinely is multiplier language; d confirmed 2026-07-16). 093-b's
  remaining in-edge 093-e is the genuine atom. Frame 68 KCs / 80 edges; validates
  all-4 offline + live. Backup `bak_h3_cut_090d_093b_20260722_174711`.
- **H4 (from 3.2) — the D3 bridge's address is wrong.** The representation-
  independent "k = unit rate" statement needs 7.RP.2's concept of k, which is
  defined in THIS frame — it cannot live wholly in a strictly-prior 6.RP/7.RP.1
  frame (dependency inversion). The frame's own bridge pattern agrees: all
  existing identifications (092-c, 094, 099, 104) live in the LATER frame.
  **RESOLVED 2026-07-22: Bill adjudicated REWORD.** The boundary note now
  records the bridge as a future mint IN THIS FRAME once Ratios & Rates exists
  to dock against, citing the frame's own bridge-placement pattern
  (identifications live in the later frame: 092-c, 094, 099, 104). D3's
  substance (no mint yet) unchanged. Backup
  `bak_h4_bridge_address_20260722_180909`. Description-only.
- **H5 (from 4.1) — comparison-family sign conventions.** Verified in the
  longs. PR side (001-c/d/e, 106): "greater constant (steeper line)" is false
  if negative constants are admitted; ratio contexts are positive, but the
  statements don't say so. LF side (097-a/b/c, 107): "greater rate of change"
  is genuinely ambiguous once negative rates (which the frame admits) appear —
  algebraic order vs steepness give different winners. **RESOLVED 2026-07-22:
  Bill adjudicated a structural fix — smaller-grain SIGN KCs plus an integrating
  schema, in addition to the wording repairs.** Applied: new leaf schema
  **Direction of Change** (under linear-functions; description carries the
  integration: sign = direction, magnitude = steepness, value-comparison and
  steepness-comparison agree exactly when both rates are positive); minted
  **LF-110** (positive ⇒ increasing), **LF-111** (zero ⇒ constant, the y = b
  case per A3), **LF-112** (negative ⇒ decreasing, carrying the
  direction-vs-steepness distinction). Wiring: in {085-j} each (equation
  presentation names the rate unlocated — C26; graph presentation visual,
  COP&CQ dock; bundling across presentations per Bill, one-sided feeder
  recorded as accepted C16 tension); out 110/112 → all four LF compares
  (mixed-sign tasks embed the sign-as-value content); 111 sink (zero-rate
  compares marginal, recorded). Wording: positivity clause on the
  graph-involving PR compares (001-c/d, 106); values clause on all four LF
  compares (097-a/b/c, 107). Frame: 71 KCs / 91 edges / 16 schemas, components
  59+2+2+2+2+1+1+1+1, 21 roots; validates all-4 offline + live. Backup
  `bak_h5_direction_of_change_20260722_182434`.
- **H6 (from 4.2 + 4.3) — two statement-level wording repairs. RESOLVED
  2026-07-22.** (a) 084-d reworded as proposed: constancy of rate is the
  criterion; the initial value is the second parameter that, with the rate,
  specifies y = mx + b (with the domain caveat). (b) Bill amended the fix:
  rather than adding "solved form," the coefficient clauses were CUT entirely —
  085-j now reads "determine the rate of change" and 090-c "identify the value
  of k," no method specified (the clause was simultaneously a method
  prescription and false for the admitted forms; cutting fixes both). Backup
  `bak_h6_wording_20260722_182823`. Description-only.

**§8.3 headline: the auditor's overall verdict is that the map is mathematically
well-constructed with no wrong conceptions; every defect is a rewording or a
targeted cut, and the deepest one (the 084-b converse) is a two-sentence text
repair. Three §8.2/§8.1 decisions were independently re-derived by a reader
with no context (the 085-l/LF-100 distinction praised as "genuinely careful";
the comparison family's graph/no-graph structure "exactly right"; the
special-case-first lattice sound), which is the strongest external validation
the frame has received.**

---

## §8.4 Pedagogical audit (2026-07-23)

Frame under test: 71 KCs / 91 edges / 16 schemas (post-H5 state). Run per the §8.3
pattern: a **fresh reader** (AI instance, no authoring context) given a content
dump — KC statements + types, the 91 edges, schema descriptions + membership, the
recorded language demands, roots/sinks/isolated lists — and the five §8.4
questions. Per the §8.3 method note, the packet this time INCLUDED the C17
cognitive-vs-mathematical edge semantics up front (it worked: zero findings
wasted on Principle-gating), plus the atlas context (docking roots legal).
Packet: `audit_packet.md` (session scratchpad); full report in the session record.

### Auditor's report (abridged headers)

<details><summary>Finding headers (full text in session record)</summary>

1.1 (major) 093-a/b an order of magnitude coarser than frame grain — six percent
contexts + both directions bundled; backwards-percent invisible to the mastery bit.
1.2 (minor) LF-105 bundles three performances (two equations, reciprocal
recognition, axes-exchange coordination).
1.3 (minor) 110/111/112 bundle equation+graph presentation against the frame's
own split convention. 1.4/1.5 (obs) fine grain of 085/092 earns its keep; 093-e untyped.
2.1 (major) language-demands hole: one contiguous block (auditor counted 21; the
mechanical check says 22 — the auditor missed 089-c), including the most
linguistically demanding KCs (093, 096, 097, 098, 099). 2.2 084-e/f/g/h omit
Writing despite "justify"; mirror family 089 has it. 2.3 084-d Reading-only for a
stating Principle. 2.4 089-b records spurious "Producing." 2.5 Speaking applied
per-author, not per-rule (092 has it; 103/096 would not).
3.1 (minor) both comparison families lack every verbal cell; 8.F.2/8.EE.5 name
verbal; no recorded exclusion. 3.2–3.4 (obs) T+T/E+E compare absence, PR
table↔graph absence, LF verbal→graph/table absence all judged deliberate and
defensible. 3.5 (minor) interpret-in-context family: equation-pinned on LF side,
agnostic on PR side, table cell nowhere; the one wobble in representation discipline.
4.1 (minor) 106 root presumes in-frame vocabulary. 4.2 (minor) 108/109 roots
undocumented. 4.3 (minor) 084-d definition-first root. 4.4 (minor) 084-g
isolation undocumented while mirror 089-b's is. 4.5 (obs) all 34 sinks sound; no
abandoned wiring. 4.6 (obs) 099 bridge invisible to graph-walkers.
5.1 (major) entry gates dock against frames that don't exist yet — no remediation
path below the 090 family until Ratios & Rates ships. 5.2 (major) 085-l→085-f/h
(and 085-m→085-g) gate the rate region behind the hardest computation, inverting
instructional order. 5.3 (major) high-fan-out nodes (085-j:7, 090-b:6, 090-d:6)
concentrate lockout risk. 5.4 (minor) 110/112 gated only through equation-side
085-j. 5.5 (minor) 095-a gated only by 108; 085-j/k not upstream. 5.6 (minor)
isolated KCs need a surfacing rule. 5.7 (minor) 106 surfaceable day-one. 5.8
(obs) 100/085-l zero-transfer twins; 084-b/093-e need machine-readable flags.

Overall verdict: "well-architected … close to release-ready as a *map*. Not yet
release-ready as an *adaptive gating graph*" — for the language-demands hole, the
085-l gates, and the not-yet-existing docking frames.

</details>

### Verification triage

**Dissolved against the record** (decisions the auditor could not see):

- **1.3 + 5.4 (110/111/112 bundling; one-sided feeder)** — initially dissolved
  against H5 (Bill adjudicated the bundling-across-presentations and the
  one-sided 085-j feeder explicitly, recorded as accepted C16 tension; the
  auditor independently re-derived the exact cost of that tension). **REOPENED
  and PARKED by Bill 2026-07-23**: the independent re-derivation is grounds to
  revisit rather than dissolve. Open question annotation on LF-110 (applies to
  111/112): split by presentation, add 085-h as alternative feeder, or keep.
- **4.1 + 5.7 (106 root)** — dissolves against A2/C18: marked-vs-determined
  rationale annotation on the KC; §8.2's task for 106 uses plain language ("which
  store charges more per pound"), so the vocabulary worry is a task-authoring
  matter the frame already handles.
- **4.2 (108/109 undocumented)** — rationale annotations exist on both KCs
  (evaluation-suffices, COP&CQ dock). KC-level rationale is the frame's
  documentation convention; the auditor could not see annotations.
- **4.3 (084-d definition-first root)** — dissolves against C4/C10: roots mean
  "no in-frame prerequisite," not "arrival knowledge." 084-d is a first-encounter
  root on the justified list since C10's updates. **Method note for future §8.4
  packets: state the two kinds of roots (docking vs first-encounter) explicitly —
  this is the §8.4 analog of the C17 omission §8.3 flagged.**
- **4.4 + 5.6's documentation half (084-g, 088-b/c isolation)** — G1 and H2
  rationale annotations exist on all three; 089-b's schema-note mention is the
  outlier, not the rule.
- **4.6 (099 dead-end bridge)** — by design per C24-D4/C17: bridges carry
  identifications; Principles gate nothing.
- **5.5 (095-a missing 085-j/k gates)** — dissolves against C20
  evaluation-suffices + no-method-restriction: 095-a's long says "for example by
  plotting the y-intercept…" — the substitution method (compute two points, plot)
  never extracts m or b, exactly the argument that made 108/109 roots. Flagged
  now by BOTH fresh readers (§8.3 finding 1.2 aside, §8.4 finding 5.5), so a
  rationale annotation on 095-a recording this defense is warranted
  (description-only; see P-items).
- **5.1 + 5.3 (docking frames absent; fan-out lockout)** — deployment-sequencing
  observations, not frame defects: the atlas plan and islands policy already
  record that gating waits for (or soft-gates until) the docking frames. Worth
  carrying into any deployment spec; no frame change.
- **3.2/3.3/3.4** — the auditor itself judged these deliberate; 3.4's one-line
  schema-note suggestion folded into P4.
- **1.5 (093-e untyped)** — the §8.1 mechanical flag; **FIXED 2026-07-23**
  (kc_type=Skill annotation added; checkpoint
  `living_map.db.bak_sec84_093e_kctype_20260723_060551`). All 71 KCs now typed.

**Surviving items (P1–P6) — for Bill:**

- **P1 (from 1.1) — 093-a/b grain. RESOLVED 2026-07-23: Bill adjudicated KEEP,
  record the defense.** The forward-vs-backward split reaches into precursor
  territory around ratios and rates and belongs, if anywhere, to the future
  Ratios & Rates frame; the bundling matches 7.RP.3's own grain; these are
  terminal application capstones whose machinery (proportional reasoning) is
  carried by the 093-e feeder. Rationale annotations on both KCs.
  Description-unchanged; annotation-only. Bill also noted, and deferred, the
  broader question of whether the frame has already split too much.
- **P2 (from 2.1–2.5) — the language-demands pass. RESOLVED 2026-07-23: Bill
  adjudicated FRAME-RELATIVE RUBRIC + FULL RE-TAG.** Bill's diagnosis went past
  the auditor's: the defect wasn't an abandoned pass but a vocabulary designed
  for Counting Numbers (where Speaking and Reading-vs-Listening genuinely
  discriminate) stretched over a frame where Reading fired on every tagged KC
  (49/49 — pure adornment) and Speaking was vestigial (3). New principle: **the
  demand vocabulary is atlas-shared, but each frame declares which tags
  discriminate and by what rule.** LF rubric keyed to each KC's stated given and
  deliverable (C26 makes demands derivable): Reading = verbal given;
  Interpreting = graph/table/equation given; Producing = representation
  deliverable; Writing = prose deliverable; Speaking/Listening unused. Applied
  to all 71 KCs: 78 tags kept, 43 added (computed), 66 removed; end state
  Interpreting 52, Writing 37, Reading 17, Producing 15; 084-b (placeholder)
  deliberately untagged; all four auditor inconsistencies (2.2–2.5) settled by
  rule. Frame-level rationale annotation. LF-105 tagged R+P+W per current text —
  if P6 keeps the axis-swap clause, add Interpreting. Checkpoint
  `bak_sec84_p2_langdemands_20260723_062735`.
- **P3 (from 5.2) — the 085-l→085-f/h and 085-m→085-g gates. RESOLVED
  2026-07-23: Bill adjudicated FIX BY DECREASING GRAIN — mint the easy-instance
  rungs.** Another genuinely-in-frame grain issue (unlike P1's, which reached
  into Ratios & Rates territory): the frame should capture the instructionally
  earlier performances — unit-step tables, countable grid slopes — as KCs below
  the general two-point computation. Applied: minted **LF-113** (rate from a
  table whose inputs step by 1 — the rate is the common difference) and
  **LF-114** (rate from a graph through labeled whole-number points — rise and
  run readable from the grid), both Skills in
  determining-rate-and-initial-value, both ROOTS (differencing/grid-reading
  dock outside the frame; the given never forces the general quotient), with
  same-given special-case-first out-edges 113→085-f and 114→085-h (C7/TS).
  Deliberately NOT wired to 085-l (different given — the H2 precedent forbids
  given-switching edges) nor to LF-100 (F1 keeps the function-rate and
  geometric-slope strands distinct). Input-structure splits, not method splits
  (C1/C16): either method stays legal on either KC. The §8.2 embedded-atom
  verdicts on 085-l→085-f/h stand at full-mastery grain; an adaptive system now
  has rungs to offer below 085-l. Language demands per the P2 rubric
  (Interpreting only). Rationale annotations on 113/114/085-l. Checkpoint
  `bak_sec84_p3_mint_113_114_20260723_063618`. **Addendum (same day, Bill):
  minted the initial-value twin LF-115** (initial value from a table that
  includes x = 0 — read directly; special-case-first out-edge 115→085-g; ROOT;
  no 085-m feeder; graph-side twin deliberately not minted since 085-i already
  IS the easy case and is already a root; checkpoint
  `bak_sec84_p3_mint_115_20260723_064024`). Frame: **74 KCs / 94 edges / 16
  schemas**, components 62+2+2+2+2+1+1+1+1, 24 roots; validates all-4 offline +
  live (reload used; 142 nodes / 210 edges).
- **P4 (from 3.1) — verbal comparison cells. RESOLVED 2026-07-23: Bill
  adjudicated RECORD, NO MINT.** Scope notes added to both comparison schemas:
  verbal-side comparisons (named by 8.EE.5/8.F.2) factor through extraction
  (090-d / 085-d) followed by value comparison and would fail the
  wiring-differential test (C16) — same reasoning as the absent T+T and E+E
  cells; only the same-axes graph pairs (106/107) are distinct perceptual
  performances. Also applied 3.4's fix: representing-and-interpreting's "mirror"
  claim corrected to "partial mirror" with the words-given asymmetry spelled out
  (verbal→graph/table at LF level decomposes via 085-a then 095-a/b, per H2).
  Description-only. Checkpoint `bak_sec84_p4_verbal_exclusion_20260723_064348`.
- **P5 (from 3.5) — interpret-from-table. RESOLVED 2026-07-23: Bill
  adjudicated MINT.** **LF-116** "Interpret the rate of change of a linear
  function as the constant difference in a table of values" — the table sibling
  of 104, completing 8.F.4's "in terms of its graph or a table of values" and
  consistent with the C23/C24 ruling that how-the-parameter-appears
  identifications are real KCs. Skill, linear-function-properties; wiring
  mirrors 104 (085-f→116 as 085-h→104; sink); no PR-side special-case in-edge
  yet (the D3/H4 deferred bridge, when minted, wires to 116 on the 094→104
  pattern — noted in 116's rationale); initial-value twin deliberately not
  minted (115's statement already carries the x=0-row identification). Demands:
  Interpreting + Writing. Frame: **75 KCs / 95 edges / 16 schemas**, components
  63+2+2+2+2+1+1+1+1, 24 roots; validates all-4 offline + live (reload used;
  143 nodes / 211 edges). Checkpoint `bak_sec84_p5_mint_116_20260723_064633`.
- **P6 (from 1.2) — 105's third clause. RESOLVED 2026-07-23: Bill adjudicated
  TRIM.** The axis-exchange coordination clause cut from 105's long — it was a
  second, harder performance on the equation-writing KC, never exercised by the
  §8.2 task, and closer to COP&CQ territory; IM G7U2 L13 stays covered by the
  core content plus 102. The P2 demand tags (R+P+W) already matched the trimmed
  statement. Rationale on the KC. Also recorded during closeout: the
  twice-flagged 095-a defense (no 085-j/k feeders per no-method-restriction +
  evaluation-suffices) as a rationale annotation on 095-a. Description-only.
  Checkpoint `bak_sec84_p6_trim_105_20260723_065021`.

**Not carried as items:** 5.8's soft-equivalence hint (100/085-l) and
machine-readable placeholder flags (084-b) — deployment-spec territory, noted
for the atlas-level design doc.

**§8.4 headline: the auditor's verdict — "well-architected … close to
release-ready as a map" — with all three major findings landing either on
already-recorded tensions (H5, atlas sequencing) or on the two genuine work
items this audit was built to catch: the language-demands layer (P2) and the
093 grain question (P1). No wiring was falsified; the §8.2 edge verdicts all
survived pedagogical re-examination, with P3 the one edge family where mastery
semantics and instructional order pull apart.**

**§8.4 closeout (2026-07-23).** All six adjudication items resolved by Bill same
day; one finding reopened and parked (the 110–112 presentation bundling — open
question on LF-110). Final frame state: **75 KCs / 95 edges / 16 schemas**,
components 63+2+2+2+2+1+1+1+1, 24 justified roots, four standalone diagnostics;
validates all-4 offline + live. New KCs this pass: LF-113/114/115 (easy-instance
rungs under the rate/initial-value extractors) and LF-116 (rate-as-constant-
difference table bridge). The language-demands layer is complete for the first
time: every KC except the 084-b placeholder tagged under the frame-relative
rubric (casebook C28). **With §8.1–8.4 all passed, the frame has completed the
Standards §8 stress-test suite and is release-ready per §8; state is UNPUBLISHED
relative to the 2026-07-21 publish.**
