# Next Agent Handoff

## Project state

- Current milestone: DISC-002 corpus-wide concept discovery IN PROGRESS —
  session 14 re-verified the baseline (663/663 tests on the first run —
  the editable install was run FIRST per the session-13 lesson; both
  vaults byte-identical to manifests at start AND end, HEAD ==
  origin/main == 2d577cd at start), extended the ADR-0010 replay to
  FOURTEEN decide rounds (content-identical to the committed index on
  the first try), found and fixed ONE new tooling defect (F-0021:
  unclosed-fence spans in the probe family), and completed the batch-14
  review tranche: 17 covers + 43 rejects, no new confirmed gap, no
  merge. The subagent cross-check returned 60/60 first-pass AGREE — the
  SECOND consecutive fully-agreeing tranche. All ten flagged citation
  errata were independently re-verified and ACCEPTED, plus one further
  level slip found by the orchestrator's own post-fix audit. After
  DISC-002: per-domain semantic classification of the dossier-extension
  overlap pairs, then disposition assignment, then GATED synthesis.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002
  sessions A+B (merged), sessions 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
  and 14 (this checkpoint).
- Framework version 0.9.0; 24 capabilities (23 implemented-and-tested +
  1 planned CAP-014 'source-to-output coverage and frequency regression
  reports', synthesis-time; test-verified).
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never
  mark a task completed before its commit exists; always re-run the
  suite after the last mutation).
- FRESH-SANDBOX NOTE (sessions 13-14 lesson): run `python3 -m pip
  install -e .` BEFORE the baseline pytest — tests/test_discovery.py
  spawns `python -m vault_unification` as a subprocess, which requires
  the editable install (FRAMEWORK_SETUP.md style 2). Without it the
  suite fails 662/663 on that one test; this is environment setup, not
  a code defect. Session 14 ran the install first and the baseline
  passed 663/663 on the first run.

## Session 14 summary (evidence-backed)

- Baseline verified: 663/663 tests at session start
  (reports/discovery/disc002-session14-baseline-pytest.json — first-run
  pass after the documented install); clean tree with HEAD ==
  origin/main == 2d577cd; both vaults byte-identical to committed
  manifests at session start (reports/discovery/
  disc002-session14-manifest-{ai-course,master-ai}.json, 0
  added/removed/changed).
- ADR-0010 replay extended to FOURTEEN decide rounds via
  scripts/disc002_batch14_replay.py: `vu discover-gaps` over all 70
  batches (recorded args), then FOURTEEN decide rounds replayed with the
  recorded --decided-utc values (r1, r2, batch2..batch13), then `vu
  discovery-index` — CONTENT-IDENTICAL to the committed index (60,154
  records; status counts matched exactly: 51,372/7,197/1,580/3/1/1;
  validate green; F-0019 heeded; ran clean on the first try; post-
  batch13 chain state preserved at scratch/disc002-s14-batch13.jsonl).
- F-0021 (NEW, fixed in session): the probe family's fence_spans
  mishandled UNCLOSed code fences — mdextract reports end_line=null
  with closed=false, and f.get("end_line", start) does not default an
  explicit JSON null, so the span comparison crashed (TypeError) when
  the batch-14 probe hit the 'fill:#' mermaid-color term family. Fixed:
  unclosed spans extend to EOF. Batches 10-13 share the latent defect
  but never triggered it (impact analysis in F-0021). Future probe
  scripts MUST copy the batch-14 fence_spans signature
  fence_spans(struct, total_lines).
- Batch-14 review tranche: 60 highest-signal unreviewed provisional
  candidates (of 4,394 matching the signal rule — exactly the
  session-13 prediction), individually reviewed with a ~290-term
  fence-aware definitional-treatment coverage probe
  (scripts/disc002_batch14_probe.py), 178-check citation verification
  (scripts/disc002_batch14_verify.py, all OK after five pattern fixes:
  a paraphrased quote replaced by the verbatim '(the RNN version of
  this design space)'; heading-number prefix '### 4. Hierarchical
  features'; 'The update rule:' with the formula on the next line; 'to
  break symmetry (so neurons learn different features)'; '**Checkpoint
  selection**: save checkpoints periodically' bold markers + :206),
  and an independent subagent cross-check of ALL 60 judgment calls:
  60/60 first-pass AGREE (second consecutive fully-agreeing tranche).
