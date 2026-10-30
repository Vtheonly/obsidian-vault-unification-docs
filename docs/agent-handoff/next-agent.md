# Next Agent Handoff

## Project state

- Current milestone: DISC-002 corpus-wide concept discovery IN PROGRESS —
  session 4 (fresh clone) re-verified the entire baseline, replayed the
  ADR-0010 chain end-to-end, and completed the batch-4 review tranche.
  After DISC-002: per-domain semantic classification of the
  dossier-extension overlap pairs, then disposition assignment, then
  GATED synthesis.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002
  sessions A+B (merged), session 3, and session 4 (this checkpoint).
- Framework version 0.9.0; 24 capabilities (23 implemented-and-tested +
  1 planned, test-verified).
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never
  mark a task completed before its commit exists; always re-run the
  suite after the last mutation).

## Session 4 summary (evidence-backed)

- Baseline verified ON A FRESH CLONE: 662/662 tests
  (reports/discovery/disc002-session4-baseline-pytest.json); both vaults
  byte-identical to committed manifests at session start AND after all
  operations (four manifest reports, 0 added/removed/changed);
  capabilities test-verified 23+1
  (reports/discovery/disc002-session4-capabilities-verified.json).
- ADR-0010 replay re-verified end-to-end: `vu discover-gaps` over all 70
  batches (recorded args), then r1/r2/batch2/batch3 replayed with the
  recorded --decided-utc values, then `vu discovery-index` — the result
  was CONTENT-IDENTICAL to the committed index (60,154 records, status
  counts matched exactly; validate green). F-0019 recorded: the
  recorded sha256 88a538eb... is script-writer-specific
  (ensure_ascii=False); the CLI writer is byte-different but
  content-identical — always compare parsed content, not raw bytes.
- Batch-4 review tranche: 60 highest-signal unreviewed provisional
  candidates (of 4,994 matching the signal rule), individually reviewed
  with a 51-term definitional-treatment coverage probe
  (scripts/disc002_batch4_probe.py) plus targeted corpus verification
  for boundary cases (triangle inequality, batch size, weight sharing,
  loss-spikes stability, perceptron history) and an independent
  subagent cross-check of 14 judgment calls: 14/14 AGREE, 4 citation
  corrections incorporated. Result: 36 evidence-cited covers + 24 noise
  rejects. No new confirmed gaps (2 remain: second moment, bradley-terry).
- Current candidate set: 51,912 provisional / 6,981 already_covered /
  1,258 rejected / 2 confirmed_gap / 1 deferred.
- New findings: F-0018 (old helper scripts hardcode sandbox-absolute
  paths — batch-4 scripts are repo-relative; do not reuse old
  extNNN/disc002 scripts without fixing paths), F-0019 (writer-specific
  ADR-0010 sha256 — see above). README repository-status paragraph
  refreshed to the verified state (was stale at REGEN-001).

## Next task: DISC-002 continuation

1. **Continue the semantic review in bounded tranches** (51,912
   provisional; ~4,934 more match the signal rule). Reuse the
   REPO-RELATIVE scripts/disc002_batch4_tranche.py (selection + brief),
   scripts/disc002_batch4_probe.py (coverage probe — edit TERMS), and
   the decisions pattern scripts/disc002_batch4_decisions.py (new
   decision IDs D-DISC002-B5-****). Standard: individual evidence
   review with file:line citations; subagent cross-check of judgment
   calls; confirmed gaps are RARE — look for concepts used in
   dependency position with NO definitional treatment anywhere.
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

## Replay recipe (ADR-0010, now five decide rounds)

`vu discover-gaps` over all 70 batches (exact args in
reports/discovery/disc002-full-corpus-run.json report_meta.args; ~5 min,
fits one tool call) then `vu discovery-decide` r1 (--decided-utc
2026-10-28T00:45:00Z), r2 (01:30:00Z), batch2 (02:30:00Z), batch3
(2026-10-28T05:30:00Z), batch4 (2026-10-30T13:05:00Z), then `vu
discovery-index`. Expected result: 60,154 records; 51,912 provisional /
6,981 already_covered / 1,258 rejected / 2 confirmed_gap / 1 deferred.
CAUTION (F-0019): compare the regenerated index against the committed
index by PARSED CONTENT (e.g. json.loads each line, re-dump with
sort_keys), not raw sha256 — the recorded hash is script-writer-specific
while the CLI writer escapes Unicode.

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
- F-0018: old extNNN/disc002 helper scripts hardcode
  /home/z/my-project/obsidian-vault-unification-docs — fix paths or use
  the batch-4 repo-relative scripts.
- F-0014 (open): two ai-course files end with 'END OF FILE / File Name'
  marker headings — synthesis must not copy them as knowledge headings.
