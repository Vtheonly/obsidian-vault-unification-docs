# Next Agent Handoff

## Project state

- Current milestone: Milestone 3 (extraction). Framework bootstrap DONE and
  verified (BOOT-000..004; omission-detection hard gate PASSED). EXT-001
  (first real batch, AI Course regression) DONE and verified. EXT-002
  (paired Master AI batch) DONE and verified. EXT-003 (CAP-013 + first 14
  evidence-based overlap classifications, regression domain) DONE and
  verified. EXT-004 (AI Course tree-based batch + 28 evidence-based
  classifications, tree domain) DONE and verified. EXT-005
  (evaluation-metrics domain pair, BOTH sides extracted, + 29 evidence-based
  classifications) DONE and verified.
- Current task ID: EXT-006 (status: ready — record already in the queue).
  EXT-007 (evaluation classification addendum candidates, queued,
  priority normal) was added 2026-10-27 — see
  reports/extraction/ext005-independent-confirmation.md section 3.
- Current Git commit: the EXT-005 verification/session commit on LOCAL
  `main` (on top of 765774c state + 4f369bd push-blocker docs commits);
  verify with `git log --oneline -5`.
  PUSH BLOCKER (STILL OPEN, retried 2026-10-27): the push of the EXT-005
  commits to origin/main FAILED on 2026-10-26 AND the retry on 2026-10-27
  with the SAME three PATs (re-supplied by the user, "one of them should
  work") also failed — each returns 401 Bad credentials on the GitHub API
  (Bearer AND token schemes) and 'Invalid username or token' on git push
  (x-access-token URL format). All three tokens are expired/revoked.
  The commits exist ONLY locally. The next session MUST obtain FRESH
  credentials (new PAT with repo scope for
  Vtheonly/obsidian-vault-unification-docs) and push (7d9e65f..HEAD) to
  origin/main BEFORE doing any other work, then verify with `git fetch` +
  `git status`. Evidence: reports/extraction/ext005-independent-
  confirmation.md section 2 (full retry matrix).
- Working tree status: clean after commits (verify with `git status`)
- Registry/checkpoint version: task-queue v8 (BOOT-000..004 + EXT-001..005
  completed with tests_run evidence; EXT-006 ready; EXT-007 queued on
  2026-10-27); KU schema v1.1
  (ADR-0008); classification schema
  `schemas/overlap-classification.schema.json` (ADR-0009 pair-level
  overlay); checkpoint `state/checkpoints/checkpoint-2026-10-26-ext-005.json`
  (EXT-005) — the 2026-10-27 session was verification-only (no new
  extraction): batch 004/005 re-extracted byte-identical in a separate
  clone, classification set independently re-derived and convergent, all
  recorded in reports/extraction/ext005-independent-confirmation.md
- Framework version: 0.5.0 (unchanged in EXT-005 — no code changes);
  407/407 tests; capabilities: 16 implemented-and-tested, 1 planned
  (CAP-014)

## Verified completed work

- 2026-10-27 verification session (no new extraction; this session):
  - Independent re-derivation of EXT-005 in a fresh clone CONFIRMS the
    committed work: batches 004 (43 KUs) and 005 (275 KUs) re-extracted
    byte-identical (cmp); determinism double-runs byte-identical; a new
    both-batch fidelity checker passed 43/43 + 275/275; an independently
    built term map (123 terms / 90 aliases / 44 cross-vault, machine-
    verified) and CAP-013 run (318 KUs, 45 cross-vault topics, 1927
    pairs, 0 hash duplicates) reproduce the discovery conclusions; a
    29-record classification set generated with byte-exact quotes
    converges with the committed one on every major cluster. Evidence:
    reports/extraction/ext005-independent-confirmation.md.
  - Push retried with all three PATs (API Bearer, API token, git push
    x-access-token): ALL rejected (401 / Invalid username or token).
    Blocker persists; fresh credentials required. Evidence: same report,
    section 2.
  - Four candidate additional classification clusters (C1-C4) recorded
    as UNREVIEWED candidates in the report section 3 and queued as
    EXT-007 for adoption-or-rejection with independent review. The
    duplicate unreviewed artifacts were deliberately NOT committed
    (competing-records discipline, ADR-0009); nothing was silently
    discarded — the candidates and their byte-exact quotes are in the
    committed report.
  - Tests re-run this session: pytest 407/407 in `/home/z/my-project/repo`;
    registry rebuild kureg-validate valid (775 KUs, 71 classifications,
    234 participating, 0 errors/warnings); both vaults immutable
    (exit 0 x2); task queue + classification validation valid 12/12 +
    29/29 after the EXT-007 append (report
    reports/extraction/ext005-verification-taskqueue-validate.json).

- EXT-005 (2026-10-26), evaluation-metrics domain pair — the first EXT task
  where BOTH sides needed extraction (two batches in one task). Single
  session; every claim below has a committed evidence artifact.
  - Batch 004 `state/knowledge-units/004-ext005-master-ai-evaluation.jsonl`:
    43 KUs from master-ai '03 - Machine Learning/Evaluation/05 - ML
    Evaluation Metrics.md' (1/1 extracted, 0 excluded, 0 failed; frontmatter
    1, callout 1, math_block 9, prose 20, table 1, list 10, code_block 1).
    Double-run byte-identical (sha256 dd5d27f5...). Coverage report
    reports/extraction/ext005-coverage-master-ai.json.
  - Batch 005 `state/knowledge-units/005-ext005-ai-course-03.6-model-
    evaluation.jsonl`: 275 KUs from the 5 files of ai-course '03 - Machine
    Learning/03.6 - Model Evaluation' (5/5 extracted, 0 excluded, 0 failed;
    prose 155, list 57, math_block 37, table 8, callout 8, quote 6,
    code_block 4). Double-run byte-identical (sha256 6afa011b...). None of
    the 03.6 files is among the 14 F-0002 unclosed-fence files (verified
    against the committed parse-error list before extraction).
  - Fidelity (`scripts/ext005_fidelity.py`, checks BOTH batches at once):
    43/43 + 275/275 byte-exact excerpts + excerpt hashes + unique ids
    (uniqueness enforced within AND across the two batches) + structural
    purity + 0 heading-crossing spans (reports/extraction/
    ext005-fidelity-{master-ai,ai-course}.json).
  - Term map `state/term-maps/evaluation-domain-v1.json` (98 terms, 33
    aliases, 40 cross-vault terms) built from ACTUAL batch content; every
    canonical term and alias machine-verified to occur in an in-scope KU
    excerpt (`scripts/ext005_term_map.py`; first run passed with zero
    invented entries — candidate vocabulary was pre-probed against both
    batches before writing the map; evidence reports/extraction/
    ext005-term-map-verification.json). No French aliases (probe: précision/
    rappel/exactitude/métrique/seuil/étiquette all absent). Deliberate
    design choice: 'mAP' is included although case-insensitive matching
    lets ai-course CV mAP collide with master-ai ranking MAP and with
    'Color map' (ai-course L436) — homonym adjudication is the
    classification's job, which is exactly what happened (OC-0023/OC-0024).
  - CAP-013 discovery over BOTH full batches (no derived subset needed for
    this domain): 318 KUs, 40 cross-vault topics, 1604 term pairs (1566
    confirmed, 38 unconfirmed-only), 0 exact/normalized hash duplicates, 2
    truncated topics (precision and recall at the 250-pairs-per-topic cap;
    per-KU evidence stays complete — known limitation)
    (reports/extraction/ext005-overlap-candidates.json + -pairs.jsonl).
  - `state/classifications/003-ext005-evaluation-overlap.jsonl`: 29
    evidence-based classifications — 23 Semantic Duplicate (accuracy
    formula; accuracy trap; confusion-matrix table + derived-metrics claim;
    precision formula; recall formula; precision-recall tension + error
    costs; spam-precision example; cancer-recall example; F1 formula;
    harmonic-mean rationale; ROC definition; AUC probabilistic
    interpretation; AUC threshold-independence + imbalance-insensitivity;
    PR-AUC under extreme imbalance; macro averaging; micro averaging; MSE;
    MAE; RMSE; R^2; Huber; ranking mAP; metric-choice-is-a-business-
    decision), 5 Partial Overlap (F-beta convention; mAP name collision;
    cross-validation for small data; sklearn.metrics tooling; held-out
    test-data discipline), 1 Complementary Content (calibration treatment
    vs AUC-ranking-only note). 91 participating KUs of 318; 105 byte-exact
    evidence quotes; rationale + method per record. Generated by
    `scripts/ext005_classifications.py` which verifies EVERY quote
    byte-exact inside the referenced KU excerpt before writing (caught 2
    wrong-KU-id citations and 1 callout-prefix transcription error during
    development) and validates schema + cross-checks before exit 0.
  - Judgment classifications per the EXT-003 precedent: master-ai's
    confusion-matrix table and Huber description carry names only in
    section headings (outside KU excerpts), so term matching could not pair
    them — paired by structure/description identity with byte-exact quotes
    (OC-0003, OC-0022); the mAP name collision is split into OC-0023
    (ranking sense, Semantic Duplicate — both vaults use it for
    search/recommendation) and OC-0024 (cross-sense, Partial Overlap);
    calibration is Complementary Content (course states the AUC limitation,
    master-ai supplies definition + remedies; neither subsumes the other).
  - Independent review (EXT-005-REVIEW subagent, read-only): verdict
    PASS-WITH-NOTES — 95/95 quotes byte-exact including ORIGINAL-source
    line verification (0 off-by-one), 28/28 cross-vault, 26 AGREE + 2
    AGREE-BORDERLINE + 0 DISAGREE semantic verdicts; found 2 required
    rationale repairs (both wrongly claimed master-ai 'never names' the
    confusion matrix / Huber loss — file-level headings DO carry the names
    at source lines 22 and 111; the orchestrator independently verified
    both against the source before applying) and 1 genuine coverage gap
    (held-out/leakage cluster participated in no record). ALL repairs
    applied and the file regenerated at 29 records before commit: R1
    (OC-0003 reworded — naming difference is presentational: heading vs
    prose), R2 (OC-0022 reworded likewise), CG-1 closed with new
    OC-ext005-0029 (held-out test-data discipline, Partial Overlap), plus
    all 6 suggested evidence extensions (course file-01 table into 0003;
    balanced-adequacy + trap callout into 0002; reliability diagram into
    0025; LOOCV into 0027; Gaussian-MLE into 0018; visualization block
    into 0028). Evidence: reports/extraction/ext005-review.md.
  - F-0008 opened (open, medium): 'mAP' name collision across vaults —
    ranking (IR) sense (both vaults) vs computer-vision detection sense
    (ai-course 03.6 file 05); synthesis must disambiguate explicitly
    (e.g. mAP_ranking vs mAP_detection); also records the known 'Color
    map' spurious-candidate source. OC-ext005-0023/0024 are the
    classification anchors.
  - Registry rebuilt: init --force + load x5 (298 + 65 + 94 + 43 + 275 =
    775) + apply-overlap x3 (14 + 28 + 29 = 71 inserted, 0 rejected) +
    kureg-validate (valid, 0 errors/warnings; 775 KUs all Unaccounted by
    design; 234 participating KUs overall; overlap counts 43 SD + 25 PO +
    2 CC + 1 CHD). Evidence: reports/extraction/ext005-kureg-*.json.
  - Dispositions deliberately NOT assigned: all 775 KUs remain
    `Unaccounted` — no synthesis output exists yet.

