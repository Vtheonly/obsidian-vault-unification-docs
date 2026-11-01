# Risk Register and Decision Log

## Active risk register

| ID | Risk | Required mitigation |
|---|---|---|
| R-001 | Small or obscure source details are omitted | Exhaustive source-unit accounting, rare-term alerts, semantic audit, deliberate omission tests |
| R-002 | AI rewrites into shallow summaries | Editorial contract, source evidence bundles, detail-retention checks, depth audits |
| R-003 | Early notes are polished but later notes degrade | Batch gates, cross-batch audits, full-vault editorial audit |
| R-004 | Known topics dominate and unknown topics are missed | Corpus-derived open taxonomy; no fixed topic whitelist; all-unit coverage |
| R-005 | Duplicate detection collapses meaningful distinctions | Semantic comparison, context-aware units, unique-detail review |
| R-006 | Contradictions are silently resolved incorrectly | Evidence-based reconciliation and explicit findings |
| R-007 | Context exhaustion causes lost state or hallucinated continuation | Persistent registry, tasks, checkpoints, tests, verified handoffs |
| R-008 | Subagents produce inconsistent changes | Bounded scopes, shared rules, controlled integration, independent review |
| R-009 | A polished note is mistaken for complete preservation | Separate accounting, semantic validation, technical tests, independent acceptance |
| R-010 | Source files/assets cannot be extracted | Explicit extraction status, OCR/alternate inspection, unresolved blocker reporting |
| R-011 | Global style changes cause drift | Decision control, impact analysis, corpus-wide migration and regression checks |
| R-012 | Metrics hide weak areas | Explicit denominators, per-file/per-type/per-topic breakdowns, no compensating aggregate |
| R-013 | Provenance becomes stale after edits | Hashes, stable IDs, change detection, registry migrations |
| R-014 | Agents trust previous session claims | Verify repository evidence, rerun tests if unsupported |
| R-015 | Output vault relies on source vaults to make sense | Standalone final-vault integration and navigation audit |

## Decision log format

Use stable IDs such as `ADR-0001`. Each decision records:
- status: proposed, accepted, superseded;
- context and problem;
- options considered;
- decision and rationale;
- risks and consequences;
- affected docs, schemas, scripts, and data;
- migration/verification plan;
- approval evidence if human approval is required.

## Initial decisions

### ADR-0001 — Synthesis rather than concatenation
**Decision:** Generate a new canonical vault from combined evidence.  
**Rationale:** Mechanical concatenation cannot resolve redundancy, contradiction, structure, or inconsistent explanations.  
**Consequence:** Requires source-unit provenance and independent verification.

### ADR-0002 — Immutable source vaults
**Decision:** Treat originals as read-only during processing and generate output separately.  
**Rationale:** Prevents accidental source loss and allows comparison and recovery.

### ADR-0003 — Persistent multi-session state
**Decision:** Repository artifacts are the durable source of truth across GLM 5.3 sessions.  
**Rationale:** Fresh sessions cannot depend on previous conversational context.

### ADR-0004 — Full-corpus care
**Decision:** All notes and knowledge units receive the same required preservation and editorial standard; examples do not form an exhaustive topic list.  
**Rationale:** Avoids selective excellence and hidden omissions.

### ADR-0005 — Independent verification
**Decision:** Synthesis cannot self-certify completeness; acceptance uses separate evidence-based audit.  
**Rationale:** A fluent, polished output can still omit or distort knowledge.

## Additional risks and mitigations

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-009 | Rare or one-off details disappear while high-frequency concepts look complete. | Critical | Atomic knowledge-unit accounting, per-concept coverage, frequency alarms, and deliberate omission mutation tests. |
| R-010 | Global coverage percentages hide an entirely missing domain, file, or unusual subtopic. | Critical | Report explicit numerators and denominators by vault, file, domain, concept, and KU; unresolved units block release. |
| R-011 | Tool documentation is mistaken for a working implementation. | High | Capability status must be generated from inspected code and actual test runs, with command, exit code, and report evidence. |
| R-012 | A parser silently drops unfamiliar Markdown, malformed math, embedded assets, or code blocks. | Critical | Preserve raw source locators, report unsupported cases, test malformed fixtures, and keep affected units unaccounted or under review until resolved. |
| R-013 | Automated similarity incorrectly labels complementary or conflicting content as duplicates. | High | Treat deterministic matching as candidate generation; retain independent semantic classification and explicit conflict review. |
| R-014 | Repairs erase already accepted content or regenerate too much of the vault. | High | Require targeted repairs with regression checks, preserve unaffected sections, and quarantine after three failed attempts. |

