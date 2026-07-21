# Living Map Frame Authoring Standards

**Status:** Draft v2 (2026-07-13).

**Audience:** Frame authors, reviewers, and collaborators. This document states the
principles; its companion, [FRAME_AUTHORING_CASEBOOK.md](FRAME_AUTHORING_CASEBOOK.md),
records the concrete cases that motivated each principle, with full knowledge-component
identifiers, dates, and evidence. The casebook is primarily for AI auditors and for
anyone who wants to see a principle's provenance; this document is meant to be readable
on its own.

---

## 1. What a frame is

A **knowledge frame** is a directed acyclic graph of **knowledge components (KCs)**
connected by **prerequisite edges**, organized into a nested family of **schemas**.
Every frame must pass four structural checks at all times: schema convexity, downward
closure, frame acyclicity, and laminarity. These are enforced by the validator and are
necessary but nowhere near sufficient — the rest of this document is about the content
standards the validator cannot check.

---

## 2. Source documents for ingestion

What the source document is shapes everything downstream.

**Build top-down from standards, not bottom-up from skill inventories.** Bottom-up
attempts curate plenty of KCs and edges but stall at the schema layer: with no
organizing structure given in advance, the grouping problem is the hard part and it
arrives last, when it is hardest. Building from a standards document gives the schema
scaffolding for free — the standards' own cluster structure proposes the schema leaves,
and KCs are generated *into* that structure.

**Good ingestion sources have, in rough priority order:**

1. **Explicit hierarchy** — clusters, units, or strands that can seed the schema layer.
2. **A clear content boundary** — what is in scope and what is prior knowledge.
3. **Named representations** — sources that distinguish verbal, table, graph, and
   equation presentations seed the family structure (§3) directly.
4. **Progression order** — sequencing information that can be mined for candidate
   edges, to be verified against the counterfactual test (§4), never imported as-is.
5. **Within-document keys** — any key unique inside the source (a row number, a
   heading path) is enough for provenance to survive the ingest; the importer mints
   the map's own IDs (§9). The source does not need a real identifier system.

**Hazards:**

- **Flat parsing of structured documents.** A row-per-chunk parser applied to a
  multi-sheet relational workbook silently flattens the schema layer into spurious KCs.
  Fingerprint: an ingest that produces zero schemas and a pile of "define X" KCs.
  Structured sources need structure-aware importers.
- **Importing curricular sequence as prerequisite structure.** "Taught before" is
  evidence, not proof. Every mined edge goes through the §4 test.
- **Sources that mix concepts and skills without marking which is which.** These
  generate concept-proxy KCs (§3) that must be manually unpicked later.

---

## 3. KC authoring standards

**A KC is an observable, assessable student performance** (for Skills; Principles and
Definitions have their own grain). The long description states: given what stimulus,
the student does what, to what success criteria.

**Differentiate KCs by input representation, never by solution method.** The family
pattern — the same performance with verbal, table, graph, or equation input — is the
frame's basic granularity device. A student who translates the given representation
into another and then succeeds has still demonstrated the KC.

**The wiring-differential test: split by representation only when the variants would
be wired differently** — different prerequisites or different dependents. A bundled
multi-representation KC with several representation-specific in-edges is making a
conjunctive overclaim (each edge asserts the student needs *that* representation's
skill for the *whole* bundle), and splitting fixes it: each variant keeps only its
own feeder. But when the variants would all get identical wiring (typically all
roots, with dependents hanging off one variant), the split adds KCs and no
information — keep the KC generic and, if needed, rewrite it to name the breadth of
stimulus honestly. Paired precedents: the write-y=kx family was split (each variant
had its own identify-k feeder and its own construct-family dependent) while
solve-for-unknown-values stayed generic (all variants would be roots feeding the
same contextual problems); see casebook C16, which also records the earlier
instances (085-a split, 087 kept generic).

**Never restrict how a student demonstrates a KC.** Banned phrasings: "without using a
table," "by graphing," "mentally," "first find the rate and then work backwards."
Wanting a method restriction is a symptom that the KC is badly written or too broad —
fix by re-anchoring to the input representation, or by splitting. The same applies to
**task-form restrictions**: requiring that a problem combine skill X with skill Y is
the same disease as requiring method X.

**Permitted in long descriptions:** definitional parentheticals ("rate of change — the
change in output per unit change in input"), product criteria for production KCs (a
created graph must have labeled axes and scale), justification requirements, and worked
examples of what counts as an adequate explanation. For derivation KCs the argument
*is* the content and may be spelled out.