## Tests actually run

| Command/test | Result | Evidence/report | Limitations |
|---|---|---|---|
| `python3 -m vault_unification selftest` (startup) | exit 0; ok | — | — |
| `python3 -m pytest tests -q` (startup and final) | exit 0; 407/407 | reports/extraction/ext005-pytest-report.json | no framework changes in EXT-005 |
| `vu verify-manifest` both vaults (startup AND after all operations) | exit 0 x4; 333 + 276 unchanged | reports/extraction/ext005-immutable-{startup,after}-{master-ai,ai-course}.json | — |
| `vu extract-kus` master-ai scope + double-run cmp | exit 0; 1/1 file, 43 KUs; byte-identical | reports/extraction/ext005-coverage-master-ai.json + ext005-determinism-master-ai.txt | — |
| `vu extract-kus` ai-course scope + double-run cmp | exit 0; 5/5 files, 275 KUs; byte-identical | reports/extraction/ext005-coverage-ai-course.json + ext005-determinism-ai-course.txt | — |
| `python3 scripts/ext005_fidelity.py` (both batches) | exit 0; 43/43 + 275/275 byte-exact + pure | reports/extraction/ext005-fidelity-{master-ai,ai-course}.json | — |
| `python3 scripts/ext005_term_map.py` | exit 0 first run | reports/extraction/ext005-term-map-verification.json | vocabulary pre-probed before writing, so zero invented entries this time |
| `vu overlap-candidates` (batches 004 + 005) | exit 0; 1604 pairs, 40 cross-vault topics | reports/extraction/ext005-overlap-candidates.json + -pairs.jsonl | candidates only; 2 truncated topics (precision/recall at the 250-pair cap; per-KU evidence complete) |
| `python3 scripts/ext005_classifications.py` | exit 0 pre-review (28) and final (29) | classification file + stdout | byte-exact check caught 2 wrong-KU-id citations + 1 transcription error during development |
| EXT-005-REVIEW independent subagent review | PASS-WITH-NOTES; all repairs applied pre-commit | reports/extraction/ext005-review.md | see review's own limitations section |
| `vu kureg-init --force` + `kureg-load` x5 + `kureg-apply-overlap` x3 + `kureg-validate` | exit 0 x10; 775 KUs, 71 inserted, valid 0 err | reports/extraction/ext005-kureg-*.json | derived index; rebuildable from committed stores |
| `vu capabilities --verify` | exit 0; 16 implemented-and-tested, 1 planned | reports/extraction/ext005-capabilities.json | runs only referenced test files |
| `vu validate-registry --tasks --classifications` (all three files) | exit 0; valid, 0 problems | reports/extraction/ext005-taskqueue-validate.json (+ two /tmp runs for 001/002) | schema + cross-checks only |

