# Next Agent Handoff

## Project state

- Current milestone: DISC-002 corpus-wide concept discovery IN PROGRESS —
  session 11 re-verified the baseline (663/663 tests, both vaults
  byte-identical to manifests at start AND end, HEAD == origin/main ==
  ee36362), extended the ADR-0010 replay to ELEVEN decide rounds
  (content-identical to the committed index on the first try), reused the
  fence-aware batch-10 probe pattern unchanged, and completed the batch-11
  review tranche: 27 covers + 33 rejects, no new confirmed gap, no merge.
  After DISC-002: per-domain semantic classification of the
  dossier-extension overlap pairs, then disposition assignment, then GATED
  synthesis.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002
  sessions A+B (merged), sessions 3, 4, 5, 6, 7, 8, 9, 10, and 11 (this
  checkpoint).
- Framework version 0.9.0; 24 capabilities (23 implemented-and-tested +
  1 planned CAP-014 'source-to-output coverage and frequency regression
  reports', synthesis-time; test-verified).
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never
  mark a task completed before its commit exists; always re-run the
  suite after the last mutation).

## Session 11 summary (evidence-backed)

- Baseline verified: 663/663 tests at session start
  (reports/discovery/disc002-session11-baseline-pytest.json); clean tree
  with HEAD == origin/main == ee36362; both vaults byte-identical to
  committed manifests at session start
  (reports/discovery/disc002-session11-manifest-{ai-course,master-ai}.json,
  0 added/removed/changed) and again at session end (-end- reports).
- ADR-0010 replay extended to ELEVEN decide rounds via
  scripts/disc002_batch11_replay.py: `vu discover-gaps` over all 70
  batches (recorded args), then ELEVEN decide rounds replayed with the
  recorded --decided-utc values (r1, r2, batch2..batch10), then `vu
  discovery-index` — CONTENT-IDENTICAL to the committed index (60,154
  records; status counts matched exactly: 51,552/7,115/1,482/3/1/1;
  validate green; F-0019 heeded; ran clean on the first try). NO NEW
  TOOLING DEFECTS this session; the fence-aware probe/verify pattern from
  batch 10 was reused unchanged.
- Batch-11 review tranche: 60 highest-signal unreviewed provisional
  candidates (of 4,574 matching the signal rule — exactly the count the
  session-10 handoff predicted), individually reviewed with a 129-term
  fence-aware definitional-treatment coverage probe
  (scripts/disc002_batch11_probe.py), targeted citation verification
  (scripts/disc002_batch11_verify.py, 102 locator checks, all OK after 5
  pattern fixes — heading-prefix, curly-quote, note-title, **bold**-marker
  and regex-escape classes), and an independent subagent cross-check of
  ALL 60 judgment calls: 60/60 AGREE. Result: 27 evidence-cited covers +
  33 noise rejects.
- Subagent errata were INDEPENDENTLY RE-VERIFIED before incorporation;
  TWO were themselves wrong and rejected (third consecutive session with
  at least one wrong subagent correction — keep the mandatory
  re-verification step): the file name '02 - Conceptual Interview
  Questions 2.md' (actual: '06 - Conceptual Interview Questions 2.md';
  substance was right, locator wrong) and the count '16 computed-gradient
  occurrences' (actual: 13 in ai-course, 0 in master-ai). VERIFIED errata
  incorporated: 'vgg16_bn = VGG16 with Batch Normalization' at PyTorch
  Advanced :28 (not :26); io-aware glossary entries at
  '28 - Glossary/Terms/A-Z Terms.md:98' AND ':135'; full
  rejection-sampling interview treatment at '29 - Interview Prep/
  Conceptual/06 - Conceptual Interview Questions 2.md:102'; DDPM
  cross-vault usage with the forward-process formula at
  '23 - Multimodal AI/Diffusion/05 - DiT and FLUX.md:20' and ':129'.
- NO NEW CONFIRMED GAP this tranche. The one gap-shaped candidate,
  'ddpm' (CG-27d8b1b0734f: cross-vault, 3 homonym clusters, used in
  dependency position across the ai-course 10.4 chapter and master-ai
  DiT/FLUX, with no 'DDPM' heading corpus-wide), resolved as COVER — the
  acronym is EXPANDED in the master-ai glossary: '28 - Glossary/Acronyms/
  Acronyms Index.md:45' '**DDPM** — Denoising Diffusion Probabilistic
  Models', and the underlying algorithm is the subject of the dedicated
  3-note 10.4 Diffusion Models chapter. NEW PROBE LESSON (extends the
  session-10 hyphenation lesson): check the master-ai glossary Acronyms
  Index AND A-Z Terms (and underscore as well as hyphen variants) before
  claiming acronym/term absence. Corpus confirmed_gap total stays 3
  (second moment, bradley-terry, async def).
- Current candidate set: 51,492 provisional / 7,142 already_covered /
  1,515 rejected / 3 confirmed_gap (second moment, bradley-terry, async
  def) / 1 merged / 1 deferred.
