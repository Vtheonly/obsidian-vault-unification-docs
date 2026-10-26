# Next Agent Handoff

## Project state

- Current milestone: Milestone 3 (extraction). Framework bootstrap DONE and
  verified (BOOT-000..004). EXT-001..005 DONE and verified (batches 001-005:
  775 KUs; 71 evidence-based overlap classifications across regression, tree
  and evaluation domains). EXT-006 (concept-dossier scaffolding) DONE and
  verified 2026-10-27: `schemas/concept-dossier.schema.json`,
  `scripts/ext006_dossiers.py` (deterministic, rule set
  ext006-category-rules-v1), `state/dossiers/{regression,tree-based,
  evaluation}-v1.json` (71 concepts over all 234 classified KUs, explicit
  per-(concept, category) gap markers), coverage + determinism evidence, 8
  new integration tests (suite now 415/415).
- Current task ID: EXT-007 (status: queued — record already in the queue;
  make it in_progress when starting). Evaluation-domain classification
  addendum: adjudicate candidates C1-C4 from
  reports/extraction/ext005-independent-confirmation.md section 3.
- Current Git commit: the EXT-006 work/state commits on LOCAL `main`, on top
  of the EXT-005 verification commit a5e9d47. PUSH BLOCKER (STILL OPEN):
  all three PATs from the brief were rejected on 2026-10-26 AND re-rejected
  2026-10-27 (401 Bad credentials). The user has instructed the session to
  continue committing locally and deliver a ZIP (repo + git bundle) that the
  user will push personally. Do NOT re-clone while local-only commits exist.
- Working tree status: clean after the EXT-006 commits (verify `git status`)
- Registry/checkpoint version: task-queue v9 (BOOT-000..004 + EXT-001..006
  completed with tests_run evidence; EXT-007 queued); KU schema v1.1
  (ADR-0008); classification schema (ADR-0009); NEW dossier schema
  `schemas/concept-dossier.schema.json`; checkpoint
  `state/checkpoints/checkpoint-2026-10-27-ext-006.json`.
- Framework version: 0.5.0 (unchanged in EXT-006 — no framework code
  changes); 415/415 tests (8 new dossier integration tests); capabilities:
  16 implemented-and-tested, 1 planned (CAP-014)

## Verified completed work

- EXT-006 (2026-10-27), concept-dossier scaffolding, single session:
  - Schema `schemas/concept-dossier.schema.json` (draft 2020-12): dossier =
    domain + version + rule_set + provenance (batch/classification paths with
    sha256 + record counts) + concepts + accounting; concept = one per
    classification record (label = topic, ku_ids = record ku_ids, overlap_type
    carried as pair-level REFERENCE); ten fixed evidence categories from
    KNOWLEDGE_AND_PROVENANCE.md section 7; per-category ku_ids + by_vault +
    assignment_bases; gap kinds no_evidence / single_vault; accounting carries
    bidirectional_check + zero_evidence_categories + standing
    disposition_note. NO disposition fields anywhere (schema-level).
  - Generator `scripts/ext006_dossiers.py`: deterministic (no timestamps, no
    absolute paths, sort_keys JSON, stable orders); rule set
    ext006-category-rules-v1 = unit_type rules (math_block ->
    mathematical_foundations; code_block -> code_implementation) + heading
    keyword rules (example / failure-case / implementation / mathematical /
    algorithm-mechanics / engineering-guidance / versus-distinction /
    year-reference / interview-misconception / interpretation-intuition) +
    excerpt rules (complexity notation O(...); library mention sklearn /
    scikit-learn; French alternative treatment = >= 5 distinct French words)
    + total default (definitions_terminology). Every assignment records its
    basis; multiple categories per KU allowed (many-to-many, invariant 5).
  - Validation before writing: V1 every KU id exists in the domain's
    committed batches; V2 classification ids exist and are unique; V3 concept
    KU set == record KU set; V4 bidirectional coverage (participating <->
    covered, both directions); V5 output validates against the schema.
  - Dossiers: regression-v1 = 14 concepts / 61 KUs; tree-based-v1 = 28
    concepts / 82 KUs; evaluation-v1 = 29 concepts / 91 KUs. 234 participating
    KUs total — exactly the classified KU population (registry agrees).
    Zero-evidence categories explicit: interview_misconceptions_comparisons in
    ALL THREE domains (genuine gap: no interview/misconception content
    participates yet); historical_deprecated in regression + evaluation;
    computational_mechanics + alternative_explanations in evaluation.
    single_vault gaps: 29 (regression) + 39 (tree) + 40 (evaluation) — e.g.
    CD-evaluation-0025 calibration definitions present only on master-ai side.
  - Determinism: double-run byte-identical; `--check` regenerates in memory
    and compares byte-exactly with committed files (exit 0).
  - 8 new integration tests `tests/test_concept_dossier.py`: schema
    self-validates with ten categories; no disposition properties; committed
    dossiers validate; byte-identical regeneration (--check subprocess); all
    referenced KU ids exist in committed batches; no disposition fields in
    committed dossiers + bidirectional flags true; zero-evidence categories
    match counts and per-concept gap markers match empty categories; coverage
    report consistent with dossiers. Suite 415/415 (was 407).
  - Registry NOT reloaded (dossiers are a derived view): rebuild verified at
    startup (775 KUs, 71 classifications, valid, 0 errors/warnings); all 775
    KUs remain Unaccounted; committed batches and classification files
    untouched (git status: only new files).