## Findings and unresolved work

- Open findings: F-0001 (trailing-space dir `source-vaults/AI ` — always
  quote), F-0002 (14 AI Course unclosed-fence files — extractor handles
  them), F-0003 (175 broken wikilinks + 10 missing anchors in AI Course —
  synthesis-time dispositions), F-0007 (boosted-tree library dating —
  synthesis-time reconciliation), F-0008 (mAP name collision ranking vs
  detection — synthesis-time disambiguation).
- Resolved: F-0004, F-0005, F-0006.
- Blockers: PUSH BLOCKER for the repository itself — the EXT-005 commits
  (4d77dff work + 765774c state) are local-only because all three provided
  PATs were rejected (401 Bad credentials, API-verified 2026-10-26). Obtain
  a fresh PAT from the repository owner and push before starting EXT-006
  work. No other blockers for EXT-006.
- Known gaps (deliberate non-claims): only 17 of 609 source files extracted
  (2.8%); overlap classified for three domains only (regression, tree,
  evaluation: 71 pair-level classifications over 234 of 775 KUs); no
  dispositions/concepts/destinations anywhere yet; no synthesis output
  exists; Master AI has never been link-checked; CAP-014 still planned.

## Decisions and configuration

- Classification records are pair-level overlays (ADR-0009); one KU can
  join multiple differently-typed pairs; classifications live in
  `state/classifications/*.jsonl` (append-only once committed).
