# Next Agent Handoff

## Project state

- Current milestone: **SYNTHESIS FINAL PHASE — AREAS 01–19 COMPLETE AND
  VERIFIED (527/544)**. Session 27 (2026-11-06, commit `dcea8fb`) cleared
  the sessions-25/26 verification debt: all five areas 15–19 audits
  **valid=true, 0 findings** over 8,610 KUs / 11,394 verified markers;
  gates 5/5 pass (2 evidence-backed content-family drift waivers, source
  measurements recorded in the gate reports); lint **0 errors / 84
  documented verbatim-source warnings** over all 527 notes; 752/752 tests;
  sources immutable 276/276 + 333/333 at start and end.
- Deliverable metric: canonical notes verified **327 → 527/544**.
- **Budget position (honest):** ADR-0012's hard deadline (end of session 26)
  was missed — sessions 25/26 generated but did not verify, and session 27
  completed the verification. This is recorded in the session ledger as an
  overrun (§5.5 escalation, floor never weakened). **Only the user may
  re-baseline or extend the deadline**; the remaining scope is one focused
  session's worth (see Next task).
- Completed and verified: BOOT-000..004, EXT-001..011, REBASE-000, AUDIT-011,
  FRAME-001, DISC-001, FRAME-002, REGEN-001, DISC-002, DISP-001. SYNTH-001
  in_progress (areas 01–19 done; area 20 + final verification remain).
- Git: HEAD == origin/main == `dcea8fb`, clean tree, three pushes this
  session (`4f5c6b9`, `9ddf5f2`, `dcea8fb`), each verified via fetch +
  rev-parse.

## Session 27 summary (evidence-backed)

