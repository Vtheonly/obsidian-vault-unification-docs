# Next Agent Handoff

## Project state

- Current milestone: Phase 0 re-baseline COMPLETE (user-authorized restart);
  the project now moves to full-corpus re-extraction under the hardened
  pipeline, then corpus-wide discovery, then GATED synthesis.
- Completed and pushed this phase: REBASE-000 (machine-backed baseline),
  AUDIT-011 (17 capabilities mapped to code/tests/limitations; 13 known
  limitations L-01..L-13), FRAME-001 (framework refactor: L-01/02/03/04/06/
  07/08/13 fixed), DISC-001 (emergent-concept discovery, CAP-017), and
  FRAME-002 (quality toolkit: CAP-018 artifactlint, CAP-019 notequality,
  CAP-020 repair loop, CAP-021 promptspec).
- Framework version 0.7.0; 563/563 tests green; capabilities --verify:
  verified true (17 implemented-and-tested + 1 planned CAP-014).
- Extraction state (pre-restart work, all revalidated this phase): 11
  committed KU batches (1728 KUs, 31 of 609 files), 164 overlap
  classifications across six domains, 6 dossiers / 164 concepts / 514 KUs,
  all KUs Unaccounted; discovery candidates 6340 (provisional, coverage
  gate CLOSED: 31/609 files processed).
- Registry/checkpoint: latest checkpoint
  `state/checkpoints/checkpoint-2026-10-27-frame002.json`; task queue 22
  records valid.
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* (esp.
  PHASE_ZERO_REBASELINE_AND_FRAMEWORK_REFACTOR.md,
  EMERGENT_CONCEPT_DISCOVERY.md) -> state/task-queue.jsonl ->
  state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never
  mark a task completed before its commit exists; always re-run the suite
  after the last mutation).

## What the previous session actually did (evidence-backed)

1. Verified the interrupted Phase 0 session's uncommitted work was REAL
   (FRAME-001 + DISC-001 code, 482/482 module tests) but NOT committed, and
   its final task-queue edit broke schema validation (25 errors on 4
   records) -> repaired the records (schema-conformant), re-ran the suite.
2. Built the user-mandated quality toolkit (FRAME-002): artifactlint
   (fences, math env/delimiters, tables, headings, lists, links, mermaid,
   python/JSON AST-parse — never executed, truncation, placeholders,
   frontmatter), notequality (7 note types x 9 evidence-carrying dimensions,
   source-coverage vs KU provenance mappings, tertile drift detection that
   demonstrably flags the polished-early/thin-late pattern), batch gates
   (per-note failure enumeration; averages cannot hide failures; explicit
   waivers only), repair loop (content-addressed tasks, bounded retries,
   verification = originating check + no-new-defects + diff-scope-locality,
   regression re-opening, escalation), promptspec (testable criteria,
   vague-language rejection, ku_id resolvability, context budget, caps).
3. Ran the toolkit on the REAL corpus: full lint census of both source
   vaults (609 files) with link counts cross-validating EXACTLY against
   F-0010 (121) and F-0011 (338); mermaid grammar iterated against the
   corpus to zero false positives, every discovered form pinned by a
   regression test.
4. Full suite 563/563; capabilities verified; retrospective written.

## Next task

Queue records 20-21 (already queued, dependencies satisfied):
1. **Revalidate and regenerate full-corpus knowledge-unit evidence** —
   re-extract all 609 files under the hardened pipeline (byte-identity
   double-runs), validating the 11 existing batches regenerate identically;
   repair any that do not; rebuild the registry.
2. **Run corpus-wide concept discovery and reconcile dossiers** — with
   complete coverage the discovery gate opens; review candidates via
   `vu discovery-decide` (semantic review is YOUR job, the tool only
   collects evidence), then reconcile dossiers.
3. Then synthesis begins UNDER THE GATES: every batch through
   check-prompt -> generation -> lint -> assess -> drift -> gate -> repair.
   Use bounded batches (10-20+ iterations expected), fresh sessions, and
   the two-commit pattern (feat, then state-with-hash).

## Standing rules (unchanged, enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Machine locators for every line citation (vault_unification.locators).
- Every completion claim needs a report path or test run as evidence.
- Push to main before session end; record push verification.