- Process note: the delta script's first run failed on ITS OWN
  expectation (expected rejected 1482 instead of 1482+33=1515) while the
  data's status transitions were perfect on the first run — fixed the
  expectation and re-ran to PASS. Always separate "the data is wrong"
  from "my expectation is wrong" before 'fixing' data.

## Next task: DISC-002 continuation

1. **Continue the semantic review in bounded tranches** (51,492
   provisional; ~4,514 more match the signal rule). Reuse the
   REPO-RELATIVE scripts/disc002_batch11_{replay,tranche,probe,decisions,
   verify,delta}.py pattern (edit CAND to point at the current replayed
   state scratch/disc002-s12-batch11.jsonl; new decision IDs
   D-DISC002-B12-****; candidate IDs are asserted against the selection
   file, so a wrong ID fails loudly). The batch-11 probe is fence-aware
   (copied from batch 10) — do NOT revert to a naive startswith('#')
   probe. Standard: individual evidence review with file:line citations
   (full vault-relative paths with chapter-level parents); subagent
   cross-check of judgment calls WITH INDEPENDENT RE-VERIFICATION of
   every subagent correction (three-session pattern: at least one wrong
   correction per session); confirmed gaps are RARE — look for concepts
   used in dependency position with NO definitional treatment anywhere
   under ANY spelling variant, INCLUDING the master-ai glossary Acronyms
   Index and A-Z Terms (ddpm is the model near-miss; async def remains
   the only confirmed gap of this shape).
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

## Replay recipe (ADR-0010, now twelve decide rounds)

`vu discover-gaps` over all 70 batches (exact args in
reports/discovery/disc002-full-corpus-run.json report_meta.args; ~5 min,
fits one tool call) then `vu discovery-decide` r1 (--decided-utc
2026-10-28T00:45:00Z), r2 (01:30:00Z), batch2 (02:30:00Z), batch3
(2026-10-28T05:30:00Z), batch4 (2026-10-30T13:05:00Z), batch5
(15:30:00Z), batch6 (16:30:00Z), batch7 (2026-10-31T00:30:00Z), batch8
(2026-10-31T01:30:00Z), batch9 (2026-10-31T03:00:00Z), batch10
(2026-10-31T05:30:00Z), batch11 (2026-10-31T08:00:00Z), then `vu
discovery-index`. Expected result: 60,154 records; 51,492 provisional /
7,142 already_covered / 1,515 rejected / 3 confirmed_gap / 1 merged / 1
deferred. CAUTION (F-0019): compare the regenerated index against the
committed index by PARSED CONTENT (e.g. json.loads each line), not raw
sha256 — the recorded hash is script-writer-specific while the CLI
writer escapes Unicode. scripts/disc002_batch11_replay.py performs the
whole chain in one run (adjust the output paths for a batch-12 replay or
reuse as-is after adding the batch-11 round to DECIDE_CHAIN: it verifies
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
  If a session lacks credentials, record the blocker exactly per the
  session-8 pattern and make the push the next session's first action.
- F-0016: background processes are reaped between tool calls — long runs
  must fit one tool call (< 10 min); corpus discovery ~5 min; a six-domain
  overlap-candidates sweep takes ~4 min total.
- F-0018: old extNNN/disc002 helper scripts (pre-batch-4) hardcode
  /home/z/my-project/obsidian-vault-unification-docs — fix paths or use
  the batch-4..11 repo-relative scripts.
- F-0020 (fixed, regression-tested): never invoke the CLI via
  `python -m vault_unification.cli` in old checked-out code without the
  guard — use `vu` or `python -m vault_unification` if unsure.
- F-0014 (open): two ai-course files end with 'END OF FILE / File Name'
  marker headings — synthesis must not copy them as knowledge headings.
- Subagent discipline (sessions 9-11): subagent corrections are hints,
  not facts — INDEPENDENTLY RE-VERIFY every correction against the
  corpus before incorporating it (session 9: two wrong corrections;
  session 10: one wrong correction — the false 'no ImageNet normalization
  in the VGG16 Deep Dive note' claim; session 11: one wrong file name and
  one wrong count). Probe/regex searches must account for `\\text{...}`
  wrappers, unicode characters (× vs x), **bold** markers, AND
  hyphenation/spelling variants (unembedding vs un-embedding; vgg16-bn vs
  vgg16_bn; resnet50 vs ResNet-50) inside patterns.
- Probe discipline (sessions 10-11): use the FENCE-AWARE probe pattern
  (scripts/disc002_batch11_probe.py) for all future coverage probes;
  naive startswith('#') heading scans are a closed defect class. Before
  claiming acronym/term absence, ALSO check the master-ai glossary
  ('28 - Glossary/Acronyms/Acronyms Index.md', '28 - Glossary/Terms/
  A-Z Terms.md') — the ddpm near-miss is the model case.
- Delta-verification discipline (session 11): when a delta check fails,
  verify whether the DATA or the EXPECTATION is wrong before changing
  anything; write the arithmetic of expectations down before running.
