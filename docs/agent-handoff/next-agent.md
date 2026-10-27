# Next Agent Handoff

## Project state

- Current milestone: Milestone 3 (extraction). Framework bootstrap DONE and
  verified (BOOT-000..004). EXT-001..008 DONE and verified: batches 001-007
  (889 KUs; 21 of 609 source files extracted), 102 evidence-based overlap
  classifications across four domains (regression, tree-based, evaluation,
  clustering/dimensionality-reduction), and four concept dossiers (102
  concepts over all 304 classified KUs). EXT-008 completed 2026-10-27 with a
  DOCUMENTED SCOPE CHANGE: the task title named SVM/kernel-methods, but a
  full-vault search proved master-ai has NO dedicated SVM content (16
  occurrences in 11 files, all passing mentions), so the task record's own
  contingency clause was invoked and the clustering/dimensionality-reduction
  pair was extracted instead (master-ai 'Unsupervised Learning/04' + ai-course
  03.5 + 03.8).
- Current task ID: EXT-009 (to be selected at session start — no record in
  the queue yet; see Next task).
- Current Git commit: 58ad0fa (EXT-008 state commit) — PUSHED to
  origin/main on 2026-10-27 (PUSH BLOCKER RESOLVED: a fresh user-supplied
  PAT with repo scope pushed 7d9e65f..58ad0fa; local == remote verified
  via git ls-remote). Commit and push at session end as normal.
- Working tree status: clean after the EXT-008 commits (verify `git status`)
- Registry/checkpoint version: task-queue v11 (BOOT-000..004 + EXT-001..008
  completed with tests_run evidence); KU schema v1.1 (ADR-0008);
  classification schema (ADR-0009); dossier schema with the domain enum
  EXTENDED ADDITIVELY with 'clustering' (justification in the schema
  description); checkpoint
  `state/checkpoints/checkpoint-2026-10-27-ext-008.json`.
- Framework version: 0.5.0 (unchanged in EXT-008 — no framework code
  changes); 415/415 tests; capabilities: 16 implemented-and-tested, 1 planned
  (CAP-014)

## Verified completed work

- EXT-008 (2026-10-27), clustering/dimensionality-reduction domain pair,
  scope-changed from SVM with recorded evidence:
  - Batch 006 = master-ai '04 - Clustering and Dimensionality Reduction.md'
    (27 KUs, 1/1 files, double-run byte-identical, sha256 090573e4...).
    Batch 007 = ai-course 03.5 K-Means (41 KUs) + 03.8 Dimensionality
    Reduction (46 KUs), TWO deterministic single-scope runs concatenated in
    fixed order (each part and the full concat double-run byte-identical,
    sha256 0a49a9fe...).
  - scripts/ext008_fidelity.py: 27/27 + 87/87 byte-exact excerpts + hashes +
    structural purity + 0 heading crossings + unique ids within/across the
    new batches AND vs all 775 committed ids (check extended over the
    EXT-005 pattern).
  - state/term-maps/clustering-domain-v1.json (51 terms, 22 aliases, 32
    cross-vault, 3 BRIDGED terms — 'choosing k'/'choose k'/'number of
    clusters', 'nonlinear'/'non-linear', 'sklearn'/'scikit-learn'; French
    alias 'regroupement' verified at 03.5 L4; every entry machine-verified
    in-scope, zero invented entries).
  - CAP-013 discovery: 934 pairs, 35 cross-vault topics, 0 truncated
    (reports/extraction/ext008-overlap-candidates.json + -pairs.jsonl).
  - state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl:
    27 records OC-ext008-0001..0027 (22 Semantic Duplicate + 4 Partial
    Overlap + 1 Complementary Content), 64 participating KUs, 92 byte-exact
    quotes; generator scripts/ext008_classifications.py chain X1-X9 (quotes
    byte-exact in excerpts AND at original source lines; cross-vault;
    schema-valid; sequential ids; no duplicate quotes anywhere; committed
    classification files 001-004 byte-unchanged).
  - Independent review reports/extraction/ext008-review.md (EXT-008-REVIEW,
    read-only subagent): PASS-WITH-NOTES — 89/89 quotes byte-exact (0
    off-by-one), 27/27 cross-vault, 26 AGREE + 1 AGREE-BORDERLINE + 0
    DISAGREE, 0 coverage gaps, no duplication vs committed records.
    ALL repairs R1-R3 (rationale wording) + suggestions S1-S5 (evidence
    extensions, each new quote verified at its source line before adding)
    applied; orchestrator addendum records the repairs. Final: 92 quotes /
    64 KUs.
  - R4: schemas/concept-dossier.schema.json domain enum extended additively
    with 'clustering'; scripts/ext006_dossiers.py DOMAINS extended;
    state/dossiers/clustering-v1.json generated (27 concepts / 64 KUs;
    zero-evidence categories: interview_misconceptions_comparisons,
    historical_deprecated); ALL FOUR dossiers regenerate byte-identically
    (--check exit 0 x4); tests/test_concept_dossier.py updated (dossier
    list + test rename; suite still 415/415).
  - Registry rebuilt: init --force + load x7 (889 KUs) + apply-overlap x5
    (102 classifications, 0 rejected); kureg-validate valid; 304
    participating KUs; all 889 KUs remain Unaccounted.
  - Sources unchanged before/after (verify-manifest exit 0 x4).
  - Deliberate non-records (single-vault in scope, verified): silhouette
    (master-ai only — the course's silhouette teaching lives in batch
    005/03.6; cross-batch connection noted for synthesis), curse of
    dimensionality (course only), K-Means++/n_init/K-Medians (course only),
    mini-batch k-means + vector-DB ANN indexing (master-ai only),
    SVD/eigendecomposition + Student-t/crowding + Riemannian/fuzzy-topology
    mechanics (course only), VAE/denoising/contractive AE variants
    (master-ai only).

