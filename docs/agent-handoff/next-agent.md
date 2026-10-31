# Next Agent Handoff

## Project state

- Current milestone: DISC-002 corpus-wide concept discovery IN PROGRESS —
  session 13 re-verified the baseline (663/663 tests after the documented
  editable install; both vaults byte-identical to manifests at start AND
  end, HEAD == origin/main == c8fcfb8 at start), extended the ADR-0010
  replay to THIRTEEN decide rounds (content-identical to the committed
  index on the first try), reused the fence-aware batch-10/11/12 probe
  pattern unchanged, and completed the batch-13 review tranche: 30 covers
  + 30 rejects, no new confirmed gap, no merge. The subagent cross-check
  returned 60/60 first-pass AGREE — the first fully-agreeing tranche
  since the discipline began. After DISC-002: per-domain semantic
  classification of the dossier-extension overlap pairs, then
  disposition assignment, then GATED synthesis.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002
  sessions A+B (merged), sessions 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, and
  13 (this checkpoint).
- Framework version 0.9.0; 24 capabilities (23 implemented-and-tested +
  1 planned CAP-014 'source-to-output coverage and frequency regression
  reports', synthesis-time; test-verified).
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never
  mark a task completed before its commit exists; always re-run the
  suite after the last mutation).
- FRESH-SANDBOX NOTE (session-13 lesson): run `python3 -m pip install
  -e .` BEFORE the baseline pytest — tests/test_discovery.py spawns
  `python -m vault_unification` as a subprocess, which requires the
  editable install (FRAMEWORK_SETUP.md style 2). Without it the suite
  fails 662/663 on that one test; this is environment setup, not a code
  defect.

## Session 13 summary (evidence-backed)

- Baseline verified: 663/663 tests at session start
  (reports/discovery/disc002-session13-baseline-pytest.json; the first
  run failed 662/663 in the un-installed sandbox — see the fresh-sandbox
  note); clean tree with HEAD == origin/main == c8fcfb8; both vaults
  byte-identical to committed manifests at session start
  (reports/discovery/disc002-session13-manifest-{ai-course,master-ai}.json,
  0 added/removed/changed).
- ADR-0010 replay extended to THIRTEEN decide rounds via
  scripts/disc002_batch13_replay.py: `vu discover-gaps` over all 70
  batches (recorded args), then THIRTEEN decide rounds replayed with the
  recorded --decided-utc values (r1, r2, batch2..batch12), then `vu
  discovery-index` — CONTENT-IDENTICAL to the committed index (60,154
  records; status counts matched exactly: 51,432/7,167/1,550/3/1/1;
  validate green; F-0019 heeded; ran clean on the first try). NO NEW
  TOOLING DEFECTS this session; the fence-aware probe/verify pattern
  from batches 10/11/12 was reused unchanged.
- Batch-13 review tranche: 60 highest-signal unreviewed provisional
  candidates (of 4,454 matching the signal rule — exactly the count the
  session-12 handoff predicted), individually reviewed with a ~230-term
  fence-aware definitional-treatment coverage probe
  (scripts/disc002_batch13_probe.py), targeted citation verification
  (scripts/disc002_batch13_verify.py, 160 locator checks, all OK after
  pattern fixes — heading-number prefixes like '# 14 - Learning Rate
  Schedules', bold-marker placement like '**TN** (True Negative)',
  unicode-× vs LaTeX \times regex escaping (in regex \t means TAB;
  literal '\times' needs '\\times'), and LaTeX-command escaping ('\cos'
  is a bad escape; use '\\cos')), and an independent subagent
  cross-check of ALL 60 judgment calls: 60/60 first-pass AGREE.
- Subagent errata were INDEPENDENTLY RE-VERIFIED before incorporation;
  ONE ACCEPTED, ONE REJECTED: ACCEPTED — a symbol gloss '- $\hat{y}$ is
  the predicted label.' exists at master-ai '04 - Neural
  Networks/Foundations/01 - Perceptrons and MLPs.md:63' (it defines the
  symbol ŷ, not the phrase as a unit, so the 'predicted labels' reject
  stands; the rationale now cites it as concept-side coverage).
  REJECTED — the subagent claimed the latent-representation definition
  sits at '02. The Information Bottleneck and Latent Space.md:14';
  direct line inspection AND the regex verify both place it at :15 (the
  original citation stands). FIFTH consecutive session with subagent
  erratum re-verification required — it cuts BOTH ways: verify subagent
  corrections AND your own claims against the corpus.