## Tests actually run

| Command/test | Result | Evidence/report |
|---|---|---|
| `vu selftest` (startup) | exit 0 | — |
| `python3 -m pytest tests -q` (startup) | 407/407 | — |
| `vu verify-manifest` both vaults (startup AND after) | exit 0 x4; 333 + 276 unchanged | reports/extraction/ext006-immutable-{start,after}-{master-ai,ai-course}.json |
| registry rebuild: `kureg-init --force` + `kureg-load` x5 + `kureg-apply-overlap` x3 + `kureg-validate` | exit 0 x10; 775 KUs, 71 inserted, valid 0 err/warn | reports/extraction/ext006-kureg-*.json |
| `python3 scripts/ext006_dossiers.py` (x2 + `--check`) | exit 0; byte-identical double-run AND vs committed | reports/extraction/ext006-determinism.txt |
| `python3 -m pytest tests/test_concept_dossier.py -v` | 8/8 | reports/extraction/ext006-pytest-report.json |
| `python3 -m pytest tests -q` (final) | 415/415 | reports/extraction/ext006-pytest-report.json |
| `vu capabilities --verify` | 16 implemented-and-tested, 1 planned | reports/extraction/ext006-capabilities.json |

## Findings and unresolved work

- Open findings: F-0001 (trailing-space dir), F-0002 (14 unclosed-fence
  files), F-0003 (175 broken wikilinks + 10 missing anchors), F-0007
  (boosted-tree library dating), F-0008 (mAP name collision).
- Blockers: PUSH BLOCKER (see Project state) — user pushes the delivered
  zip/bundle personally; local commits accumulate in `/home/z/my-project/repo`.
- Known gaps (deliberate non-claims): 17 of 609 source files extracted (2.8%);
  overlap classified for three domains only; dossiers cover ONLY the 234
  classified KUs (541 extracted KUs have no classification and therefore no
  dossier participation yet — by design); no dispositions/concepts-as-
  destinations; no synthesis output; CAP-014 still planned.

## Decisions and configuration

- Dossier concepts are classification-record-scoped (one concept per record,
  label = record topic). Concepts are NOT merged across records even when
  they share KUs — merging is a synthesis-time judgment, not a scaffolding
  job. A KU may appear in several concepts (many-to-many, invariant 5).
