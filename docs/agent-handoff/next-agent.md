# Next Agent Handoff

## Project state

- Current milestone: DISC-002 corpus-wide concept discovery IN PROGRESS —
  session 15 re-verified the baseline (663/663 tests on the first run —
  the editable install was run FIRST per the session-13/14 lesson; both
  vaults byte-identical to manifests at start AND end, HEAD ==
  origin/main == 541d046 at start), extended the ADR-0010 replay to
  FIFTEEN decide rounds (content-identical to the committed index on
  the first try), found NO new tooling defect (the F-0021-fixed
  fence_spans held: the batch-15 probe ran 267 terms clean), closed the
  session-14 '^#+' verify blind spot STRUCTURALLY (level-exact heading
  guard in the batch-15 verify script), and completed the batch-15
  review tranche: 12 covers + 48 rejects, no new confirmed gap, no
  merge. The subagent cross-check returned 60/60 first-pass AGREE — the
  THIRD consecutive fully-agreeing tranche. All twelve flagged citation
  errata were independently re-verified and ACCEPTED, and four
  strengthening citations were verified and incorporated. After
  DISC-002: per-domain semantic classification of the dossier-extension
  overlap pairs, then disposition assignment, then GATED synthesis.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002
  sessions A+B (merged), sessions 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
  14, and 15 (this checkpoint).
- Framework version 0.9.0; 24 capabilities (23 implemented-and-tested +
  1 planned CAP-014 'source-to-output coverage and frequency regression
  reports', synthesis-time; test-verified).
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never
  mark a task completed before its commit exists; always re-run the
  suite after the last mutation).
- FRESH-SANDBOX NOTE (sessions 13-15 lesson): run `python3 -m pip
  install -e .` BEFORE the baseline pytest — tests/test_discovery.py
  spawns `python -m vault_unification` as a subprocess, which requires
  the editable install (FRAMEWORK_SETUP.md style 2). Without it the
  suite fails 662/663 on that one test; this is environment setup, not
  a code defect. Sessions 14 and 15 ran the install first and the
  baseline passed 663/663 on the first run.
- DISK NOTE (session-15 lesson): each ADR-0010 replay chain state is
  ~259MB and the scratch volume could not hold sixteen simultaneous
  intermediates — scripts/disc002_batch15_replay.py deletes each
  intermediate as soon as its successor is written, preserving only the
  final CAND. Keep this delete-as-consumed pattern in future replay
  scripts when the scratch volume is tight; it is an environmental
  constraint, not a semantic change (chain states are deterministic
  replays of committed inputs per ADR-0010).

## Session 15 summary (evidence-backed)

- Baseline verified: 663/663 tests at session start
  (reports/discovery/disc002-session15-baseline-pytest.json — first-run
  pass after the documented install, 216.4s); clean tree with HEAD ==
  origin/main == 541d046; both vaults byte-identical to committed
  manifests at session start (reports/discovery/
  disc002-session15-manifest-{ai-course,master-ai}.json, 0
  added/removed/changed; 276+333 files).
- ADR-0010 replay extended to FIFTEEN decide rounds via
  scripts/disc002_batch15_replay.py: `vu discover-gaps` over all 70
  batches (recorded args), then FIFTEEN decide rounds replayed with the
  recorded --decided-utc values (r1, r2, batch2..batch14), then `vu
  discovery-index` — CONTENT-IDENTICAL to the committed index (60,154
  records; status counts matched exactly: 51,312/7,214/1,623/3/1/1;
  validate green; F-0019 heeded; ran clean on the first try; the CAND
  post-batch14 chain state preserved at scratch/disc002-s15-batch14.jsonl;
  disk-frugal intermediates per the disk note above).
- NO new tooling defect: the batch-15 probe copied the F-0021-FIXED
  fence_spans(struct, total_lines) verbatim from the batch-14 probe and
  ran clean end-to-end (267 terms, exit 0, scratch/
  disc002-batch15-probe.json). The session-14 '^#+' verify blind spot
  is closed STRUCTURALLY: every require_heading check in
  scripts/disc002_batch15_verify.py uses a level-exact '^### '-style
  pattern (a '^### Foo' regex cannot match a '## Foo' or '#### Foo'
  line by construction) and a startup guard REJECTS any '^#+' pattern
  in the CHECKS list — future verify scripts must keep this guard.
