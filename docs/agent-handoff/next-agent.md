# Next Agent Handoff

## Project state

- Current milestone: Milestone 3 (extraction). Framework bootstrap DONE and
  verified (BOOT-000..004; omission-detection hard gate PASSED). EXT-001
  (first real batch, AI Course regression) DONE and verified. EXT-002
  (paired Master AI batch) DONE and verified.
- Current task ID: EXT-003 (status: ready)
- Current Git commit: the EXT-002 state commit on `main` (after the EXT-002
  work commit); verify with `git log --oneline -5`
- Working tree status: clean after commit/push (verify with `git status`)
- Registry/checkpoint version: task-queue v4 (BOOT-000..004 + EXT-001 +
  EXT-002 completed with tests_run evidence; EXT-003 ready); KU schema v1.1
  (ADR-0008); checkpoint
  `state/checkpoints/checkpoint-2026-10-26-ext-002.json`
- Framework version: 0.4.0 (unchanged in EXT-002 — existing CAP-016
  consumed); 338/338 tests; capabilities: 15 implemented-and-tested,
  2 planned (CAP-013, CAP-014)

## Verified completed work

- EXT-002 (2026-10-26), paired Master AI extraction:
  - Scope decision: the whole `03 - Machine Learning/Supervised Learning`
    folder (2 files, 334 lines) — the EXT-002 task record's optional wider
    scope, chosen so both files receive verified outcomes now and no
    half-extracted folder is left behind. The regression pairing file is
    `02 - Linear and Logistic Regression.md` (35 KUs);
    `03 - Decision Trees and Gradient Boosting.md` (30 KUs) pairs with AI
    Course `03.7 - Tree-Based Models` in a later batch.
  - Batch `state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl`:
    2/2 files extracted (0 excluded, 0 failed), 65 records (prose 31,
    list 16, math_block 10, code_block 3, frontmatter 2, callout 2,
    table 1), all disposition `Unaccounted`, schema-valid, double-run
    byte-identical (sha256
    e0ef12187b3792dbdc9e2868a31ff7a77f57eb4809fc3ad09aab6663d5871118).
    Line accounting consistent for both files (167/167 each:
    93+22+52 and 105+18+44).
  - Fidelity: `scripts/ext002_fidelity.py` → 65/65 byte-exact excerpts,
    65/65 valid excerpt hashes, 65 unique IDs, source hashes agree with the
    baseline manifest, no unit span crosses a real heading. IMPORTANT
    method note: heading detection MUST use
    `vault_unification.mdextract.extract_structure_text` — a naive `#`
    matcher false-positives on Python comments inside code fences (hit
    during EXT-002, fixed).
  - Registry rebuilt with both batches: 363 KUs (298 + 65), 0 load errors,
    `kureg-validate` valid, 0 warnings, 363 `Unaccounted` (expected).
  - Independent review (EXT-002-REVIEW subagent, read-only): verdict PASS —
    32/32 rare details with KU-id evidence (16 per file, incl. ridge
    closed form + "no singularity" + MAP-Gaussian, lasso/Laplace prior,
    batch BCE, softmax formula, O(d^3) remark, sklearn `# C = 1/lambda`
    two-space comment, calibration/temperature scaling, ESL ch3/4 + Murphy
    ch10–11 citations, RF averaging formula, "SOTA in 2026", XGBoost
    2014 second-order gradients, `scale_pos_weight`, ASCII tree diagram
    exact spacing); 40/40 headings (22 + 18, counted via mdextract); 0
    boundary anomalies (0 span overlaps, 0 heading crossings, 0 type
    misclassifications); 65/65 structurally pure; in-memory re-run of
    `kuextract.segment_note` reproduces the batch exactly. Orchestrator
    spot-checked sampled evidence (4/4 KU-ids real; softmax pair:
    master-ai formula KU-74814e20d567d124 vs ai-course
    `activation='softmax'` usage KU-d758cb4d3ebb7e4d).
  - Cross-vault observation (evidence for EXT-003, NOT a classification):
    7 topic pairs with one KU-id per side — MSE, normal equations, gradient
    descent, logistic sigmoid, binary cross-entropy, softmax, sklearn
    usage. Master-AI-only so far: ridge/L2, lasso/L1, MAP/prior
    interpretations, calibration/temperature scaling, O(d^3) caveat (the
    AI Course regression batch has zero genuine regularization content).