- Classification evidence MUST be byte-exact quotes verified inside the
  referenced KU excerpt; term counts are never evidence.
- Heading text is NOT KU evidence (EXT-004 rule, re-confirmed by EXT-005
  review repairs R1/R2): a name that appears only in a section heading
  exists at file level but not inside any KU excerpt — rationales must say
  exactly that, never 'the vault never names it' without checking the
  source headings.
- Term maps must be built from ACTUAL batch content and machine-verified
  before use. Pre-probing candidate vocabulary against both batches before
  writing the map (as done in EXT-005) avoids the EXT-004 invented-entry
  iteration.
- Case-insensitive homonym collisions in term matching (mAP vs MAP vs
  'Color map') are a feature, not a bug: discovery surfaces them for
  evidence-based adjudication; classification records must resolve them
  explicitly (OC-0023/0024 pattern) and open a finding when the name is
  genuinely ambiguous (F-0008).
- Dispositions wait for synthesis output (all KUs stay Unaccounted).
- Pinned vault-ids: `ai-course` and `master-ai`.
- Heading/construct detection authority: `mdextract.extract_structure_text`
  (CAP-003) — never naive `#` regex.
- Task-queue schema note: the work-commit hash field is `commit`.
- Batch naming: `<sequence>-<task-id>-<scope>.jsonl`; classification
  batches: `<sequence>-<task-id>-<scope>-overlap.jsonl`. Two batches may
  share one task id when both sides are extracted in one task (004 + 005
  are both EXT-005).

