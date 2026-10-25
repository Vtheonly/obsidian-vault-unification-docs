# Next Agent Handoff

## Project state

- Current milestone: Milestone 0 (DONE: BOOT-001 source location, BOOT-002
  inventory) + Milestone 1 operating foundation (DONE: BOOT-000 framework,
  BOOT-003 KU registry) + Milestone 2 verification prototype (DONE: BOOT-004
  omission-detection pilot PASSED — the hard gate).
- Current task ID: EXT-001 (status: ready)
- Current Git commit: the BOOT-004 work commit on `main` (after the BOOT-003
  state commit `7d0088b`); verify with `git log --oneline -5`
- Working tree status: clean after commit/push (verify with `git status`)
- Registry/checkpoint version: task-queue v2 (BOOT-000..004 completed with
  tests_run evidence; EXT-001 ready); KU schema v1.1 (ADR-0008); checkpoint
  `state/checkpoints/checkpoint-2026-10-26-boot-004.json`

## Verified completed work

- BOOT-004 (2026-10-26), framework-first, hard gate PASSED:
  - New capability CAP-012 (omission-detection pilot + reusable output
    auditor): module `src/vault_unification/omission.py`; CLI
    `vu omission-pilot` and `vu audit-output`; framework version 0.3.0.
  - Synthetic paired-source fixture (deterministic, in an explicit temp
    dest, never inside `source-vaults/`): vault-a (deep notes: chain-rule
    theory, 4-step equation derivation, 2022 warehouse-forecast project
    caveat, Linnainmaa rare fact, PyTorch 1.x-vs-2.0 version distinction,
    reference code, wikilinks) + vault-b (course notes: semantic-duplicate
    overview with a conflicting Parker-1985 attribution, exact-duplicate
    equation, partial-overlap update rule, complementary numerical-gradient
    code, further-reading link) + known-good baseline synthesis (4 notes,
    consistent numbering, prose everywhere, all links resolve) + 11 KU
    records with `mint_ku_id` stable IDs, dispositions/overlap types and
    destinations + accepted manifest.
  - 12 planted defects (one per mutated copy of the baseline): unique-detail
    omission, equation omission, derivation-step omission, caveat omission,
    equation sign alteration, obscure one-file concept removal, wikilink
    break, heading-convention change, bullet-only prose degradation,
    version-distinction loss, accepted-output drift (post-acceptance repair
    scenario), code-parameter deletion — mirroring VERIFICATION_SPECIFICATION
    "Deliberate omission tests" + section 6.
  - Pilot result (real run, recorded exit codes): verdict PASS; 12/12
    detected; 12/12 localized to the expected KU and destination note;
    0 false negatives; 0 false positives on the clean baseline; fixture
    sources byte-identical before/after.
  - `vu audit-output` reusable checks: KU-batch schema+cross-checks, output
    drift vs accepted manifest, disposition/destination accounting,
    marker retention (rare-term + equation + code fingerprints per KU),
    link integrity (CAP-004), heading-convention lint, prose-quality lint;
    findings carry KU IDs, destinations, expected/observed, repair hints.
  - Honesty guarantees: the pilot FAILS by design when an injected defect is
    undetectable (test DX99 injects an invisible paraphrase -> verdict
    fail); mutation anchors raise when not found exactly once; audit
    exceptions per defect are recorded as honest misses.
- Evidence: 285/285 tests (`reports/bootstrap/boot-004-pytest-report.json`);
  capabilities --verify: 14 implemented-and-tested incl. CAP-012, 2 planned
  (`reports/bootstrap/boot-004-capabilities.json`); pilot evidence
  (`reports/bootstrap/boot-004-omission-pilot.json` + `boot-004-run-summary.json`);
  source immutability before AND after
  (`reports/bootstrap/boot-004-immutable-{before,after}-{master-ai,ai-course}.json`).

## Tests actually run

| Command/test | Result | Evidence/report | Limitations |
|---|---|---|---|
| `python3 scripts/boot004_pilot.py` | exit 0; 5 steps all exit 0 | reports/bootstrap/boot-004-run-summary.json | fixture is synthetic by design |
| `vu omission-pilot --dest <temp> --report ...` | exit 0; verdict pass, 12/12, 0 FP | reports/bootstrap/boot-004-omission-pilot.json | — |
| `vu run-tests --tests-dir tests` | exit 0; 285/285 passed | reports/bootstrap/boot-004-pytest-report.json | — |
| `vu capabilities --verify` | exit 0; 14 implemented-and-tested, 2 planned | reports/bootstrap/boot-004-capabilities.json | runs only referenced test files (270 tests) |
| `vu verify-manifest` both vaults, before + after | exit 0 x4; unchanged | reports/bootstrap/boot-004-immutable-*.json | — |
| `vu validate-registry --tasks state/task-queue.jsonl` | exit 0; 6 records valid | terminal (rerun to verify) | schema + cross-checks only |
| `vu selftest` (resume verification) | exit 0 | terminal | — |

## Findings and unresolved work