- Evidence: `reports/extraction/ext002-*` (coverage, determinism, fidelity,
  immutable before/after ×2 vaults, kureg init/load-batch1/load-batch2/
  validate, pytest 338/338, capabilities 15+2, review, taskqueue-validate).

## Tests actually run

| Command/test | Result | Evidence/report | Limitations |
|---|---|---|---|
| `python3 -m pytest tests -q` (startup + final) | exit 0; 338/338 | reports/extraction/ext002-pytest-report.json | no framework changes made in EXT-002 |
| `vu capabilities --verify` | exit 0; 15 implemented-and-tested, 2 planned | reports/extraction/ext002-capabilities.json | runs only referenced test files |
| `vu extract-kus` (Master AI scope) | exit 0; 2/2 files, 65 records, batch valid | reports/extraction/ext002-coverage.json | structural extraction only |
| determinism: second run + `cmp` | exit 0; byte-identical | reports/extraction/ext002-determinism.json | — |
| `vu kureg-init --force` + `kureg-load` ×2 batches | exit 0; 363/363 inserted, 0 errors | reports/extraction/ext002-kureg-*.json | — |
| `vu kureg-validate` | exit 0; valid, 0 errors/warnings, 363 Unaccounted (expected) | reports/extraction/ext002-kureg-validate.json | — |
| `vu verify-manifest` both vaults, before + after | exit 0 ×4; unchanged | reports/extraction/ext002-immutable-*.json | — |
| `python3 scripts/ext002_fidelity.py` | exit 0; 65/65 byte-exact, unique IDs, manifest-hash agreement | reports/extraction/ext002-fidelity.json | — |
| `vu validate-registry --tasks state/task-queue.jsonl` | exit 0; 8 records valid (after fixing a draft `work_commit` → schema field `commit`) | reports/extraction/ext002-taskqueue-validate.json | schema + cross-checks only |
| EXT-002-REVIEW independent subagent review | PASS | reports/extraction/ext002-review.md | read-only review; spot-checks, not exhaustive semantic verification |

## Findings and unresolved work

- Open findings: F-0001 (trailing-space dir `source-vaults/AI ` — always
  quote), F-0002 (14 AI Course unclosed-fence files — extractor handles
  them; none of the 8 extracted files affected), F-0003 (175 broken
  wikilinks + 10 missing anchors in AI Course — synthesis-time
  dispositions), F-0006 (NEW, open: naive substring term matching
  false-positives — 'bridge' matches 'ridge', mermaid `L1[`/`L2[` node
  labels match L1/L2; CAP-013 and any term tooling MUST use word-boundary
  matching + excerpt-level confirmation).
- Resolved: F-0004, F-0005.
- Blockers: none for EXT-003.
- Known gaps (deliberate non-claims): only 8 of 609 source files extracted
  (1.3%); no dispositions/overlap/concepts/destinations exist anywhere yet;
  no synthesis output exists; Master AI has never been link-checked;
  CAP-013 and CAP-014 still planned.

## Decisions and configuration

- EXT-002 scope: whole `Supervised Learning` folder (task record's optional
  wider scope) — both files get outcomes now; the tree-based file waits for
  its AI Course 03.7 counterpart before overlap classification.
- Pinned vault-ids: `ai-course` and `master-ai` (unchanged; changing them
  would mint different source ids and KU ids).
- Heading/construct detection authority: `mdextract.extract_structure_text`
  (CAP-003) — never naive `#` regex (Python comments inside fences).
- Task-queue schema note: the work-commit hash field is `commit` (not
  `work_commit`); validate-registry enforces this.