## Next task

- Task ID and title: EXT-006 — Concept-dossier scaffolding for the three
  classified domains (regression, tree-based, evaluation) per
  docs/KNOWLEDGE_AND_PROVENANCE.md section 7 (ten evidence categories;
  accounting invariants). Full record (inputs/outputs/acceptance criteria/
  forbidden side effects) is in `state/task-queue.jsonl` (status: ready).
- Why it is next: three domains now have complete extraction + evidence-
  based overlap classification (regression 14, tree 28, evaluation 29
  records; 234 participating KUs); the standing EXT-004/EXT-005 handoff
  suggestion; directly prepares synthesis by aggregating classified KU ids
  per concept per dossier category with explicit gap markers.
- Alternative candidates (decide with evidence at session start): another
  domain pair (e.g. SVM: ai-course 03.4 vs master-ai SVM content), or
  CAP-014 (source-to-output coverage reports — required before synthesis
  batches are accepted, but no synthesis batch exists yet).

## Resume procedure

1. PUSH FIRST (still blocked — see Project state): with FRESH credentials
   (the three PATs from the brief are all dead — 401 on API and 'Invalid
   username or token' on git push, retried 2026-10-27), push
   `git push origin main` from `/home/z/my-project/repo` (range
   7d9e65f..HEAD), then `git fetch` + `git status` to verify
   origin/main == local main. If credentials are unavailable, CONTINUE
   ANYWAY in `/home/z/my-project/repo` (it is the most-advanced working
   copy; commits accumulate locally and push later) — but never work in a
   fresh clone while local-only commits exist, or work will be duplicated
   (this happened on 2026-10-27; see
   reports/extraction/ext005-independent-confirmation.md).
2. Read `AGENTS.md`, this file, `state/current-state.json`,
   `state/task-queue.jsonl`, `state/findings.jsonl`, and
   `/home/z/my-project/worklog.md` (cross-session log; contains the
   local-commits warning that a fresh clone CANNOT see).
3. Sanity-verify the framework: `PYTHONPATH=src python3 -m vault_unification
   selftest` (exit 0) and `PYTHONPATH=src python3 -m pytest tests -q`
   (407/407 unless tests were legitimately added — update the count then).
4. Verify source immutability: `vu verify-manifest` on both vaults (exit 0).
5. Verify the registry rebuilds from canonical stores:
   `vu kureg-init --db state/registries/kuregistry.db --force` then
   `vu kureg-load --kus` batches 001-005 then `vu kureg-apply-overlap
   --classifications` for ALL THREE classification files (001-ext003,
   002-ext004, 003-ext005) then `vu kureg-validate` (775 KUs, 71
   classifications, 0 errors).
6. Execute EXT-006 per its task record; framework-first (deterministic
   dossier assembly script that validates every referenced KU id and
   classification id before writing; double-run byte-identical); record
   evidence with actual exit codes; update task queue, current-state,
   checkpoint, findings; write this handoff file; commit (work + state)
   and push to main. EXT-007 (queued) can follow or be folded into EXT-006
   at the session's discretion, with evidence.

## Explicit non-claims

- Overlap is classified for the regression, tree and evaluation domains
  only (71 pair-level records over 234 of 775 extracted KUs); 541
  extracted KUs have no overlap classification, and 592 of 609 source
  files are not extracted at all.
- All 775 KUs remain `Unaccounted`; no dispositions, concept assignments
  or destinations exist anywhere.
- The 29 EXT-005 classifications are pair-level semantic judgments with
  byte-exact evidence quotes; several rest on structure/description-level
  identity with no mechanical candidate-pair grounding (the confusion
  matrix and Huber cases — names in headings on the master-ai side) —
  independently review-verified, but they are judgments, not measurements.
- The 2 truncated discovery topics (precision, recall) mean the pairs
  JSONL lists at most 250 pairs per topic; the per-KU topic membership
  evidence is complete, but the pair enumeration for those two topics is
  capped.
- No semantic verification of any synthesis exists; no synthesis output
  exists; `output_synthesis_started` is false.
- Master AI has not been link-checked at all.
