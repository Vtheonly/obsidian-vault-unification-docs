# Next Agent Handoff

## Project state

- Current milestone: Milestone 3 (extraction). Framework bootstrap DONE and
  verified (BOOT-000..004). EXT-001..009 DONE and verified: batches 001-009
  (1229 KUs; 26 of 609 source files extracted), 128 evidence-based overlap
  classifications across five domains (regression, tree-based, evaluation,
  clustering/dimensionality-reduction, generalization/regularization), and
  five concept dossiers (128 concepts over all 372 classified KUs).
  EXT-009 completed 2026-10-27 ACROSS TWO SESSIONS (the first session was
  interrupted mid-review-repair by a tool-infrastructure failure after
  completing batches, term map, discovery, classifications, and the
  independent review; the completing session re-verified the review claims
  at source, applied the remaining repairs R1/R2 + S1-S5, and finished R3).
- Current task ID: EXT-010 (to be selected at session start — no record in
  the queue yet; see Next task).
- Current Git commit: the EXT-009 work/state commits on `main`.
  PUSH BLOCKER RESOLVED (2026-10-27): a fresh PAT pushed
  7d9e65f..58ad0fa (the previously local-only EXT-005..EXT-008 commits) to
  origin/main; commit 7041d47 records the resolution. Push new work to
  origin/main directly; always push to main (user instruction).
- Working tree status: clean after the EXT-009 commits (verify `git status`)
- Registry/checkpoint version: task-queue v14 records (BOOT-000..004 +
  EXT-001..009 completed with tests_run evidence); KU schema v1.1
  (ADR-0008); classification schema (ADR-0009); dossier schema with the
  domain enum EXTENDED ADDITIVELY with 'clustering' (EXT-008) and
  'generalization' (EXT-009, justification in the schema description);
  checkpoint `state/checkpoints/checkpoint-2026-10-27-ext-009.json`.
- Framework version: 0.5.0 (unchanged in EXT-009 — no framework code
  changes); 415/415 tests; capabilities: 16 implemented-and-tested, 1
  planned (CAP-014)

## Verified completed work

