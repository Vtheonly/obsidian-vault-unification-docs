# Next Agent Handoff

## Project state

- Current milestone: Milestone 3 (extraction). Framework bootstrap DONE and
  verified (BOOT-000..004). EXT-001..010 DONE and verified: batches 001-011
  (1728 KUs; 31 of 609 source files extracted), 164 evidence-based overlap
  classifications across six domains (regression, tree-based, evaluation,
  clustering/dimensionality-reduction, generalization/regularization,
  training-stability), and six concept dossiers (164 concepts over all 514
  classified KUs, explicit per-category gap markers). EXT-010 completed
  2026-10-27 in ONE session, including an evidence-based COUNTERPART
  ADJUSTMENT of the EXT-009 reservation (see Verified completed work).
- Current task ID: EXT-011 (to be selected at session start with evidence —
  no record in the queue yet; see Next task).
- Current Git commit: the EXT-010 work/state commits on `main`, pushed to
  origin/main (user push policy: always push to main, always merge into the
  head branch; never leave commits local-only at session end).
- Working tree status: clean after the EXT-010 commits (verify `git status`).
- Registry/checkpoint version: task-queue v15 records (BOOT-000..004 +
  EXT-001..010 completed with tests_run evidence); KU schema v1.1
  (ADR-0008); classification schema (ADR-0009); dossier schema with the
  domain enum EXTENDED ADDITIVELY with 'clustering' (EXT-008),
  'generalization' (EXT-009), and 'training-stability' (EXT-010,
  justification in the schema description); checkpoint
  `state/checkpoints/checkpoint-2026-10-27-ext-010.json`.
- Framework version: 0.5.0 (unchanged in EXT-010 — no framework code
  changes); 415/415 tests (test_concept_dossier.py iterates all six dossier
  files internally, so the suite count is legitimately unchanged);
  capabilities: 16 implemented-and-tested, 1 planned (CAP-014).

## Verified completed work

