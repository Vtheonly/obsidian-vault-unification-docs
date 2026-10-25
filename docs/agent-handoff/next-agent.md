# Next Agent Handoff

## Project state

- Current milestone: Milestone 0 — repository and source discovery (DONE:
  BOOT-001) + file inventory (DONE: BOOT-002) + registry formalization (DONE:
  BOOT-003); next: BOOT-004 omission-detection pilot (Milestone 1 gate).
- Current task ID: BOOT-004 (status: ready)
- Current Git commit: the BOOT-003 work commit on `main` (after the BOOT-002
  commit `6169cfe`); verify with `git log --oneline -5`
- Working tree status: clean after commit/push (verify with `git status`)
- Registry/checkpoint version: task-queue v2 (BOOT-000..003 completed with
  tests_run evidence); KU schema v1.1 (ADR-0008); checkpoint
  `state/checkpoints/checkpoint-2026-10-26-boot-003.json`

## Verified completed work

- BOOT-003 (continuation session, 2026-10-26), framework-first:
  - New capability CAP-011 (KU registry persistence): module
    `src/vault_unification/kuregistry.py`; CLI `vu kureg-init / kureg-load /
    kureg-query / kureg-validate`; hybrid design per ADR-0007 — canonical
    committed JSONL batches in `state/knowledge-units/` (0 records: no
    extraction yet) + derived rebuildable SQLite index in
    `state/registries/` (git-ignored).
  - Load semantics: schema validation (v1.1) before insert; shared
    cross-record rules (`registry.check_ku_records`: duplicate IDs,
    self-parents, self-supports, Superseded rationale, parent/support
    references against batch ∪ database); atomic single-transaction inserts
    with deferred FKs; idempotent identical re-loads; conflicting IDs
    rejected; failed batches leave the DB unchanged.
  - Stable IDs: `mint_ku_id` derives IDs from source id + file hash + heading
    path + line range + excerpt hash (explicit excerpt_hash authoritative
    over excerpt text); locator-less records are rejected explicitly.
  - Schema v1.1 per ADR-0008: `overlap_type` (separate from disposition)
    and `superseded_rationale` (required when disposition is Superseded —
    enforced by cross-checks in both `validate-registry --kus` and
    `kureg-load`).
  - `kureg-validate`: referential integrity, enum violations, corrupt JSON,
    accounting counts by disposition with denominators, unaccounted /
    needs-review counts, needs-review-without-finding as warning.
  - Path safety: `kureg-init`/`kureg-load` refuse databases under protected
    roots (default `<repo>/source-vaults/` when present; `--protected-root`
    repeatable); reports pass through `ensure_dest_safe`.
  - Evidence: 248/248 tests
    (`reports/bootstrap/boot-003-pytest-report.json`); capabilities --verify:
    13 implemented-and-tested incl. CAP-011, 3 planned
    (`reports/bootstrap/boot-003-capabilities.json`); 9-step lifecycle demo
    with double-rebuild reproducibility
    (`reports/bootstrap/boot-003-kureg-demo.json`); post-op immutability
    both vaults 0 added/removed/changed.

## Tests actually run

| Command/test | Result | Evidence/report | Limitations |
|---|---|---|---|
| `vu run-tests --tests-dir tests` | exit 0; 248/248 passed | reports/bootstrap/boot-003-pytest-report.json | — |
| `vu capabilities --verify` | exit 0; 13 implemented-and-tested, 3 planned | reports/bootstrap/boot-003-capabilities.json | runs only referenced test files (233 tests) |
| `python3 scripts/boot003_demo.py` | exit 0; expected exit pattern + byte-identical double rebuild | reports/bootstrap/boot-003-kureg-demo.json | synthetic records only |
| `vu verify-manifest` both vaults (post-ops) | exit 0; unchanged | reports/bootstrap/boot-003-immutable-{master-ai,ai-course}.json | — |
| `vu validate-registry --tasks state/task-queue.jsonl` | exit 0; valid | reports/bootstrap/boot-003-queue-valid.json | schema + cross-checks only |
| `vu selftest` (resume verification) | exit 0 | terminal | — |