- Batch-15 review tranche: 60 highest-signal unreviewed provisional
  candidates (of 4,334 matching the signal rule — exactly the
  session-14 prediction), individually reviewed with a 267-term
  fence-aware definitional-treatment coverage probe
  (scripts/disc002_batch15_probe.py), 168-check citation verification
  (scripts/disc002_batch15_verify.py, all OK after four pattern fixes:
  the f-string quote tail "print(f'Epoch [{epoch+1}/{num_epochs}], '",
  the '.to(device)' backtick removal, the 'second conv' comment is
  actually '# Batch normalization after second conv', and the scheduler
  comment is '# Update learning rate'), and an independent subagent
  cross-check of ALL 60 judgment calls: 60/60 first-pass AGREE (third
  consecutive fully-agreeing tranche).
- Subagent errata were INDEPENDENTLY RE-VERIFIED before incorporation;
  ALL TWELVE ACCEPTED (seventh consecutive session where re-verification
  was required): three heading-LEVEL markers on sibling phrasings the
  orchestrator's bulk fix had missed ('## Mistake 1: Forgetting
  `optimizer.zero_grad()`' Common Mistakes:10; '# 6. Advanced Pooling
  Mechanisms and Global Average Pooling' GAP note:1; '## Draft Model
  Choices' Speculative Decoding:61); the '[!warning] Wrong Normalization
  = Broken Pre-Trained Model' callout title sits at Data
  Augmentation:479 with the body at :480; the 'gradients are *added*'
  clause is at Backprop CNNs:263 while '**Why accumulation is the
  default**' is :265; the 'a Python float, releasing the graph' comment
  belongs to PyTorch Implementation Basics:574-575, NOT to the Backprop
  CNNs note and not :578; the N-gram note title '# 07 - N-gram Language
  Models' is at :9 after frontmatter; the notation note title
  '# Mathematical Notation in Linear Regression: A Deep Dive' is at :3;
  the ResNet transform block is :594-597 (RandomResizedCrop :595,
  RandomHorizontalFlip :596, ToTensor :597). FOUR strengthening
  citations were verified real and incorporated: the Mini Agent
  tool-registry gloss 'web_search: Search the web for current
  information.' (:150) and implementation 'def web_search(query: str,
  max_results: int = 5) -> str:' (:59); the A-Z Terms glossary entries
  '**Chat template** — format for wrapping user/assistant messages'
  (:48) and '**Memory** — persistent state for agents' (:166); the
  Acronyms Index entry '**VLM** — Vision-Language Model' (:202).
- NO NEW CONFIRMED GAP this tranche (gap-watch verdict: none). 'tulu'
  was adversarially probed by BOTH the orchestrator and the subagent:
  exactly 4 corpus occurrences (DPO Derivation:182; Instruction Tuning
  and Chat Templates:159; DPO 2023:133/:175), all bare example-list
  mentions; NO in-situ gloss anywhere (both glossaries and the quiz
  banks checked — no entry); NOT in dependency position (every
  occurrence's load-bearing concepts — DPO, instruction tuning,
  synthetic data, open-weights alignment — have dedicated treatments);
  so the confirm_gap dependency test FAILS and the OpenHermes/Sora
  in-situ-gloss cover precedents do NOT apply — REJECT stands as the
  FIRST BARE-NAMED-ENTITY REJECT PRECEDENT (named entities WITH in-situ
  glosses are covers; named entities in bare example lists whose
  concept side is covered are rejects; neither is a gap). Gap-shaped
  covers this tranche: 'web search' via operational treatments (ReAct
  fresh-information motivation :16/:426; Mini Agent tool set :12/:19
  plus the tool-registry gloss :150 and implementation :59; MCP tool
  category :118) — the session-14 operational-definition precedent;
  'chat template' via the dedicated instruction-tuning note (:9/:53/
  :149) plus the A-Z Terms entry :48; 'memories' via FFN key-value
  memories (:97/:98) plus the memory-systems chapter (:12) and the
  glossary entry :166.
- Current candidate set: 51,252 provisional / 7,226 already_covered /
  1,671 rejected / 3 confirmed_gap (second moment, bradley-terry, async
  def) / 1 merged / 1 deferred.
