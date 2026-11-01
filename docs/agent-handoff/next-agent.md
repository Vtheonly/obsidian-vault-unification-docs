# Next Agent Handoff

## Project state

- Current milestone: DISC-002 **dossier-extension classification COMPLETE** —
  session 18 (2026-11-01) classified ALL 69,185 extension pairs in one
  session under the ADR-0011/ADR-0012 accelerated mode: 5,441 participate /
  63,744 reject-pair; 5,168 distinct extension participant KUs; 294
  term-level extension classification records; 4,893 subagent+orchestrator
  review verdicts. The S18–20 phase target finished one session early.
- USER DIRECTIVE IN FORCE (2026-11-01): BINDING POLICY (ADR-0012): read
  `docs/ACCELERATED_COMPLETION_POLICY.md` and AGENTS.md §12 BEFORE planning.
  Hard deadline: final vault by the END OF SESSION 26. Budget after session
  18: 8 sessions remaining. Deliverable-first reporting; a bookkeeping-only
  session is a FAILED session; every checkpoint carries the
  `accelerated_mode` block; synthesis MUST START by session 23.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002 sessions
  A+B, 3–16 (signal pool: 4,274 decided in session 16; pool verified empty;
  46,978 low-signal documented exclusion; 3 confirmed gaps: second moment,
  bradley-terry, async def), 17 (policy), 18 (this dossier-extension
  classification).
- Framework version 0.9.0; 663/663 tests at session start (first run after
  editable install) and re-run after the last mutation.

## Session 18 summary (evidence-backed)

- Baseline verified: clean tree, HEAD == origin/main == 4361229; AI Course
  276/276 and Master AI 333/333 byte-identical to committed manifests;
  663/663 tests first-run.
- Regenerated all six extension pair files (69,185 pairs; counts exactly
  match the committed run reports). All pairs are cross-vault NEW-KU pairs
  from the 59 regen batches (the original domain files live in ext batches
  001–011 and are excluded from the regen pool by construction).
- Tiering (scripts/s18_dext_tiering.py + state/term-maps/dext-tier-config-v1.json):
  per-side verdicts — A1 auto-participate (domain folder + specific term via
  STRONG alias), A2 auto-participate (specific term + heading/definition-
  window evidence anywhere, session-16 cover evidence class), B1 broad-term-
  only non-domain reject, B2 no-gloss-evidence non-domain reject, nav-file
  reject; quiz/interview folders exempt from B2. CALIBRATION: C1-folder +
  C2 zero-counter-example tests against the 164 hand-classified EXT-003..010
  records and the six original pair pools — the engine exits non-zero on any
  counter-example; calibration caught and fixed 3 real issues during design
  (broad terms that anchored hand-accepted evidence were removed from the
  broad lists; code-block-only matches moved from auto-reject to review).
- Two ADR-0011 pull-backs after orchestrator sampling found wrong-class
  members: (1) WEAK ALIASES (singular, default, ones, rotate, closed-form
  solution, shrinks, decay, MAP, Bayes, …) pulled from auto-accept to review;
  (2) CANONICAL HOMONYMS (compound, cycle, catastrophic, identity,
  orthogonal, flat, spikes, gain, shrink for training-stability; L1/L2 for
  generalization; precision for evaluation) pulled to review. Residual Tier A
  noise after both: ~17% single-side over-inclusion, safe direction only
  (documented in reports/dossier-ext/s18-dext-final-report.json; further
  pull-backs were assessed and rejected as they would effectively reinstate
  the universal review ADR-0011 removed).
- Four review rounds (2,482 (file,term) combos / 4,893 (domain,file,term,ku)
  verdicts): round 1 six domain subagents; round 2 five delta subagents +
  orchestrator personal review of 9 tiny evaluation/clustering combos; round 3
  three delta subagents; round 4 one micro-bundle subagent (251 KU-level
  coverage gaps after the calibration iterations). Mechanical verification
  after every round: completeness (every combo line, every ku_id exactly
  once) + citation anchors (every reviewed-accept has the term/alias/
  matched_text in the KU excerpt or match context; 0 failures).
