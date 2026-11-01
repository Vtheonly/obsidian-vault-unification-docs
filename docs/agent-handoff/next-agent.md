# Next Agent Handoff

## Project state

- Current milestone: DISC-002 **signal-pool review COMPLETE** — session 16
  (2026-11-01) executed the user-authorized accelerated completion mode
  (ADR-0011) and decided ALL 4,274 remaining signal-rule candidates in one
  session: 667 covers + 3,607 rejects + 0 new confirmed gaps. The corpus
  confirmed_gap total remains 3 (second moment, bradley-terry, async def).
- USER DIRECTIVE IN FORCE (2026-11-01): "remove the universal
  review and do it fast then ... the final vault should be done in
  less than 12 additional sessions". **BINDING POLICY IN FORCE
  (session 17, ADR-0012): read `docs/ACCELERATED_COMPLETION_POLICY.md`
  and AGENTS.md §12 BEFORE planning.** Hard deadline: final vault by
  the END OF SESSION 26 (strict reading: sessions 16-26 = 11; this
  supersedes the earlier "session 27" wording). Deliverable-first
  reporting; tiered verification only (ADR-0011); a bookkeeping-only
  session is a FAILED session; every checkpoint carries the
  `accelerated_mode` block; budget after session 17: 9 sessions
  remaining.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002 sessions
  A+B (merged), 3-15 (60-candidate tranches), and 16 (this session —
  4,274 candidates, the whole remaining signal pool).
- Current candidate ledger: 46,978 provisional (documented low-signal
  exclusion: max score 0.77, max contexts 9, no fragmented derivations;
  the 6,404 rare_essential members are single-occurrence score-0.43
  numeric-led extraction noise, structurally below the confirm_gap
  dependency bar, which requires cross-context recurrence) / 7,893
  already_covered / 5,278 rejected / 3 confirmed_gap / 1 merged / 1
  deferred. Index committed at
  state/concept-candidates/002-disc002-full-corpus.index.jsonl; validate
  green (60,154 records, 0 errors).
- Framework version 0.9.0; 663/663 tests at session start AND re-run
  after the last mutation (both first-run passes after the documented
  editable install).

## Session 16 summary (evidence-backed)

- Baseline verified: clean tree, HEAD == origin/main == 182ac37; both
  vaults byte-identical to committed manifests (scratch/
  disc002-s16-manifest-{ai-course,master-ai}.json, 0 diffs); 663/663
  tests first-run (scratch/disc002-s16-baseline-pytest.json).
- ADR-0011 written and committed BEFORE the mode change was applied:
  calibrated bulk decisions + tiered verification; approval evidence =
  the user's 2026-11-01 direction, recorded verbatim in the ADR.
- Sixteen-round ADR-0010 replay (scripts/disc002_batch16_replay.py, new):
  content-identical to the committed index ON THE FIRST TRY
  (51,252/7,226/1,671/3/1/1); CAND preserved at
  scratch/disc002-s16-batch15.jsonl; delete-as-consumed disk pattern kept.
