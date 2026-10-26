# Next Agent Handoff

## Project state

- Current milestone: Milestone 3 (extraction). Framework bootstrap DONE and
  verified (BOOT-000..004). EXT-001..007 DONE and verified (batches 001-005:
  775 KUs; 75 evidence-based overlap classifications across regression, tree
  and evaluation domains — 71 from EXT-003..005 plus the 4-record EXT-007
  addendum). EXT-006 (concept-dossier scaffolding) DONE: 3 dossiers, now 75
  concepts over all 240 classified KUs after the EXT-007 evaluation-dossier
  regeneration. EXT-007 (evaluation classification addendum) DONE and verified
  2026-10-27: all four C1-C4 candidates ADOPTED into the new append-only file
  `state/classifications/004-ext007-evaluation-addendum.jsonl` (OC-ext007-0001
  ..0004: 2 Semantic Duplicate + 2 Partial Overlap, 14 byte-exact quotes, 11
  participating KUs); independent review PASS-WITH-NOTES with all repairs
  (R1-R3 wording + R4 process) and suggestions (S1-S5) applied before commit.
- Current task ID: EXT-008 (status: ready — record already in the queue).
  SVM/kernel-methods domain pair: extract AI Course 03.4 + Master AI SVM
  content, classify cross-vault overlap, extend dossiers with svm-v1.
- Current Git commit: the EXT-007 work/state commits on LOCAL `main`, on top
  of the EXT-006 commits. PUSH BLOCKER (STILL OPEN): all three PATs from the
  brief were rejected on 2026-10-26 AND re-rejected 2026-10-27 (401 Bad
  credentials). The user has instructed the session to continue committing
  locally and deliver a ZIP (repo + git bundle) that the user will push
  personally. Do NOT re-clone while local-only commits exist.
- Working tree status: clean after the EXT-007 commits (verify `git status`)
- Registry/checkpoint version: task-queue v10 (BOOT-000..004 + EXT-001..007
  completed with tests_run evidence; EXT-008 queued); KU schema v1.1
  (ADR-0008); classification schema (ADR-0009); dossier schema
  `schemas/concept-dossier.schema.json`; checkpoint
  `state/checkpoints/checkpoint-2026-10-27-ext-007.json`.
- Framework version: 0.5.0 (unchanged in EXT-007 — no framework code
  changes); 415/415 tests; capabilities: 16 implemented-and-tested, 1 planned
  (CAP-014)

## Verified completed work