- Verified the inherited s25/s26 state first (527/544 on disk, zero
  unplanned files, claims cross-checked against canonical structure and
  git history), then: rebuilt scratch inputs deterministically (byte-identical
  reports), drove lint to 0 errors (14 ambiguous links → path form after the
  area-19 quiz basename collisions, 3 F-0031 fence labels, 1 table cell),
  added framework **F-0033/F-0034** (tilde-fence extraction with nested-fence
  precedence; unlabelled-quotation exemption — corpus survey: exactly 1 KU
  affected; contiguous-containment code matching — truncated KU excerpts vs
  preserved note fences), 8 new unit tests (744→752), root-caused all 91
  audit findings and repaired 90 via `scripts/s27_marker_repairs_area15..19.py`
  (probe-idempotent, double-run no-op verified): 26 bare-fence equations
  restored as ```text fences, 10 mermaid subgraph labels + 1 arrow restored
  verbatim, ASCII-dash forms, chapter-NN references, math-span line-structure
  restorations (the audit's inline spans pair $-signs PER LINE — restore the
  source's sentence/line structure), source-own forms kept sic
  (Self-RAF, communityfine-tunes, the 2024-2024 typo'd path), keep-both
  carriers for escaped table cells. 1 gate repair (KG Pipeline tutorial
  examples band via grounded source-verbatim WORKS_FOR/FOUNDED_BY/LOCATED_IN
  instance markers).
- Waiver evidence (areas 16/17, both `drift::concept` on the examples
  dimension): area16 first-third sources 2.11 vs last-third 0.66 example
  markers/1k words (3.2× source-side drop); area17 labeled-fence density 15
  vs 8 across the two 18-note halves (marker density identical 1.33/1k). The
  output drift is milder than the source drift in both cases.

## Next task (SYNTH-001 final phase — one focused session)

1. **Read first**: AGENTS.md §12–13 → `docs/ACCELERATED_COMPLETION_POLICY.md`
   (ledger rows 25–27 record the deadline overrun) → this file →
   `state/checkpoints/checkpoint-2026-11-06-synth001-session27.json`.
2. **Verify baseline** (policy §7): HEAD == origin/main, clean tree,
   `python3 -m pip install -e .`, full suite green (**752 expected**),
   manifests 276/276 + 333/333.
3. **Area 20 (17 notes, "20 - Vault and Project Context")**: add the
   full-area `AREA_CONFIG` entry to `scripts/s20_build_synthesis_inputs.py`
   (note types from the canonical-structure rationales; MOC target; the
   area is the Contextualized archival layer — presentation decided at the
   release audit) → extend/re-run the link-rules script → build inputs →
   check prompts → generate (subagent waves capped at 4 notes / ~12K source
   words, orientation notes LAST; scratch wave plans via the s25_pack_waves
   pattern) → `python3 scripts/s21_run_gates.py area20` →
   `vu audit-output --source-root "source-vaults/AI " --output-root
   output/Unified-Vault --ku-batch scratch/synth/area20/audit-kus.jsonl
   --report reports/synthesis/s2X-area20-audit.json` → anchored
   probe-idempotent repairs if findings (all s27 repair scripts are
   templates). Push each green unit immediately (§13).
4. **Cross-batch consistency + gaps**: corpus-wide drift re-audit incl.
   **ALL 12 waivers** (s21–23: 10; s27: 2 — list in the gate reports);
   F-0014 grep pass over areas 15–20 note bodies (marker headings must never
   appear as knowledge — verified absent areas 01–14 at s24); terminology
   and cross-area wikilink sweep now that all notes exist (bare links whose
   basenames collide must be path-form — the lint's LINK_AMBIGUOUS is the
   detector); the three confirmed-gap dedicated treatments (second moment,
   bradley-terry, async def).
5. **Final verification and delivery**: release-gate predicates from
   `docs/MILESTONES_AND_ACCEPTANCE.md`; final audit over ALL 27,536 KUs;
   final report with denominators; Unaccounted = 0 re-check; sources
   immutable; full suite after the last mutation.

## Standing rules (enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Every completion claim needs a report path or test run as evidence.
- Marker-retention repairs go through anchored, PROBE-idempotent scripts
  citing their source KUs — never hand-edits without a record. Keep BOTH
  duplicate source treatments; hyphenated vs spaced forms are different
  markers; NFKC superscript lesson (s24); **math spans pair $-signs per
  LINE** (s27) — restore the source's line structure when a span fails.
- Drift waivers are for EXPLAINED artifacts with source measurements +
  audit 0 findings + 0 below band — never for hiding a regression.
- **Continuous persistence (ADR-0015 / AGENTS.md §13):** commit and push
  each bounded green unit immediately; verify the remote ref after every
  push; record SHAs in the checkpoint.
- ADR-0011 discipline stands; subagent outputs are verified (gates +
  audits + sampling), never trusted.
- Delta-verification discipline: write the arithmetic of expectations down
  BEFORE running.
- Fresh-sandbox setup: `python3 -m pip install -e .` BEFORE the baseline
  pytest. F-0016: long runs must fit one tool call (< 10 min). F-0020:
  invoke via `vu`. Scratch is git-ignored and regenerable: rerun the
  recorded scripts after a sandbox recycle — never hand-rebuild
  (s20_build_synthesis_inputs.py per area; s25_link_rules.py;
  s25_launch_manifest.py; s21_run_gates.py per slug).
- Display artifact: the IM channel strips `[m` from displayed output —
  verify suspected defects byte-level (hex) before acting.

## Explicit non-claims

- Area 20 (17 notes) is NOT generated; the vault has 527/544 notes.
- The corpus-wide drift re-audit (12 waivers) and the F-0014 grep pass over
  areas 15–19 have NOT been run yet; the areas 15–19 gates passed on
  per-area drift with 2 waivers.
- The semantic-fidelity layer for areas 01–19 prose is the cross-batch
  consistency pass plus the release audit — marker retention proves
  lexical/formula preservation, not full semantic equivalence.
- The three confirmed gaps (second moment, bradley-terry, async def) still
  need their dedicated treatments.
- The 46,978 low-signal provisional discovery candidates remain a
  documented exclusion (not silently resolved).
- Tier A dossier-extension auto-accepts retain ~17% single-side
  over-inclusion (safe direction, documented in the session-18 report).
- Release gates have NOT all passed yet; the project is NOT complete.