- Tiered pipeline over the 4,274-candidate signal pool:
  1. scripts/disc002_batch16_calibrate.py — joined all 2,063 committed
     decisions with candidate features; NO term-shape class was 100%
     predictive (verb_single had 1 cover, code_identifier 5, fragment 6),
     proving citation-evidence classes (not term shape) must drive bulk
     decisions.
  2. scripts/disc002_batch16_rfilter.py — second lexicon layer; the
     CALIBRATION REJECTED the first attempt (ends-everyday: 20 covers;
     greedy vault-meta regex matched the confirmed cover 'class index');
     after tightening, R2/R3aux/R4 passed 50/50, 1/1, 2/2.
  3. scripts/disc002_batch16_assemble.py — final classification:
     318 validated noise rejects + 290 citation-backed P-covers (heading
     or fence-aware def-window hits, F-0021-fixed fence_spans, def-window
     citations re-derived to the TERM's own line) + 3,666-candidate review
     bundle in 6 slices. Attempted classes N11/N12/N13 were calibration-
     rejected ('use tools', 'chapter 07', '13 inference', '20 tokens per'
     are legitimate covers) and routed to review.
  4. Six parallel review subagents (S16-R1..R6, one slice of ~611 each)
     with the 15-session precedent rubric: 3,299 rejects / 366 covers /
     1 gap_watch.
  5. scripts/disc002_batch16_verifyreview.py — orchestrator verification:
     0 missing/extra/duplicate decisions; EVERY cover citation checked
     against the corpus (322 direct OK; 44 flagged → 43 were citation-
     FORMAT variants re-verified OK, 1 'resnets' manually confirmed);
     150-reject random sample (4.6%) personally re-reviewed: ~97%
     agreement, ALL disagreements conservative reject→cover overrides,
     ZERO hidden gaps; the flagged borderline terms (SAM, llm-as-judge,
     open-weights, gaussian processes, micro-batch, all-reduce,
     adversarial inputs, kernel fusion, bleu, slo, credit assignment)
     were individually corpus-probed by the orchestrator.
  6. scripts/disc002_batch16_finalize.py — 11 orchestrator overrides
     applied (each with an independently verified citation), the single
     gap_watch 'credit assignment' OVERTURNED to cover (three in-situ
     colon-glosses: Policy Gradients and Actor Critic.md:57, Process
     Reward Models 2023.md:23, Verifiable Rewards vs PRMs.md:31 — the
     gap dependency test fails), final file
     state/concept-candidates/002-disc002-decisions-batch16.jsonl
     (4,274 decisions, IDs D-DISC002-B16-0001..4274).
- Applied via `vu discovery-decide --decided-utc 2026-11-01T22:30:00Z`
  (decisions_applied cumulative 6,338 = 2,064 + 4,274); index regenerated
  and DELTA-VERIFIED against PRE-WRITTEN arithmetic on the first try:
  provisional 51,252−4,274=46,978; already_covered 7,226+667=7,893;
  rejected 1,671+3,607=5,278; exactly 4,274 records changed, 55,880
  unchanged; `vu discovery-validate` green; 663/663 tests re-run after
  the last mutation.
- Signal pool verified EMPTY afterwards: 0 unreviewed candidates match
  the signal rule (fragmented_derivation OR score ≥ 0.8 OR contexts ≥
  10).

## Next task (in order, per the binding session budget — see the session
ledger in docs/ACCELERATED_COMPLETION_POLICY.md; deadline: session 26)

1. **DOSSIER-EXTENSION CLASSIFICATION** (next session's main work; the
   69,185 overlap pairs across six domains). Regenerate the six pairs
   files via the commands recorded in
   reports/dossier-ext/disc002-dext-<domain>-overlap-run.json (~4 min
   total, F-0016). Then apply ADR-0011 tiering PER DOMAIN:
   - Tier A (auto-participate): pair evidence where the new-KU source
     file lives in a domain-relevant folder AND the matched term is
     domain-specific — accept with rule + calibration against the 164
     hand-classified EXT-003..010 records (state/classifications/
     001..007). 
   - Tier B (auto-non-participate): broad-term-only matches (the
     topics_at_pair_cap_250 lists in reports/dossier-ext/
     disc002-dext-summary.json show the broad terms: 'scale', 'noise',
     'distance', 'labels', ...) from non-domain files — reject-pair with
     rationale.
   - Tier C (ambiguous middle): parallel subagent review with evidence
     bundles (the session-16 pattern), orchestrator citation checks +
     sampling.
   - Extend each domain's state/classifications/00X file, regenerate
     dossiers via the ext006 rule set (scripts/ext006_dossiers.py),
     keep --check byte-identity for the six committed dossier versions
     until each extension lands as a new version. NO bulk absorption of
     term matches.
2. **DISPOSITION ASSIGNMENT** (Unaccounted blocks release; 27,536 KUs).
   Rule-driven from classification + dossier + file-level synthesis
   mapping; exceptions to individual review.
3. **GATED SYNTHESIS** (the actual vault; MUST START by session 23 per
   the policy anti-stall rules): check-prompt → bounded
   generation → lint-artifacts → assess-quality → quality-drift →
   quality-gate → repair loop per batch. Target: final vault by the
   end of session 26 (11 sessions from session 16; sessions 18-26
   remain).