- NO NEW CONFIRMED GAP this tranche. Gap-shaped candidates resolved:
  'still sota' COVER via the master-ai glossary SOTA entry ('28 -
  Glossary/Acronyms/Acronyms Index.md:177' — the batch-11 ddpm
  precedent applied); 'runtimeerror' COVER via the dedicated '8. Error
  Handling and Exception Management' note (ai-course '02.2 - Python
  Programming Essentials/08. Error Handling and Exception
  Management.md:1' teaches try/except/else/finally, the
  common-exception catalog and raise) plus in-situ PyTorch cause/fix
  diagnostics (channel mismatch '04. Demystifying Tensors.md:134',
  backward-twice master-ai '06 - Backpropagation.md:262', view-vs-
  reshape master-ai '06 - Tensors and Broadcasting.md:349', device
  mismatch '02. Common Mistakes.md:184') — the async def
  zero-treatment standard is NOT met; 'def' COVER via the dedicated
  Functions note ('05. Functions and Lambda Expressions.md:3' '##
  5.1 Defining Functions'); 'super' COVER via the dedicated OOP note
  ('## 6.3 Inheritance' :33 with the in-line super() gloss :40);
  'lfloor'/'rfloor'/'cos'/'sin' REJECTED as LaTeX command artifacts
  whose concept side is covered (floor function '05. The Output Spatial
  Dimension Formula.md:98' heading + '01. The Convolution Operation
  Deep Dive.md:258' definition; dedicated cosine-similarity note;
  dedicated sinusoidal positional-encoding note; Fourier components
  '4.2 The Fourier Transform.md:28'). Corpus confirmed_gap total stays
  3 (second moment, bradley-terry, async def).
- Current candidate set: 51,372 provisional / 7,197 already_covered /
  1,580 rejected / 3 confirmed_gap (second moment, bradley-terry, async
  def) / 1 merged / 1 deferred.
- Delta verification PASSED — the expectation arithmetic was written
  down BEFORE running (51,432-60 / 7,167+30 / 1,550+30). One iteration:
  the first delta run failed because the SCRIPT's embedded
  expected_counts still held the pre-batch13 values; the per-record
  checks were green and the data matched the pre-written arithmetic, so
  per the session-11 lesson the EXPECTATION side was identified as
  wrong and patched; no data was touched.

## Next task: DISC-002 continuation

1. **Continue the semantic review in bounded tranches** (51,372
   provisional; 4,394 more match the signal rule). Reuse the
   REPO-RELATIVE scripts/disc002_batch13_{replay,tranche,probe,decisions,
   verify,delta}.py pattern (edit CAND to point at the current replayed
   state scratch/disc002-s14-batch13.jsonl; new decision IDs
   D-DISC002-B14-****; candidate IDs are asserted against the selection
   file, so a wrong ID fails loudly). The batch-13 probe is fence-aware
   (inherited from batches 10/11/12) — do NOT revert to a naive
   startswith('#') probe. Standard: individual evidence review with
   file:line citations (full vault-relative paths with chapter-level
   parents); subagent cross-check of judgment calls WITH INDEPENDENT
   RE-VERIFICATION of every subagent correction AND of every
   orchestrator-proposed confirm_gap (sessions 9-13 precedent: of six
   flagged errata across those sessions, several were wrong and one —
   cifar10 — overturned the orchestrator's own gap claim); confirmed
   gaps are RARE — look for concepts used in dependency position with
   NO definitional treatment anywhere under ANY spelling variant,
   INCLUDING the master-ai glossary Acronyms Index and A-Z Terms, AND
   the Group-B description lines of quiz matching blocks, AND symbol
   glosses in math notation blocks (the session-13 'ŷ is the predicted
   label' case at Perceptrons and MLPs.md:63 — search property-based
   phrases near term occurrences, not just the term).
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

## Replay recipe (ADR-0010, now fourteen decide rounds)

`vu discover-gaps` over all 70 batches (exact args in
reports/discovery/disc002-full-corpus-run.json report_meta.args; ~5 min,
fits one tool call) then `vu discovery-decide` r1 (--decided-utc
2026-10-28T00:45:00Z), r2 (01:30:00Z), batch2 (02:30:00Z), batch3
(2026-10-28T05:30:00Z), batch4 (2026-10-30T13:05:00Z), batch5
(15:30:00Z), batch6 (16:30:00Z), batch7 (2026-10-31T00:30:00Z), batch8
(2026-10-31T01:30:00Z), batch9 (2026-10-31T03:00:00Z), batch10
(2026-10-31T05:30:00Z), batch11 (2026-10-31T08:00:00Z), batch12
(2026-10-31T10:30:00Z), batch13 (2026-10-31T13:30:00Z), then `vu
discovery-index`. Expected result: 60,154 records; 51,372 provisional /
7,197 already_covered / 1,580 rejected / 3 confirmed_gap / 1 merged / 1
deferred. CAUTION (F-0019): compare the regenerated index against the
committed index by PARSED CONTENT (e.g. json.loads each line), not raw
sha256 — the recorded hash is script-writer-specific while the CLI
writer escapes Unicode. scripts/disc002_batch13_replay.py performs the
whole chain in one run (adjust the output paths for a batch-14 replay or
reuse as-is after adding the batch-13 round to DECIDE_CHAIN: it verifies
content-identity against the committed index automatically).

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
  the batch-4..13 repo-relative scripts.
- F-0020 (fixed, regression-tested): never invoke the CLI via
  `python -m vault_unification.cli` in old checked-out code without the
  guard — use `vu` or `python -m vault_unification` if unsure.
- F-0014 (open): two ai-course files end with 'END OF FILE / File Name'
  marker headings — synthesis must not copy them as knowledge headings.
- Fresh-sandbox setup (session-13 lesson): `python3 -m pip install -e .`
  before the baseline pytest; the subprocess CLI test requires it.
- Subagent discipline (sessions 9-13): subagent corrections are hints,
  not facts — INDEPENDLY RE-VERIFY every correction against the corpus
  before incorporating it (session 9: two wrong corrections; session 10:
  one wrong correction; session 11: one wrong file name and one wrong
  count; session 12: the one disagreement was RIGHT and overturned the
  orchestrator's own confirm_gap; session 13: of two flagged errata, one
  was right and one was wrong). Symmetrically, re-verify your OWN gap
  claims before applying them: term-separated definitions (quiz matching
  blocks, glossary cross-references) and symbol glosses in notation
  blocks defeat term-only search. Probe/regex searches must account for
  `\text{...}` wrappers, unicode characters (× vs x), **bold** markers,
  heading LEVELS (## vs ###) AND heading-number prefixes ('# 14 - ...',
  '## 9. ...'), note titles that differ from filenames, hyphenation and
  spelling variants (unembedding vs un-embedding; vgg16-bn vs vgg16_bn;
  resnet50 vs ResNet-50), AND regex-vs-LaTeX escaping (in a regex, \t is
  TAB and \c is a bad escape — literal '\times'/'\cos' need '\\times'/
  '\\cos') inside patterns.
- Probe discipline (sessions 10-13): use the FENCE-AWARE probe pattern
  (scripts/disc002_batch13_probe.py) for all future coverage probes;
  naive startswith('#') heading scans are a closed defect class. Before
  claiming acronym/term absence, ALSO check the master-ai glossary
  ('28 - Glossary/Acronyms/Acronyms Index.md', '28 - Glossary/Terms/
  A-Z Terms.md') — the ddpm and sota cases are the models — AND the
  Group-B description lines of quiz matching blocks near every term
  occurrence (the cifar10 model), AND math-notation symbol-gloss blocks
  near the term (the 'ŷ is the predicted label' model at Perceptrons
  and MLPs.md:63).
- Delta-verification discipline (sessions 11-13): write the arithmetic
  of expectations down BEFORE running (e.g. 51,432-60 / 7,167+30 /
  1,550+30); when a delta check fails, verify whether the DATA or the
  EXPECTATION is wrong before changing anything (session 13: the
  script's embedded expected_counts was the wrong side; the data was
  correct throughout).
