# Next Agent Handoff

## Project state

- Current milestone: **SYNTHESIS IN PROGRESS — AREAS 04, 05, 06 COMPLETE**.
  Session 21 (2026-11-02) drove two full areas end-to-end: **area 05 -
  Neural Network Foundations (21 notes) and area 06 - Computer Vision (79
  notes)**, both GREEN through the complete gate chain (lint 0 errors →
  assess 0 dimensions below band → drift explained → quality-gate PASS →
  audit-output **valid=true, 0 findings**: area 05 over 2,411 KUs, area 06
  over 4,983 KUs; every equation, code block and rare term verified
  present). Deliverable metric: canonical notes verified **27 → 127/544**.
- USER DIRECTIVE IN FORCE (2026-11-01): BINDING POLICY (ADR-0012): read
  `docs/ACCELERATED_COMPLETION_POLICY.md` and AGENTS.md §12 BEFORE planning.
  Budget after session 21: **5 sessions remaining (22–26)**. Deliverable-first
  reporting; a bookkeeping-only session is a FAILED session; every checkpoint
  carries the `accelerated_mode` block.
- Completed and verified: BOOT-000..004, EXT-001..011, REBASE-000, AUDIT-011,
  FRAME-001, DISC-001, FRAME-002, REGEN-001, DISC-002, DISP-001. SYNTH-001 is
  in_progress (areas 04–06 done; 13 areas / 417 notes remain).
- Framework: 740/740 tests at session end (725 at start + 15 new: 9
  FRONTMATTER_FIELD_TYPE lint tests, 6 F-0030/F-0031 marker tests); sources
  byte-identical 276/276 + 333/333 at start AND end; omission pilot
  re-verified 12/12 after every marker-machinery change.

## Session 21 summary (evidence-backed)

- Baseline verified: clean tree, HEAD == origin/main == cbaed73; 725/725
  first-run; manifests unchanged; derived registry rebuilt exactly as the
  session-20 checkpoint records (applied=27,536, Unaccounted=0, valid).