- Batch naming convention (state/knowledge-units/README.md):
  `<sequence>-<task-id>-<scope>.jsonl`.

## Next task

- Task ID and title: EXT-003 — Build CAP-013 cross-vault candidate
  discovery and classify overlap for the regression domain
  (evidence-based)
- Why it is next: both sides of the linear/logistic regression domain are
  now extracted (298 AI Course KUs + 35 Master AI regression KUs) and the
  EXT-002-REVIEW Check 5 provides 7 evidenced topic-pair hypotheses.
  Overlap classification is the next workflow state (RegistryValidation →
  ConceptDiscovery/overlap) and it needs a tested, word-boundary-safe
  candidate-discovery tool first (F-0006; TOOLING_FRAMEWORK.md section 9
  loop).
- Exact inputs: batches 001 and 002 (paths above);
  `reports/extraction/ext002-review.md` Check 5 (hypotheses, NOT
  classifications); F-0006; `schemas/knowledge-unit.schema.json` v1.1
  (overlap_type + superseded_rationale); docs/KNOWLEDGE_AND_PROVENANCE.md
  section 7 (overlap_type is separate from disposition — never collapse
  them).
- Expected outputs: new capability CAP-013 (module + CLI + tests + docs:
  word-boundary term/alias matching across vaults, candidate pair lists
  with match positions and excerpt references, machine-readable reports;
  regression tests for the F-0006 false-positive cases); then
  evidence-based overlap_type assignments for the regression-domain pairs
  recorded as new classification records / registry updates (append-only —
  never edit committed batches), with rationale per assignment.
- Acceptance criteria: CAP-013 tested incl. F-0006 cases ('bridge' must
  not match 'ridge'; mermaid `L1[`/`L2[` must not match L1/L2 without
  excerpt confirmation); every candidate pair carries evidence; no
  dispositions/overlap without recorded rationale; batches unedited;
  full suite + registry cross-checks pass; sources unchanged.
- Suggested follow-up (EXT-004+, decide with evidence): continue
  domain-paired extraction (e.g. AI Course 03.7 Tree-Based Models to pair
  with the already-extracted decision-trees file), or concept dossier
  scaffolding for the regression domain once overlap is classified.

## Resume procedure

1. `git clone` / `git pull`; `git status` must be clean; confirm HEAD
   includes the EXT-002 commits (work + state).
2. Read `AGENTS.md`, this file, `state/current-state.json`,
   `state/task-queue.jsonl`, `state/findings.jsonl`.
3. Sanity-verify the framework: `PYTHONPATH=src python3 -m vault_unification
   selftest` (exit 0) and `PYTHONPATH=src python3 -m pytest tests -q`
   (338/338 unless tests were legitimately added — update the count then).
4. Verify source immutability: `vu verify-manifest` on both vaults (exit 0).
5. Verify the registry rebuilds from the canonical batches:
   `vu kureg-init --db state/registries/kuregistry.db --force` then
   `vu kureg-load` batch 001 then batch 002 then
   `vu kureg-validate --db state/registries/kuregistry.db` (363 KUs,
   0 errors).
6. Execute EXT-003 per the acceptance criteria above; framework-first
   (build CAP-013 before any manual classification work); record evidence
   with actual exit codes; update task queue, current-state, checkpoint,
   findings; write this handoff file; commit and push to main.

## Explicit non-claims

- No dispositions, overlap classifications, concept assignments or
  destinations exist for any of the 363 extracted records; all are
  `Unaccounted`.
- The 7 cross-vault topic pairs in `reports/extraction/ext002-review.md`
  are observational hypotheses with KU-id evidence, not overlap
  classifications.
- No semantic verification of real source content has occurred; both
  review subagents verified extraction fidelity (byte-exact excerpts,
  detail presence, heading coverage), not semantic completeness of any
  future synthesis.
- No synthesis output exists; `output_synthesis_started` is false.
- Only 8 of 609 source files (1.3%) have been extracted; do not
  extrapolate corpus-wide claims from these batches.
- Master AI has not been link-checked at all.
