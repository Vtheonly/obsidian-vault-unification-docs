# Next Agent Handoff

## Project state

- Current milestone: **DISPOSITIONS COMPLETE — SYNTHESIS NEXT**. Session 19
  (2026-11-01) executed the S21–22 phase target two sessions early: all
  **27,536/27,536 KU dispositions assigned, Unaccounted = 0**
  (Preserved 18,478 / Consolidated 8,106 / Contextualized 950 / Superseded 2;
  ADR-0014 rule engine + committed ledger + registry overlay). The remaining
  phase is GATED SYNTHESIS (SYNTH-001) — **must start by session 23; final
  vault by the END OF SESSION 26**.
- USER DIRECTIVE IN FORCE (2026-11-01): BINDING POLICY (ADR-0012): read
  `docs/ACCELERATED_COMPLETION_POLICY.md` and AGENTS.md §12 BEFORE planning.
  Budget after session 19: **7 sessions remaining** (20–26). Deliverable-first
  reporting; a bookkeeping-only session is a FAILED session; every checkpoint
  carries the `accelerated_mode` block.
- Completed and verified: BOOT-000..004, EXT-001..011, REBASE-000, AUDIT-011,
  FRAME-001, DISC-001, FRAME-002, REGEN-001, DISC-002 (ALL discovery layers:
  signal pool, dossier-extension classification, dossier v2), DISP-001
  (dispositions).
- Framework: 708/708 tests at session end (663 at start + 45 new); sources
  byte-identical 276/276 + 333/333 at start AND end.

## Session 19 summary (evidence-backed)

- Baseline verified: clean tree, HEAD == origin/main == 0c9b31e; 663/663
  tests first-run; manifests unchanged.
- **F-0022 found and repaired** (would have been caught by the new batch
  cross-check): session-18's assembly script wrote evidence `lines: []`
  (field-name bug: `source_lines` vs `line_start`/`line_end`) in ALL 7,034
  evidence entries of state/classifications/009..014. Narrow mechanical
  repair (`scripts/s19_repair_ext_evidence.py`, idempotent, decision fields
  byte-unchanged) + assembly script fixed + NEW validator
  (`vu validate-registry --extension-classifications F [--ku-batch B ...]`)
  with batch cross-checks (lines == KU span, source_path equality,
  byte-exact quote). New record-class schema
  `schemas/dossier-extension-classification.schema.json` (ADR-0013: term-level
  extension records are NOT pair-level overlap classifications; ku_ids
  minItems 1, no cross-vault requirement).
- **Dossier v2 (EXT-011)**: six `<domain>-v2.json` dossiers = original
  classification records + the 294 extension records + all 59 regen batches.
  47/69/82/67/73/120 concepts; participating KUs 923/749/561/454/1,105/1,890
  (= 514 originals + 5,168 per-domain extension participants = 5,682).
  `scripts/ext006_dossiers.py --check`: 12/12 byte-identical (v1 untouched);
  V6 acceptance block in `reports/extraction/ext006-dossier-coverage.json`.
  Concept-dossier schema admissions (single-KU concepts; DX classification
  ids) documented per ADR-0013.
- **Canonical structure + file mapping (ADR-0014)**: 20-area unified backbone
  (orchestrator design, learning progression) in
  `state/synthesis/canonical-structure-v1.json` (544 planned canonical notes);
  `state/synthesis/file-mapping-v1.jsonl` maps ALL 609 source files
  (276 ai-course + 333 master-ai) to planned notes. Produced by 13 bounded
  mapping subagents + one orchestrator-reviewed context group (area 20: the
  17 source-vault construction/meta files, individually reviewed →
  Contextualized archival layer). Mechanical verification:
  `scripts/s19_verify_mapping.py` (0 problems) +
  `scripts/s19_integrate_mapping.py` (609 asserted).
- **Disposition assignment (DISP-001, ADR-0014)**: new framework command
  `vu assign-dispositions` (rules: DISP-R1 dossier concept member →
  Consolidated w/ concept source_refs; R2 multi-feeder note → Consolidated;
  R3 sole feeder → Preserved; R4 archival context → Contextualized; X =
  3 individually reviewed exceptions incl. the two F-0014 marker units →
  Superseded). Ledger `state/dispositions/001-disp001-rule-driven.jsonl`
  (27,536 records; deterministic double-run sha256 747caab2…748c00).
  `vu kureg-apply-dispositions` applied it to the rebuilt registry
  (applied=27,536; idempotent re-apply exit 0); `vu kureg-validate`:
  valid=True, 0 errors, 0 warnings, Unaccounted=0.