- Subagent errata were INDEPENDENTLY RE-VERIFIED before incorporation;
  ALL TEN ACCEPTED (sixth consecutive session where re-verification was
  required): the IoU definitional sentence is at '05. Computer Vision
  Metrics - IoU, mAP, Dice.md:20' (cited :21; formula :22), and nine
  heading-LEVEL markers were wrong in the rationales ('### Correlation,
  Not Causation' Probing.md:84; '### Doesn't Explain Causation' Logit
  Lens.md:146; '### Encoder-Decoder Models' Roadmap:210; '###
  Outliers' Linear Regression from Scratch.md:282; '### 4.
  Hierarchical features' CNNs.md:40; '#### The Adam Parameter Update'
  Hyperparameters Summary.md:387; '# 2. Neural Network Architecture'
  Fundamentals.md:40; '#### The Exploding Gradient Problem' Weight Init
  Techniques.md:20; '### ML Engineer' AI Engineer Roles.md:74 / '### 4.
  Machine Learning Engineer' Careers.md:32; '### 2. ReLU (Rectified
  Linear Unit)' Fundamentals.md:145). ROOT CAUSE: the verify script's
  require_heading checks use '^#+' which matches ANY heading level, so
  exact-level citation slips pass — the subagent caught a verify-script
  blind spot the orchestrator's own tool could not. ONE further level
  slip found by the orchestrator's OWN post-fix audit ('### One-stage
  detectors: YOLO and SSD' at Detection and Segmentation.md:69).
  LESSON: consider level-exact heading patterns (e.g. '^## ' vs '^### ')
  in future verify scripts, and keep the symmetric discipline — verify
  subagent corrections AND your own citations.