- Category assignments are SCAFFOLDING, not judgments: every assignment
  carries its deterministic basis string; synthesis re-examines and never
  blindly trusts. The default rule is honest and visible
  (`default:no-rule-fired(unit_type=...)`).
- Heading text IS usable for dossier scaffolding (it is structural metadata
  already committed in the KU records), but is NOT classification evidence
  (EXT-004 rule, unchanged — those are different uses).
- Dossiers never assign dispositions; overlap_type appears only as a
  pair-level reference carried from the source record (ADR-0009).
- The dossier generator auto-includes `state/classifications/004-ext007-
  evaluation-addendum.jsonl` in the evaluation domain once that file exists
  — EXT-007 must REGENERATE the evaluation dossier after committing the
  addendum (same v1, provenance updated) and re-run the dossier tests.
- Pinned vault-ids: `ai-course` and `master-ai`.

## Next task

- Task ID and title: EXT-007 — Evaluation-domain classification addendum:
  independently review and (if adopted) commit the four candidate clusters
  (C1-C4) from the 2026-10-27 confirmation session. Full record (inputs /
  outputs / acceptance criteria / forbidden side effects) is in
  `state/task-queue.jsonl` (status: queued).
- Why it is next: the four cross-vault clusters (C1 track-multiple-metrics
  SD; C2 pixel-accuracy degenerate-model PO; C3 loss-vs-metric role
  distinction PO; C4 imbalanced-data PR-AUC + macro-F1 pairing, possibly an
  evidence extension of OC-ext005-0015 instead of a new record) carry
  byte-exact quotes but NO independent review; they must not silently rot as
  unreviewed report content. Adopted records go to a NEW append-only file
  `state/classifications/004-ext007-evaluation-addendum.jsonl` with OC-ext007-*
  ids; `003-ext005` stays byte-unchanged.
- After EXT-007: candidate EXT-008 directions (decide with evidence): another
  domain pair (e.g. SVM: ai-course 03.4 vs master-ai SVM content), CAP-014
  (source-to-output coverage reports), or dossier-driven synthesis prep.

## Resume procedure

1. PUSH STATE: local main is ahead of origin/main (EXT-005 verification +
   EXT-006 commits, and EXT-007 if completed). The user pushes the delivered
   zip/bundle personally. NEVER clone fresh while local-only commits exist;
   work in `/home/z/my-project/repo`.
2. Read `AGENTS.md`, this file, `state/current-state.json`,
   `state/task-queue.jsonl`, `state/findings.jsonl`, and
   `/home/z/my-project/worklog.md`.
3. Sanity-verify: `PYTHONPATH=src python3 -m vault_unification selftest`
   (exit 0) and `PYTHONPATH=src python3 -m pytest tests -q` (415/415 unless
   tests were legitimately added — update the count then).
4. Verify source immutability: `vu verify-manifest` on both vaults (exit 0).
5. Verify the registry rebuilds (775 KUs, 71 classifications — 74 after
   EXT-007 if all four candidates are adopted as new records).
6. Execute EXT-007 per its task record; regenerate the evaluation dossier
   after committing the addendum; update task queue, current-state,
   checkpoint, findings; rewrite this handoff; commit (work + state).

## Explicit non-claims

- Dossiers are scaffolding: category assignments are deterministic rule
  outputs with recorded bases, NOT semantic judgments; several will be
  re-examined at synthesis (especially the default assignments —
  regression 15/61, tree 38/82, evaluation 45/91 KUs landed in
  definitions_terminology by default).
- Dossier participation is limited to the 234 classified KUs; the other 541
  extracted KUs appear in no dossier because they have no classification
  records yet.
- All 775 KUs remain `Unaccounted`; no dispositions, concept destinations or
  synthesis output exist; `output_synthesis_started` is false.
- The four C1-C4 candidates in the confirmation report are NOT
  classifications (unreviewed); EXT-007 must adopt or reject them with
  recorded rationale and independent review.
- Master AI has not been link-checked at all.
