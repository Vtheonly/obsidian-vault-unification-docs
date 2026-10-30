# Next Agent Handoff

## Project state

- Current milestone: DISC-002 corpus-wide concept discovery IN PROGRESS —
  session 6 re-verified the six-round ADR-0010 chain end-to-end (fresh
  replay, content-identical to the committed index before the batch-6
  apply; the replay ran clean on the first try, validating the F-0020
  fix), and completed the batch-6 review tranche (5 covers + 55 noise
  rejects). After DISC-002: per-domain semantic classification of the
  dossier-extension overlap pairs, then disposition assignment, then
  GATED synthesis.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002
  sessions A+B (merged), sessions 3, 4, 5, and 6 (this checkpoint).
- Framework version 0.9.0; 24 capabilities (23 implemented-and-tested +
  1 planned, test-verified).
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never
  mark a task completed before its commit exists; always re-run the
  suite after the last mutation).

## Session 6 summary (evidence-backed)

- Baseline verified: 663/663 tests at session start
  (reports/discovery/disc002-session6-baseline-pytest.json); both vaults
  byte-identical to committed manifests at session start
  (reports/discovery/disc002-session6-manifest-{ai-course,master-ai}.json,
  0 added/removed/changed) and again at session end (-end- reports).
- ADR-0010 replay re-verified via scripts/disc002_batch6_replay.py: `vu
  discover-gaps` over all 70 batches (recorded args), then SIX decide
  rounds replayed with the recorded --decided-utc values (r1, r2,
  batch2, batch3, batch4, batch5), then `vu discovery-index` —
  CONTENT-IDENTICAL to the committed index (60,154 records; status
  counts matched exactly: 51,852/7,001/1,298/2/1; validate green;
  F-0019 heeded: parsed content compared, not raw bytes). NO NEW
  TOOLING DEFECTS this session; the replay running clean on the first
  try is post-fix regression evidence for F-0020.
- Batch-6 review tranche: 60 highest-signal unreviewed provisional
  candidates (of 4,874 matching the signal rule; tranche dominated by
  generic English vocabulary and prose fragments), individually
  reviewed with a 34-term definitional-treatment coverage probe
  (scripts/disc002_batch6_probe.py), targeted citation verification
  (scripts/disc002_batch6_verify.py, 37 locator checks), and an
  independent subagent cross-check of 15 judgment calls: 15/15 AGREE;
  corrections incorporated (ai-course chapter-level path completions;
  master-ai '28 - Glossary/03 - Notation Conventions.md:54' supplies
  the diag(x) definitional entry for the diagonal cover — note that
  '02 - Mathematics/Linear Algebra/06 - Tensors and Broadcasting.md:258'
  ("# 6. Diagonal extraction") is a CODE COMMENT inside a code block,
  not a markdown section; master-ai '02 - Mathematics/Probability/09 -
  Gaussian Distribution.md' strengthens the randn cover). Result: 5
  evidence-cited covers (randn, eval set, sklearn, probability
  distribution, diagonal) + 55 noise rejects. No new confirmed gaps (2
  remain: second moment, bradley-terry).
- Current candidate set: 51,792 provisional / 7,006 already_covered /
  1,353 rejected / 2 confirmed_gap / 1 deferred.

## Next task: DISC-002 continuation

1. **Continue the semantic review in bounded tranches** (51,792
   provisional; ~4,814 more match the signal rule). Reuse the
   REPO-RELATIVE scripts/disc002_batch6_tranche.py (selection + brief —
   edit CAND to point at the current replayed state),
   scripts/disc002_batch6_probe.py (coverage probe — edit TERMS), and
   the decisions pattern scripts/disc002_batch6_decisions.py (new
   decision IDs D-DISC002-B7-****). Standard: individual evidence
   review with file:line citations (full vault-relative paths with
   chapter-level parents); subagent cross-check of judgment calls;
   confirmed gaps are RARE — look for concepts used in dependency
   position with NO definitional treatment anywhere.
2. **Dossier extension classification** (per domain, bounded batches):
   review the overlap candidate pairs in scratch (regenerate via the
   commands in reports/dossier-ext/disc002-dext-<domain>-overlap-run.json
   if needed), classify with dossier discipline (new-KU side must have
   real domain participation, not a broad-term hit), extend the domain's
   state/classifications/ file, regenerate dossiers with the ext006 rule
   set, and keep --check byte-identity for the six committed dossiers
   until their extension lands as a new version. NO bulk absorption of
   term matches.
3. **Then disposition assignment** (Unaccounted blocks release) and
   GATED synthesis: check-prompt -> generation -> lint-artifacts ->
   assess-quality -> quality-drift -> quality-gate -> repair loop per
   batch.

## Replay recipe (ADR-0010, now seven decide rounds)

`vu discover-gaps` over all 70 batches (exact args in
reports/discovery/disc002-full-corpus-run.json report_meta.args; ~5 min,
fits one tool call) then `vu discovery-decide` r1 (--decided-utc
2026-10-28T00:45:00Z), r2 (01:30:00Z), batch2 (02:30:00Z), batch3
(2026-10-28T05:30:00Z), batch4 (2026-10-30T13:05:00Z), batch5
(2026-10-30T15:30:00Z), batch6 (2026-10-30T16:30:00Z), then `vu
discovery-index`. Expected result: 60,154 records; 51,792 provisional /
7,006 already_covered / 1,353 rejected / 2 confirmed_gap / 1 deferred.
CAUTION (F-0019): compare the regenerated index against the committed
index by PARSED CONTENT (e.g. json.loads each line), not raw sha256 —
the recorded hash is script-writer-specific while the CLI writer
escapes Unicode. scripts/disc002_batch6_replay.py performs the whole
chain in one run (adjust the output paths for a batch-7 replay or
reuse as-is after adding the batch-6 round to DECIDE_CHAIN: it verifies
content-identity against the committed index automatically).

## Standing rules (unchanged, enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Machine locators for every line citation (vault_unification.locators).
- Every completion claim needs a report path or test run as evidence.
- Push to main before session end; record push verification. When a push
  is rejected because a parallel session moved main: fetch, review their
  commits, MERGE (do not rebase away history), reconcile decisions
  through the audit trail, and re-verify the chain before pushing again.
- F-0016: background processes are reaped between tool calls — long runs
  must fit one tool call (< 10 min); corpus discovery ~5 min; a six-domain
  overlap-candidates sweep takes ~4 min total.
- F-0018: old extNNN/disc002 helper scripts (pre-batch-4) hardcode
  /home/z/my-project/obsidian-vault-unification-docs — fix paths or use
  the batch-4/5/6 repo-relative scripts.
- F-0020 (fixed, regression-tested): never invoke the CLI via
  `python -m vault_unification.cli` in old checked-out code without the
  guard — use `vu` or `python -m vault_unification` if unsure; the new
  regression test catches the no-op form on current code.
- F-0014 (open): two ai-course files end with 'END OF FILE / File Name'
  marker headings — synthesis must not copy them as knowledge headings.
- Subagent citation lessons (sessions 5-6, recurring): ai-course note
  paths in rationales must include the chapter-level parent (e.g. '05 -
  Convolutional Neural Networks (CNN)/05. Pipeline, Evaluation, and
  Interpretability/...'); prefer full vault-relative paths so citations
  stay machine-resolvable; verify that a claimed heading is a real
  markdown heading, not a '#' comment inside a code block (session-6
  example: 'Tensors and Broadcasting.md:258').