- Orchestrator sampling per ADR-0011 tier-(b): 179/539 reviewed-rejects (5%
  min-30 per domain) personally re-reviewed — 99.4% agreement, 1
  conservative reject→participate override; Tier A fresh 30-sample (~17%
  safe over-inclusion); Tier B 20-sample (19/20, the one borderline was a
  thin symptom line whose full treatment is in-domain); Tier B3 15-sample
  (1 prose-definition miss overridden to participate). Both overrides are
  recorded in scripts/s18_dext_assembly.py OVERRIDES and in the verdicts
  file with round='orchestrator-override'.
- Final assembly (scripts/s18_dext_assembly.py): review verdicts override
  mechanical verdicts; pair participates iff BOTH sides participate; KU joins
  the extension set iff ≥1 participate side verdict. Pre-written arithmetic
  asserted first try: 69,185 = 9,211+10,833+10,603+6,672+11,275+20,591;
  participate+reject-pair = total.
- Final gates (scripts/s18_final_gates.py): G1 extension-record ku_ids all
  exist in regen batches; G2 unique classification ids; G3 review-verdict
  ku_ids exist; G4 69,185 decisions; G5 source manifests unchanged after ALL
  operations; G6 verification evidence appended to the final report.

## Committed session-18 artifacts (the durable state)

- `state/classifications/008-disc002-dext-review-verdicts.jsonl` — 4,893
  effective review decisions (domain, file, term, ku_id, verdict, round,
  rationale, source). THE irreplaceable decision record.
- `state/classifications/009..014-disc002-dext-<domain>-extension.jsonl` —
  294 term-level extension classification records (topic "<term> — corpus
  extension evidence", ku_ids, evidence quotes, overlap_type Complementary
  Content, full method/rationale). Dossier-v2 input.
- `state/term-maps/dext-tier-config-v1.json` — the calibrated tier config
  (broad_terms, domain_folders, nav_rules, weak_aliases).
- `scripts/s18_*.py` — tiering, bundle builder, verifiers, assembly, gates
  (all deterministic; pair decisions replay from committed inputs).
- `reports/dossier-ext/s18-tiering-report.json` and
  `reports/dossier-ext/s18-dext-final-report.json`.
- `state/checkpoints/checkpoint-2026-11-01-disc002-session18.json`.

## Next task (in order, per the binding session budget — deadline: session 26)

1. **DOSSIER V2 REGENERATION** (bounded, mechanical): extend
   scripts/ext006_dossiers.py DOMAINS config per domain with (a) the regen
   batches that cover the extension KUs (state/knowledge-units/012..070) and
   (b) the new extension classification file (009..014). Emit NEW dossier
   versions (dossier_id `<domain>-v2`, version "v2"); keep the committed v1
   dossiers untouched and `--check`-able. V1–V5 validations must pass (every
   extension ku_id resolves in the regen batches — note KUs come from ALL 59
   regen batches, so the v2 domain config must include them or the loader
   must be extended); add/extend tests; regenerate the coverage report.
   Acceptance: v2 dossiers regenerate byte-identically on re-run; every
   extension KU appears in ≥1 v2 concept; all 514 original participating KUs
   still present; full suite green.
2. **DISPOSITION ASSIGNMENT** (S21–22 target, currently ahead of schedule):
   rule-driven dispositions for the 27,536 KUs from classification + dossier
   membership + file-level synthesis mapping; exceptions to individual
   review; Unaccounted → 0 (release blocker).
3. **GATED SYNTHESIS** (MUST START by session 23): check-prompt → bounded
   generation → lint-artifacts → assess-quality → quality-drift →
   quality-gate → repair loop per batch. The three confirmed gaps (second
   moment, bradley-terry, async def) get their dedicated treatments. Target:
   final vault by end of session 26.