**No concept-proxy KCs.** "Understands proportionality" is not a KC — concept-level
understanding lives at the **schema** level, expressed by the schema's membership and
description. A warning sign: a KC that has accumulated a large number of outgoing
edges is often standing in for a concept rather than describing a performance. Demote
it to its literal performance and cut the proxy edges.

**The atoms-already-exist test (when a whole KC is suspected of being a schema).**
Sometimes the suspect is not an edge pattern but the KC itself — an
"interpret/understand the meaning of X" node. To adjudicate, enumerate the assessable
atoms in its description and look for each in the frame. If every atom already exists
as a KC, the suspect is a schema description trapped in a KC: demoting it to a
literal performance would mint a duplicate, and splitting it would mint several — so
**absorb** it into the enclosing schema's description (naming where the assessable
atoms live), rewire its one or two non-redundant edges to an heir (typically the
frame's working definition or the atoms themselves), and delete it. A concept-proxy's
out-edges are usually already redundant with its heir's, which makes dissolution
cheap — that redundancy is itself confirming evidence. Precedent: casebook C22
(LF-084-a dissolved into linear-function-properties; C3's mirror on the LF side).

**Attach terminology to its object.** Mathematical terms that are numerically equal
can still belong to different objects, and a KC's description uses the term of the
object the student is actually handling. In the ratio–proportionality–linearity
strand: a **unit rate** is the per-one value of a ratio or of a "y per 1 x" reading;
the **constant of proportionality** is the parameter of a proportional relationship
taken as an object; **rate of change** and **slope** belong to linear functions and
their graphs. So extracting or comparing the parameter of a relationship uses
*constant of proportionality*, while interpreting a per-one reading uses *unit rate*
— even inside the same frame, and even though the numbers coincide. The equalities
between the terms are themselves content and live in bridge KCs (the point (1, r)
exhibits the unit rate on the graph; unit-rate-as-slope works because slope is
itself a per-one reading); they must not leak into loose synonymy elsewhere
("unit rate or constant of proportionality"). A global search-and-replace is
exactly the wrong tool: classify each occurrence by its object. Precedent:
casebook C23.

**Sibling KCs get parallel wording.** Parallelism across a family is a feature, and
its absence is an audit signal (§7).

---

## 4. Edge semantics

**What an edge means — and two things it does not.** An edge A → B is a claim about
learners: mastery of B cannot arise without A. It is not a claim about mathematics —
that B's justification rests on A — and it is not a claim about teaching order. All
three relations are tempting to draw as arrows on the same nodes, and the frame
separates them deliberately:

- *Mathematical dependency* enters the frame either as a derivation KC, when the
  argument itself is content students learn, or as a placeholder, when the
  justification is real but deferred to another frame. It is never, by itself,
  an edge.
- *Pedagogical sequence* is a walk through the frame, not part of it. Edges
  constrain the order of **mastery**, not the order of **encounter**: a curriculum
  may open with the punchline — exhibit the destination before anything upstream is
  mastered — without violating an edge, because encountering a phenomenon is not
  performing a KC. Different curricula walk the same frame differently; the frame
  records what every successful walk must respect. (Spiral designs that teach an
  informal version early and formalize it later are not counterexamples: the
  informal and formal performances are different KCs — a grain question, not a
  contradiction.)

A consequence worth keeping: **pedagogy cannot contradict a correct edge, only
refute a wrong one.** If some teaching sequence reliably produces mastery of B
before A, the edge was false — cut it. Teaching experience is evidence against
edges, alongside task-based falsification (§8.2). See casebook C17.

**The strict counterfactual test:** an edge A → B means a student who cannot do A
cannot do B, other than in edge cases. Not "A is usually taught first," not "A would
help," not "A and B are about the same thing."

**Known anti-patterns** (each caught at least once in practice; see casebook):

- **Proxy edges.** An edge standing in for background familiarity rather than the
  literal performance. Test: does the target need the *performance* the source
  describes, or just acquaintance with the source's subject matter?
- **Production → interpretation.** Making a representation is rarely prerequisite to
  reading one: identifying a quantity from a table does not require the ability to
  construct such a table. When cutting one of these, the true prerequisite is usually
  the interpretive sibling — the deciding or identifying KC for the same
  representation. Production → production edges are fine when the source is a genuine
  special case of the target.
- **Curricular adjacency.** Imported sequence with no logical dependency.
- **Classification-before-extraction.** A decide/classify KC as prerequisite to its
  identify/extract sibling is usually a concept-proxy in disguise ("understands X"
  wearing a classification costume). The dependency runs the other way: one decides a
  relationship has a property by finding — or failing to find — its parameter, so the
  extraction is the atom inside the classification. Exception: when the classification
  criterion genuinely does not involve the extracted parameter (deciding
  proportionality from a graph uses straight-line-through-origin, never k), the pair
  is independent — cut, don't reverse. *(This overturns an earlier version of this
  document that listed decide → identify as a legitimate pattern; see casebook C14.)*

**Legitimate patterns:**

- **Identify → decide** and **identify → use/compare** within a single
  representation: extracting a relationship's parameter precedes classifying the
  relationship (see the classification-before-extraction anti-pattern above) and
  precedes using or comparing the parameter. Decide KCs are typically terminal
  diagnostics, not middle links.
- **Special-case-before-general** across the frame's main development (for example,
  each proportional-relationships skill feeding its linear-functions generalization).
  When such a family of parallel edges exists, it should be *complete* — a missing
  member is an audit finding, not a stylistic variation.