- NO NEW CONFIRMED GAP this tranche. The subagent adversarially probed
  the two nearest misses: 'exponential moving average' has an
  operational definition at Batch Normalization.md:122-128 ('updated
  using an exponential moving average (EMA)... preferred over a simple
  average because it gives more weight to recent batches') plus the
  momentum-velocity gloss (Optimizers Deep Dive.md:272); the loss curve
  has the LR-range-test operational definition (Hyperparameters.md:140
  'plotting the loss. The optimal learning rate is typically near the
  steepest point of the loss curve') plus the learning-curve
  definitional treatment (master-ai Bias Variance Tradeoff.md:254-256).
  Gap-shaped candidates resolved: 'sora' COVER via in-situ glosses
  (master-ai '23 - Multimodal AI/Vision-Language/01 - Multimodal AI
  Overview.md:72-73' heading '### Sora (OpenAI, 2024)' + gloss
  'Text-to-video generation. Minutes-long, high quality.'; '23 -
  Multimodal AI/Diffusion/05 - DiT and FLUX.md:114' 'Sora (OpenAI's
  video generation model) uses a DiT-based architecture, scaled to
  video' — the OpenHermes named-entity precedent); 'causality' COVER
  via the interpretability domain (activation patching 'gold standard
  for establishing causality' '14 - Interpretability/Mechanistic/04 -
  Activation Patching and Causal Tracing.md:11'; probing 'Correlation,
  Not Causation' '14 - Interpretability/Probing/05 - Probing.md:84';
  logit lens 'Doesn't Explain Causation' '14 -
  Interpretability/Mechanistic/02 - Logit Lens and Tuned Lens.md:146')
  plus the regression-assumption framing (ai-course '03. Linear
  Regression (DL Perspective).md:3/:21'); 'goodfellow et'/'goodfellow
  et al'/'radford et'/'radford et al' REJECTED as citation-format
  fragments whose entity/model sides are covered (batch-13 goodfellow
  cover D-DISC002-B13-0035; dedicated CLIP '23 - Multimodal AI/
  Vision-Language/02 - CLIP.md', GPT-2 '26 - Papers/LLMs/15 - GPT-2
  2019.md', GAN notes); 'vdots' REJECTED as a LaTeX artifact
  (lfloor/rfloor/cos/sin batch-13 precedent; concept side covered by
  the matrix-notation/Jacobian notes). Corpus confirmed_gap total stays
  3 (second moment, bradley-terry, async def).
- Current candidate set: 51,312 provisional / 7,214 already_covered /
  1,623 rejected / 3 confirmed_gap (second moment, bradley-terry, async
  def) / 1 merged / 1 deferred.
- Delta verification PASSED ON THE FIRST TRY — the expectation
  arithmetic was written down BEFORE running (51,372-60 / 7,197+17 /
  1,580+43). 60 status changes (17+43), 60,094 unchanged, history
  cleanly appended for all 60, final counts exactly as expected. The
  cumulative decisions_applied counter read 2004 (batch-12 replay
  decide reported 1884; +60 batch13 +60 batch14 — consistent with the
  committed chain).

## Next task: DISC-002 continuation

1. **Continue the semantic review in bounded tranches** (51,312
   provisional; 4,334 more match the signal rule). Reuse the
   REPO-RELATIVE scripts/disc002_batch14_{replay,tranche,probe,decisions,
   verify,delta}.py pattern (edit CAND to point at the current replayed
   state scratch/disc002-s15-batch14.jsonl; new decision IDs
   D-DISC002-B15-****; candidate IDs are asserted against the selection
   file, so a wrong ID fails loudly). The batch-14 probe carries the
   F-0021 FIX (fence_spans(struct, total_lines); unclosed fences extend
   to EOF) — do NOT copy the batch-13 probe's fence_spans. Standard:
   individual evidence review with file:line citations (full
   vault-relative paths with chapter-level parents); subagent
   cross-check of judgment calls WITH INDEPENDENT RE-VERIFICATION of
   every subagent correction AND of every orchestrator-proposed
   confirm_gap (sessions 9-14 precedent: of eighteen flagged errata
   across those sessions, several were wrong and one — cifar10 —
   overturned the orchestrator's own gap claim; in session 14 all ten
   were right and exposed a verify-script blind spot). Consider
   LEVEL-EXACT heading patterns in the verify script (the '^#+' blind
   spot: '^#+ ' matches any level; cite the exact level you verified).
   Confirmed gaps are RARE — look for concepts used in dependency
   position with NO definitional treatment anywhere under ANY spelling
   variant, INCLUDING the master-ai glossary Acronyms Index and A-Z
   Terms, AND the Group-B description lines of quiz matching blocks,
   AND symbol glosses in math notation blocks, AND operational
   definitions (the LR-range-test 'loss curve' and BatchNorm 'EMA'
   patterns from session 14).
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

## Replay recipe (ADR-0010, now fifteen decide rounds)

`vu discover-gaps` over all 70 batches (exact args in
reports/discovery/disc002-full-corpus-run.json report_meta.args; ~5 min,
fits one tool call) then `vu discovery-decide` r1 (--decided-utc
2026-10-28T00:45:00Z), r2 (01:30:00Z), batch2 (02:30:00Z), batch3
(2026-10-28T05:30:00Z), batch4 (2026-10-30T13:05:00Z), batch5
(15:30:00Z), batch6 (16:30:00Z), batch7 (2026-10-31T00:30:00Z), batch8
(2026-10-31T01:30:00Z), batch9 (2026-10-31T03:00:00Z), batch10
(2026-10-31T05:30:00Z), batch11 (2026-10-31T08:00:00Z), batch12
(2026-10-31T10:30:00Z), batch13 (2026-10-31T13:30:00Z), batch14
(2026-11-01T03:30:00Z), then `vu discovery-index`. Expected result:
60,154 records; 51,312 provisional / 7,214 already_covered / 1,623
rejected / 3 confirmed_gap / 1 merged / 1 deferred. CAUTION (F-0019):
compare the regenerated index against the committed index by PARSED
CONTENT (e.g. json.loads each line), not raw sha256 — the recorded hash
is script-writer-specific while the CLI writer escapes Unicode.
scripts/disc002_batch14_replay.py performs the whole chain in one run
(adjust the output paths for a batch-15 replay or reuse as-is after
adding the batch-14 round to DECIDE_CHAIN: it verifies content-identity
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
  the batch-4..14 repo-relative scripts.
- F-0020 (fixed, regression-tested): never invoke the CLI via
  `python -m vault_unification.cli` in old checked-out code without the
  guard — use `vu` or `python -m vault_unification` if unsure.
- F-0021 (fixed this session, batch-14 probe only): probe fence_spans
  must treat unclosed fences (end_line=null) as extending to EOF — copy
  the batch-14 signature fence_spans(struct, total_lines), NOT the
  batch-13 one.
- F-0014 (open): two ai-course files end with 'END OF FILE / File Name'
  marker headings — synthesis must not copy them as knowledge headings.
- Fresh-sandbox setup (sessions 13-14 lesson): `python3 -m pip install
  -e .` BEFORE the baseline pytest; the subprocess CLI test requires it.
  Session 14 ran the install first and the baseline passed first-try.
- Subagent discipline (sessions 9-14): subagent corrections are hints,
  not facts — INDEPENDENTLY RE-VERIFY every correction against the
  corpus before incorporating it (session 9: two wrong corrections;
  session 10: one wrong correction; session 11: one wrong file name and
  one wrong count; session 12: the one disagreement was RIGHT and
  overturned the orchestrator's own confirm_gap; session 13: of two
  flagged errata, one was right and one was wrong; session 14: all ten
  flagged errata were right and exposed a verify-script blind spot).
  Symmetrically, re-verify your OWN gap claims and citations before
  applying them: term-separated definitions (quiz matching blocks,
  glossary cross-references) and symbol glosses in notation blocks
  defeat term-only search. Probe/regex searches must account for
  \text{...} wrappers, unicode characters (× vs x), **bold** markers,
  heading LEVELS (## vs ### vs #### — use level-exact patterns where
  the level is load-bearing) AND heading-number prefixes ('# 14 - ...',
  '## 9. ...', '### 4. ...'), note titles that differ from filenames,
  hyphenation and spelling variants (unembedding vs un-embedding;
  vgg16-bn vs vgg16_bn; resnet50 vs ResNet-50), AND regex-vs-LaTeX
  escaping (in a regex, \t is TAB and \c is a bad escape — literal
  '\times'/'\cos'/'\vdots' need '\\times'/'\\cos'/'\\vdots') inside
  patterns, AND formulas that sit on the line AFTER the sentence that
  introduces them.
- Probe discipline (sessions 10-14): use the FENCE-AWARE probe pattern
  (scripts/disc002_batch14_probe.py — the F-0021-fixed version) for all
  future coverage probes; naive startswith('#') heading scans are a
  closed defect class. Before claiming acronym/term absence, ALSO check
  the master-ai glossary ('28 - Glossary/Acronyms/Acronyms Index.md',
  '28 - Glossary/Terms/A-Z Terms.md') — the ddpm and sota cases are the
  models — AND the Group-B description lines of quiz matching blocks
  near every term occurrence (the cifar10 model), AND math-notation
  symbol-gloss blocks near the term (the 'ŷ is the predicted label'
  model at Perceptrons and MLPs.md:63), AND operational definitions
  (the 'loss curve' LR-range-test and BatchNorm-EMA models from
  session 14).
- Delta-verification discipline (sessions 11-14): write the arithmetic
  of expectations down BEFORE running (e.g. 51,372-60 / 7,197+17 /
  1,580+43); when a delta check fails, verify whether the DATA or the
  EXPECTATION is wrong before changing anything (session 13: the
  script's embedded expected_counts was the wrong side; session 14:
  first-try PASS with the pre-written arithmetic).
