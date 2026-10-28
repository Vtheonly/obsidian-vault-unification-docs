# Next Agent Handoff

## Project state

- Current milestone: DISC-002 corpus-wide concept discovery IN PROGRESS
  (session 1 complete: the discovery run itself is done and verified; the
  multi-batch semantic review of the candidate set has started and must
  continue). After DISC-002: dossier extension, then disposition assignment,
  then GATED synthesis.
- Completed and verified so far: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002 session 1
  (feat commit recorded in the queue record and checkpoint).
- Framework version 0.9.0; capabilities --verify: 23 implemented-and-tested +
  1 planned (CAP-014). NEW this session: CAP-023 (`vu discovery-index`) and
  the F-0015 corpus-scale performance fix (see below).
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never mark
  a task completed before its commit exists; always re-run the suite after
  the last mutation).

## What this session actually did (evidence-backed)

1. Verified the REGEN-001 handoff BEFORE working: fresh full-suite run
   604/604 green (reports/discovery/disc002-startup-pytest.json), both vaults
   byte-unchanged vs manifests, registry rebuilt green via
   scripts/regen001_registry.py (27,536 KUs, 0 duplicates, 609/609 covered).
2. Fixed F-0015 (HIGH, resolved): corpus-scale performance regression.
   Evidence: `jsonschema.validate()` per record cost 8.52 ms (235 s for the
   corpus) vs 0.09 ms with one reused validator; the discovery term loop
   compiled 24 term-anchored regexes per distinct term. Fixes: single reused
   validator (overlap.load_ku_batches, discovery.validate_candidates,
   discovery.apply_decisions); inverted relationship matching (per-KU
   term-agnostic trigger-position sets + one cached `\b{t}\b` occurrence
   pattern per term); locate-before-classify reordering; lazy signature
   computation; per-KU normalized-text caches under non-persistent `_disc_*`
   keys. Equivalence evidence: reports/discovery/disc002-f0015-equivalence.json
   (110,799-pair differential, 0 mismatches; full-pipeline A/B byte-identical;
   48 new parametrized unit tests in TestRelationshipFastEquivalence). Net:
   3-batch A/B 83.4 s -> 8.1 s, byte-identical (sha256 324c12b158ec5eff).
3. Ran the corpus-wide discovery over ALL 70 batches: 60,154 candidates,
   coverage COMPLETE (609/609: 276/276 ai-course + 333/333 master-ai), double
   -run byte-identical (run1 291.1 s, run2 288.9 s), discovery-validate green
   vs all 70 batches. Kinds: 44,990 unexplained_prerequisite, 1,796
   fragmented_derivation, 6,512 rare_essential, 6,856 concept_sighting.
4. The 270 MB full candidates file EXCEEDS the 100 MB GitHub blob limit: it
   is now git-ignored as an ADR-0007-class regenerable artifact (deterministic
   from committed batches + manifests; exact command recorded in
   reports/discovery/disc002-full-corpus-run.json report_meta.args). The
   DURABLE committed state is: the compact index (46 MB,
   state/concept-candidates/002-disc002-full-corpus.index.jsonl) + the
   decisions files. CAP-023 `vu discovery-index` regenerates the index from
   any candidates file.
5. Semantic review batch 1 (THE AGENT'S JOB, not the tool's): all 114
   top-priority candidates decided with evidence-cited rationales
   (state/concept-candidates/002-disc002-decisions-batch1.jsonl): 63 REJECTED
   as non-concept noise (numeric literals, code/API identifiers, import
   statements, citation fragments, prose fragments); 51 COVERED (real
   concepts whose treatments exist in the corpus — each rationale cites
   file:line evidence collected by scripts/disc002_coverage_probe.py). ZERO
   confirmed gaps in this slice: every real concept examined already has a
   corpus treatment. Coverage evidence + noise classes are reusable review
   heuristics for the next batches. Post-decide statuses: 53,184 provisional
   / 6,907 already_covered / 63 rejected; discovery-validate green.
6. Dossier reconciliation SCOPED (not extended): all six dossiers verified
   byte-identical against their inputs (scripts/ext006_dossiers.py --check,
   exit 0). Gap report (reports/discovery/disc002-dossier-reconciliation-gap
   .json) quantifies the extension funnel per domain with an explicit
   upper-bound caveat: term-map matches are NOT evidence of domain
   participation; extension MUST go through vu overlap-candidates +
   classification discipline (as EXT-003..010 did), never bulk absorption.

## Next task: DISC-002 continuation (semantic review + dossier extension)

1. **Continue the semantic review in bounded batches.** 53,184 provisional
   candidates remain. Recommended priority order: (a) remaining
   fragmented_derivation (score < 0.85, 1,796 total minus reviewed);
   (b) rare_essential high-score; (c) unexplained_prerequisite ranked by
   independent_contexts (cross-vault first). Reuse the working pattern:
   scripts/disc002_reviewset.py (selection rules) ->
   scripts/disc002_coverage_probe.py (corpus coverage evidence) ->
   decisions JSONL with evidence-cited rationales -> `vu discovery-decide` ->
   `vu discovery-validate` -> regenerate the index with `vu discovery-index`.
   Learn from batch 1's noise classes (numeric/code/import/citation/prose
   fragments are ~55% of the top slice) and coverage heuristics (the corpus
   treats most real concepts; genuine gaps are RARE — look for concepts used
   in dependency position with NO definitional treatment anywhere).
2. **Dossier extension** per the gap report's next_action: for each domain,
   run `vu overlap-candidates` between the domain's existing participating
   KUs and the REGEN KUs, classify semantically (bounded batches), then
   extend the dossiers via the ext006 rule set (keep the byte-identical
   regeneration property; version the dossiers v1 -> v2 with migration notes).
3. **Then disposition assignment** (Unaccounted blocks release) and GATED
   synthesis: check-prompt -> generation -> lint-artifacts -> assess-quality
   -> quality-drift -> quality-gate -> repair loop per batch.

## Standing rules (unchanged, enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Machine locators for every line citation (vault_unification.locators).
- Every completion claim needs a report path or test run as evidence.
- Push to main before session end; record push verification.
- Note F-0014 (open): two ai-course files end with 'END OF FILE / File Name'
  marker headings — synthesis must not copy them as knowledge headings.
- The sandbox kills background processes when a tool call ends (verified:
  setsid/nohup do NOT survive) — long jobs MUST fit in one tool call
  (< 10 min) or be split; corpus-wide discovery now takes ~5 min per run
  thanks to F-0015.