## Replay recipe (ADR-0010 decide chain — unchanged, SEVENTEEN rounds)

`vu discover-gaps` over all 70 batches (exact args in
reports/discovery/disc002-full-corpus-run.json report_meta.args; ~5 min) then
`vu discovery-decide` r1 (2026-10-28T00:45:00Z), r2 (01:30:00Z), batch2
(02:30:00Z), batch3 (2026-10-28T05:30:00Z), batch4 (2026-10-30T13:05:00Z),
batch5 (15:30:00Z), batch6 (16:30:00Z), batch7 (2026-10-31T00:30:00Z),
batch8 (01:30:00Z), batch9 (03:00:00Z), batch10 (05:30:00Z), batch11
(08:00:00Z), batch12 (10:30:00Z), batch13 (13:30:00Z), batch14
(2026-11-01T03:30:00Z), batch15 (04:15:00Z), batch16 (2026-11-01T22:30:00Z),
then `vu discovery-index`. Expected: 60,154 records; 46,978 provisional /
7,893 already_covered / 5,278 rejected / 3 confirmed_gap / 1 merged / 1
deferred. F-0019: compare PARSED CONTENT, not raw sha256.
scripts/disc002_batch16_replay.py is the template.

Dossier-extension replay (session-18 layer): regenerate the six pair files
via the commands in reports/dossier-ext/disc002-dext-<domain>-overlap-run.json
(~40s per domain; the term map for tree is state/term-maps/tree-domain-v1.json),
then `python3 scripts/s18_dext_tiering.py` (calibration must pass),
`python3 scripts/s18_build_review_bundles.py`, then
`python3 scripts/s18_dext_assembly.py` — the review verdicts are COMMITTED
(008 file), so review rounds do NOT re-run; the assembly reproduces pair
decisions and extension records deterministically from committed state.

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
  calibration set — CALIBRATE BEFORE APPLYING (session 18's own tiering
  was caught by its calibration three times: broad terms anchoring
  hand-accepted evidence; code-block-only matches; then the sampling
  pull-backs for weak aliases and canonical homonyms — the failures were
  caught by the calibration/sampling steps, which is the point).
  confirm_gap is NEVER bulk-decided; every proposed gap keeps individual
  verification with the full probe discipline (glossaries, quiz Group-B
  lines, notation symbol glosses, operational definitions, spelling
  variants, colon-glosses).
- Subagent discipline: subagent decisions are verified, not trusted —
  mechanically check completeness and citation anchors, sample the rejects
  (~5%), personally re-verify every flagged borderline; session 18 measured
  99.4% sample agreement with the disagreement in the safe direction.
- Delta-verification discipline: write the arithmetic of expectations
  down BEFORE running.
- Fresh-sandbox setup: `python3 -m pip install -e .` BEFORE the baseline
  pytest.
- F-0016: long runs must fit one tool call (< 10 min). F-0018: old
  pre-batch-4 scripts hardcode /home/z/my-project/obsidian-vault-
  unification-docs. F-0020: invoke via `vu` or
  `python -m vault_unification`. F-0014 (open): two ai-course files end
  with 'END OF FILE / File Name' marker headings — synthesis must not
  copy them as knowledge headings.

## Explicit non-claims

- The 46,978 low-signal provisional discovery candidates were NOT
  individually reviewed (documented exclusion under the batch-3..16
  signal-rule standard).
- Dossier v2 has NOT been regenerated yet: the 294 extension records are
  committed and ready, but the six dossiers on disk are still v1; extension
  KUs are not yet inside any dossier JSON.
- Disposition assignment has NOT started: all 27,536 KUs remain
  Unaccounted by design (release blocker until S21–22 work).
- The three confirmed gaps (second moment, bradley-terry, async def)
  still need their dedicated treatments at synthesis time.
- Tier A auto-accepts retain ~17% single-side over-inclusion (safe
  direction, documented); B2 can miss prose definitions without
  colon-gloss markers (measured ~1/35 in sampling; override mechanism
  exists).