- EXT-010 (2026-10-27), training-stability domain pair — the EXT-009
  handoff reserved "master-ai '11 - Training/Optimization/05 - Loss Spikes
  and Stability.md' + ai-course 04.3 files 01-03" but required verifying the
  master-ai file's content first. The scope probe (heading evidence via
  mdextract, CAP-003 authority) showed that file is LLM-PRETRAINING
  OPERATIONS (bad batches, checkpoint rollback, BF16 switching, spike
  logging), NOT classical init/gradient theory. The EXECUTED pair:
  - Batch 010 = master-ai '04 - Neural Networks/Training/07 - Initialization
    Schemes.md' (259 lines) + '08 - Vanishing and Exploding Gradients.md'
    (293 lines): 117 KUs, 2/2 files (a deliberate 2-of-3 partial-folder
    master-ai scope; 06 Backpropagation excluded as a distinct autodiff
    domain), double-run byte-identical (sha256 5cc0eb42...).
  - Batch 011 = ai-course 04.3 '01. Weight Initialization.md' (792 lines) +
    '02. Weight Initialization Techniques.md' (73 lines) + '03. The
    Vanishing and Exploding Gradient Problems.md' (1082 lines): 382 KUs,
    three deterministic single-file runs concatenated in fixed order
    (each part and the full concat double-run byte-identical, sha256
    fc58559b...). ai-course 04.3 is now 6 of 7 files extracted (only 04
    Hyperparameters remains, still reserved for a future optimization/tuning
    pair per the EXT-009 scope note).
  - scripts/ext010_fidelity.py: 117/117 + 382/382 byte-exact excerpts +
    hashes + structural purity + 0 heading crossings + ids unique
    within/across the new batches AND vs all 1229 committed ids.
  - state/term-maps/training-stability-domain-v1.json: 98 terms, 165
    aliases, 66 cross-vault, 2 bridged ('Gaussian', 'diagnose'); built after
    FOUR probe rounds; 6 unverified entries were caught and fixed by the
    machine verifier on the first run; no French vocabulary in scope
    (probe-verified); sense-collision vocabulary (the course's 'careful
    attention' idiom vs master-ai's attention mechanism, 'spikes', the
    'norm' family, 'scale', 'decay'-as-shrinkage vs weight-decay) documented
    in the map comment and adjudicated per pair with evidence.
  - CAP-013 discovery: 7486 pairs, 68 cross-vault topics, 21 topics
    truncated at the 250-pair cap (per-KU evidence complete) — the largest
    discovery run of the project so far.
  - state/classifications/007-ext010-training-stability-overlap.jsonl: 36
    records OC-ext010-0001..0036 (32 SD + 3 PO + 1 CC), 142 participating
    KUs, 159 byte-exact quotes. PROCESS IMPROVEMENT: the X2 check now
    MACHINE-LOCATES every quote's lines in the original source at runtime
    (unique in-span occurrence required) — hand-typed line numbers are
    eliminated, closing the error class EXT-009-REVIEW found as R2. The
    first run caught 5 defects (2 KU-id swaps, 1 truncated KU id, 1
    fan-in/fan-out hyphenation mismatch), all fixed at source.
  - Independent review reports/extraction/ext010-review.md (EXT-010-REVIEW,
    read-only subagent): PASS-WITH-NOTES — 10/10 spot quotes byte-exact at
    source, 34 AGREE + 2 BORDERLINE (0006/0032 topic-wording style only) +
    0 DISAGREE, NO coverage gaps (all hunt directions cleared with
    evidence; 0 uncovered discovery topics), scope decision verified
    legitimate, F-0009 confirmed genuine at source. ALL repairs applied
    before commit: R1 F-0009 appended to state/findings.jsonl (via
    scripts/ext010_findings.py); S2 applied WITH CORRECTION — the
    reviewer's course KU id was wrong (KU-892e72cc63cf286a is the L688
    prose; the clipping-API quote lives in KU-32b1dde0ac8ea1de;
    orchestrator-verified unique in-span), so OC-ext010-0024 now carries
    159 quotes / 142 KUs after regeneration. Orchestrator addendum records
    every repair with its re-verification.
  - NEW FINDING F-0009 (state/findings.jsonl, appended via
    scripts/ext010_findings.py): the AI Course is internally inconsistent on
    the PyTorch Conv2d default BIAS initialization — file 01 L407 says
    "Biases are initialized to zero." inside the Conv2d-defaults passage
    while file 02 L68-70 and file 01's own Linear section L411-415 give the
    uniform bound U(-1/sqrt(fan_in), 1/sqrt(fan_in)), which matches
    PyTorch's actual reset_parameters. Cross-referenced from the
    OC-ext010-0033/0036 rationales; synthesis must present the uniform bound
    as PyTorch's default and may keep the zero-bias statement as the
    manual-init recommendation.
  - Dossier: schemas/concept-dossier.schema.json domain enum extended
    additively with 'training-stability'; scripts/ext006_dossiers.py
    DOMAINS extended; state/dossiers/training-stability-v1.json generated
    (36 concepts / 142 KUs; ZERO zero-evidence categories — the FIRST
    dossier with all ten categories populated); ALL SIX dossiers regenerate
    byte-identically (--check exit 0 x6); the five committed dossiers were
    unchanged vs git HEAD; tests/test_concept_dossier.py DOSSIER_FILES
    updated.
  - Registry rebuilt: init --force + load x11 (1728 KUs) + apply-overlap x7
    (164 classifications, 0 rejected) + kureg-validate valid; 514
    participating KUs; all 1728 KUs remain Unaccounted.
  - Sources unchanged before/after (verify-manifest exit 0 x4).

## Tests actually run

