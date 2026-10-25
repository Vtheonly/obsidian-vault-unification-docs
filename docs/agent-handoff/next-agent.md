# Next Agent Handoff

## Project state

- Current milestone: Milestone 3 (extraction). Framework bootstrap is DONE
  and verified (BOOT-000..004; omission-detection hard gate PASSED at
  BOOT-004). EXT-001 (first real extraction) is DONE and verified.
- Current task ID: EXT-002 (status: ready)
- Current Git commit: the EXT-001 state commit on `main` (after the EXT-001
  work commit); verify with `git log --oneline -5`
- Working tree status: clean after commit/push (verify with `git status`)
- Registry/checkpoint version: task-queue v3 (BOOT-000..004 + EXT-001
  completed with tests_run evidence; EXT-002 ready); KU schema v1.1
  (ADR-0008); checkpoint
  `state/checkpoints/checkpoint-2026-10-26-ext-001.json`
- Framework version: 0.4.0 (CAP-016 added); 338/338 tests; capabilities:
  15 implemented-and-tested, 2 planned (CAP-013, CAP-014)

## Verified completed work

- EXT-001 (2026-10-26), deterministic KU extraction, first real batch:
  - New capability CAP-016 `vu extract-kus` (module
    `src/vault_unification/kuextract.py`): deterministic structural
    segmentation of source notes into schema-v1.1 KU records with stable
    content-derived IDs (via CAP-011 `mint_ku_id`), immutable locators
    (source id/path/hash, heading path, line range, excerpt, excerpt hash)
    and exact byte-excerpts. Construct detection delegates to CAP-003 via a
    new `mdextract.extract_structure_text` entry point (one authority).
  - Line-accounting invariant: every line of every file lands in exactly
    one bucket (unit span / heading context / excluded blank / excluded
    horizontal rule); violations fail the run. The invariant caught a real
    double-count bug during development (frontmatter span) — it is load-bearing.
  - First real batch
    `state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl`:
    scope `AI Course/03 - Machine Learning/03.1 - Regression` — 6/6 files
    extracted (0 excluded, 0 failed), 298 records (prose 149, list 62,
    math_block 50, code_block 23, callout 10, table 3, quote 1), all
    disposition `Unaccounted` (extractor claims no semantics), batch
    schema-valid, double-run byte-identical
    (sha256 b3ffdf972203cbe804a69e1e3fc8b2f9f1118a8d6c713d79f799ae419831af4a).
  - Independent review (EXT-001-REVIEW subagent, read-only): verdict PASS —
    10/10 sampled rare details found with KU-id evidence (incl. the 1/2m
    trick callout, simultaneous-update theta example, odds examples, OLS
    O(m^3) caveat, taxi-fare analogy, French random_state=42 and softmax
    explanations, NaN learning-rate warning); 100/100 headings covered; no
    span crosses a heading; no overlaps/type misclassifications; French
    diacritics + oe ligature intact, no mojibake.
  - SCOPE-COUNT CORRECTION (F-0005): the previous handoff said "7 files";
    the actual scope holds 6 (numbering skips 06). Denominators always come
    from manifests, never from handoff prose.
- Evidence: `reports/extraction/ext001-coverage.json` (per-file outcomes +
  line accounting), `ext001-pytest-report.json` (338/338),
  `ext001-capabilities.json` (15+2), `ext001-kureg-{init,load,validate}.json`
  (298 inserted, 0 errors/warnings), `ext001-immutable-{before,after}-
  {master-ai,ai-course}.json` (all unchanged).

## Tests actually run

| Command/test | Result | Evidence/report | Limitations |
|---|---|---|---|
| `python3 -m pytest tests -q` | exit 0; 338/338 | reports/extraction/ext001-pytest-report.json | — |
| `vu capabilities --verify` | exit 0; 15 implemented-and-tested incl. CAP-016, 2 planned | reports/extraction/ext001-capabilities.json | runs only referenced test files (323 tests) |
| `vu extract-kus` (real scope) | exit 0; 6/6 files, 298 records, batch valid | reports/extraction/ext001-coverage.json | structural extraction only |
| determinism: second run + `cmp` | exit 0; byte-identical | session tests_run record | — |
| `vu kureg-init --force` + `kureg-load` | exit 0; 298/298 inserted, 0 errors | reports/extraction/ext001-kureg-load.json | — |
| `vu kureg-validate` | exit 0; valid, 0 errors, 0 warnings, unaccounted 298 (expected) | reports/extraction/ext001-kureg-validate.json | — |
| `vu verify-manifest` both vaults, before + after | exit 0 x4; unchanged | reports/extraction/ext001-immutable-*.json | — |
| `vu validate-registry --tasks state/task-queue.jsonl` | exit 0; 7 records valid | terminal (rerun to verify) | schema + cross-checks only |
| excerpt fidelity ad-hoc check | 298/298 byte-exact, 298/298 unique IDs | session tests_run record | — |

## Findings and unresolved work

