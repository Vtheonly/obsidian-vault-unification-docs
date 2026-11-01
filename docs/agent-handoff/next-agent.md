# Next Agent Handoff

## Project state

- Current milestone: **SYNTHESIS IN PROGRESS — AREA 04 COMPLETE**. Session 20
  (2026-11-02) started gated synthesis and drove one full area end-to-end:
  **area 04 - Machine Learning, 27/27 canonical notes GREEN through the
  complete FRAME-002 gate chain** (lint 0 errors/0 warnings → assess-quality
  0 dimensions below band → drift explained → quality-gate PASS →
  audit-output **valid=true, 0 findings over all 8 checks for all 1,829
  area-04 KUs**). Deliverable metric: canonical notes verified **0 →
  27/544**.
- USER DIRECTIVE IN FORCE (2026-11-01): BINDING POLICY (ADR-0012): read
  `docs/ACCELERATED_COMPLETION_POLICY.md` and AGENTS.md §12 BEFORE planning.
  Budget after session 20: **6 sessions remaining (21–26)**. Deliverable-first
  reporting; a bookkeeping-only session is a FAILED session; every checkpoint
  carries the `accelerated_mode` block.
- Completed and verified: BOOT-000..004, EXT-001..011, REBASE-000, AUDIT-011,
  FRAME-001, DISC-001, FRAME-002, REGEN-001, DISC-002, DISP-001. SYNTH-001 is
  in_progress (area 04 done; 15 areas / 517 notes remain).
- Framework: 725/725 tests at session end (708 at start + 17 new regression
  tests for F-0024..F-0029); sources byte-identical 276/276 + 333/333 at
  start AND end; omission pilot re-verified 12/12 after the F-0029 change.

## Session 20 summary (evidence-backed)

- Baseline verified: clean tree, HEAD == origin/main == 3abf295; 708/708
  first-run; manifests unchanged; derived registry rebuilt and valid
  (applied=27,536, Unaccounted=0, 0 warnings).
- **Editorial conventions v1 recorded** in `docs/EDITORIAL_STYLE_GUIDE.md`
  BEFORE generation (frontmatter contract, no-H1 bodies, unnumbered
  sentence-case ##/### sections, `$`/`$$` math, verbatim equations/code,
  wikilink policy with the 32 colliding basenames path-linked, no merge
  narration, sources = source-note titles in frontmatter).
- **Synthesis pipeline (reusable for every remaining area)**:
  `python3 scripts/s20_build_synthesis_inputs.py --area "<NN - Name>" --slug
  areaNN --report reports/synthesis/s20-areaNN-inputs-report.json` →
  per-note evidence bundles (full verbatim sources + KU checklist + dossier
  concepts), specs, audit batch (KU records + ledger overlay incl.
  superseded_rationale), provenance mapping, expected-notes;
  `python3 scripts/s20_check_prompts.py areaNN` (all specs must pass);
  generation by bounded subagents (1–4 notes each, full bundle as evidence,
  contract in prompt: preserve everything, equations/code verbatim,
  multi-destination KUs split by topic with shared terms mentioned);
  `vu lint-artifacts output/Unified-Vault` → `vu assess-quality
  output/Unified-Vault --provenance scratch/synth/areaNN/provenance.jsonl
  --ku-batch state/knowledge-units/*.jsonl --out ... --report ...` →
  `vu quality-drift` → `vu quality-gate --expected ... [--waiver
  drift::<type>=reason]` → `vu audit-output --source-root "source-vaults/AI "
  --output-root output/Unified-Vault --ku-batch scratch/synth/areaNN/audit-kus.jsonl`.
- **Area 04 result**: 27 notes / 87,300 words (26 notes by 13 parallel
  subagents; MOC written by the orchestrator after the siblings existed).
  Audit initially found 398 findings → root-caused into three classes:
  (1) the French MNIST lab (330 rare French terms) → preserved VERBATIM as
  an alternating-fence appendix inside Linear Regression
  (`scripts/s20_french_lab_appendix.py`) alongside the translated synthesis;
  (2) real verbatim-form gaps (28 equation fingerprints, formatting variants,
  rare English terms, file-name tokens from the vaults' quoted-file
  convention) → 60+ anchored repairs (`scripts/s20_marker_repairs.py`,
  idempotent); (3) marker-machinery false positives → framework fixes below.
- **Framework fixes (F-0024..F-0029, all with regression tests)**:
  F-0024 `check_prompt`/`_ku_terms` now resolve the canonical
  `knowledge_unit_id` field (both silently failed on real batches);
  F-0025 mermaid grammar accepts open dotted links (`A-. text .-B`);
  F-0026 bracket balance ignores inline math (half-open intervals);
  F-0027 wikilink targets in tables strip the escaped-pipe backslash;
  F-0028 depth measures prose only (code/math/tables are not paragraphs);
  F-0029 markdown-quotation fences and `--- + File N: x.md` scaffolding
  fragments are not code markers — **the omission pilot was re-run and
  re-verified 12/12 after this change** (release-gate integrity).
- Orchestrator independent review: 10/10 semantic probes across 10 notes;
  SVM Lagrangian Dual derivation read in full; F-0014 END-OF-FILE marker
  confirmed absent from all output.

## Committed session-20 artifacts (the durable state)

- `output/Unified-Vault/04 - Machine Learning/**` — THE deliverable (27
  notes; first synthesized area).