- EXT-009 (2026-10-27, two sessions), generalization/regularization domain
  pair — FIRST PARTIAL-FOLDER ai-course scope (04.3 files 05/06/07 of 7;
  per-file justification in the task record's scope-decision notes):
  - Batch 008 = master-ai '03 - Machine Learning/Generalization' (both
    files: 01 Bias Variance Tradeoff 325 lines + 06 Regularization
    Techniques 199 lines): 106 KUs, 2/2 files, double-run byte-identical
    (sha256 2e258f18...).
  - Batch 009 = ai-course 04.3 '05. Batch Normalization' (597 lines) +
    '06. Dropout and Regularization' (589 lines) + '07. Data Augmentation'
    (734 lines): 234 KUs, three deterministic single-file runs concatenated
    in fixed order (each part and the full concat double-run
    byte-identical, sha256 479e1eda...).
  - scripts/ext009_fidelity.py: 106/106 + 234/234 byte-exact excerpts +
    hashes + structural purity + 0 heading crossings + ids unique
    within/across the new batches AND vs all 889 committed ids.
  - state/term-maps/generalization-domain-v1.json: 65 terms, 40 aliases,
    38 cross-vault, 2 BRIDGED ('hyperparameter', 'test set'); vocabulary
    pre-probed against both batches before writing; every entry
    machine-verified in-scope; no French vocabulary in scope
    (probe-verified); sense-collision vocabulary (noise / translation /
    shift / scaling / inference / bias / variance) documented in the map
    comment and adjudicated per pair with evidence.
  - CAP-013 discovery: 2961 pairs, 40 cross-vault topics, 5 topics
    truncated at the 250-pair cap (per-KU evidence complete).
  - state/classifications/006-ext009-generalization-overlap.jsonl: 26
    records OC-ext009-0001..0026 (21 Semantic Duplicate + 3 Partial
    Overlap + 2 Complementary Content), 68 participating KUs, 88
    byte-exact quotes; generator scripts/ext009_classifications.py chain
    X1-X9 (quotes byte-exact in excerpts AND at original source lines;
    cross-vault; schema-valid; sequential ids; no duplicate quotes;
    committed files 001-005 byte-unchanged).
  - Independent review reports/extraction/ext009-review.md (EXT-009-REVIEW,
    read-only subagent): PASS-WITH-NOTES — 86/86 quotes byte-exact (0
    off-by-one), 25/25 cross-vault, 25 AGREE + 0 BORDERLINE + 0 DISAGREE,
    scope decision verified legitimate, ONE coverage gap (CG-1). ALL
    repairs applied before commit: R1 OC-ext009-0026 added (LayerNorm-
    preference cluster, master 06 L123 x course 05 L551, SD) + 0018's
    master-only clause fixed; R2 four rationale line-reference corrections
    (0002 L111->L115 + section span L254-269; 0008 L443-446->L455-456;
    0009 L423->L422; 0022 L189->L190); suggestions S1-S5 applied (S1 0019
    'underfits' acknowledgment; S2 0009 validation-anchor scoped to
    master-ai + AdamW-era characterization grounded at L173/L161/L167; S3
    0025 cross-reference to OC-ext005-0029; S4 0016/0023 name the
    OC-ext004-0005/0010/0016/0026 adjacencies; S5 synthesis notes recorded
    below in Cross-domain connections). Orchestrator addendum records
    every repair with its source re-verification.
  - Dossier: schemas/concept-dossier.schema.json domain enum extended
    additively with 'generalization'; scripts/ext006_dossiers.py DOMAINS
    extended; state/dossiers/generalization-v1.json generated (26 concepts
    / 68 KUs; zero-evidence categories: computational_mechanics,
    interview_misconceptions_comparisons); ALL FIVE dossiers regenerate
    byte-identically (--check exit 0 x5); tests/test_concept_dossier.py
    DOSSIER_FILES updated (suite 415/415).
  - Registry rebuilt: init --force + load x9 (1229 KUs) + apply-overlap x6
    (128 classifications, 0 rejected) + kureg-validate valid; 372
    participating KUs; all 1229 KUs remain Unaccounted.
  - Sources unchanged before/after (verify-manifest exit 0 x4).
  - Deliberate non-records (single-vault in scope, review-verified):
    master-ai-only — bias-variance decomposition derivation, double
    descent / interpolation regimes, LLM-specific levers (LoRA rank, SFT
    epochs, prompt overfitting, self-consistency), elastic net +
    ridge/lasso prior interpretations, weight tying, RMSNorm, text/audio
    augmentation lists; ai-course-only — BN four-step mathematics, ICS +
    Santurkar caveat, running statistics / EMA / eval-mode mechanics,
    batch-size effects, GN/IN alternatives, placement debate, Bernoulli-
    mask algebra, mixup/cutmix/RandAugment mechanics, RandomResizedCrop
    parameters, Gaussian-noise/random-erasing implementations, invariance
    philosophy.

## Tests actually run

| Command/test | Result | Evidence/report |
|---|---|---|
| `vu selftest` (startup, both sessions) | exit 0 | — |
| `python3 -m pytest tests -q` (startup AND final) | 415/415 | reports/extraction/ext009-pytest-report.json |
| extraction batches 008 + 009 (double-run x2 per part + concat) | byte-identical | coverage reports per file |
| `python3 scripts/ext009_fidelity.py` | 106/106 + 234/234 byte-exact; ids unique vs 889 committed | reports/extraction/ext009-fidelity-{master-ai,ai-course}.json |
| `python3 scripts/ext009_term_map.py` (after 2 probe rounds) | exit 0 first run; 65 terms / 40 aliases / 38 cross-vault / 2 bridged | reports/extraction/ext009-term-map-verification.json |
| `vu overlap-candidates` (batches 008+009) | 2961 pairs, 40 cross-vault topics, 5 truncated | reports/extraction/ext009-overlap-candidates.json + -pairs.jsonl |
| `python3 scripts/ext009_classifications.py` | 26 records, 88 quotes, X1-X9 green (pre- and post-review) | state/classifications/006-ext009-generalization-overlap.jsonl |
| EXT-009-REVIEW (read-only subagent) | PASS-WITH-NOTES; all repairs applied | reports/extraction/ext009-review.md |
| `python3 scripts/ext006_dossiers.py` (x2 + `--check` x5) | generalization-v1 new (26 concepts / 68 KUs); all five byte-identical | reports/extraction/ext006-dossier-coverage.json |
| registry rebuild: `kureg-init --force` + `kureg-load` x9 + `kureg-apply-overlap` x6 + `kureg-validate` | exit 0 x16; 1229 KUs, 128 classifications, 372 participating, valid | reports/extraction/ext009-kureg-*.json |
| `vu verify-manifest` both vaults (startup AND after) | exit 0 x4; 333 + 276 unchanged | reports/extraction/ext009-immutable-{start,end}-{master-ai,ai-course}.json |
| `vu capabilities --verify` | 16 implemented-and-tested, 1 planned | reports/extraction/ext009-capabilities.json |
| `vu validate-registry --tasks + --classifications 006-ext009` | valid, 0 problems | reports/extraction/ext009-taskqueue-validate.json |

## Findings and unresolved work

- Open findings: F-0001 (trailing-space dir `source-vaults/AI ` — always
  quote), F-0002 (14 AI Course unclosed-fence files — extractor handles
  them), F-0003 (175 broken wikilinks + 10 missing anchors in AI Course —
  synthesis-time dispositions), F-0007 (boosted-tree library dating —
  synthesis-time reconciliation), F-0008 (mAP name collision).
- Blockers: NONE. The push blocker was resolved 2026-10-27 (fresh PAT;
  7d9e65f..58ad0fa on origin/main).
- Known gaps (deliberate non-claims): 26 of 609 source files extracted
  (4.3%); overlap classified for five domains only; dossiers cover ONLY
  the 372 classified KUs (857 extracted KUs have no classification and
  therefore no dossier participation yet — by design); no
  dispositions/concepts-as-destinations; no synthesis output; CAP-014
  still planned; Master AI has never been link-checked.
- Cross-domain connections noted for synthesis (not actionable in
  extraction): the implicit-regularization concept family (master SGD
  noise L62; course weight-sharing and BN-noise — the instances are
  recorded in OC-ext009 records but the concept-level link is not);
  noise-as-augmentation across modalities (master audio 'noise injection'
  L107 vs course image Gaussian-noise section — modality-different,
  worth a synthesis note in the augmentation dossier); the course's
  silhouette teaching (batch 005) vs master-ai's silhouette mention
  (batch 006, OC-ext008-0006 rationale); the course's chapter-10
  autoencoder teaching vs batch 006's autoencoder definition
  (OC-ext008-0027 rationale).

## Decisions and configuration

- Partial-folder scopes are legitimate when justified per file with
  headings evidence and recorded in the task record (EXT-009 precedent:
  3 of 7 files in 04.3; the excluded files remain eligible for later
  batches — this is a scope decision, never a preservation decision).
- A task interrupted mid-flight (after review, before repairs) may be
  completed by a following session provided it (a) re-runs the startup
  battery, (b) independently re-verifies the review claims at source
  before applying repairs, and (c) regenerates artifacts through the
  verification-chain scripts rather than editing outputs by hand
  (EXT-009 two-session precedent).
- Rationale wording repairs and review-suggested evidence extensions are
  applied in the GENERATOR script and the file is regenerated, so the
  X1-X9 chain re-verifies every quote on every run (EXT-005..009
  precedent).
- Classification records are pair-level overlays (ADR-0009); addendum
  discipline (new append-only file with a fresh id prefix when a
  committed domain gains post-commit classifications); dispositions wait
  for synthesis output (all KUs stay Unaccounted).
- Term maps must be built from ACTUAL batch content, pre-probed and
  machine-verified (EXT-004 rule; EXT-009 adds: probe for French
  vocabulary too, and document sense-collision vocabulary in the map
  comment).
- Heading/construct detection authority: `mdextract.extract_structure_text`
  (CAP-003) — never naive `#` regex. Pinned vault-ids: `ai-course` and
  `master-ai`. Task-queue schema note: the work-commit hash field is
  `commit`.
- Push policy (user instruction, 2026-10-27): always push to `main`,
  always merge into the head branch; never leave commits local-only at
  session end.

## Next task

- Task ID and title: EXT-010 — to be selected and queued at session start
  with evidence. Two candidate directions:
  1. Training-stability pair (RESERVED by the EXT-009 scope notes):
     master-ai '11 - Training/Optimization/05 - Loss Spikes and
     Stability.md' (15,583 bytes, verified present) + ai-course 04.3
     files 01 'Weight Initialization' (58,081 bytes), 02 'Weight
     Initialization Techniques' (7,496 bytes), 03 'The Vanishing and
     Exploding Gradient Problems' (71,416 bytes). NOTE: this is a
     DL-training-stability pairing, not a classical-ML one — check
     master-ai's file actually covers init/gradient-stability content
     before committing (the same evidence-first scoping discipline as
     EXT-008/009; master-ai '11 - Training/Optimization' also holds
     '04 - Mixed Precision Training' as an alternative counterpart).
  2. CAP-014 source-to-output coverage reports (required before synthesis
     batches are accepted, but no synthesis batch exists yet — check the
     task-queue record for whether the dependency is now considered ripe).
- Why not yet queued: the EXT-009 record's notes left the choice to the
  next session with evidence; consult state/manifests and the registry
  coverage report first, then append a full EXT-010 record to
  state/task-queue.jsonl before executing (14/14 valid entries pattern).

## Resume procedure

1. PUSH STATE: origin/main should equal local main (push blocker resolved
   2026-10-27). If local-only commits exist at session end, push them to
   origin/main (fresh PAT if needed) — never leave commits local-only.
   Work in `/home/z/my-project/repo` while unpushed commits exist.
2. Read `AGENTS.md`, this file, `state/current-state.json`,
   `state/task-queue.jsonl`, `state/findings.jsonl`, and
   `/home/z/my-project/worklog.md` (the outside-repo cross-session log —
   read it BEFORE starting work; a fresh clone cannot reveal unpushed
   commits).
3. Sanity-verify: `PYTHONPATH=src python3 -m vault_unification selftest`
   (exit 0) and `PYTHONPATH=src python3 -m pytest tests -q` (415/415
   unless tests were legitimately added — update the count then).
4. Verify source immutability: `vu verify-manifest` on both vaults (exit 0).
5. Verify the registry validates (1229 KUs, 128 classifications, 372
   participating; kureg-validate --db state/registries/kuregistry.db).
6. Select EXT-010 with evidence, append its full record to
   state/task-queue.jsonl, execute per the EXT-005/EXT-008/EXT-009 pattern
   (extract -> fidelity -> term map -> discovery -> classifications ->
   independent review -> repairs -> dossier extension if a new domain ->
   registry rebuild -> state updates); rewrite this handoff; commit (work +
   state) and push to main.

## Explicit non-claims

- Dossiers are scaffolding: category assignments are deterministic rule
  outputs with recorded bases, NOT semantic judgments; several will be
  re-examined at synthesis (especially the default assignments).
- Dossier participation is limited to the 372 classified KUs; the other
  857 extracted KUs appear in no dossier because they have no
  classification records yet.
- All 1229 KUs remain `Unaccounted`; no dispositions, concept destinations
  or synthesis output exist; `output_synthesis_started` is false.
- The EXT-009 partial-folder scope (04.3 files 01-04 excluded) does NOT
  mark those files done: they remain unextracted and are reserved for a
  future training-stability/optimization pair (see Next task).
- Master AI has not been link-checked at all.