Coverage statistics and frequency distributions are diagnostic signals, not standalone proof of semantic preservation. A high percentage cannot override a single unaccounted critical knowledge unit, and a frequency drop must trigger investigation rather than automatic rewriting.

### ADR-0006 — Optional `notes` field on task records
**Status:** accepted (2026-10-25, BOOT-000 session)
**Context:** Cross-session handoffs need free-text context attached to specific
task records (e.g. preliminary evidence gathered while executing a
predecessor task). The original task schema had `additionalProperties: false`
and no place for such context, forcing either loss of context or schema
violations.
**Options considered:** (1) keep context only in handoff documents; (2) extend
task records with an optional `notes` string; (3) a separate task-notes file.
**Decision:** Option 2: add optional `notes` (string) to
`schemas/task.schema.json`.
**Rationale:** Task-attached context survives task-queue-first navigation and
cannot drift from its task; a separate file adds a second authority to keep in
sync. The field is optional and does not participate in state-machine
semantics, dependencies, or acceptance criteria.
**Impact / migration:** Backward compatible — existing records remain valid
(none used `notes` before). `validate-registry` (CAP-006) picks up the schema
change automatically; its tests are schema-driven and unaffected. Verified by
re-running `vu validate-registry --tasks state/task-queue.jsonl` after the
change (exit 0).
**Verification plan:** every future schema change follows the same pattern:
documented ADR + schema edit + validator re-run + suite re-run.

### ADR-0007 — Persistent KU registry: canonical JSONL store + derived SQLite index
**Status:** accepted (2026-10-26, BOOT-003 session)
**Context:** BOOT-003 requires a persistent knowledge-unit registry that
survives fresh sessions, supports many-to-many provenance (units to
destinations, concepts, findings, supporting units), enforces disposition
accounting, and is queryable at corpus scale (est. tens of thousands of
units). `docs/TOOLING_AND_SETUP.md` suggests SQLite as a reasonable default
at this scale; the project already uses committed JSONL for tasks and
findings.
**Options considered:** (1) SQLite as the sole store, committed to Git;
(2) JSONL files only, no relational index; (3) hybrid: canonical committed
JSONL batches plus a derived, rebuildable SQLite index.
**Decision:** Option 3. JSONL batch files under `state/knowledge-units/`
(each validated against `schemas/knowledge-unit.schema.json` before use) are
the canonical, committed record of every knowledge unit — diff-friendly,
append-only and auditable like the existing task queue. A SQLite database
(default under `state/registries/`, git-ignored) is a derived index rebuilt
via `vu kureg-init` + `vu kureg-load`; in v1 all writes flow exclusively
through `kureg-load`, which schema-validates, cross-checks and atomically
inserts each batch. No direct-to-database record creation exists.
**Rationale:** committing a binary database invites merge conflicts and
opaque diffs, and makes "trust the repository evidence" harder; plain JSONL
cannot enforce referential integrity or answer provenance queries
efficiently. The hybrid keeps Git as the durable authority while SQLite
provides integrity and queries. Database corruption or loss is recoverable
by rebuild from the canonical batches (tested: two independent rebuilds from
the same JSONL produce byte-identical query output).
**Consequences / risks:** the database can lag behind the canonical batches
if someone loads selectively — rebuilds are cheap and validated
(`kureg-validate`); reconciliation after a source-file change is explicit
(new IDs, never silent reuse) per `docs/KNOWLEDGE_AND_PROVENANCE.md`.
**Affected artifacts:** `src/vault_unification/kuregistry.py`,
`src/vault_unification/cli.py` (kureg-* commands),
`state/knowledge-units/README.md`, `.gitignore` (`state/registries/`),
`tests/test_kuregistry.py`, `tests/test_cli.py`.
**Migration/verification plan:** `vu kureg-init --db <path> [--force]` then
`vu kureg-load --db <path> --kus <batch.jsonl>` per batch; `vu
kureg-validate --db <path>` reports integrity and accounting counts. Suite:
248/248 passed at adoption (evidence:
`reports/bootstrap/boot-003-pytest-report.json`).