- `scripts/s20_build_synthesis_inputs.py`, `scripts/s20_check_prompts.py`,
  `scripts/s20_french_lab_appendix.py`, `scripts/s20_marker_repairs.py` —
  the replayable synthesis pipeline (scratch/ bundles+specs+audit batches
  are git-ignored and regenerable; reports are committed).
- `docs/EDITORIAL_STYLE_GUIDE.md` — Unified Vault Conventions v1.
- `state/checkpoints/checkpoint-2026-11-02-synth001-session20.json` (with
  the `accelerated_mode` block); `state/findings.jsonl` F-0024..F-0029;
  session-ledger row 20 in `docs/ACCELERATED_COMPLETION_POLICY.md`.
- `reports/synthesis/s20-*` (inputs, checkprompt, lint, assess, drift,
  gate, audit, omission-pilot-refix, capabilities, manifests ×4).
- Framework fixes in `src/vault_unification/{promptspec,notequality,
  artifactlint,mdextract,omission}.py` + tests (725 total).

## Next task (SYNTH-001 continue — area waves)

1. **Read first**: AGENTS.md §12 → `docs/ACCELERATED_COMPLETION_POLICY.md`
   → this file → the "Synthesis pipeline" recipe above (it is complete and
   battle-tested on area 04).
2. **Verify baseline** (policy §7): HEAD == origin/main, clean tree,
   `python3 -m pip install -e .`, full suite green (**725 expected**),
   manifests 276/276 + 333/333. Rebuild the derived registry exactly as the
   session-20 checkpoint records (kureg-init → kureg-load ×71 →
   kureg-apply-dispositions → kureg-validate).
3. **Run the remaining areas in waves** (suggested for sessions 21–24):
   - 21: area 05 - Neural Network Foundations (79 notes) + 06 - Computer
     Vision (26) — the largest pair; split subagent waves accordingly.
   - 22: 07 - Sequence Models (38) + 08 - Attention and Transformers (31) +
     09 - NLP and Language Models (37).
   - 23: 10 - Large Language Models (41) + 11 - Foundation Models and
     Multimodal (31) + 12 - Generative Models (81).
   - 24: 13 - Training and Adaptation (48) + 14 - Inference and Production
     (17) + 15 - Agents and Tooling (17) + 16 - Interpretability and
     Research (26) + 17 - Papers (47) + 18 - Projects (79) + 19 - Reference
     and Practice (81) + 01..03 (20+47+27) — compress further if earlier
     waves overrun; widen subagent waves, never the floor.
   - 20 (Vault and Project Context, 12 notes) is the Contextualized
     archival layer: present as context documents, NOT ordinary knowledge
     notes (SOURCE_POLICY); decide presentation at release audit.
4. **Per area, the gates are the same and all must be green** before the
   area counts: audit-output valid=true with 0 findings is the acceptance
   record. Multi-area files (12 vault-wide) make some KU batches non-
   self-contained — for those, either synthesize the co-destination areas in
   the same session or run audit-output with the union of the co-generated
   areas' audit batches (document the choice in the report).
5. **Session 25 (planned)**: cross-batch consistency (terminology, link
   completeness — add cross-area wikilinks once all notes exist, drift
   re-audit corpus-wide) + the three confirmed-gap dedicated treatments
   (second moment, bradley-terry, async def) + area-20 presentation
   decision.
6. **Session 26 (planned)**: final verification and delivery — release-gate
   predicates from `docs/MILESTONES_AND_ACCEPTANCE.md`, final audit-output
   over ALL 27,536 KUs, final report with denominators.

## Standing rules (enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Every completion claim needs a report path or test run as evidence.
- Marker-retention repairs go through anchored, asserted, idempotent scripts
  (s20_marker_repairs.py pattern) — never hand-edits without a record.
- The drift waiver mechanism is for EXPLAINED artifacts with evidence, never
  for hiding a real regression; re-check the arithmetic before waiving.
- Push to main before session end; record push verification; if a push is
  rejected because a parallel session moved main: fetch, review, MERGE
  (never rebase away history), reconcile, re-verify.
- ADR-0011 discipline stands; subagent outputs are verified (gates +
  sampling), never trusted.
- Delta-verification discipline: write the arithmetic of expectations down
  BEFORE running.
- Fresh-sandbox setup: `python3 -m pip install -e .` BEFORE the baseline
  pytest. F-0016: long runs must fit one tool call (< 10 min). F-0020:
  invoke via `vu`.
- F-0014 (open): marker headings must never be copied as knowledge —
  verified absent in area 04; re-check per area.

## Explicit non-claims

- 26 of 27 area-04 notes were subagent-written; the GATES (not subagent
  self-reports) are the acceptance evidence. Marker retention proves
  lexical/formula preservation of every KU excerpt; full semantic-fidelity
  review of the rewritten prose is the session-25 cross-batch consistency
  layer plus release audit.
- Cross-area wikilinks do not exist yet by design (only area-4 notes exist);
  they are added once all areas are generated (session 25).
- The 46,978 low-signal provisional discovery candidates remain a documented
  exclusion (not silently resolved).
- The three confirmed gaps (second moment, bradley-terry, async def) still
  need their dedicated treatments at synthesis time.
- Tier A dossier-extension auto-accepts retain ~17% single-side
  over-inclusion (safe direction, documented in the session-18 report).
- Areas 01–03 and 05–19 are NOT synthesized yet; the unified vault currently
  contains only area 04.