- **Atomic-skill-inside:** a computation on minimal input (two points) feeding the
  versions of the same computation embedded in richer inputs (a table, a graph).

**The expansion test.** An edge whose source and target feel far apart is a smell even
when the dependency is real: look for missing intermediate KCs or a missing connecting
edge. Diagnostic: read the target's long description — every capability it *mentions
using* must be present upstream. A derivation that "uses the definition of slope" with
no slope KC anywhere upstream is missing structure, and the fix is usually a new
intermediate KC or a reconnected chain, not deletion of the edge.

**Flag taxonomy.** Every edge is one of:

- **confirmed** — passes the counterfactual test cleanly;
- **borderline** — plausibly fails the strict test but kept for a stated reason,
  recorded in an annotation;
- **placeholder** — the dependency is real but its development is deliberately
  deferred to another frame (recorded as such, with the destination frame named).

**Roots and islands policy.** A KC with no in-frame prerequisites is a claim that its
prerequisites live *outside the frame*. Roots must be justified as genuine docking
points for other frames — the places where a prior frame's content is expected to
connect. An accidental root, created by cutting edges, must be either justified or
rewired.

The same reasoning extends to connectivity. **Connectedness is a property of the
eventual map, not of a single frame**: a frame may contain disconnected islands, and
an island is legal exactly when its roots are justified docking points. Disconnection
is a *diagnostic*, not a violation — it signals either missing edges (fix in-frame) or
a missing frame (record the expected frame in the boundary schemas' descriptions and
move on; do not patch the island to the main component with an edge that fails the
counterfactual test). In the limit a single KC may be deliberately isolated, when it
is at once a justified docking root and a justified terminal performance. A cluster
held onto the main component only by edges that fail the counterfactual test is the
signature of a missing frame (casebook C18). Validation should *report* components
and check their roots against the justified list, not gate on connectedness.

---

## 5. Schema standards