- Open findings: F-0001 (trailing-space dir `source-vaults/AI ` — always
  quote), F-0002 (14 AI Course unclosed-fence files — extractor handles
  them: content preserved + warning + `--unclosed-fence-finding` linkage;
  none of the 6 EXT-001 files are affected), F-0003 (175 broken wikilinks +
  10 missing anchors in AI Course — synthesis-time dispositions),
  F-0005 (resolved: handoff scope-count discrepancy 7 vs 6; manifest is the
  denominator authority).
- Blockers: none for EXT-002.
- Known gaps (deliberate non-claims): only 6 of 609 source files extracted
  (1.0%); no dispositions/overlap/concepts/destinations exist anywhere yet;
  no synthesis output exists; Master AI has never been link-checked;
  CAP-013 (duplicate discovery) and CAP-014 (coverage/frequency regression)
  are still planned — build CAP-013 when cross-vault overlap classification
  begins in earnest.

## Decisions and configuration

- CAP-016 design: extraction is STRUCTURAL. Controlled unit types
  (prose/list/table/code_block/math_block/callout/quote/frontmatter/
  empty_section); disposition always `Unaccounted` at extraction;
  no overlap_type/concept_ids/destinations. Semantic classification is
  later, evidence-based work (prevents metric laundering per
  TOOLING_FRAMEWORK.md principle 10).
- Pinned vault-ids: `ai-course` and `master-ai` (changing them would mint
  different source ids and KU ids — treat as explicit reconciliation,
  never an accident). Recorded in docs/FRAMEWORK_SETUP.md.
- `verification_status` wording inside records is part of the stable
  fingerprint (idempotent re-loads); keep it version-free — versions live
  in reports.
- Batch naming convention (state/knowledge-units/README.md):
  `<sequence>-<task-id>-<scope>.jsonl`.

## Next task

- Task ID and title: EXT-002 — Extract the paired Master AI regression
  domain batch (cross-vault evidence for overlap classification)
- Why it is next: the AI Course side of the linear/logistic regression
  domain is extracted; overlap classification and concept dossiers need the
  Master AI side. Term search shows the primary paired source is
  `Master AI/03 - Machine Learning/Supervised Learning/02 - Linear and
  Logistic Regression.md` (167 lines, 25 headings; 27 "regression" + 13
  "logistic regression" matches — the highest in that vault).
- Exact inputs: read-only `source-vaults/AI /Master AI` (quoted);
  `state/manifests/master-ai.jsonl`; CAP-016 `vu extract-kus` with
  `--vault-id master-ai`; the EXT-001 batch for reference.
- Expected outputs: batch under `state/knowledge-units/` (suggest
  `002-ext002-master-ai-linear-logistic-regression.jsonl`) for that file
  (or the whole `03 - Machine Learning/Supervised Learning` folder: 2
  files, 334 lines); coverage report; registry rebuild + kureg-validate;
  determinism check; verify-manifest before/after.
- Acceptance criteria: every scope file has a verified outcome or explicit
  failure/exclusion; batch validates + loads (0 anomalies); sources
  unchanged; double run byte-identical; no semantic claims.
- Suggested follow-up (EXT-003+, decide next session with evidence):
  cross-vault overlap classification for the regression domain
  (evidence-based, likely wants CAP-013 duplicate/near-duplicate candidate
  discovery built first — see TOOLING_FRAMEWORK.md section 9 loop).

## Resume procedure

1. `git clone` / `git pull`; `git status` must be clean; confirm HEAD
   includes the EXT-001 commits.
2. Read `AGENTS.md`, this file, `state/current-state.json`,
   `state/task-queue.jsonl`, `state/findings.jsonl`.
3. Sanity-verify the framework: `PYTHONPATH=src python3 -m vault_unification
   selftest` (exit 0) and `PYTHONPATH=src python3 -m pytest tests -q`
   (338/338 unless tests were legitimately added — update the count then).
4. Verify source immutability: `vu verify-manifest` on both vaults (exit 0).
5. Verify the registry rebuilds from the canonical batch:
   `vu kureg-init --db state/registries/kuregistry.db --force` then
   `vu kureg-load --db state/registries/kuregistry.db --kus
   state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl` then
   `vu kureg-validate --db state/registries/kuregistry.db` (298 KUs,
   0 errors).
6. Execute EXT-002 per the acceptance criteria above; framework-first;
   record evidence with actual exit codes; update task queue,
   current-state, checkpoint, findings; write this handoff file; commit and
   push to main.

## Explicit non-claims

- No dispositions, overlap classifications, concept assignments or
  destinations exist for any of the 298 extracted records; all are
  `Unaccounted`.
- No semantic verification of real source content has occurred; the
  EXT-001-REVIEW subagent spot-check verified extraction fidelity
  (byte-exact excerpts, detail presence, heading coverage), not semantic
  completeness of any future synthesis.
- No synthesis output exists; `output_synthesis_started` is false.
- Only 6 of 609 source files (1.0%) have been extracted; do not extrapolate
  corpus-wide claims from this batch.
- Master AI has not been link-checked at all.
