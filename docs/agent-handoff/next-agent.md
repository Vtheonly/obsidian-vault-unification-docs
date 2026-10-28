# Next Agent Handoff

## Project state

- Current milestone: DISC-002 corpus-wide concept discovery IN PROGRESS —
  session 3 (post-merge) completed a full review tranche (batch 3) and the
  mechanical stage of the dossier extension. After DISC-002: per-domain
  classification of the extension overlap pairs, then disposition
  assignment, then GATED synthesis.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000, AUDIT-011,
  FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002 sessions A+B (merged)
  and session 3 (this checkpoint).
- Framework version 0.9.0; 24 capabilities.
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never mark
  a task completed before its commit exists; always re-run the suite after
  the last mutation).

## Session 3 summary (evidence-backed)

- Baseline verified: 662/662 tests; both vaults byte-identical to manifests at
  session start AND after all operations.
- ADR-0010 replay verified end-to-end: regenerated candidates are
  byte-identical (sha256 88a538eb...), r1+r2+batch2 replayed with the recorded
  --decided-utc values, statuses matched the committed index exactly
  (52032/6907/1212/2/1), discovery-validate green.
- Batch-3 review tranche: 60 highest-signal unreviewed provisional candidates
  (of 5,054 matching the signal rule), individually reviewed with a 44-term
  definitional-treatment coverage probe
  (scripts/disc002_batch3_probe.py) and an independent subagent cross-check of
  the 16 judgment calls. The subagent disagreed on 3 (input shape, scaling
  laws predict, training diverges); the orchestrator re-verified each cited
  treatment and accepted all 3 revisions. Result: 38 evidence-cited covers +
  22 noise rejects. No new confirmed gaps (2 remain: second moment,
  bradley-terry).
- Fragment-boundary rule now recorded in the decision file: fragments that
  LEXICALLY name a covered parent concept -> cover; synonymy-only parents ->
  reject. This resolves a recurring review ambiguity consistently.
- Dossier-extension mechanical stage COMPLETE for all six domains:
  vu overlap-candidates over the 59 regen batches with each domain's term map
  (reports/dossier-ext/disc002-dext-summary.json): 69,185 candidate pairs;
  1,660-5,524 distinct new KUs per domain. Pairs live in scratch,
  regenerable ~40s/domain via the recorded commands.
- Current candidate set: 51,972 provisional / 6,945 already_covered /
  1,234 rejected / 2 confirmed_gap / 1 deferred.

## Next task: DISC-002 continuation

1. **Continue the semantic review in bounded tranches** (51,972 provisional;
   4,994 more match the signal rule). Reuse scripts/disc002_batch3_tranche.py
   (selection + brief), scripts/disc002_batch3_probe.py (coverage probe —
   edit TERMS), and the batch-3 decision-file pattern
   (scripts/disc002_batch3_decisions.py). Standard: individual evidence review
   with file:line citations; subagent cross-check of judgment calls; confirmed
   gaps are RARE — look for concepts used in dependency position with NO
   definitional treatment anywhere.
2. **Dossier extension classification** (per domain, bounded batches):
   review the overlap candidate pairs in scratch (regenerate via the commands
   in reports/dossier-ext/disc002-dext-<domain>-overlap-run.json if needed),
   classify with dossier discipline (new-KU side must have real domain
   participation, not a broad-term hit), extend the domain's
   state/classifications/ file, regenerate dossiers with the ext006 rule set,
   and keep --check byte-identity for the six committed dossiers until their
   extension lands as a new version. NO bulk absorption of term matches.
3. **Then disposition assignment** (Unaccounted blocks release) and GATED
   synthesis: check-prompt -> generation -> lint-artifacts -> assess-quality
   -> quality-drift -> quality-gate -> repair loop per batch.

## Replay recipe (ADR-0010, now four decide rounds)

`vu discover-gaps` over all 70 batches (exact args in
reports/discovery/disc002-full-corpus-run.json report_meta.args; ~5 min,
fits one tool call) then `vu discovery-decide` r1 (--decided-utc
2026-10-28T00:45:00Z), r2 (01:30:00Z), batch2 (02:30:00Z), batch3
(2026-10-28T05:30:00Z), then `vu discovery-index`. Expected result:
60,154 records; 51,972 provisional / 6,945 already_covered / 1,234 rejected /
2 confirmed_gap / 1 deferred.

## Standing rules (unchanged, enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Machine locators for every line citation (vault_unification.locators).
- Every completion claim needs a report path or test run as evidence.
- Push to main before session end; record push verification. When a push is
  rejected because a parallel session moved main: fetch, review their
  commits, MERGE (do not rebase away history), reconcile decisions through
  the audit trail, and re-verify the chain before pushing again.
- F-0016: background processes are reaped between tool calls — long runs
  must fit one tool call (< 10 min); corpus discovery ~5 min; a six-domain
  overlap-candidates sweep takes ~4 min total.
- F-0014 (open): two ai-course files end with 'END OF FILE / File Name'
  marker headings — synthesis must not copy them as knowledge headings.