| Command/test | Result | Evidence/report |
|---|---|---|
| `vu selftest` (startup) | exit 0 | — |
| `python3 -m pytest tests -q` (startup AND final) | 415/415 | reports/extraction/ext010-{startup-pytest,pytest-report}.json |
| extraction batches 010 + 011 (double-run x2 per part + concats) | byte-identical | coverage reports per file |
| `python3 scripts/ext010_fidelity.py` | 117/117 + 382/382 byte-exact; ids unique vs 1229 committed | reports/extraction/ext010-fidelity-{master-ai,ai-course}.json |
| `python3 scripts/ext010_term_probe{,2,3,4}.py` then `ext010_term_map.py` | 4 probe rounds first; 98 terms / 165 aliases / 66 cross-vault / 2 bridged | reports/extraction/ext010-term-map-verification.json |
| `vu overlap-candidates` (batches 010+011) | 7486 pairs, 68 cross-vault topics, 21 truncated | reports/extraction/ext010-overlap-candidates.json + -pairs.jsonl |
| `python3 scripts/ext010_classifications.py` (x2: pre-review, post-S2) | 36 records, 159 quotes, X1-X9 green both times | state/classifications/007-ext010-training-stability-overlap.jsonl |
| EXT-010-REVIEW (read-only subagent) | PASS-WITH-NOTES; R1 + S2 applied (S2 with the reviewer's KU-id error corrected) | reports/extraction/ext010-review.md + orchestrator addendum |
| `python3 scripts/ext010_review_check.py` (machine checks R1-R8 + topic coverage) | all green; 0 uncovered discovery topics | reports/extraction/ext010-review-check.json |
| `python3 scripts/ext006_dossiers.py` (x2 + `--check` x6) | training-stability-v1 new (36 concepts / 142 KUs, zero empty categories); all six byte-identical | reports/extraction/ext006-dossier-coverage.json |
| registry rebuild: `kureg-init --force` + `kureg-load` x11 + `kureg-apply-overlap` x7 + `kureg-validate` | exit 0 x19; 1728 KUs, 164 classifications (120 SD + 37 PO + 6 CC + 1 CHD), 514 participating, valid | reports/extraction/ext010-kureg-*.json |
| `vu verify-manifest` both vaults (startup AND after) | exit 0 x4; 333 + 276 unchanged | reports/extraction/ext010-immutable-{start,end}-{master-ai,ai-course}.json |
| `vu capabilities --verify` | 16 implemented-and-tested, 1 planned | reports/extraction/ext010-capabilities.json |
| `vu validate-registry --tasks + --classifications 007-ext010` | valid, 0 problems (queue 15/15) | reports/extraction/ext010-{taskqueue-validate-final,classifications-validate}.json |

## Findings and unresolved work

- Open findings: F-0001 (trailing-space dir `source-vaults/AI ` — always
  quote), F-0002 (14 AI Course unclosed-fence files — extractor handles
  them), F-0003 (175 broken wikilinks + 10 missing anchors in AI Course —
  synthesis-time dispositions), F-0007 (boosted-tree library dating —
  synthesis-time reconciliation), F-0008 (mAP name collision), F-0009 (NEW,
  EXT-010: course internally inconsistent on the PyTorch Conv2d default
  bias init, zeros vs uniform bound — synthesis-time reconciliation; the
  uniform bound matches PyTorch's actual reset_parameters).
- Blockers: NONE.
- Known gaps (deliberate non-claims): 31 of 609 source files extracted
  (5.1%); overlap classified for six domains only; dossiers cover ONLY the
  514 classified KUs (1214 extracted KUs have no classification and
  therefore no dossier participation yet — by design); no
  dispositions/concepts-as-destinations; no synthesis output; CAP-014 still
  planned; Master AI has never been link-checked.
- Review suggestions recorded for future sessions (from EXT-010-REVIEW,
  non-blocking): S1 phrase future classification `topic` fields so shared
  vs vault-specific elements are distinguishable; S3 add an explicit
  `committed_files_unchanged` field to the review-check JSON; S4 the
  training-stability dossier's sigmoid/tanh concepts should cite master
  line 08 L34 once, not twice (both OC-ext010-0014/0015 quote fragments of
  it).

## Decisions and configuration

- Counterpart adjustments of handoff reservations are legitimate when made
  with per-file heading evidence BEFORE extraction and recorded in the task
  record (EXT-010 precedent: the reserved 'Loss Spikes' file was verified to
  be LLM-operations content and replaced by master-ai 04/Training 07+08;
  the excluded 'Loss Spikes'/'Mixed Precision' files remain eligible for a
  future LLM-operations pair — a scope decision, never a preservation
  decision).
- Machine-located evidence lines (X2 locator requiring a unique in-span
  occurrence) are the new standard for classification generators,
  eliminating hand-typed line numbers (EXT-010 improvement over the
  EXT-005..009 pattern); reviewers can still cite quotes at source.
- Orchestrator re-verification of reviewer claims before applying repairs
  remains mandatory (EXT-010 caught a KU-id misattribution in the review's
  S2 and applied the corrected version).
- Classification records are pair-level overlays (ADR-0009); addendum
  discipline (new append-only file with a fresh id prefix when a committed
  domain gains post-commit classifications); dispositions wait for
  synthesis output (all KUs stay Unaccounted).
- Term maps must be built from ACTUAL batch content, pre-probed and
  machine-verified (EXT-004 rule; EXT-009 adds French probing and
  sense-collision documentation; EXT-010 ran FOUR probe rounds and the
  machine verifier still caught 6 unverified entries — always let the
  verifier fail loudly and fix the map rather than trusting the draft).
- Heading/construct detection authority: `mdextract.extract_structure_text`
  (CAP-003) — never naive `#` regex. Pinned vault-ids: `ai-course` and
  `master-ai`. Task-queue schema note: the work-commit hash field is
  `commit`.
- Push policy (user instruction, 2026-10-27): always push to `main`, always
  merge into the head branch; never leave commits local-only at session
  end.

## Next task

- Task ID and title: EXT-011 — to be selected and queued at session start
  with evidence. Candidate directions (decide with evidence, then append a
  full EXT-011 record to state/task-queue.jsonl before executing):
  1. Backpropagation/autodiff pair: master-ai '04 - Neural
     Networks/Training/06 - Backpropagation.md' (315 lines, verified
     present, never extracted; deliberately excluded from EXT-010 as a
     distinct autodiff/BPTT domain) + ai-course backpropagation content
     ('13. Backpropagation and Gradient Flow in CNNs' is referenced by the
     course's own prerequisites callouts — locate it in the manifests
     first).
  2. LLM-operations pair: master-ai '11 - Training/Optimization/05 - Loss
     Spikes and Stability.md' (15,583 bytes) + '04 - Mixed Precision
     Training.md' (14,850 bytes) + ai-course optimization/scheduling
     content (check what exists in the manifests before committing).
  3. A further ai-course chapter (consult state/manifests and the dossier
     gap markers; ai-course 04.3/04 Hyperparameters is still reserved for a
     tuning pair).
- Why not yet queued: the EXT-010 record's notes left the choice to the
  next session with evidence; consult state/manifests, the registry
  coverage report, and the task-queue notes first (15/15 valid entries
  pattern).

## Resume procedure

1. PUSH STATE: origin/main should equal local main (EXT-010 pushed at
   session end). If unpushed commits exist at session end, push them to
   origin/main (fresh PAT if needed) — never leave commits local-only.
2. Read `AGENTS.md`, this file, `state/current-state.json`,
   `state/task-queue.jsonl`, `state/findings.jsonl`, and
   `/home/z/my-project/worklog.md` (the outside-repo cross-session log —
   read it BEFORE starting work; a fresh clone cannot reveal unpushed
   commits).
3. Sanity-verify: `PYTHONPATH=src python3 -m vault_unification selftest`
   (exit 0) and `PYTHONPATH=src python3 -m pytest tests -q` (415/415
   unless tests were legitimately added — update the count then).
4. Verify source immutability: `vu verify-manifest` on both vaults (exit 0).
5. Verify the registry validates (1728 KUs, 164 classifications, 514
   participating; kureg-validate --db state/registries/kuregistry.db; on a
   fresh clone rebuild first: kureg-init --force + kureg-load x11 +
   kureg-apply-overlap x7).
6. Select EXT-011 with evidence, append its full record to
   state/task-queue.jsonl, execute per the EXT-005/EXT-008/EXT-009/EXT-010
   pattern (extract -> fidelity -> term map (probe first, let the verifier
   fail loudly) -> discovery -> classifications (X2 machine-locator) ->
   independent review -> orchestrator re-verification -> repairs ->
   dossier extension if a new domain -> registry rebuild -> state
   updates); rewrite this handoff; commit (work + state) and push to main.

## Explicit non-claims

- Dossiers are scaffolding: category assignments are deterministic rule
  outputs with recorded bases, NOT semantic judgments; several will be
  re-examined at synthesis (especially the default assignments).
- Dossier participation is limited to the 514 classified KUs; the other 1214
  extracted KUs appear in no dossier because they have no classification
  records yet.
- All 1728 KUs remain `Unaccounted`; no dispositions, concept destinations
  or synthesis output exist; `output_synthesis_started` is false.
- The EXT-010 scope exclusions (master-ai 06 Backpropagation; the
  11-Training files; ai-course 04.3/04) do NOT mark those files done: they
  remain unextracted and eligible for future pairs (see Next task).
- Master AI has not been link-checked at all.