## Tests actually run

| Command/test | Result | Evidence/report |
|---|---|---|
| `vu selftest` (startup) | exit 0 | — |
| `python3 -m pytest tests -q` (startup AND final) | 415/415 | reports/extraction/ext008-pytest-report.json |
| extraction batch 006 + 007 (double-run x2 per part + concat) | byte-identical | reports/extraction/ext008-determinism-{master-ai,ai-course}.txt |
| `python3 scripts/ext008_fidelity.py` | 27/27 + 87/87 byte-exact; ids unique vs 775 committed | reports/extraction/ext008-fidelity-{master-ai,ai-course}.json |
| `python3 scripts/ext008_term_map.py` | exit 0 first run; 51 terms / 22 aliases / 32 cross-vault / 3 bridged | reports/extraction/ext008-term-map-verification.json |
| `vu overlap-candidates` (batches 006+007, clustering terms) | 934 pairs, 35 cross-vault topics, 0 truncated | reports/extraction/ext008-overlap-candidates.json |
| `python3 scripts/ext008_classifications.py` | 27 records, 92 quotes, X1-X9 green (pre- and post-review) | state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl |
| EXT-008-REVIEW (read-only subagent) | PASS-WITH-NOTES; all repairs applied | reports/extraction/ext008-review.md |
| `python3 scripts/ext006_dossiers.py` (x2 + `--check` x4) | clustering-v1 new (27 concepts / 64 KUs); all four byte-identical | reports/extraction/ext006-dossier-coverage.json |
| registry rebuild: `kureg-init --force` + `kureg-load` x7 + `kureg-apply-overlap` x5 + `kureg-validate` | exit 0 x13; 889 KUs, 102 classifications, 304 participating, valid | reports/extraction/ext008-kureg-*.json |
| `vu verify-manifest` both vaults (startup AND after) | exit 0 x4; 333 + 276 unchanged | reports/extraction/ext008-immutable-{master-ai,ai-course}.json |
| `vu capabilities --verify` | 16 implemented-and-tested, 1 planned | reports/extraction/ext008-capabilities.json |
| `vu validate-registry --tasks + --classifications 005-ext008` | valid, 0 problems | reports/extraction/ext008-taskqueue-validate.json |

## Findings and unresolved work

- Open findings: F-0001 (trailing-space dir), F-0002 (14 unclosed-fence
  files), F-0003 (175 broken wikilinks + 10 missing anchors), F-0007
  (boosted-tree library dating), F-0008 (mAP name collision).
- Blockers: none. The 2026-10-26/27 PAT push blocker is RESOLVED (fresh
  PAT worked; origin/main == local main at 58ad0fa).
- Known gaps (deliberate non-claims): 21 of 609 source files extracted
  (3.4%); overlap classified for four domains only; dossiers cover ONLY the
  304 classified KUs (585 extracted KUs have no classification and therefore
  no dossier participation yet — by design); no
  dispositions/concepts-as-destinations; no synthesis output; CAP-014 still
  planned.
