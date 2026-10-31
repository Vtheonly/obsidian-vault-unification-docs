# Next Agent Handoff

## Project state

- Current milestone: DISC-002 corpus-wide concept discovery IN PROGRESS —
  session 12 re-verified the baseline (663/663 tests, both vaults
  byte-identical to manifests at start AND end, HEAD == origin/main ==
  6d1cf8e), extended the ADR-0010 replay to TWELVE decide rounds
  (content-identical to the committed index on the first try), reused the
  fence-aware batch-10/11 probe pattern unchanged, and completed the
  batch-12 review tranche: 25 covers + 35 rejects, no new confirmed gap,
  no merge. The session also found and fixed a stale README status
  paragraph (session 11 had missed the README update; it described
  post-batch-10 state). After DISC-002: per-domain semantic
  classification of the dossier-extension overlap pairs, then
  disposition assignment, then GATED synthesis.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002
  sessions A+B (merged), sessions 3, 4, 5, 6, 7, 8, 9, 10, 11, and 12
  (this checkpoint).
- Framework version 0.9.0; 24 capabilities (23 implemented-and-tested +
  1 planned CAP-014 'source-to-output coverage and frequency regression
  reports', synthesis-time; test-verified).
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never
  mark a task completed before its commit exists; always re-run the
  suite after the last mutation).

## Session 12 summary (evidence-backed)

- Baseline verified: 663/663 tests at session start
  (reports/discovery/disc002-session12-baseline-pytest.json); clean tree
  with HEAD == origin/main == 6d1cf8e; both vaults byte-identical to
  committed manifests at session start
  (reports/discovery/disc002-session12-manifest-{ai-course,master-ai}.json,
  0 added/removed/changed).
- ADR-0010 replay extended to TWELVE decide rounds via
  scripts/disc002_batch12_replay.py: `vu discover-gaps` over all 70
  batches (recorded args), then TWELVE decide rounds replayed with the
  recorded --decided-utc values (r1, r2, batch2..batch11), then `vu
  discovery-index` — CONTENT-IDENTICAL to the committed index (60,154
  records; status counts matched exactly: 51,492/7,142/1,515/3/1/1;
  validate green; F-0019 heeded; ran clean on the first try). NO NEW
  TOOLING DEFECTS this session; the fence-aware probe/verify pattern
  from batches 10/11 was reused unchanged.
- Batch-12 review tranche: 60 highest-signal unreviewed provisional
  candidates (of 4,514 matching the signal rule — exactly the count the
  session-11 handoff predicted), individually reviewed with a 137-term
  fence-aware definitional-treatment coverage probe
  (scripts/disc002_batch12_probe.py), targeted citation verification
  (scripts/disc002_batch12_verify.py, 154 locator checks, all OK after 5
  exact-text pattern fixes — heading-form, **bold**-marker,
  missing-word, heading-level and note-title-vs-filename classes), and
  an independent subagent cross-check of ALL 60 judgment calls: 59/60
  first-pass AGREE.