- **Leaves are family-based** — the organizing principle for a leaf (a bottom-level
  schema, the only kind that directly contains KCs) is the performance family of §3:
  the same student performance across its input representations. Example: "decide
  whether two quantities in a context are proportional" given a verbal description,
  given a table, given a graph, and given an equation is four KCs and one leaf —
  one performance, four input representations. One leaf may hold a few tightly
  coupled families (determining the rate of change and determining the initial
  value, say); what it must not be is a topical grab-bag ("miscellaneous
  proportionality skills").
- **Minimum of three KCs per leaf** — a leaf with one or two KCs is not doing any
  grouping work. A family too small to stand alone waits inside a neighboring leaf
  until growth (typically a granularity split) makes its own leaf viable.
- **Convexity outranks family purity.** A schema is convex when every prerequisite
  path between two of its KCs stays inside the schema — if A → B → C with A and C in
  the leaf but B outside, the leaf is not a self-contained unit and cannot be
  collapsed to a single node. When splitting a multi-family leaf into finer leaves
  would create such a path, the families stay together: do not subdivide if the
  split would break convexity.
- **A schema-quotient cycle is a schema smell, not (only) an edge smell.** When
  correcting edge directions creates a cycle in the schema-level quotient while the
  KC graph stays acyclic, suspect that a family is sitting in the wrong schema —
  typically a terminal diagnostic layer lodged inside a concept schema (the inverse
  of the misplaced-bridge-content case). Move the family to its own leaf rather than
  sacrifice edges that pass the counterfactual test (casebook C19).
- **Schema descriptions carry the concept-level meaning** that KCs must not (§3), plus
  curriculum references and, for boundary schemas, a statement of what frame is
  expected to dock there.
- **Structural invariants** (validator-enforced): convexity, laminarity, downward
  closure, acyclicity. Run the validator after *every* applied change set, not just
  before publish.

---

## 6. The human–AI interaction protocol

### 6.1 Roles

- **The human** holds mathematical and pedagogical authority: every structural change
  to a frame (edge, KC, schema) requires explicit human approval. The human also
  adjudicates every borderline flag and every new principle.
- **The AI** is the systematic auditor and mechanic: it generalizes single
  observations into whole-frame patterns, gathers evidence from the frame's own
  structure, presents grouped proposals with rationale, applies approved changes
  mechanically (backup → transaction → validate → record), and maintains provenance.

### 6.2 Human-initiated: the smell loop

1. **The human reports a smell** — a single edge or description that feels wrong.
   There is no obligation to diagnose it; "not sure these are strictly prerequisite"
   is enough to start.
2. **The AI generalizes** — is this an instance of a pattern? Where else does the
   pattern occur? What does the frame's own structure say? The most persuasive
   evidence is internal: an inconsistency between siblings that ought to be parallel.
3. **The AI presents a grouped proposal** — deletions, additions, expansions, each
   with a counterfactual argument, each group independently acceptable. Proposals
   distinguish confident findings from weak ones and say which the AI would leave out.
4. **The human adjudicates** — approve all, trim, or redirect.
5. **The AI applies and verifies** — see safety rails (§6.4).
6. **The correction is distilled** — if the adjudication revealed a general principle,
   it is added to this document (§10), its case to the casebook, and the frame
   re-audited against it.

### 6.3 AI-initiated: AI smells

As a frame grows past what a human can eyeball, the direction inverts: the AI runs
detectors and brings **questions**, not answers. The output of an AI-smell pass is a
short list of questions for the human, each with evidence, a severity estimate, and a
proposed resolution — never silent fixes.

Detector catalog (each has caught at least one real defect; extend as new detectors
prove out — precedents in the casebook):

| Detector | Signal |
|---|---|
| **Family asymmetry** | One sibling's edges differ from its parallel siblings' |
| **Parallel-structure gaps** | A special→general edge family with missing members |
| **Degree outliers** | A KC with far more outgoing edges than its grain warrants |
| **Long edges** | Source and target far apart in conceptual or derivation depth |
| **Disconnected subchains** | Two chains that plainly should touch but do not |
| **Unjustified roots/sinks** | A root that is not a docking point; a sink that is not a terminal performance |
| **Description smells** | Method or task-form restrictions; "understands/knows" verbs |
| **Mentions-without-prerequisite** | A long description references a capability absent upstream |

Rules of engagement for AI-smell passes:

- **Batch and rank.** Bring at most about five questions per pass, most severe first.
  A fifty-item dump defeats the purpose of the human's limited attention.
- **Phrase as adjudicable questions** — "is constructing a model genuinely
  prerequisite to interpreting one?" — not "there are problems in the modeling leaf."
- **Show the frame's own evidence** (the asymmetry, the description text), not just
  reasoning.
- **State what was checked and found clean**, so silence is informative.

### 6.4 Safety rails (non-negotiable, for all automated actions)

1. **Backup before any applied change set**, named for the change.
2. **Single transaction** per approved change set.
3. **Validator after every change set** — all four structural checks, plus acyclicity
   of the KC graph, plus a no-orphan check on every KC whose edges were touched.
4. **Provenance annotations** on new KCs and non-obvious changes: who proposed, why,
   which audit pass.
5. **Borderline flags recorded**, not just remembered.
6. **Publish only on explicit human instruction**, with a dry-run diff that must
   reconcile against the expected change count before pushing.

---

## 7. Pre-publish audit passes

Run before any publish; all are repeatable procedures:

1. **Structural validation** — the validator's four checks; no cycles; every root and
   sink justified.
2. **Proxy-edge sweep** — every edge from a high-out-degree KC through the
   counterfactual test.
3. **Production→interpretation sweep** — every edge whose source is a production KC
   and whose target is an interpretation KC.
4. **Method-restriction sweep** — every long description against the §3 banned list.
5. **Family-parallelism sweep** — every representation family and every
   special→general edge family checked for completeness and symmetric wiring.
6. **Gap/expansion sweep** — long edges and mentions-without-prerequisite.

---

## 8. Final stress tests (frame readiness)

The audits in §7 check internal consistency. Before a frame is treated as *done*, it
must survive contact with external reality. Four stress tests:

### 8.1 Curriculum walk

Take an existing well-structured curriculum for the same content and walk it through
the frame:

- Every lesson-level learning goal should map to one or more KCs. **Unmappable goals**
  are either out of scope by design (record why) or missing KCs.
- The curriculum's sequence should be consistent with the frame's partial order —
  that is, extendable to a linear extension of it. **Order violations** (the
  curriculum teaches B before its supposed prerequisite A) either falsify edges or
  reveal that the curriculum is doing something interesting; adjudicate each.
- KCs no curriculum touches are candidates for deletion — or evidence that the
  curricula have a gap. Either way, worth knowing.

### 8.2 Task generation

Use the frame to generate assessment tasks:

- **Every Skill KC must yield a task.** A KC that cannot be turned into a task is
  mis-grained, or is a concept-proxy that escaped §3.
- **Two KCs whose tasks are indistinguishable are duplicates** — merge or sharpen.
- **Edge falsification by task:** for a sample of edges A → B, attempt to construct a
  legitimate B-task solvable by a student who cannot do A. Success falsifies the
  edge. This is the counterfactual test made operational, and it is the strongest
  single check available.

### 8.3 Mathematical audit

An edge-by-edge pass on logical content, ideally by a fresh reader (human, or an AI
instance without authoring context):

- Is each edge's dependency claim mathematically true as stated?
- Are derivation chains complete — every fact a derivation uses upstream of it, every
  definition preceding its use?
- Are boundary placeholders (§4) honest — is the deferred justification actually
  available in the frame it is deferred to?

### 8.4 Pedagogical audit

- Is grain size consistent across the frame, and consistent with instructional
  reality (a KC roughly matching what a lesson or activity can target)?
- Are language demands recorded and plausible for each KC?
- Is representation coverage complete where it should be, and deliberately incomplete
  where it should not be (record which)?
- Are the roots the places a teacher would actually expect students to arrive with
  prior knowledge? Are the sinks performances worth arriving at?
- Would the frame's structure mislead an adaptive system in any obvious way (for
  example, a borderline edge that would wrongly gate content)?