### ADR-0008 — KU schema v1.1: separate `overlap_type` and required `superseded_rationale`
**Status:** accepted (2026-10-26, BOOT-003 session)
**Context:** `docs/KNOWLEDGE_AND_PROVENANCE.md` section 7 requires overlap
classification (Exact Duplicate / Semantic Duplicate / Partial Overlap /
Complementary Content / Conflict or Historical Difference) to be stored
separately from disposition, and requires Superseded decisions to record a
rationale with evidence that unique details were preserved elsewhere. The
v1.0 draft schema had neither field; the only place for a rationale was the
free-form `verification_status` object.
**Options considered:** (1) keep the free object as the only place for
rationale and omit overlap; (2) add `overlap_type` (optional enum) and
`superseded_rationale` (optional string) to the schema; (3) encode the
conditional requirement in JSON Schema `if/then`.
**Decision:** Option 2, with the conditional rule (rationale non-empty when
disposition is `Superseded`) enforced by cross-check code shared between
file-level validation (`validate_ku_file`) and registry loads
(`kuregistry.load_records`), not by JSON Schema.
**Rationale:** a dedicated structured field is queryable and auditable;
hiding the rationale in `verification_status` would make invariant 3
unenforceable by code. Keeping the conditional rule in cross-checks (rather
than `if/then`) preserves uniform, actionable error messages across both
validation layers and keeps the schema declarative about shape only.
**Impact / migration:** backward compatible — both fields are optional and
nullable; no KU records existed before this change (zero migration).
Verified per the ADR-0006 pattern: schema edit + `vu validate-registry`
re-run + full suite re-run (248/248).
**Affected artifacts:** `schemas/knowledge-unit.schema.json` (version 1.1),
`src/vault_unification/registry.py` (`check_ku_records`,
`validate_ku_file`), `src/vault_unification/kuregistry.py` (CHECK
constraints + validate rules), `tests/test_kuregistry.py`,
`tests/test_cli.py`.

### ADR-0010 — Full-corpus discovery candidates: derived artifact, not a committed blob
**Status:** accepted (2026-10-28, DISC-002 session)
**Context:** the corpus-wide `discover-gaps` run emits 60,154 candidate
records (269,220,219 bytes) — 1.6x the size of the entire repository at
HEAD 4ae8125 (172MB). Committing the monolith would double the repo, and
the spec (docs/EMERGENT_CONCEPT_DISCOVERY.md) expects discovery re-runs as
review proceeds, each producing another 269MB blob.
**Options considered:** (1) commit the monolith; (2) shard it into
review-sized committed chunks; (3) treat it as a derived, deterministically
regenerable artifact (the ADR-0007 registry pattern) and commit only the
decision records + reports.
**Decision:** option 3. `state/concept-candidates/002-disc002-full-corpus.jsonl`
is git-ignored. The committed source of truth for review state is the
decisions JSONL (`002a-disc002-decisions-r*.jsonl`, applied via
`discovery-decide` with an explicit recorded `--decided-utc`); the
candidates file regenerates byte-identically from the committed KU batches
+ manifests (verified: double-run sha256
88a538eb3dc70e99f53093eaf5e55eaa2baa38461ea660b97e441f1fb0952bf8, both
runs, 547.4s / 544.1s, peak RSS 1.95GB).
**Rationale:** replay is exactly `discover-gaps` (deterministic, no
timestamps in candidate records) followed by `discovery-decide` with the
recorded timestamp; both commands are tested and their reports are
committed. Rejection/acceptance of a candidate never affects KU
dispositions, so no knowledge can be lost by a regeneration.
**Impact / migration:** the partial-corpus file
`001-disc001-partial-corpus.jsonl` (28MB) remains committed (historical
evidence of the coverage-gated run); no migration needed. The
`state/concept-candidates/` review outputs (decisions) stay committed.
**Affected artifacts:** `.gitignore`, `reports/discovery/disc002-*`,
`scripts/disc002_*.py`, `docs/agent-handoff/next-agent.md`.