- EXT-007 (2026-10-27), evaluation-domain classification addendum, same
  session as EXT-006 (state updates finished by the follow-up session):
  - All four unreviewed candidates C1-C4 (from
    reports/extraction/ext005-independent-confirmation.md section 3) verified
    against committed batches AND original source lines, then adjudicated:
    ALL FOUR ADOPTED — OC-ext007-0001 (SD: report-multiple-metrics
    discipline; distinct from OC-ext005-0026's which-metric business
    decision), OC-ext007-0002 (PO: degenerate majority-prediction pattern
    transferred to pixel accuracy; master-ai has zero segmentation content),
    OC-ext007-0003 (PO: loss-vs-metric role distinction; extended with S1-S3
    course evidence — both-roles sentence L139, gradient clause L30, Huber
    KU L141), OC-ext007-0004 (SD: macro-averaged metrics for imbalanced data;
    companion to OC-ext005-0015 which covers only the PR-AUC half).
  - New append-only file; `003-ext005` byte-unchanged throughout
    (sha256-verified before and after; matches git HEAD and the EXT-006
    dossier provenance chain).
  - Generator `scripts/ext007_classifications.py` (verification chain X1-X8):
    every quote verified byte-exact INSIDE the referenced KU excerpt AND at
    the stated original-source line before writing. Final: 4 records, 14
    quotes, 11 participating KUs (6 first-time ai-course participants).
  - Independent review `reports/extraction/ext007-review.md` (EXT-007-REVIEW,
    read-only): PASS-WITH-NOTES — 12/12 quotes byte-exact in excerpts and at
    exactly the stated source lines (0 off-by-one), 4/4 cross-vault, 4 AGREE +
    0 BORDERLINE + 0 DISAGREE, coverage complete, append-only discipline
    verified. Repairs R1-R3 (rationale participation/passage wording) and
    suggestions S1-S5 applied after orchestrator re-verification of each
    claim; no further independent re-review needed (changes are exactly the
    review's own required fixes).
  - R4 executed: registry apply-overlap for the addendum (4 inserted, 0
    rejected; kureg-validate valid: 775 KUs, 75 classifications, 240
    participating, all KUs Unaccounted) and evaluation dossier regenerated
    (`state/dossiers/evaluation-v1.json`: 33 concepts / 97 KUs; double-run
    byte-identical; `--check` exit 0 for all three dossiers) — the derived-view
    property of dossiers demonstrated in-repo.

## Tests actually run

| Command/test | Result | Evidence/report |
|---|---|---|
| `vu selftest` (startup) | exit 0 | — |
| `python3 -m pytest tests -q` (startup AND final) | 415/415 | reports/extraction/ext007-pytest-report.json |
| `vu verify-manifest` both vaults (startup AND after) | exit 0 x4; 333 + 276 unchanged | reports/extraction/ext007-immutable-{master-ai,ai-course}.json |
| registry apply-overlap 004-ext007 + `kureg-validate` | 4 inserted, 0 rejected; valid 0 err/warn; 775 KUs, 75 classifications, 240 participating | reports/extraction/ext007-kureg-apply-overlap.json + ext007-kureg-validate.json |
| `python3 scripts/ext006_dossiers.py` (x2 + `--check`) | exit 0; evaluation-v1 regenerated (33 concepts); byte-identical | reports/extraction/ext006-dossier-coverage.json (updated) |
| `vu validate-registry --tasks --classifications 004-ext007` | valid, 0 problems | reports/extraction/ext007-taskqueue-validate.json + ext007-classifications-validate.json |
| `vu capabilities --verify` | 16 implemented-and-tested, 1 planned | reports/extraction/ext007-capabilities.json |

## Findings and unresolved work

- Open findings: F-0001 (trailing-space dir), F-0002 (14 unclosed-fence
  files), F-0003 (175 broken wikilinks + 10 missing anchors), F-0007
  (boosted-tree library dating), F-0008 (mAP name collision).
- Blockers: PUSH BLOCKER (see Project state) — user pushes the delivered
  zip/bundle personally; local commits accumulate in `/home/z/my-project/repo`.
- Known gaps (deliberate non-claims): 17 of 609 source files extracted (2.8%);
  overlap classified for three domains only (EXT-008 adds the fourth); dossiers
  cover ONLY the 240 classified KUs (535 extracted KUs have no classification
  and therefore no dossier participation yet — by design); no
  dispositions/concepts-as-destinations; no synthesis output; CAP-014 still
  planned.

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
  already-classified domain arise after its file is committed, they go into a
  NEW append-only file with a fresh OC-extNNN-* id prefix; committed files
  are never edited. The dossier generator's DOMAINS config lists the
  classification files explicitly per domain.
- Pinned vault-ids: `ai-course` and `master-ai`.

## Next task

- Task ID and title: EXT-008 — Extract the SVM/kernel-methods domain pair
  (AI Course 03.4 + Master AI SVM content) and classify its cross-vault
  overlap. Full record (inputs / outputs / acceptance criteria / forbidden
  side effects) is in `state/task-queue.jsonl` (status: ready).
- Why it is next: the SVM/kernel domain is the largest remaining
  cross-vault ML domain with rich content on both sides (ai-course 03.4 has a
  dedicated 6-file folder; master-ai has SVM/kernel sections to locate at
  session start). It follows the now-proven EXT-005 two-sided pattern
  end-to-end: extract (double-run byte-identical) -> fidelity -> term map
  (pre-probe, machine-verified, zero invented entries) -> CAP-013 discovery
  -> evidence-based classifications (byte-exact quotes, generator-verified)
  -> independent read-only review with repairs -> svm-v1 dossier (extend
  scripts/ext006_dossiers.py DOMAINS + schema domain enum if needed, with
  documented justification) -> registry rebuild -> state updates.
- Check BEFORE extracting: whether EXT-002 batch 002 (master-ai supervised
  learning) already contains the master-ai SVM KUs — if so reuse them in
  discovery/classification instead of re-extracting, and extract only the
  missing side.
- After EXT-008: candidate directions (decide with evidence): CAP-014
  source-to-output coverage reports (required before synthesis batches are
  accepted), another domain pair from the unextracted Master AI files
  (consult state/manifests and the registry coverage report), or
  dossier-driven synthesis prep.

## Resume procedure

1. PUSH STATE: local main is ahead of origin/main (EXT-005 verification +
   EXT-006 + EXT-007 commits, and EXT-008 if completed). The user pushes the
   delivered zip/bundle personally. NEVER clone fresh while local-only
   commits exist; work in `/home/z/my-project/repo`.
2. Read `AGENTS.md`, this file, `state/current-state.json`,
   `state/task-queue.jsonl`, `state/findings.jsonl`, and
   `/home/z/my-project/worklog.md`.
3. Sanity-verify: `PYTHONPATH=src python3 -m vault_unification selftest`
   (exit 0) and `PYTHONPATH=src python3 -m pytest tests -q` (415/415 unless
   tests were legitimately added — update the count then).
4. Verify source immutability: `vu verify-manifest` on both vaults (exit 0).
5. Verify the registry validates (775 KUs, 75 classifications, 240
   participating; kureg-validate --db state/registries/kuregistry.db).
6. Execute EXT-008 per its task record; when the svm domain is classified,
   extend scripts/ext006_dossiers.py DOMAINS, regenerate ALL dossiers
   (byte-identical for the three existing ones), rebuild the registry, update
   task queue, current-state, checkpoint, findings; rewrite this handoff;
   commit (work + state).

## Explicit non-claims

- Dossiers are scaffolding: category assignments are deterministic rule
  outputs with recorded bases, NOT semantic judgments; several will be
  re-examined at synthesis (especially the default assignments —
  regression 15/61, tree 38/82, evaluation 45/97 KUs landed in
  definitions_terminology by default).
- Dossier participation is limited to the 240 classified KUs; the other 535
  extracted KUs appear in no dossier because they have no classification
  records yet.
- All 775 KUs remain `Unaccounted`; no dispositions, concept destinations or
  synthesis output exist; `output_synthesis_started` is false.
- The EXT-007 addendum records are pair-level classifications like all
  others; adopting them does NOT merge or resolve the mAP collision (F-0008
  stays open for synthesis).
- Master AI has not been link-checked at all.