A frame that has passed §7 and §8 is **release-ready**; record the date and the
stress-test results with the frame.

---

## 9. Identifiers and lineage

**Identity and classification are different jobs.** An identifier's only job is to be
a permanent, unambiguous handle; where a KC lives — schema, family, domain — is the
database's job, revisable at any time. The failure mode to avoid is the *intelligent
key*: an ID that encodes current structure is a second copy of that structure, and
the two copies always drift (casebook C13).

- **Format at minting: `<domain>-<seq>`** — a short domain code plus a per-domain
  sequential accession number, centrally minted. A family-letter suffix (`LF-084-b`)
  is permitted as a mnemonic at minting.
- **An ID is a birth record, not an address.** Everything in it — prefix, number,
  suffix — records the circumstances of minting and asserts nothing about current
  structure. A KC that later moves domains, schemas, or families keeps its ID
  unchanged.
- **Never rename, never reuse.** Merges and splits retire the old IDs and mint fresh
  accession numbers, recorded in a lineage log (`old_id → new_id(s), reason, date`)
  so provenance, casebook citations, and session history survive. Do not extend
  suffixes to encode lineage (`-b-2`) — lineage lives in the log, not the ID.
- **Hierarchy encoding is retired.** No new frame encodes schema hierarchy in IDs
  (CNM's place-value scheme). Existing CNM IDs are grandfathered as opaque handles;
  the place value is no longer asserted to mean anything.
- **Sources need only within-document keys** (§2) — the importer mints the global
  IDs; source keys go to the alignment/provenance record, not into the map's IDs.
- **In durable documents, pair an ID with its short description** — on first mention,
  and again whenever it hasn't appeared in a while. No mechanical rule; err on the
  side of re-giving it. The test: a reader should never have to scroll back or open
  the app to know what an ID refers to. Bare IDs are for live discussion, where they
  serve as short-term handles; they are not names anyone is expected to remember.

---

## 10. How this document grows

This document is the durable output of the interaction protocol in §6. The rule:

> When a human adjudication reveals a general principle — not just a local fix — the
> principle is added here, and its motivating case is added to the
> [casebook](FRAME_AUTHORING_CASEBOOK.md) with full identifiers and evidence. The
> frame(s) are then re-audited against the new principle.

Both documents are versioned in git; substantive changes to this one should name the
casebook entry that motivated them.