- Subagent errata were INDEPENDENTLY RE-VERIFIED before incorporation;
  THE ONE DISAGREEMENT WAS RIGHT AND THE ORCHESTRATOR WAS WRONG — the
  subagent disproved the orchestrator's confirm_gap claim on 'cifar10':
  a TERM-SEPARATED CIFAR-10 definition exists in the Q11 quiz matching
  block ('c) CIFAR-10 dataset' at '09 - Quizzes and Question Banks/02.
  Deep Learning - Chapter 2 (CNN)/Q11 - The Degradation Problem and
  Residual Connections.md:178' paired with 'n) A popular benchmark
  dataset for deep learning with 60,000 32x32 color images in 10
  classes' at :182, answer key 'c) -> n)' at :190). The definition line
  does NOT contain the string 'CIFAR', which is why the orchestrator's
  term-only grep missed it; the draft confirm_gap was CORRECTED to
  cover before applying. VERIFIED errata incorporated: LogSoftmax
  ':109' belongs to '08. Loss Functions and Optimizers Deep Dive.md'
  (not '02. Loss Functions and Cost Optimization.md'); the
  thought-vector definition is at '06 - Attention
  Mechanisms/Origins/01 - Origins of Attention.md:19' (not the Bahdanau
  2014 note); heading-level corrections (### not ##) for the
  running-stats, SGD and late-interaction headings. FOURTH consecutive
  session with a decisive subagent correction — re-verification cuts
  BOTH ways: verify subagent corrections AND your own gap claims
  against the corpus.
- NO NEW CONFIRMED GAP this tranche. Corpus confirmed_gap total stays 3
  (second moment, bradley-terry, async def).
- Current candidate set: 51,432 provisional / 7,167 already_covered /
  1,550 rejected / 3 confirmed_gap (second moment, bradley-terry, async
  def) / 1 merged / 1 deferred.
- Delta verification PASSED ON THE FIRST RUN — the expectation
  arithmetic was written down BEFORE running (51,492-60 / 7,142+25 /
  1,515+35), applying the session-11 delta-verification discipline.
- README status paragraph was found ONE SESSION STALE (session 11
  missed it; it still described post-batch-10 state) and was updated to
  the post-batch-12 state this session. NEXT SESSIONS: check that the
  README status paragraph is current at session end (add it to the
  end-of-session checklist; it is part of the state-persistence duty).

## Next task: DISC-002 continuation

1. **Continue the semantic review in bounded tranches** (51,432
   provisional; ~4,454 more match the signal rule). Reuse the
   REPO-RELATIVE scripts/disc002_batch12_{replay,tranche,probe,decisions,
   verify,delta}.py pattern (edit CAND to point at the current replayed
   state scratch/disc002-s13-batch12.jsonl; new decision IDs
   D-DISC002-B13-****; candidate IDs are asserted against the selection
   file, so a wrong ID fails loudly). The batch-12 probe is fence-aware
   (inherited from batches 10/11) — do NOT revert to a naive
   startswith('#') probe. Standard: individual evidence review with
   file:line citations (full vault-relative paths with chapter-level
   parents); subagent cross-check of judgment calls WITH INDEPENDENT
   RE-VERIFICATION of every subagent correction AND of every
   orchestrator-proposed confirm_gap (the cifar10 case is the model:
   term-separated definitions defeat term-only search); confirmed gaps
   are RARE — look for concepts used in dependency position with NO
   definitional treatment anywhere under ANY spelling variant,
   INCLUDING the master-ai glossary Acronyms Index and A-Z Terms, AND
   the Group-B description lines of quiz matching blocks (search
   property-based phrases like '60,000 32x32' near term occurrences,
   not just the term).
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

## Replay recipe (ADR-0010, now thirteen decide rounds)

`vu discover-gaps` over all 70 batches (exact args in
reports/discovery/disc002-full-corpus-run.json report_meta.args; ~5 min,
fits one tool call) then `vu discovery-decide` r1 (--decided-utc
2026-10-28T00:45:00Z), r2 (01:30:00Z), batch2 (02:30:00Z), batch3
(2026-10-28T05:30:00Z), batch4 (2026-10-30T13:05:00Z), batch5
(15:30:00Z), batch6 (16:30:00Z), batch7 (2026-10-31T00:30:00Z), batch8
(2026-10-31T01:30:00Z), batch9 (2026-10-31T03:00:00Z), batch10
(2026-10-31T05:30:00Z), batch11 (2026-10-31T08:00:00Z), batch12
(2026-10-31T10:30:00Z), then `vu discovery-index`. Expected result:
60,154 records; 51,432 provisional / 7,167 already_covered / 1,550
rejected / 3 confirmed_gap / 1 merged / 1 deferred. CAUTION (F-0019):
compare the regenerated index against the committed index by PARSED
CONTENT (e.g. json.loads each line), not raw sha256 — the recorded hash
is script-writer-specific while the CLI writer escapes Unicode.
scripts/disc002_batch12_replay.py performs the whole chain in one run
(adjust the output paths for a batch-13 replay or reuse as-is after
adding the batch-12 round to DECIDE_CHAIN: it verifies content-identity
against the committed index automatically).

## Standing rules (unchanged, enforced)

- Never mark a task completed before its commit hash exists in the record.
- Re-run the full suite after the LAST mutation of the session.
- Sources are immutable; all outputs are evidence, never edits.
- Machine locators for every line citation (vault_unification.locators).
- Every completion claim needs a report path or test run as evidence.
- Update the README repository-status paragraph at session end (it was
  found one session stale by session 12; the handoff, current-state and
  checkpoint alone are not enough).
- Push to main before session end; record push verification. When a push
  is rejected because a parallel session moved main: fetch, review their
  commits, MERGE (do not rebase away history), reconcile decisions
  through the audit trail, and re-verify the chain before pushing again.
  If a session lacks credentials, record the blocker exactly per the
  session-8 pattern and make the push the next session's first action.
- F-0016: background processes are reaped between tool calls — long runs
  must fit one tool call (< 10 min); corpus discovery ~5 min; a six-domain
  overlap-candidates sweep takes ~4 min total.
- F-0018: old extNNN/disc002 helper scripts (pre-batch-4) hardcode
  /home/z/my-project/obsidian-vault-unification-docs — fix paths or use
  the batch-4..12 repo-relative scripts.
- F-0020 (fixed, regression-tested): never invoke the CLI via
  `python -m vault_unification.cli` in old checked-out code without the
  guard — use `vu` or `python -m vault_unification` if unsure.
- F-0014 (open): two ai-course files end with 'END OF FILE / File Name'
  marker headings — synthesis must not copy them as knowledge headings.
- Subagent discipline (sessions 9-12): subagent corrections are hints,
  not facts — INDEPENDENTLY RE-VERIFY every correction against the
  corpus before incorporating it (session 9: two wrong corrections;
  session 10: one wrong correction; session 11: one wrong file name and
  one wrong count; session 12: the ONE disagreement was RIGHT and
  overturned the orchestrator's own confirm_gap). Symmetrically,
  re-verify your OWN gap claims before applying them: a term-separated
  definition (quiz matching blocks, glossary cross-references) defeats
  term-only search. Probe/regex searches must account for `\text{...}`
  wrappers, unicode characters (× vs x), **bold** markers, heading
  LEVELS (## vs ###), note titles that differ from filenames, AND
  hyphenation/spelling variants (unembedding vs un-embedding; vgg16-bn
  vs vgg16_bn; resnet50 vs ResNet-50) inside patterns.
- Probe discipline (sessions 10-12): use the FENCE-AWARE probe pattern
  (scripts/disc002_batch12_probe.py) for all future coverage probes;
  naive startswith('#') heading scans are a closed defect class. Before
  claiming acronym/term absence, ALSO check the master-ai glossary
  ('28 - Glossary/Acronyms/Acronyms Index.md', '28 - Glossary/Terms/
  A-Z Terms.md') — the ddpm near-miss is the model case — AND the
  Group-B description lines of quiz matching blocks near every term
  occurrence (the cifar10 near-miss is the model case: the definition
  '60,000 32x32 color images in 10 classes' at Q11:182 does not contain
  the string 'CIFAR').
- Delta-verification discipline (sessions 11-12): write the arithmetic
  of expectations down BEFORE running (e.g. 51,492-60 / 7,142+25 /
  1,515+35); when a delta check fails, verify whether the DATA or the
  EXPECTATION is wrong before changing anything.