- **F-0023 found and fixed**: UNIQUE(path, heading) cannot dedupe NULL
  headings → INSERT OR IGNORE created one destinations row per KU
  (28,754 rows / 544 paths / 28,210 orphan warnings). New
  `_upsert_destination` helper used by both kureg-load and
  kureg-apply-dispositions; registry rebuilt clean (544 rows, 0 orphans).
- Superseded is NEVER bulk-assigned (invariant 3 requires per-unit evidence);
  the 2 Superseded units are the individually reviewed F-0014 markers whose
  text is preserved verbatim in the registry record.

## Committed session-19 artifacts (the durable state)

- `state/dispositions/001-disp001-rule-driven.jsonl` — THE disposition
  ledger (27,536 records: ku_id, disposition, destinations, rule_id,
  rationale, source_refs, assigned_by, date).
- `state/synthesis/canonical-structure-v1.json` + 
  `state/synthesis/file-mapping-v1.jsonl` — the synthesis plan (544 notes;
  609 file mappings with per-file rationale and mapped_by).
- `state/dossiers/*-v2.json` — dossier v2 (six files).
- `schemas/dossier-extension-classification.schema.json` (new record class).
- `src/vault_unification/dispositions.py`, `registry.py`
  (validate_extension_classification_file), `kuregistry.py`
  (apply_dispositions, _upsert_destination), `cli.py`
  (assign-dispositions, kureg-apply-dispositions, --extension-classifications).
- `scripts/s19_*.py` (area file lists, mapping verifier, integrator, F-0022
  repair), fixed `scripts/s18_dext_assembly.py`, fixed
  `scripts/ext006_dossiers.py` (v1+v2).
- `tests/test_dispositions.py` (17), `tests/test_extension_classification.py`
  (20), extended `tests/test_concept_dossier.py` (15) and `tests/test_cli.py`.
- `reports/dispositions/disp001-*.json`,
  `reports/dossier-ext/s19-f0022-repair-report.json`,
  `reports/extraction/ext006-dossier-coverage.json` (v1+v2),
  `reports/framework/session19-*-pytest.json`.
- `state/checkpoints/checkpoint-2026-11-01-disp001-session19.json`;
  ADR-0013 + ADR-0014 + F-0022 + F-0023 in `docs/RISKS_AND_DECISIONS.md` /
  `state/findings.jsonl`; task queue: DISC-002 completed, EXT-011 + DISP-001
  completed, SYNTH-001 queued.

## Next task (SYNTH-001 — gated synthesis; MUST START by session 23)

1. **Read first**: AGENTS.md §12 → `docs/ACCELERATED_COMPLETION_POLICY.md`
   → ADR-0011/0013/0014 (`docs/RISKS_AND_DECISIONS.md`) → this file.
2. **Verify baseline** (policy §7): HEAD == origin/main, clean tree,
   `python3 -m pip install -e .`, full suite green (708 expected),
   manifests 276/276 + 333/333.
3. **Rebuild the derived registry** (sandbox may be fresh):
   `vu kureg-init --db state/registries/knowledge-registry.sqlite --force`
   then `vu kureg-load --db … --kus <each of the 70 batches>` then
   `vu kureg-apply-dispositions --db … --dispositions
   state/dispositions/001-disp001-rule-driven.jsonl` then
   `vu kureg-validate --db …` (expect Unaccounted=0, 0 errors, 0 warnings).
4. **Synthesize the first area end-to-end** (suggested: 04 - Machine
   Learning — 40 source files, 27 canonical notes, ~1,829 KUs) through the
   FRAME-002 pipeline: check-prompt → bounded generation (evidence = the
   v2 dossiers for the domain concepts + the note's mapped source files +
   per-KU destinations from the ledger) → lint-artifacts → assess-quality →
   quality-drift → quality-gate → repair loop. Then parallelize remaining
   areas with subagents (session-16/18/19 patterns: bounded scopes,
   mechanical verification of every citation, orchestrator sampling).