- **Pipeline generalized**: `scripts/s20_build_synthesis_inputs.py` now carries
  a per-area `AREA_CONFIG` (note types, MOC link target, colliding basenames);
  the area-04 rebuild was regression-verified byte-identical. New reusable
  chain script `scripts/s21_run_gates.py <slug>` (assess over the whole vault
  → deterministic filter to the area's expected notes → drift → gate).
- **Generation pattern that worked** (100 notes, 26 subagent groups): groups
  capped at ~4 notes / ~12K source words (TWO over-merged groups hit the
  context deadline — their files still landed, but keep groups small);
  orientation/MOC notes written LAST with the full sibling list
  (`expected-notes.txt`); every prompt carried the full editorial contract +
  the area's colliding-basename list (path-form links) + the Superseded-KU
  rule. The area MOC may be orchestrator-written (session-20/21 pattern).
- **Repairs are anchored, asserted, idempotent** scripts citing their source
  KUs: `scripts/s21_lint_repairs.py` (4 lint errors), `scripts/s21_marker_
  repairs.py` (area 05: 40 audit findings → 0), `scripts/s21_marker_repairs_
  area06.py` (area 06: 66 → 0). Repair root-cause classes this session:
  verbatim-form equation/code/term gaps; source-voice sentences (stacked
  adverbs); source-spelling quirks preserved verbatim per the preservation
  contract (`breakthroughths`, `presving`, `deegradation`, `zisseran`,
  `trigggs`, `downsampleing`, `un-padded`); underscore-emphasis formatting
  variants; source section cross-references kept as historical context
  (Section 13.5.3 / 13.9.1 / 14.4 / Ch. 05.07); the label-smoothing source
  self-correction preserved with both values contextualized.
- **Framework fixes (all with regression tests + pilot re-verification)**:
  FRONTMATTER_FIELD_TYPE lint check (plain-scalar brackets / non-scalar
  alias members — caught 3 real subagent frontmatter errors); F-0030
  (source-note frontmatter inside KU excerpts is provenance metadata, not
  term-knowledge); F-0031 (code fingerprints dedent-normalized — the
  contract already says code is verbatim "whitespace-insensitive").
- **Known tooling artifact (do not chase phantom defects)**: this IM channel
  strips the two-character sequence `[` + `m` from DISPLAYED tool output
  (e.g. `tags: [moc, x]` renders as `tags: oc, x]`). Verify suspected
  frontmatter/link defects byte-level (hex) before acting — session 21
  nearly "repaired" a phantom tags defect that was display-only.
- **Lint warnings policy applied**: 6 warnings remain INTENTIONALLY
  (verbatim source text: quiz `a) b) c) d)` option format ×4, `[0,∞)`
  interval, literal `$10` price). Fixing them would violate verbatim
  preservation; they are documented in `reports/synthesis/s21-lint-vault.json`
  and the session-21 checkpoint.
- **Drift waivers (area 06, 4 types)**: content-family artifact (CNN
  engineering vs classical image-processing source families), each with
  three-part evidence (0 dimensions below band; audit 0 findings; first/last
  thirds split along source-family lines). Recorded verbatim in
  `reports/synthesis/s21-area06-gate.json` — re-check in the session-25
  corpus-wide drift re-audit.
- Orchestrator independent review: 8/8 semantic probes across 8 notes;
  F-0014 marker headings confirmed absent; every repair edit personally
  verified against its source excerpt.

## Committed session-21 artifacts (the durable state)

- `output/Unified-Vault/05 - Neural Network Foundations/**` (21 notes) and
  `output/Unified-Vault/06 - Computer Vision/**` (79 notes) — THE deliverable.
- `scripts/s20_build_synthesis_inputs.py` (AREA_CONFIG), `scripts/s21_run_
  gates.py`, `scripts/s21_pack_waves.py`, `scripts/s21_marker_repairs.py`,
  `scripts/s21_marker_repairs_area06.py`, `scripts/s21_lint_repairs.py` —
  the replayable pipeline + repairs (scratch/ bundles/specs are git-ignored
  and regenerable; reports are committed).
- `state/checkpoints/checkpoint-2026-11-02-synth001-session21.json` (with
  the `accelerated_mode` block); `state/findings.jsonl` F-0030/F-0031;
  session-ledger row 21 in `docs/ACCELERATED_COMPLETION_POLICY.md`.
- `reports/synthesis/s21-*` (inputs ×2, checkprompt ×2, lint-vault, assess ×2,
  drift ×2, gate ×2, audit ×2, omission-pilot, immutable ×4).
- Framework fixes in `src/vault_unification/{omission,artifactlint}.py` +
  tests (740 total).

## Next task (SYNTH-001 continue — sessions 22–24)

1. **Read first**: AGENTS.md §12 → `docs/ACCELERATED_COMPLETION_POLICY.md` →
   this file → the session-21 checkpoint (the pipeline recipe is battle-tested
   on 127 notes now).
2. **Verify baseline** (policy §7): HEAD == origin/main, clean tree,
   `python3 -m pip install -e .`, full suite green (**740 expected**),
   manifests 276/276 + 333/333. Rebuild the derived registry exactly as the
   session-20/21 checkpoints record.
3. **Run the remaining areas in waves** (suggested):
   - 22: areas 07 - Sequence Models (14) + 08 - Attention and Transformers
     (38) + 09 - NLP and Language Models (11) — 63 notes.
   - 23: areas 10 - Large Language Models (7) + 11 - Foundation Models and
     Multimodal (13) + 12 - Generative Models (12) + 13 - Training and
     Adaptation (11) + 14 - Inference and Production (26) — 69 notes.
   - 24: areas 15 - Agents and Tooling (41) + 16 - Interpretability and
     Research (31) + 17 - Papers (56) + 18 - Projects (25) + 19 - Reference
     and Practice (48) + 01–03 (20+18+29) + 20 (17, the Contextualized
     archival layer — presentation decided at release audit) — 285 notes;
     widen subagent waves (many small parallel groups), never the floor.
   - Per area: add the `AREA_CONFIG` entry (note types from the canonical
     structure rationales; MOC target; compute the area's colliding basenames
     against the 544-note structure) → build inputs → check prompts →
     generate (groups ≤ ~4 notes / ~12K source words; orientation notes
     last) → `python3 scripts/s21_run_gates.py <slug>` → `vu audit-output
     --source-root "source-vaults/AI " --output-root output/Unified-Vault
     --ku-batch scratch/synth/<slug>/audit-kus.jsonl --report reports/
     synthesis/s2N-<slug>-audit.json` → root-cause findings (anchored
     idempotent repair scripts; framework fixes with tests + pilot re-run
     for systematic classes).
4. **Session 25 (planned)**: cross-batch consistency (terminology, cross-area
   wikilinks once all notes exist, corpus-wide drift re-audit incl. the area-06
   waivers) + the three confirmed-gap dedicated treatments (second moment,
   bradley-terry, async def) + area-20 presentation decision.
5. **Session 26 (planned)**: final verification and delivery — release-gate
   predicates from `docs/MILESTONES_AND_ACCEPTANCE.md`, final audit-output
   over ALL 27,536 KUs, final report with denominators.

## Standing rules (enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Every completion claim needs a report path or test run as evidence.
- Marker-retention repairs go through anchored, asserted, idempotent scripts
  citing their source KUs — never hand-edits without a record.
- Drift waivers are for EXPLAINED artifacts with evidence (0 below band +
  audit 0 findings), never for hiding a real regression; re-check the
  arithmetic before waiving; re-audit corpus-wide at session 25.
- Push to main before session end; record push verification; if a push is
  rejected because a parallel session moved main: fetch, review, MERGE
  (never rebase away history), reconcile, re-verify.
- ADR-0011 discipline stands; subagent outputs are verified (gates +
  sampling), never trusted.
- Delta-verification discipline: write the arithmetic of expectations down
  BEFORE running.
- Fresh-sandbox setup: `python3 -m pip install -e .` BEFORE the baseline
  pytest. F-0016: long runs must fit one tool call (< 10 min). F-0020:
  invoke via `vu`. F-0014 (open): marker headings must never be copied as
  knowledge — verified absent in areas 04–06; re-check per area.
- Display artifact: the IM channel strips `[m` from displayed output —
  verify suspected defects byte-level before acting (see above).

## Explicit non-claims

- 99 of the 100 session-21 notes were subagent-written; the GATES (not
  subagent self-reports) are the acceptance evidence.
- Marker retention proves lexical/formula preservation of every KU excerpt;
  the semantic-fidelity layer for the rewritten prose is the session-25
  cross-batch consistency pass plus the release audit.
- Cross-area wikilinks do not exist yet by design (areas 04–06 only exist);
  they are added once all areas are generated (session 25).
- The 46,978 low-signal provisional discovery candidates remain a documented
  exclusion (not silently resolved).
- The three confirmed gaps (second moment, bradley-terry, async def) still
  need their dedicated treatments at synthesis time.
- Tier A dossier-extension auto-accepts retain ~17% single-side
  over-inclusion (safe direction, documented in the session-18 report).
- Areas 01–03 and 07–20 are NOT synthesized yet; the unified vault currently
  contains areas 04, 05 and 06 only.
