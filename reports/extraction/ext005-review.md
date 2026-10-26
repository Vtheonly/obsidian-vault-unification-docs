# EXT-005 Independent Review (EXT-005-REVIEW)

- Reviewer: independent read-only review subagent (Task ID EXT-005-REVIEW). No repository
  state files modified; the only files written are this report, the permitted verification
  script `scripts/ext005_review_check.py`, and the worklog append.
- Date: 2026-10-26
- Scope: `state/classifications/003-ext005-evaluation-overlap.jsonl` — 28 overlap
  classification records (OC-ext005-0001..0028) produced by task EXT-005, comparing
  batch 004 (master-ai `03 - Machine Learning/Evaluation/05 - ML Evaluation Metrics.md`,
  43 KUs) against batch 005 (ai-course `03 - Machine Learning/03.6 - Model Evaluation`,
  5 files, 275 KUs). 95 evidence entries over 82 participating KUs (28 of 43 master-ai,
  54 of 275 ai-course).
- Type census (from the file itself): **23 Semantic Duplicate + 4 Partial Overlap
  (0011, 0024, 0027, 0028) + 1 Complementary Content (0025) = 28**; 0 Exact Duplicate,
  0 Conflict or Historical Difference. (Note: the review brief stated "22 SD + 5 PO";
  the committed file has 23 SD + 4 PO + 1 CC. The file is self-consistent at 28 records;
  the brief's arithmetic, not the file, is off.)
- Method (all read-only, run from `/home/z/my-project/repo`):
  - `python3 scripts/ext005_review_check.py` — Check 1 (byte-exact substring test of
    every quote against the referenced KU's `excerpt` in the referenced batch), Check 2
    (locate every quote in the ORIGINAL source file under
    `source-vaults/AI /Master AI` / `source-vaults/AI /AI Course` and compare the stated
    first line, off-by-one tolerance), Check 3 (both vault prefixes present in
    `ku_ids`), plus structural checks (required fields, id sequence, evidence ku_ids ⊆
    record ku_ids, source_path equality, both vaults in evidence, duplicate evidence,
    participation census).
  - A second, stricter placement pass: full multi-line quote joined against the source
    lines starting exactly at `lines[0]`.
  - Full manual reading of a generated digest of all 28 records with the COMPLETE
    excerpts of every participating KU (semantic audit + rationale fact-check), plus
    direct reads of the master-ai source at L8-12, L20-26, L66-80, L108-142, L163-186.
  - Targeted batch greps (course and master) for: calibrat*, log loss, cross-entropy,
    specificity, one-vs/OvR, top-k, NDCG, MRR, baseline, ConfusionMatrixDisplay,
    nested, leak, balanced, weighted, MAPE, RMSLE, Gaussian, Adjusted, mermaid,
    constant gradient, 200 patients, fixed recall.
  - Parsed `reports/extraction/ext005-term-map-verification.json` (40 cross-vault
    terms) and `reports/extraction/ext005-overlap-candidates.json` (98 topics, 40
    cross-vault, 1604 term pairs, 1566 confirmed) and mapped every cross-vault topic
    to a record or a justified non-overlap.

## Verdict summary

All 28 assigned overlap types are defensible (26 clean AGREE, 2 AGREE-BORDERLINE,
0 DISAGREE). All 95 evidence quotes are byte-exact in the committed excerpts AND
appear at exactly the stated lines of the original source files (0 off-by-one, 0
failures). All 28 records are cross-vault. Two minor required repairs (rationale
wording only, no type changes): R1 (OC-ext005-0003) and R2 (OC-ext005-0022) — both
claim master-ai content is "WITHOUT naming it" when the source files name it in the
section heading (and the KU `heading_path` metadata carries the name). One minor
coverage gap (CG-1: held-out/test-set discipline cluster). Six suggested (optional)
evidence extensions.

## Check 1 — Byte-exact quotes vs KU excerpts: 95/95 pass, 0 failures

Every one of the 95 evidence quotes is a byte-exact substring of the referenced
ku_id's `excerpt` field in the referenced batch. 0 failures, 0 near-misses.

## Check 2 — Quote line verification vs ORIGINAL source files: 95/95 exact, 0 off-by-one, 0 failures

Every evidence quote was located in the original source markdown (source roots
`source-vaults/AI /Master AI` and `source-vaults/AI /AI Course`, note the trailing
space in `AI `). Strict pass: 95/95 full quotes (including multi-line quotes) sit at
exactly the stated `lines[0]` — not a single quote needed the ±1 tolerance.
`source_path` fields all match the KU records.

## Check 3 — Cross-vault requirement: 28/28 pass

Every record's `ku_ids` contain at least one `master-ai:` and one `ai-course:` KU,
and every record's evidence quotes both vaults. Structural checks also pass:
required schema fields present in all 28, no extra properties beyond the schema's
allowed set, `task_id` = EXT-005 and `date` = 2026-10-26 in all 28, ids run
OC-ext005-0001..0028 with no gaps/duplicates, evidence ku_ids ⊆ record ku_ids,
no duplicate evidence entries.

## Check 4 — Semantic audit: 26 AGREE, 2 AGREE-BORDERLINE, 0 DISAGREE

Definitions applied: Exact Duplicate = byte/trivially identical; Semantic Duplicate =
same core claim, different elaboration depth; Partial Overlap = shared content AND
substantial non-shared content on both sides; Complementary Content = no duplication,
different aspects that fit together; Conflict/Historical = contradictory claims.

| ID | Type | Verdict | Note |
|-----|------|---------|-------|
| 0001 | SD | AGREE | Identical ratio (correct/total) on both sides; TP+TN expansion is elaboration. |
| 0002 | SD | AGREE | Identical majority-class-guess argument (spam 99% / 990-of-1000 / 95%-Class-A). |
| 0003 | SD | AGREE | 2×2 table + "all metrics derived from these four counts" duplicated on both sides. SD right, but see R1. |
| 0004 | SD | AGREE | Identical formula and interpretation. |
| 0005 | SD | AGREE | Identical formula and interpretation. |
| 0006 | SD | AGREE | Master-ai's entire two-part claim (tension + cost-dependence) is duplicated; course threshold-sweep/200-patient table is elaboration, so PO's "non-shared on both sides" test fails — SD correct. |
| 0007 | SD | AGREE | Same canonical example, error type, and metric recommendation. |
| 0008 | SD | AGREE | Same canonical example, error type, and metric recommendation. |
| 0009 | SD | AGREE | Formula-level identity; the master-ai↔course-file-02 pair is trivially identical (byte-identical LaTeX), so Exact Duplicate is arguable for that sub-pair, but the third KU (file 01, `\times` notation) is not, and the EXT-003 precedent treats formula identity as SD. Fine as SD. |
| 0010 | SD | AGREE | Same harmonic-mean rationale (penalizes imbalance); counterexample/inequality are additions. |
| 0011 | PO | AGREE-BORDERLINE | At the claim level master-ai's entire F-beta content IS the shared convention (→ SD defensible); at the cited-KU level both KUs carry substantial non-shared content (→ PO defensible). The rationale is transparent about "shared convention, asymmetric depth"; either reading is defensible, PO acceptable. |
| 0012 | SD | AGREE | Same ROC definition (TPR vs FPR over threshold sweep). |
| 0013 | SD | AGREE | Same probabilistic AUC reading + both endpoint values; <0.5 case is an addition. |
| 0014 | SD | AGREE | The three-vs-three claim mapping in the rationale checks out. |
| 0015 | SD | AGREE | Same PR-AUC-over-ROC-AUC recommendation under imbalance; mechanism explanation is elaboration. |
| 0016 | SD | AGREE | Identical macro definition (per-class, unweighted, all classes equal). |
| 0017 | SD | AGREE | Same micro definition + same bias note ("favors larger classes" ≡ "dominated by the majority class"); micro=accuracy property is an addition. SD correct. |
| 0018 | SD | AGREE | Same formula + quadratic-penalty + outlier-sensitivity claims. |
| 0019 | SD | AGREE | Same formula + linear/robust/interpretable claims. |
| 0020 | SD | AGREE | Same definition + units rationale. |
| 0021 | SD | AGREE | Same formula + variance-explained reading + identical value trichotomy. |
| 0022 | SD | AGREE | Same characterization (MSE-like near zero, MAE-like for large errors, robust). SD right — indeed strengthened by the heading — but see R2. |
| 0023 | SD | AGREE-BORDERLINE | Shared core: the mAP↔search/recommendation/retrieval association. Master-ai defines MAP; the course only recommends it (one row of a decision table), so PO ("substantial non-shared on both sides": 3 other ranking-metric definitions vs 7 other table rows) is arguable. SD acceptable given the record is scoped to the mAP association and 0024 handles the collision. |
| 0024 | PO | AGREE | Correct handling of the name collision: shared name + average-precision foundation, different aggregation unit (queries vs classes), matching criterion (rank vs IoU), and application (retrieval vs detection). Not Complementary (there IS shared content), not Conflict (no contradiction). PO + terminology hazard (F-0008) is right. |
| 0025 | CC | AGREE | Verified the course batch contains exactly ONE 'calibrat*' occurrence (the cited AUC-limitation KU) — no definition, diagram, or remedy anywhere in 03.6; master-ai never links calibration to the AUC limitation. No duplicated claim → CC is correct, matching the stated EXT-004 precedent. |
| 0026 | SD | AGREE | Same principle (metric/threshold choice = business decision driven by error costs, made before/independently of modeling); consultation recommendation is an addition. |
| 0027 | PO | AGREE | Thin shared claim (CV for small data / anti-lucky-split), full K-fold/LOOCV/stratified mechanics on the course side, nested-CV mention on the master-ai side (verified at source L184; also verified absent from the course batch). PO fits. |
| 0028 | PO | AGREE | Shared sklearn.metrics tooling + core classification metric functions; master-ai's log_loss/regression-metric snippet vs course's full PyTorch pipeline + visualization. PO fits. |

Special-attention items from the review brief, resolved:
- **0003**: SD is right — the table structure and the derived-metrics claim are
  semantically identical; the naming question affects only rationale wording (R1).
- **0017**: SD is right — shared definition + shared majority-bias note.
- **0022**: SD is right for an "unnamed" description — the description itself is the
  same knowledge; and the name actually IS present in the heading (R2).
- **0023/0024**: the SD/PO split is coherent — 0023 for the retrieval sense both
  vaults share, 0024 for the collision between master-ai's retrieval MAP and the
  course's detection mAP. 0023 is borderline (see table), 0024 is clean.
- **0025**: CC is right (verified the course has no calibration treatment).
- **0027**: PO is right (verified nested-CV asymmetry).

## Check 5 — Coverage: 1 minor gap (CG-1); all other non-participation justified

All 40 cross-vault topics in the term map map onto existing records except `test set`
and `logits`. `logits` is term co-occurrence without a claim-level overlap (master-ai:
calibration remedies; course: inference code inside 0028's cited KU) — justified
non-record.

**CG-1 (minor coverage gap): held-out / test-set discipline cluster.**
Master-ai: "Always evaluate on held-out data" (L173, inside KU-d68fa9657e07ba54,
which participates in 0026/0027 only for other claims) and "Test set leakage —
feature engineering on the whole dataset, time-based splits ignored" (L183, inside
KU-0496ce782a36efe9, which participates in NO record). Course: file 01 §8.1.A
standard split — "A completely 'locked' dataset used only once at the very end"
(KU-7b9487c801c5477f L15-17) and KU-ebc5b35369cf6e32 (L13) — participate in NO
record. The shared claim (test data must stay held out / locked) is real on both
sides but has no record. Recommended fix (orchestrator's discretion, the master-ai
side is thin): add a record pairing master-ai KU-d68fa9657e07ba54 + KU-0496ce782a36efe9
with course KU-7b9487c801c5477f (likely Partial Overlap: shared discipline, master-ai
adds leakage modes, course adds the 70/15/15 three-way split mechanics), or at minimum
extend 0027's evidence with KU-7b9487c801c5477f and note the leakage pitfall.

Justified non-overlaps (each verified by batch grep — zero counterpart occurrences):
- **log loss / cross-entropy** (master L66-76, 3 KUs incl. L68-70 formula and L72):
  0 'log loss'/'cross-entropy' hits in the entire course batch (only the `log_loss`
  import inside 0028's already-cited code KU). No counterpart → no record justified.
- **specificity** (course, 12 KUs incl. file-01 §8.3.5): 0 master-ai hits.
- **one-vs-all / OvR** (course file-01 §8.4 L92 + file-02 code): 0 master-ai hits.
- **weighted averaging** (course L239-243): 0 master-ai hits (master has macro/micro only).
- **MAPE / RMSLE** (course file 03): 0 master-ai hits (master's regression set is MSE/MAE/RMSE/R²/Huber).
- **top-k accuracy** (master L79): 0 course hits; the containing KU participates in 0016/0017 for the macro/micro lines.
- **NDCG / MRR / Hit Rate@K as individual metrics** (master L118-121): 0 course hits; the containing KU participates in 0023/0024 via its MAP line.
- **calibration reliability diagram / ECE / Guo et al. miscalibration** (master L130/L133/L140): the course has exactly one 'calibrat*' occurrence (already cited in 0025) — no treatment to pair with.
- **nested CV** (master L184): 0 course hits (correctly described as master-ai-only in 0027's rationale).
- **course-only domains**: clustering metrics (file 04: silhouette/DBI/ARI/NMI), CV metrics beyond mAP (IoU, Dice, mIoU, pixel accuracy), the file-02 decision-framework mermaid/one-paragraph-guide/summary (restatements of claims already classified via 0002/0015/0016/0026).
- **structural/reference KUs**: master-ai frontmatter (L1-6), Further Reading (L188-190), See Also (L194-198), RAG pointer (L123), LLM-eval pointer (L167) — no knowledge counterpart.
- **summary blocks**: master-ai TL;DR (L10-11) and Why This Matters (L165-167) restate claims already classified (0001/0002/0009/0012-0015/0018-0021/0025/0026); L165's "99% accuracy can be worthless" could optionally be folded into 0002's evidence. Common Pitfalls L180-184 restates 0002 (imbalance), 0015 (ROC-AUC misuse nuance), 0025 (calibration) claims and carries the nested-CV note already acknowledged in 0027 — except the test-set-leakage line, which belongs to CG-1.
- **lead-in fragments**: L24 "For binary classification:", L76 "For $K$-class:", L116 "For search / recommendation / retrieval:" — no standalone claim.

## Check 6 — Rationale accuracy: all factual claims verified TRUE except R1/R2

Verified true, among others: 0002's four course imbalance rates (99.8/99.9/99.99/99.5);
0006's 200-patient table (course L157) and asymmetry callout (L70-71); 0009's byte-identical
LaTeX between master-ai L50-52 and course L177; 0012's mermaid diagram (course L262) and
endpoint mechanics (L255); 0013's course-only <0.5 case; 0016's per-class formulas
(course L215-219); 0018's Gaussian-MLE justification (course L39/L151) and squared-units
pitfall (L44-45); 0019's constant-gradient pitfall (course L30); 0021's Adjusted R²
(course L89/L151); 0022's differentiability/DL context (master L112) and
train-Huber/eval-MAE pattern (course L141); 0023's decision-table row (course L504);
0025's "no calibration definition or remedy" on the course side (grep: 1 occurrence
total); 0026's domain-expert consultation (course L168-169); 0027's nested CV (master
L184) and its absence from the course; 0028's 5-example snippet, stated workflow quote
(L302), and master-only log_loss/regression functions. Two rationale-wording failures
(R1, R2 below).

## Required repairs (wording only; no overlap_type changes)

- **R1 — OC-ext005-0003 (rationale factual inaccuracy).** The rationale says
  master-ai shows the table "WITHOUT naming it" and calls "the naming gap on the
  master-ai side … a synthesis-time labeling task". False at file level: the source
  has a `### Confusion Matrix` heading (L22), and the KU's own `heading_path`
  metadata is `[…, 'Classification Metrics', 'Confusion Matrix']`. The name is absent
  only from the excerpt body text. Fix: reword to "the name appears in the file's
  section heading (and the KU's heading_path) but not in the excerpt body", and drop
  or soften the "synthesis-time labeling task" implication (there is no naming gap to
  fix). Type stays SD.
- **R2 — OC-ext005-0022 (rationale factual inaccuracy).** Same pattern: "master-ai
  describes Huber loss WITHOUT naming it" and "synthesis must attach the master-ai
  description to the Huber name". The source has a `### Huber Loss` heading (L111)
  and the KU's `heading_path` ends in 'Huber Loss'. Fix: reword accordingly; the SD
  classification is unaffected (if anything, strengthened).

## Suggested improvements (optional, non-required)

- **S1 — OC-ext005-0003**: extend evidence with the course file-01 confusion-matrix
  table KU (KU-f08cc586a5ec436a, file 01 L42-45) — the closest structural counterpart
  (bare 2×2 table, like master-ai's). The whole course file-01 §8.2 cluster (L40-54)
  currently participates in no record.
- **S2 — OC-ext005-0002**: extend evidence with course KU-d2d46793f6ca5c36 (L5,
  "accuracy is perfectly adequate for balanced datasets … dangerously misleading when
  these conditions are not met") and/or KU-4c0d0ce1a717e047 (L15-16, "Accuracy Trap"
  callout) — both restate the classified claim and are uncited.
- **S3 — OC-ext005-0025**: the rationale cites "the reliability diagram" as part of
  what master-ai supplies, but no reliability-diagram KU is in evidence; add
  KU-732c2b897c6af276 (L130), optionally also the ECE KU-1e284a6a23e4e4ba (L133).
- **S4 — OC-ext005-0028**: the rationale's "ConfusionMatrixDisplay/ROC plotting"
  lives in course KU-b2c649622c91636c (L436-485, visualization section), not in the
  cited KU-201647def24836cf; add it to evidence (this also tightens the loose
  "imports the same metric functions" phrasing — the shared set is
  accuracy/precision/recall/f1/roc_auc).
- **S5 — OC-ext005-0027**: the rationale names LOOCV as course mechanics; the LOOCV
  KU (KU-1b3ccda7b8f85076, L23-25) is uncited; add it.
- **S6 — OC-ext005-0018**: the rationale's "Gaussian-noise MLE justification" (course
  L39) is described but not quoted; optionally add KU-6ec5d6a736b… (L39) for
  completeness (EXT-003 OC-0014 precedent for rationale-referenced evidence).

## Limitations

- Semantic verdicts are this reviewer's judgment calls against the section-7
  taxonomy; the two BORDERLINE calls (0011, 0023) hinge on claim-level vs
  KU-pair-level readings of "Partial Overlap" and could reasonably be settled either
  way by the orchestrator.
- Check 2's needle-based fallback was not needed (all 95 quotes matched in full at
  the exact stated line), but line verification confirms placement, not surrounding
  context; context was assessed separately via full-excerpt reading.
- Coverage analysis relied on the committed term map (40 cross-vault terms) and
  candidate report plus targeted greps; a different term set could surface other
  candidate clusters (though every major evaluation-metric topic in both sources was
  manually reviewed via the full digest).
- This review did not re-run the CAP-013 discovery pipeline, did not validate the
  registry state, and did not re-verify batch fidelity (that is EXT-005's own
  acceptance evidence: ext005-fidelity-*.json, ext005-determinism-*.txt).

## Final verdict

VERDICT: PASS-WITH-NOTES