5. **Per-batch acceptance**: `vu audit-output` against the KU batches and
   the accepted manifest; destinations resolve to real notes; editorial
   consistency across batches; the three confirmed gaps (second moment,
   bradley-terry, async def) get dedicated treatments; F-0014 markers never
   copied as knowledge headings.
6. **Deadline arithmetic**: sessions 20–26 remain. Suggested: 20–24
   synthesis batches (areas in parallel), 25 cross-batch consistency + gap
   treatments, 26 final verification + delivery. Compress via parallelism,
   never by weakening the floor (§5.5 of the policy: escalate instead).

## Replay recipes (deterministic from committed state)

- Disposition ledger: `vu assign-dispositions --ku-batch <70 batches>
  --dossier <6 v2 dossiers> --file-mapping
  state/synthesis/file-mapping-v1.jsonl --out <path>` (byte-identical;
  sha256 747caab21c8c2d1923724bc33752b9e3fc9c6c4d2570ac0d996c11253d748c00).
- Dossiers v1+v2: `python3 scripts/ext006_dossiers.py --check` (12/12).
- F-0022 repair state: `python3 scripts/s19_repair_ext_evidence.py --check`
  (0 changed).
- Extension file validation: `vu validate-registry
  --extension-classifications <009..014 file> --ku-batch <70 batches>`
  (exit 0 x6).
- ADR-0010 decide chain (unchanged, SEVENTEEN rounds + index): see the
  session-18 handoff section in git history (commit 02f373d) —
  `vu discover-gaps` over all 70 batches then `vu discovery-decide` with the
  recorded timestamps, then `vu discovery-index`. Expected: 60,154 records;
  46,978 provisional / 7,893 already_covered / 5,278 rejected / 3
  confirmed_gap / 1 merged / 1 deferred.

## Standing rules (enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Machine locators for every line citation; F-0021-fixed fence_spans(struct,
  total_lines) signature; LEVEL-EXACT '^### '-style heading patterns with
  the startup guard that rejects '^#+'.
- Every completion claim needs a report path or test run as evidence.
- Update the README repository-status paragraph at session end.
- Push to main before session end; record push verification; if a push is
  rejected because a parallel session moved main: fetch, review, MERGE
  (never rebase away history), reconcile, re-verify.
- ADR-0011 discipline: bulk classes need ZERO counter-examples in the
  calibration set; confirm_gap is NEVER bulk-decided. Subagent decisions
  are verified, not trusted (mechanical completeness/citation checks +
  ~5% reject sampling + personal re-verification of flagged borderlines).
- Delta-verification discipline: write the arithmetic of expectations down
  BEFORE running.
- Fresh-sandbox setup: `python3 -m pip install -e .` BEFORE the baseline
  pytest.
- F-0016: long runs must fit one tool call (< 10 min). F-0018: old
  pre-batch-4 scripts hardcode the sandbox path. F-0020: invoke via `vu` or
  `python -m vault_unification`. F-0023: any code inserting into registry
  `destinations` MUST use `_upsert_destination` (NULL heading defeats
  UNIQUE). F-0014 (open): two ai-course files end with 'END OF FILE / File
  Name' marker headings — synthesis must not copy them as knowledge
  headings.

## Explicit non-claims

- The 46,978 low-signal provisional discovery candidates were NOT
  individually reviewed (documented exclusion under the batch-3..16
  signal-rule standard).
- Dispositions are PLANNING statements with recorded destinations:
  semantic verification that destination notes actually preserve each
  KU's content happens at the SYNTHESIS gates (audit-output per batch),
  not at assignment time (ADR-0014 rationale).
- The three confirmed gaps (second moment, bradley-terry, async def) still
  need their dedicated treatments at synthesis time.
- Canonical note titles/folders (structure v1) may be refined at synthesis
  start under EDITORIAL_STYLE_GUIDE change control with a versioned
  migration of the file mapping — they are PLANNED destinations, not
  written notes.
- The final PRESENTATION of area 20 (archival context layer: source-vault
  construction documents) is an open release-audit decision; ordinary notes
  must never narrate merges (SOURCE_POLICY).
- Zero notes have been synthesized yet: output/Unified-Vault/ does not
  exist; SYNTH-001 is the first synthesis session's work.
- Tier A dossier-extension auto-accepts retain ~17% single-side
  over-inclusion (safe direction, documented in the session-18 report).