- Delta verification PASSED ON THE FIRST TRY — the expectation
  arithmetic was written down BEFORE running (51,312-60 / 7,214+12 /
  1,623+48). 60 status changes (12+48), 60,094 unchanged, history
  cleanly appended for all 60, final counts exactly as expected. The
  cumulative decisions_applied counter read 2064 (batch-14 replay
  decide reported 2004; +60 batch15 — consistent with the committed
  chain).
- Session-15 push verified: feat commit e75173b pushed to origin/main
  (541d046..e75173b); the state commit 985171c records the push
  verification. HEAD == origin/main, working tree clean after the push.

## Next task: DISC-002 continuation

1. **Continue the semantic review in bounded tranches** (51,252
   provisional; 4,274 more match the signal rule). Reuse the
   REPO-RELATIVE scripts/disc002_batch15_{replay,tranche,probe,decisions,
   verify,delta}.py pattern (edit CAND to point at the current replayed
   state scratch/disc002-s16-batch15.jsonl; new decision IDs
   D-DISC002-B16-****; candidate IDs are asserted against the selection
   file, so a wrong ID fails loudly). Keep BOTH hard-won probe/verify
   disciplines: the F-0021-FIXED fence_spans(struct, total_lines) and
   the LEVEL-EXACT heading guard (never '^#+'). Standard: individual
   evidence review with file:line citations (full vault-relative paths
   with chapter-level parents); subagent cross-check of judgment calls
   WITH INDEPENDENT RE-VERIFICATION of every subagent correction AND of
   every orchestrator-proposed confirm_gap (sessions 9-15 precedent: of
   thirty flagged errata across those sessions, several were wrong and
   one — cifar10 — overturned the orchestrator's own gap claim; in
   session 15 all twelve were right and four strengthening citations
   were added). Confirmed gaps are RARE — look for concepts used in
   dependency position with NO definitional treatment anywhere under
   ANY spelling variant, INCLUDING the master-ai glossary Acronyms
   Index and A-Z Terms, AND the Group-B description lines of quiz
   matching blocks, AND symbol glosses in math notation blocks, AND
   operational definitions (the 'loss curve', EMA, and 'web search'
   patterns). Named entities: WITH an in-situ gloss -> cover
   (OpenHermes/Sora); bare example-list mention with covered concept
   side -> reject (the session-15 'tulu' precedent); gap requires
   dependency position.
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

## Replay recipe (ADR-0010, now sixteen decide rounds)

`vu discover-gaps` over all 70 batches (exact args in
reports/discovery/disc002-full-corpus-run.json report_meta.args; ~5 min,
fits one tool call) then `vu discovery-decide` r1 (--decided-utc
2026-10-28T00:45:00Z), r2 (01:30:00Z), batch2 (02:30:00Z), batch3
(2026-10-28T05:30:00Z), batch4 (2026-10-30T13:05:00Z), batch5
(15:30:00Z), batch6 (16:30:00Z), batch7 (2026-10-31T00:30:00Z), batch8
(2026-10-31T01:30:00Z), batch9 (03:00:00Z), batch10 (05:30:00Z), batch11
(08:00:00Z), batch12 (10:30:00Z), batch13 (13:30:00Z), batch14
(2026-11-01T03:30:00Z), batch15 (2026-11-01T04:15:00Z), then `vu
discovery-index`. Expected result: 60,154 records; 51,252 provisional /
7,226 already_covered / 1,671 rejected / 3 confirmed_gap / 1 merged / 1
deferred. CAUTION (F-0019): compare the regenerated index against the
committed index by PARSED CONTENT (e.g. json.loads each line), not raw
sha256 — the recorded hash is script-writer-specific while the CLI
writer escapes Unicode. scripts/disc002_batch15_replay.py performs the
whole chain in one run (adjust the output paths for a batch-16 replay
after adding the batch-15 round to DECIDE_CHAIN: it verifies
content-identity against the committed index automatically; keep the
delete-as-consumed disk pattern).

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
  the batch-4..15 repo-relative scripts.
- F-0020 (fixed, regression-tested): never invoke the CLI via
  `python -m vault_unification.cli` in old checked-out code without the
  guard — use `vu` or `python -m vault_unification` if unsure.