- Cross-domain connections noted for synthesis (not actionable in
  extraction): the course's silhouette metrics teaching (batch 005) vs
  master-ai's silhouette mention (batch 006, OC-ext008-0006 rationale); the
  course's chapter-10 autoencoder teaching vs batch 006's autoencoder
  definition (OC-ext008-0027 rationale).

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
- Addendum discipline (EXT-007 precedent): when new classifications for an
  already-classified domain arise after its file is committed, they go into
  a NEW append-only file with a fresh OC-extNNN-* id prefix; committed files
  are never edited. The dossier generator's DOMAINS config lists the
  classification files explicitly per domain.
- Schema-change discipline (EXT-008 precedent): extending an enum
  additively (domain enum + 'clustering') is acceptable when the
  justification is recorded in the schema itself and existing artifacts
  remain valid; anything non-additive requires an ADR.
- Evidence discipline (EXT-008 precedent): a code-block KU can serve as
  quote evidence for a Partial Overlap shared element when the framing is
  transparent (OC-ext008-0021, perplexity named only in master-ai's worked
  example) — the reviewer upheld this on the term-map code-match precedent.
- Pinned vault-ids: `ai-course` and `master-ai`.

## Next task

- Task ID and title: EXT-009 — to be selected and queued at session start
  with evidence. Two candidate directions:
  1. Another domain pair from the unextracted Master AI files: the
     Generalization pair (master-ai '01 - Bias Variance Tradeoff.md' 325
     lines + '06 - Regularization Techniques.md' 199 lines vs ai-course
     regularization content — NOTE: ai-course generalization vocabulary is
     scattered across 84 files, mostly DL chapters, so scoping needs care),
     or the Reinforcement Learning set (master-ai 4 files; ai-course has no
     RL folder — likely ill-scoped like SVM, verify first).
  2. CAP-014 source-to-output coverage reports (required before synthesis
     batches are accepted, but no synthesis batch exists yet — check the
     task-queue record for whether the dependency is now considered ripe).
- Why not yet queued: the EXT-008 record's alternatives clause left the
  choice to the next session with evidence; consult state/manifests and the
  registry coverage report first, then append a full EXT-009 record to
  state/task-queue.jsonl before executing (12/12 valid entries pattern).

## Resume procedure

1. PUSH STATE: origin/main == local main at 58ad0fa (pushed 2026-10-27
   with a working PAT). Run `git fetch origin && git status` to confirm; if
   local-only commits ever accumulate again, work in
   `/home/z/my-project/repo` and never clone fresh; push at session end.
2. Read `AGENTS.md`, this file, `state/current-state.json`,
   `state/task-queue.jsonl`, `state/findings.jsonl`, and
   `/home/z/my-project/worklog.md`.
3. Sanity-verify: `PYTHONPATH=src python3 -m vault_unification selftest`
   (exit 0) and `PYTHONPATH=src python3 -m pytest tests -q` (415/415 unless
   tests were legitimately added — update the count then).
4. Verify source immutability: `vu verify-manifest` on both vaults (exit 0).
5. Verify the registry validates (889 KUs, 102 classifications, 304
   participating; kureg-validate --db state/registries/kuregistry.db).
6. Select EXT-009 with evidence, append its full record to
   state/task-queue.jsonl, execute per the EXT-005/EXT-008 pattern
   (extract -> fidelity -> term map -> discovery -> classifications ->
   independent review -> repairs -> dossier extension if a new domain ->
   registry rebuild -> state updates); rewrite this handoff; commit (work +
   state).

## Explicit non-claims

- Dossiers are scaffolding: category assignments are deterministic rule
  outputs with recorded bases, NOT semantic judgments; several will be
  re-examined at synthesis (especially the default assignments).
- Dossier participation is limited to the 304 classified KUs; the other 585
  extracted KUs appear in no dossier because they have no classification
  records yet.
- All 889 KUs remain `Unaccounted`; no dispositions, concept destinations or
  synthesis output exist; `output_synthesis_started` is false.
- The EXT-008 scope change (SVM -> clustering) does NOT mark SVM as
  "done": the ai-course 03.4 SVM folder (6 files, 436 lines) remains
  unextracted; if master-ai ever gains SVM content, the pair can be
  revisited. Master-ai's absence of SVM content is a vault-content fact,
  not a project finding.
- Master AI has not been link-checked at all.