## Replay recipe (ADR-0010, now SEVENTEEN decide rounds)

`vu discover-gaps` over all 70 batches (exact args in
reports/discovery/disc002-full-corpus-run.json report_meta.args; ~5 min)
then `vu discovery-decide` r1 (2026-10-28T00:45:00Z), r2 (01:30:00Z),
batch2 (02:30:00Z), batch3 (2026-10-28T05:30:00Z), batch4
(2026-10-30T13:05:00Z), batch5 (15:30:00Z), batch6 (16:30:00Z), batch7
(2026-10-31T00:30:00Z), batch8 (01:30:00Z), batch9 (03:00:00Z), batch10
(05:30:00Z), batch11 (08:00:00Z), batch12 (10:30:00Z), batch13
(13:30:00Z), batch14 (2026-11-01T03:30:00Z), batch15 (04:15:00Z),
batch16 (2026-11-01T22:30:00Z), then `vu discovery-index`. Expected:
60,154 records; 46,978 provisional / 7,893 already_covered / 5,278
rejected / 3 confirmed_gap / 1 merged / 1 deferred. F-0019: compare
PARSED CONTENT, not raw sha256. scripts/disc002_batch16_replay.py is
the template — extend DECIDE_CHAIN with the batch16 round for future
replays and keep the delete-as-consumed disk pattern.

## Standing rules (enforced; ADR-0011 modifies the review tiering only)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Machine locators for every line citation
  (vault_unification.locators); F-0021-fixed fence_spans(struct,
  total_lines) signature; LEVEL-EXACT '^### '-style heading patterns
  with the startup guard that rejects '^#+'.
- Every completion claim needs a report path or test run as evidence.
- Update the README repository-status paragraph at session end.
- Push to main before session end; record push verification; if a push
  is rejected because a parallel session moved main: fetch, review,
  MERGE (never rebase away history), reconcile, re-verify.
- ADR-0011 discipline: bulk classes need ZERO counter-examples in the
  calibration set — CALIBRATE BEFORE APPLYING (session 16's own
  lexicon attempts failed calibration three times: ends-everyday,
  greedy vault-meta, N11/N12/N13; the failures were caught by the
  calibration step, which is the point). confirm_gap is NEVER
  bulk-decided; every proposed gap keeps individual verification with
  the full probe discipline (glossaries, quiz Group-B lines, notation
  symbol glosses, operational definitions, spelling variants,
  colon-glosses — the credit-assignment overturn shows why).
- Subagent discipline: subagent decisions are verified, not trusted —
  mechanically check every cover citation, sample the rejects (~5%),
  personally re-verify every flagged borderline; session 16 measured
  ~97% sample agreement with all disagreements in the safe direction.
- Delta-verification discipline: write the arithmetic of expectations
  down BEFORE running.
- Fresh-sandbox setup: `python3 -m pip install -e .` BEFORE the baseline
  pytest (sessions 13-16 first-run passes).
- F-0016: long runs must fit one tool call (< 10 min). F-0018: old
  pre-batch-4 scripts hardcode /home/z/my-project/obsidian-vault-
  unification-docs. F-0020: invoke via `vu` or
  `python -m vault_unification`. F-0014 (open): two ai-course files end
  with 'END OF FILE / File Name' marker headings — synthesis must not
  copy them as knowledge headings.

## Explicit non-claims

- The 46,978 low-signal provisional candidates were NOT individually
  reviewed; they are a documented exclusion under the batch-3..16
  signal-rule standard (their max score 0.77 / max contexts 9 sit below
  every reviewed tranche; single-occurrence rare_essential members
  cannot meet the confirm_gap dependency bar). If the user or a future
  gate requires it, the session-16 tiered pipeline can sweep them —
  but that was NOT done.
- Dossier-extension classification, disposition assignment, and
  synthesis have NOT started; the 69,185 pairs are still unclassified
  and all 27,536 KUs remain Unaccounted by design.
- The three confirmed gaps (second moment, bradley-terry, async def)
  still need their dedicated treatments at synthesis time.