- Open finding IDs: F-0001 (trailing-space dir `source-vaults/AI ` — always
  quote; never rename), F-0002 (14 AI Course unclosed-fence files — extraction
  must record content with parse warning, never silently drop), F-0003 (175
  broken wikilinks + 10 missing anchors in AI Course — synthesis-time
  dispositions needed), F-0004 (README/status wording — see findings.jsonl).
- Blockers: none for EXT-001.
- Unverified claims: none made; capability statuses are test-backed.
- Known gaps (deliberate non-claims): the canonical KU store holds 0 records
  (no real extraction yet); no synthesis output exists; Master AI has never
  been link-checked; the pilot verified the auditor on SYNTHETIC data —
  corpus-scale marker noise must be re-measured on real batches (feeds
  CAP-014).

## Decisions and configuration

- CAP-012 auditor design: deterministic evidence classes only (term/math/code
  fingerprints, structure, links, manifest hashes); semantic verification
  stays a separate human/AI evidence class. Limitations are machine-emitted
  into every audit/pilot report and the capability inventory.
- Pilot pass criteria (all required): 100% detection, 100% localization to
  expected KU + note, zero false positives on the clean baseline, fixture
  sources unchanged. An audit exception counts as an honest miss.
- Defect D11 (accepted-output drift) is audited WITH the accepted manifest
  (post-acceptance regression scenario); the other eleven are audited
  WITHOUT it (pre-acceptance synthesis state) so detection cannot lean on
  the manifest alone.
- Framework version 0.3.0; capability roadmap after BOOT-004: CAP-013
  (duplicate discovery) and CAP-014 (source-to-output coverage/frequency
  regression) remain planned — both become relevant during EXT/synthesis.

## Next task

- Task ID and title: EXT-001 — Build the deterministic KU extraction pipeline
  and extract the first bounded real batch
- Why it is next: BOOT-004 hard gate passed, so Milestone 3 (complete
  inventory and extraction) begins; extraction is the first real work on
  source content and everything downstream (dossiers, synthesis, coverage
  reports CAP-014) depends on it.
- Exact inputs: read-only source vaults (quoted paths, see current-state);
  `state/manifests/*.jsonl` baselines; `schemas/knowledge-unit.schema.json`
  v1.1; CAP-003 `mdextract`; CAP-011 `kuregistry.mint_ku_id`/`kureg-load`;
  docs/KNOWLEDGE_AND_PROVENANCE.md; docs/EDITORIAL_STYLE_GUIDE.md.
- Expected outputs: new framework capability (e.g. CAP-016 `vu extract-kus`)
  that segments source notes into schema-valid KU records with stable IDs,
  locators and excerpts; first real batch under `state/knowledge-units/`
  for ONE bounded domain (suggested: AI Course `03 - Machine
  Learning/03.1 - Regression`, 7 files); extraction coverage report with
  explicit denominators and exclusions; registry rebuild + `kureg-validate`
  accounting evidence; unit/integration/CLI tests.
- Acceptance criteria (from task queue): every file in scope has a verified
  extraction outcome or explicit failure/exclusion disposition; batches
  validate and load; sources unchanged before/after (`vu verify-manifest`);
  malformed-input tests include the F-0002 unclosed-fence case; the extractor
  claims no semantic dispositions (units + locators only; overlap/disposition
  classification is later, evidence-based work).
- Forbidden side effects: do not modify source vaults; do not claim semantic
  preservation from extraction counts; do not skip short/obscure/duplicated
  files.

## Resume procedure

1. `git clone` / `git pull`; `git status` must be clean; confirm HEAD
   includes the BOOT-004 commit.
2. Read `AGENTS.md`, this file, `state/current-state.json`,
   `state/task-queue.jsonl`, `state/findings.jsonl`.
3. Sanity-verify the framework: `PYTHONPATH=src python3 -m vault_unification
   selftest` (exit 0) and `PYTHONPATH=src python3 -m pytest tests -q`
   (285/285 unless tests were legitimately added — update the count then).
4. Verify source immutability: `vu verify-manifest` on both vaults (exit 0).
5. Re-verify the hard gate if desired:
   `python3 scripts/boot004_pilot.py` must exit 0 (deterministic).
6. Execute EXT-001 per the acceptance criteria above; framework-first (the
   extractor is a reusable, tested capability, not a one-off script); record
   evidence with actual exit codes; update task queue, current-state,
   checkpoint, findings; write this handoff file; commit and push to main.

## Explicit non-claims

- No knowledge units have been extracted from the real vaults; the canonical
  store `state/knowledge-units/` holds 0 records.
- No semantic verification of real source content has occurred; BOOT-004
  verified the auditor machinery on synthetic data.
- No synthesis output exists; `output_synthesis_started` is false.
- Pilot metrics (12/12, 0 FP, 0 FN) apply to the declared synthetic fixture
  only; corpus-scale behavior is unmeasured until EXT-001+ produces real
  batches.
- Master AI has not yet been link-checked at all.
