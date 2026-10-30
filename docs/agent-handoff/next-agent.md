# Next Agent Handoff

## Project state

- Current milestone: DISC-002 corpus-wide concept discovery IN PROGRESS —
  session 10 re-verified the baseline (663/663 tests, both vaults
  byte-identical to manifests at start AND end, HEAD == origin/main ==
  f54204e), answered the user's toolkit-status question with repository
  evidence, extended the ADR-0010 replay to TEN decide rounds
  (content-identical to the committed index on the first try), made the
  batch-10 probe FENCE-AWARE (toolkit improvement; see below), and
  completed the batch-10 review tranche: 30 covers + 30 rejects, no new
  confirmed gap, no merge. After DISC-002: per-domain semantic
  classification of the dossier-extension overlap pairs, then
  disposition assignment, then GATED synthesis.
- Completed and verified: BOOT-000..004, EXT-001..010, REBASE-000,
  AUDIT-011, FRAME-001, DISC-001, FRAME-002, REGEN-001; DISC-002
  sessions A+B (merged), sessions 3, 4, 5, 6, 7, 8, 9, and 10 (this
  checkpoint).
- Framework version 0.9.0; 24 capabilities (23 implemented-and-tested +
  1 planned CAP-014 'source-to-output coverage and frequency regression
  reports', synthesis-time; test-verified).
- Read FIRST (mandatory startup battery): AGENTS.md -> docs/* ->
  state/task-queue.jsonl -> state/current-state.json -> this file ->
  reports/rebaseline/iteration-retrospective.md (lessons A-1/A-2: never
  mark a task completed before its commit exists; always re-run the
  suite after the last mutation).

## Session 10 summary (evidence-backed)

- Baseline verified: 663/663 tests at session start
  (reports/discovery/disc002-session10-baseline-pytest.json); clean tree
  with HEAD == origin/main == f54204e; both vaults byte-identical to
  committed manifests at session start
  (reports/discovery/disc002-session10-manifest-{ai-course,master-ai}.json,
  0 added/removed/changed) and again at session end (-end- reports).
- USER STATUS QUESTION ANSWERED WITH EVIDENCE: the 2026-10-27 refactor
  requirements ARE implemented and tested — discovery (CAP-017),
  artifact linting (CAP-018, 25 check families), quality
  assessment/drift/gates (CAP-019), repair loop (CAP-020), prompt
  checking (CAP-021). Only CAP-014 (source-to-output coverage and
  frequency regression reports) remains planned; it is a synthesis-time
  capability. `vu capabilities` reports the 23+1 inventory; `vu --help`
  lists all commands; 663 tests green.
- ADR-0010 replay extended to TEN decide rounds via
  scripts/disc002_batch10_replay.py: `vu discover-gaps` over all 70
  batches (recorded args), then TEN decide rounds replayed with the
  recorded --decided-utc values (r1, r2, batch2..batch9), then `vu
  discovery-index` — CONTENT-IDENTICAL to the committed index (60,154
  records; status counts matched exactly: 51,612/7,085/1,452/3/1/1;
  validate green; F-0019 heeded; ran clean on the first try). NO NEW
  TOOLING DEFECTS this session.
- TOOLKIT IMPROVEMENT (session-9 handoff follow-up, recurring defect
  class closed): scripts/disc002_batch10_probe.py is FENCE-AWARE —
  heading detection uses the authoritative mdextract
  extract_structure_text headings + code-fence spans instead of the
  naive startswith('#') scan; in-fence definition-window hits are
  excluded from def_hits and reported separately; the verify script
  asserts heading citations against the authoritative heading list. The
  '# comment in code fence looks like a heading' class (batches 7/8/9)
  is now structurally prevented in the tranche tooling. Reuse this
  pattern for all future probes.
- Batch-10 review tranche: 60 highest-signal unreviewed provisional
  candidates (of 4,634 matching the signal rule — exactly the count the
  session-9 handoff predicted), individually reviewed with a 62-term
  fence-aware definitional-treatment coverage probe
  (scripts/disc002_batch10_probe.py), targeted citation verification
  (scripts/disc002_batch10_verify.py, 91 locator checks, all OK after 9
  pattern fixes — mostly **bold** markers plus two wrong-file pointers),
  and an independent subagent cross-check of 40 judgment calls: 40/40
  AGREE. Result: 30 evidence-cited covers + 30 noise rejects.
- Subagent errata were INDEPENDENTLY RE-VERIFIED before incorporation;
  ONE was itself wrong and rejected: the claim that '06. VGG16
  Architecture Deep Dive.md' contains no ImageNet normalization — the
  note HAS 4 ImageNet mentions incl. the mean-RGB preprocessing at
  :131 and code defaults :513/:620/:622. (Two-session pattern now: at
  least one wrong subagent correction per session. Keep the mandatory
  re-verification step.) VERIFIED errata incorporated: ColPali
  'embeds it via a VLM (PaliGemma)' quote at :132 (:12 carries the
  other in-situ mention); Transfer Learning ImageNet mean/std at :564;
  heading levels (### for Perplexity :87/:90, channel headings, Eval
  :50, ResNet :477, TF-IDF :210, Scaling Laws :45; ## for
  Agent-vs-Workflow :97).
- NO NEW CONFIRMED GAP this tranche. The one gap-shaped candidate,
  'unembedding' (CG-4b5ef691d415: used in dependency position at
  Initialization Schemes :176/:238, Logit Lens :85, InstructGPT :52,
  with no 'unembedding' heading corpus-wide), resolved as COVER — the
  defining note spells it HYPHENATED: master-ai '07 - Transformers/
  Components/06 - Embedding Layer.md:60' 'The output layer
  (un-embedding) is also a R^{d x |V|} matrix' inside '## Tied vs
  Untied Embeddings' :58. NEW PROBE LESSON (extends session-9
  LaTeX/unicode lessons): search hyphenation/spelling variants before
  claiming absence.
- Current candidate set: 51,552 provisional / 7,115 already_covered /
  1,482 rejected / 3 confirmed_gap (second moment, bradley-terry, async
  def) / 1 merged / 1 deferred.

## Next task: DISC-002 continuation

1. **Continue the semantic review in bounded tranches** (51,552
   provisional; ~4,574 more match the signal rule). Reuse the
   REPO-RELATIVE scripts/disc002_batch10_{replay,tranche,probe,decisions,
   verify}.py pattern (edit CAND to point at the current replayed state
   scratch/disc002-s11-batch10.jsonl; new decision IDs D-DISC002-B11-****;
   candidate IDs are asserted against the selection file, so a wrong ID
   fails loudly). The batch-10 probe is fence-aware — copy it, do NOT
   revert to the batch-9 naive probe. Standard: individual evidence
   review with file:line citations (full vault-relative paths with
   chapter-level parents); subagent cross-check of judgment calls WITH
   INDEPENDENT RE-VERIFICATION of every subagent correction (two-session
   pattern: at least one wrong correction per session); confirmed gaps
   are RARE — look for concepts used in dependency position with NO
   definitional treatment anywhere under ANY spelling variant (async def
   is the model; the 'unembedding' near-miss shows why hyphenation
   variants must be searched).
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

## Replay recipe (ADR-0010, now eleven decide rounds)

`vu discover-gaps` over all 70 batches (exact args in
reports/discovery/disc002-full-corpus-run.json report_meta.args; ~5 min,
fits one tool call) then `vu discovery-decide` r1 (--decided-utc
2026-10-28T00:45:00Z), r2 (01:30:00Z), batch2 (02:30:00Z), batch3
(2026-10-28T05:30:00Z), batch4 (2026-10-30T13:05:00Z), batch5
(15:30:00Z), batch6 (16:30:00Z), batch7 (2026-10-31T00:30:00Z), batch8
(2026-10-31T01:30:00Z), batch9 (2026-10-31T03:00:00Z), batch10
(2026-10-31T05:30:00Z), then `vu discovery-index`. Expected result:
60,154 records; 51,552 provisional / 7,115 already_covered / 1,482
rejected / 3 confirmed_gap / 1 merged / 1 deferred. CAUTION (F-0019):
compare the regenerated index against the committed index by PARSED
CONTENT (e.g. json.loads each line), not raw sha256 — the recorded hash
is script-writer-specific while the CLI writer escapes Unicode.
scripts/disc002_batch10_replay.py performs the whole chain in one run
(adjust the output paths for a batch-11 replay or reuse as-is after
adding the batch-10 round to DECIDE_CHAIN: it verifies content-identity
against the committed index automatically).

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
  the batch-4..10 repo-relative scripts.
- F-0020 (fixed, regression-tested): never invoke the CLI via
  `python -m vault_unification.cli` in old checked-out code without the
  guard — use `vu` or `python -m vault_unification` if unsure.
- F-0014 (open): two ai-course files end with 'END OF FILE / File Name'
  marker headings — synthesis must not copy them as knowledge headings.
- Subagent discipline (sessions 9-10): subagent corrections are hints,
  not facts — INDEPENDENTLY RE-VERIFY every correction against the
  corpus before incorporating it (session 9: two wrong corrections;
  session 10: one wrong correction — the false 'no ImageNet
  normalization in the VGG16 Deep Dive note' claim). Probe/regex
  searches must account for `\\text{...}` wrappers, unicode characters
  (× vs x), **bold** markers, AND hyphenation/spelling variants
  (unembedding vs un-embedding) inside patterns.
- Probe discipline (session 10): use the FENCE-AWARE probe pattern
  (scripts/disc002_batch10_probe.py) for all future coverage probes;
  naive startswith('#') heading scans are a closed defect class.