- F-0021 (fixed; held in batch 15): probe fence_spans must treat
  unclosed fences (end_line=null) as extending to EOF — copy the
  batch-14/15 signature fence_spans(struct, total_lines), NOT the
  batch-13 one. The batch-15 probe ran the fixed version clean.
- LEVEL-EXACT heading discipline (new standing rule from session 15):
  verify scripts must use '^### '-style level-exact heading patterns
  with the startup guard that rejects '^#+' — a level mismatch now
  fails loudly instead of passing (nine session-14 errata were of this
  class). Cite the exact level you verified.
- DISK (session-15): replay chain intermediates are ~259MB each; keep
  the delete-as-consumed replay pattern when the scratch volume is
  tight, preserving only the final CAND.
- F-0014 (open): two ai-course files end with 'END OF FILE / File Name'
  marker headings — synthesis must not copy them as knowledge headings.
- Fresh-sandbox setup (sessions 13-15 lesson): `python3 -m pip install
  -e .` BEFORE the baseline pytest; the subprocess CLI test requires it.
  Sessions 14 and 15 ran the install first and passed first-try.
- Subagent discipline (sessions 9-15): subagent corrections are hints,
  not facts — INDEPENDENTLY RE-VERIFY every correction against the
  corpus before incorporating it (session 9: two wrong corrections;
  session 10: one wrong correction; session 11: one wrong file name and
  one wrong count; session 12: the one disagreement was RIGHT and
  overturned the orchestrator's own confirm_gap; session 13: of two
  flagged errata, one was right and one was wrong; session 14: all ten
  flagged errata were right and exposed a verify-script blind spot;
  session 15: all twelve were right and four strengthening citations
  were added). Symmetrically, re-verify your OWN gap claims and
  citations before applying them: term-separated definitions (quiz
  matching blocks, glossary cross-references) and symbol glosses in
  notation blocks defeat term-only search. Probe/regex searches must
  account for \text{...} wrappers, unicode characters (× vs x), **bold**
  markers, heading LEVELS (## vs ### vs #### — the level-exact guard
  now enforces this) AND heading-number prefixes ('# 14 - ...', '##
  9. ...', '### 4. ...'), note titles that differ from filenames (the
  padding note's title is '# 2.2 Padding: Mathematics, Edge Effects,
  and Valid vs. Same' though the FILE is '06. Padding - Mathematics,
  Edge Effects, and Valid vs Same.md'), titles that sit AFTER YAML
  frontmatter (the N-gram note title is at :9; the notation note title
  at :3), callout anchors ('[!warning]' title line vs body line — Data
  Augmentation:479/:480), hyphenation and spelling variants (unembedding
  vs un-embedding; vgg16-bn vs vgg16_bn; resnet50 vs ResNet-50), AND
  regex-vs-LaTeX escaping (in a regex, \t is TAB and \c is a bad
  escape — literal '\times'/'\cos'/'\vdots' need '\\times'/'\\cos'/
  '\\vdots' inside patterns), AND formulas that sit on the line AFTER
  the sentence that introduces them.
- Probe discipline (sessions 10-15): use the FENCE-AWARE probe pattern
  (scripts/disc002_batch15_probe.py — the F-0021-fixed version) for all
  future coverage probes; naive startswith('#') heading scans are a
  closed defect class. Before claiming acronym/term absence, ALSO check
  the master-ai glossary ('28 - Glossary/Acronyms/Acronyms Index.md',
  '28 - Glossary/Terms/A-Z Terms.md') — the ddpm, sota, chat-template,
  memory, and VLM cases are the models — AND the Group-B description
  lines of quiz matching blocks near every term occurrence (the cifar10
  model), AND math-notation symbol-gloss blocks near the term (the 'ŷ
  is the predicted label' model at Perceptrons and MLPs.md:63), AND
  operational definitions (the 'loss curve' LR-range-test, BatchNorm-EMA,
  and 'web search' Mini-Agent-tool models).
- Delta-verification discipline (sessions 11-15): write the arithmetic
  of expectations down BEFORE running (e.g. 51,312-60 / 7,214+12 /
  1,623+48); when a delta check fails, verify whether the DATA or the
  EXPECTATION is wrong before changing anything (session 13: the
  script's embedded expected_counts was the wrong side; sessions 14-15:
  first-try PASS with the pre-written arithmetic).