## Findings and unresolved work

- Open finding IDs: F-0001 (trailing-space dir `source-vaults/AI ` — always
  quote; never rename), F-0002 (14 AI Course unclosed-fence files —
  extraction must record content with parse warning, never silently drop),
  F-0003 (175 broken wikilinks + 10 missing anchors in AI Course —
  synthesis-time dispositions needed).
- Blockers: none for BOOT-004.
- Unverified claims: none made; capability statuses are test-backed.
- Known gaps (not findings, deliberate non-claims): Master AI has never been
  link-checked (only AI Course was, in BOOT-000); no KU extraction has
  started; the canonical KU store is empty by design.

## Decisions and configuration

- ADR-0007 (canonical JSONL store + derived SQLite index; all writes through
  kureg-load; rebuild not repair) and ADR-0008 (KU schema v1.1:
  overlap_type + superseded_rationale via cross-checks) — see
  docs/RISKS_AND_DECISIONS.md.
- Framework version 0.2.0; capability IDs: CAP-011 now code-backed; planned
  IDs CAP-012 (omission pilot), CAP-013 (duplicates), CAP-014 (coverage /
  frequency regression) unchanged.
- Registry conventions documented in `state/knowledge-units/README.md`
  (batch naming `<sequence>-<task-id>.jsonl`, append-only).

## Next task

- Task ID and title: BOOT-004 — Build omission-detection pilot and verify
  the auditor
- Why it is next: all dependencies complete (BOOT-002, BOOT-003); it is the
  hard gate before any large-scale synthesis (AGENTS.md section 7.5,
  TOOLING_FRAMEWORK.md sections 7 and 9).
- Exact inputs: synthetic paired notes with exact/semantic duplicates,
  partial overlap, complementary theory/code, conflicting versions, rare
  facts, equations + intermediate derivation steps, project caveats, code
  blocks, internal links; a clean baseline + manifest of planted defects;
  the registry (state/registries/ + state/knowledge-units/) for
  source-unit IDs; docs/VERIFICATION_SPECIFICATION.md;
  docs/TOOLING_FRAMEWORK.md sections 7 and 9 (acceptance contract).
- Expected outputs: pilot fixture generator (script, committed), mutated
  copies (temporary only), detection/localization report per injected
  defect (detected vs missed, affected KU ID + destination, false
  positives/negatives), machine-readable results in reports/, new
  capability CAP-012 wired into capabilities.py with tests.
- Acceptance criteria (from task queue): injected unique-detail, equation,
  caveat, link, and style defects are detected or limitations explicitly
  documented; findings link to stable source-unit IDs; the pilot does not
  modify original vaults (mutate only temporary copies).
- Forbidden side effects: do not modify original vaults; do not begin
  large-scale synthesis before the pilot passes.

## Resume procedure

1. `git clone` / `git pull`; `git status` must be clean; confirm HEAD
   includes the BOOT-003 commit.
2. Read `AGENTS.md`, this file, `state/current-state.json`,
   `state/task-queue.jsonl`, `state/findings.jsonl`.
3. Sanity-verify the framework: `PYTHONPATH=src python3 -m vault_unification
   selftest` (exit 0) and `PYTHONPATH=src python3 -m pytest tests -q`
   (248/248 unless tests were legitimately added — update the count then).
4. Verify source immutability: `vu verify-manifest` on both vaults (exit 0).
5. Execute BOOT-004 per the acceptance criteria above; framework-first
   (build the pilot as reusable, tested tooling — CAP-012 — not as a
   one-off script); record evidence with actual exit codes; update task
   queue, current-state, checkpoint, findings; write this handoff file;
   commit and push to main.

## Explicit non-claims

- No knowledge units have been extracted, classified, or dispositioned; the
  canonical store `state/knowledge-units/` holds 0 records.
- No semantic verification of any source content has occurred.
- The omission-detection pilot (BOOT-004) has NOT been run; large-scale
  synthesis remains blocked (hard gate).
- Word/heading/token counts are lexical facts, not semantic coverage.
- Master AI has not yet been link-checked at all.