### ADR-0011 — User-authorized accelerated completion mode: calibrated bulk candidate decisions + tiered verification
**Status:** accepted (2026-11-01, DISC-002 session 16)
**Context:** After 15 review sessions (2,063 committed decisions; 60 per
session), 4,274 signal-rule candidates remain, with 69,185 dossier-extension
pairs, disposition assignment, and gated synthesis still ahead. At the
historical 60-candidates/session pace the candidate stage alone needs ~72
more sessions. The user reviewed the completion arithmetic
(candidates 17.4% done; effort-weighted project completion single-digit
percent) and directed (2026-11-01): remove the universal per-candidate
subagent cross-check, streamline verification that does not advance the
deliverable, and complete the final vault in fewer than 12 additional
sessions.
**Options considered:** (1) continue 60/session with universal dual review
(~72 sessions for candidates alone — violates the user's constraint);
(2) abandon review of remaining candidates (violates the discovery
coverage contract); (3) calibrated deterministic bulk decisions for the
mechanically-decidable classes, individual semantic review reserved for
the gap-relevant residual, verification tiered by decision class.
**Decision:** option 3, with these bindings:
1. **Bulk classes are admissible only with zero counter-evidence in the
   full 2,063-decision calibration set.** A mechanical noise class
   (numeric/unit fragments, import statements, years, code identifiers,
   adverb/prose fragments, vault meta) may be bulk-rejected only if NO
   calibration member of that class received a non-reject outcome. Any
   class with a counter-example goes to individual review.
2. **Citation-backed bulk covers.** A candidate may be bulk-covered only
   with machine-generated evidence: a real (fence-aware, authoritative
   state-machine) heading hit or definition-window hit for the exact term
   recorded as file:line in the rationale — the same evidence class the
   batch-15 review cited by hand. Homonym/contradiction-suspect and
   high-score candidates are excluded from bulk cover and reviewed
   individually.
3. **confirm_gap is never bulk-decided.** Gap-possible candidates
   (probe-negative, concept-shaped, dependency-position usage) always get
   individual semantic review, and every orchestrator-proposed
   confirm_gap keeps the independent-subagent cross-check plus
   independent re-verification (standing sessions 9-15 rule).
4. **Tiered verification replaces universal cross-check:** (a) every
   confirm_gap and merge: subagent cross-check + independent
   re-verification; (b) bulk N/P classes: random 5% sample (minimum 30)
   independently re-checked per applied batch, plus full re-verification
   of any sample disagreement; if a sample reveals a wrong-decision class
   member, the whole class is pulled back to individual review for that
   batch; (c) the residual class: orchestrator individual review with
   probe evidence bundles (no universal subagent re-check).
5. **Safety argument (why this cannot lose knowledge):** per ADR-0010,
   candidate acceptance/rejection never affects KU dispositions — all
   27,536 knowledge units remain in the ledger with source locators
   regardless of candidate outcomes. The only knowledge-affecting
   candidate outcome is confirm_gap (new dedicated treatment), which
   stays fully individually verified. A bulk cover/reject mislabel only
   changes a status field between two "no new note needed" outcomes.
6. **Preserved invariants:** the F-0021-fixed fence_spans probe
   signature, level-exact heading patterns, delta-verification with
   pre-written arithmetic, validate-green requirement, decided-utc
   recording, decisions JSONL commit + ADR-0010 replayability.
**Rationale:** The project's own contract (AGENTS.md §10) requires
deterministic tooling for mechanical work and semantic review for
judgment work. 2,063 hand-reviewed decisions provide a calibration set;
classes with zero counter-examples are mechanically decidable by
definition. The user explicitly authorized removing universal review and
prioritizing the final deliverable.
**Impact / migration:** No schema changes; decisions remain
discovery-decide JSONL with rationale + reviewer fields (bulk rationales
cite the calibration + per-candidate evidence). Batch sizes may exceed 60
(decision IDs remain D-DISC002-B<n>-**** with n the session's batch
number). The remaining-sessions plan: complete DISC-002 signal pool,
dossier-extension tiered classification, disposition assignment, and
gated synthesis within the user's <12-session budget.
**Approval evidence:** user direction 2026-11-01 ("remove the universal
review and do it fast then ... the final vault should be done in less
than 12 additional sessions"), recorded in the session-16 handoff and
checkpoint.
**Affected artifacts:** `scripts/disc002_batch16_*.py`,
`reports/discovery/disc002-s16-*`, `docs/agent-handoff/next-agent.md`,
this register.

### ADR-0012 — Binding accelerated-completion policy (enforce the speed decision across all future sessions)
**Status:** accepted (2026-11-01, policy session 17; user-directed)
**Context:** ADR-0011 authorized the accelerated mode and session 16
executed it (the entire 4,274-candidate signal pool in one session). The
user then directed (2026-11-01): "make new policy to ensure the next
agent follow the new decision of becoming faster" — the speed decision
must bind future sessions structurally, through the repository's
mandatory startup chain, rather than depending on each fresh session
choosing to follow it.
**Options considered:** (1) rely on ADR-0011 + handoff prose only (weak:
handoffs are advisory and get rewritten; a fresh agent could reinstate
slow modes without violating any rule); (2) amend AGENTS.md alone (the
mandatory-read file, but a full policy inline would bloat it and split
from the decision register); (3) canonical policy document + AGENTS.md
binding section + compliance block in every checkpoint + visible session
ledger.
**Decision:** option 3. Create
`docs/ACCELERATED_COMPLETION_POLICY.md` as the canonical binding policy;
amend AGENTS.md with §12 (mandatory-read chain: AGENTS.md → policy →
ADR-0011 → handoff); require an `accelerated_mode` block in every
session checkpoint (session number, budget consumed/remaining,
deliverable metric moved with before/after/denominator, failed-session
flag); maintain a session ledger inside the policy making budget burn
visible. Policy contents: hard deadline = final vault by end of session
26 (strict reading of "less than 12 additional sessions": sessions
16–26 = 11; the session-16 handoff's "session 27" was the looser reading
and is superseded); phase allocation S18–20 dossier-extension
classification (69,185 pairs), S21–22 disposition assignment (27,536
KUs), S23–25 gated synthesis, S26 final verification and delivery;
deliverable-first measurement with the failed-session rule (bookkeeping
without deliverable movement = failed session, reported as such);
anti-stall rules (synthesis must start by S23; no new process layers
without user-approved ADR; no re-performance of verified work without a
regression trigger; blocked phases are compressed via calibrated tiers,
never by skipping calibration); enumerated inviolate quality floor
(source immutability + per-session manifest checks, full suite green at
start and after last mutation, machine-verified accept/cover citations,
full probe discipline for gap decisions, delta-verification with
pre-written arithmetic, Unaccounted-blocks-release, honesty rules);
deadline–floor conflicts are escalated to the user, never resolved by
weakening either.
**Rationale:** the failure mode the user identified was structural
(endless batches, checkpoints, replays, and handoffs with synthesis
perpetually deferred), not a one-off lapse. A policy read through the
mandatory AGENTS.md startup chain is the repository's only durable
enforcement mechanism that survives session resets and sandbox
recycling. The failed-session rule and the session ledger convert
"becoming faster" from an intention into a measurable, auditable
obligation.
**Impact / migration:** no code or schema changes; checkpoints gain a
documented free-form `accelerated_mode` JSON block (session 17's
checkpoint is the exemplar). Existing ADR-0011 tiering rules are
incorporated by reference, not duplicated. 663/663 tests green before
and after (docs-only change). The 46,978 low-signal documented exclusion
and the three confirmed gaps (second moment, bradley-terry, async def)
remain explicit non-claims requiring dedicated synthesis-time treatment.
**Approval evidence:** user direction 2026-11-01 ("make new policy to
ensure the next agent follow the new decision of becoming faster"),
following the same-day acceleration directive recorded in ADR-0011.
**Affected artifacts:** `docs/ACCELERATED_COMPLETION_POLICY.md` (new),
`AGENTS.md` (§12), this register, `docs/agent-handoff/next-agent.md`,
`README.md` (repository-status paragraph),
`state/checkpoints/checkpoint-2026-11-01-policy-session17.json`.

### ADR-0013 — Term-level dossier-extension record class; F-0022 repair; dossier v2 schema admission
**Status:** accepted (2026-11-01, DISC-002 session 19)
**Context:** Session 18 committed 294 term-level dossier-extension
classification records (state/classifications/009..014) as dossier-v2 input.
Three issues surfaced at session-19 startup:
(1) every one of the 7,034 evidence entries carried `lines: []` because
scripts/s18_dext_assembly.py read a non-existent KU field
(`source_lines` instead of `line_start`/`line_end`) — recorded as finding
F-0022 (would have been caught by a batch cross-check, which did not exist);
(2) the records were validated against
schemas/overlap-classification.schema.json, whose pair-level semantics
(`ku_ids` minItems 2, cross-vault requirement) do not model term-level
extension evidence — 23 records legitimately carry a single KU and
single-vault evidence is the normal case for corpus extension;
(3) dossier v2 concepts built from those records need
schemas/concept-dossier.schema.json to admit single-KU concepts and
DX-disc002-s18-… classification ids.
**Options considered:** (1) relax the overlap-classification schema to
minItems 1 / drop cross-vault (rejected: weakens the pair-level ADR-0009
contract for a record class it was never meant to model); (2) merge the 23
single-KU records into sibling records (rejected: falsifies the term-level
classification); (3) a separate schema for the new record class, a narrow
mechanical repair of the evidence metadata, and additive dossier-schema
admissions.
**Decision:** option 3.
- New `schemas/dossier-extension-classification.schema.json` (ku_ids
  minItems 1; evidence lines non-empty; same provenance fields).
- New framework validation:
  `vu validate-registry --extension-classifications F [--ku-batch B ...]`
  (registry.validate_extension_classification_file) with file-level
  cross-checks plus batch cross-checks — ku existence, lines == KU
  [line_start..line_end], source_path equality, byte-exact quote — the
  check that would have caught F-0022.
- F-0022 repair: scripts/s19_repair_ext_evidence.py regenerated the 7,034
  evidence entries from committed KU batches (full excerpt + inclusive span,
  the ext003..010 convention); classification ids, topics, ku_ids and all
  decision fields byte-unchanged; idempotent (--check verifies zero drift);
  scripts/s18_dext_assembly.py fixed to construct evidence identically so a
  future replay reproduces the repaired files.
- concept-dossier.schema.json: concept ku_ids/ku_count minimums 2 -> 1 and
  classification_ref extended with the DX-discNNN-sNN-<domain>-MMMM
  alternative (documented in the schema descriptions; all six v1 dossiers
  re-validated unchanged after the edit).
**Rationale:** separation of record classes keeps both contracts strict:
pair-level overlap classifications keep their >= 2 KU / cross-vault
semantics; term-level extension records get a schema that models what they
actually are. The repair is mechanical and reproducible; no decision content
(ku_ids, topics, verdicts) changed.
**Impact / migration:** none for existing records (009..014 ku_ids and
classification ids unchanged); 20 new tests
(tests/test_extension_classification.py) + 1 CLI test + 6 new dossier-v2
tests (tests/test_concept_dossier.py) prove the contracts; the six extension
files re-validate clean with batch cross-checks (exit 0, 294/294 records).
**Affected artifacts:** schemas/dossier-extension-classification.schema.json
(new), schemas/concept-dossier.schema.json (additive),
src/vault_unification/registry.py (validate_extension_classification_file),
src/vault_unification/cli.py (--extension-classifications, --ku-batch),
scripts/s19_repair_ext_evidence.py (new), scripts/s18_dext_assembly.py
(evidence construction fixed), state/classifications/009..014 (evidence
arrays repaired), reports/dossier-ext/s19-f0022-repair-report.json,
tests/test_extension_classification.py, tests/test_concept_dossier.py,
tests/test_cli.py, this register.

### ADR-0014 — Rule-driven disposition assignment: synthesis mapping + disposition ledger + registry overlay
**Status:** accepted (2026-11-01, DISP-001 session 19)
**Context:** The S21–22 phase target (accelerated policy §2) is to assign a
defensible disposition to every one of the 27,536 KUs (Unaccounted → 0,
release blocker). The handoff's method: "rule-driven dispositions from
classification + dossier membership + file-level synthesis mapping;
exceptions to individual review". Prerequisites finished this session:
dossier v2 (all extension participant KUs inside dossier concepts) and the
F-0022 repair of the extension classification evidence.
**Options considered:** (1) hand-review all 27,536 units individually
(violates the session budget; the accelerated mode exists precisely to
avoid this); (2) bulk-write dispositions into the KU batch files (mutates
the canonical extraction store and invalidates dossier provenance hashes);
(3) a committed file-level synthesis mapping (canonical structure + note
plan) feeding a deterministic rule engine whose output is a committed,
append-only disposition LEDGER, applied to the derived registry as an
effective-state overlay (the ADR-0007/0009 pattern).
**Decision:** option 3, with these components and rules:
- **Canonical structure v1** (state/synthesis/canonical-structure-v1.json):
  a 20-area unified backbone designed by the orchestrator from both vaults'
  taxonomies as a learning progression, with 544 planned canonical notes.
- **File-level synthesis mapping v1** (state/synthesis/file-mapping-v1.jsonl):
  all 609 source files mapped to planned canonical notes by 13 bounded
  subagents (one to three areas each; same-topic files from both vaults map
  to the same note) plus one orchestrator-reviewed context group; every
  output mechanically verified (completeness against the 609-file inventory,
  path format, notes/records cross-consistency, cross-group uniqueness) by
  scripts/s19_verify_mapping.py, and integration arithmetic asserted by
  scripts/s19_integrate_mapping.py.
- **Rule engine** (`vu assign-dispositions`, src/vault_unification/dispositions.py):
  DISP-R1 dossier concept member → Consolidated (source_refs carry the
  concept ids so synthesis pulls the full concept evidence); DISP-R2 file
  feeds a note alongside other files → Consolidated; DISP-R3 sole-feeder
  file → Preserved; DISP-R4 archival context area (the individually
  reviewed source-vault construction documents) → Contextualized; DISP-X a
  three-entry individually reviewed exception table (the Qs4 planning stub
  → Contextualized; the two F-0014 marker headings → Superseded with the
  marker text preserved verbatim in the registry record).
- **Ledger + overlay** (`state/dispositions/001-disp001-rule-driven.jsonl` +
  `vu kureg-apply-dispositions`): the committed JSONL is the append-only
  decision record; the derived registry materializes the EFFECTIVE
  disposition (idempotent full-apply; revisions allowed because
  dispositions legitimately get refined at synthesis — the append-only
  discipline lives in the committed ledger files, not the derived DB).
**Rationale / safety argument (why this cannot lose knowledge):** every KU
keeps its immutable source locator in the committed batches regardless of
disposition; the ledger regenerates byte-identically from committed inputs
(sha256-stable double run recorded); Superseded is never bulk-assigned
because invariant 3 (unique information preserved elsewhere) requires
per-unit evidence — a semantic judgment reserved for synthesis-time review;
dispositions are planning statements with recorded destinations whose
semantic verification happens at the synthesis gates (M6/M7 batch gates,
omission audits), not at assignment time; the mapping covers all 609 files
exactly once (machine-verified) so no KU can lack a destination.
**Impact:** metric 2 moved 0 → 27,536/27,536 (Unaccounted = 0 in the
rebuilt registry: Preserved 18,478 / Consolidated 8,106 / Contextualized
950 / Superseded 2); F-0023 (NULL-heading destination duplication) found
and fixed in the shared destination loader; 17 new tests
(tests/test_dispositions.py) + 20 (test_extension_classification.py) + 7
new dossier-v2 tests.
**Open questions carried to synthesis (explicit non-claims):** the final
PRESENTATION of area 20 (archival context layer) is a release-audit
decision — ordinary notes never narrate merges; note titles/folders may be
refined at synthesis start under EDITORIAL_STYLE_GUIDE change control with
a versioned migration of the mapping; Needs review = 0 today, but
synthesis-time semantic review may legitimately reclassify individual units
(via new ledger files, never edits).
**Affected artifacts:** state/synthesis/canonical-structure-v1.json,
state/synthesis/file-mapping-v1.jsonl,
state/dispositions/001-disp001-rule-driven.jsonl,
src/vault_unification/dispositions.py, src/vault_unification/kuregistry.py
(apply_dispositions, _upsert_destination, F-0023 fix),
src/vault_unification/cli.py (assign-dispositions,
kureg-apply-dispositions), scripts/s19_area_filelists.py,
scripts/s19_verify_mapping.py, scripts/s19_integrate_mapping.py,
reports/dispositions/*, tests/test_dispositions.py, this register.
