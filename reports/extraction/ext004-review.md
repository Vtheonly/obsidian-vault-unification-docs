# EXT-004 Independent Review (EXT-004-REVIEW)

- Reviewer: independent read-only review subagent (Task ID EXT-004-REVIEW; no
  repository files modified; scratch scripts confined to `/tmp/ext004review/`)
- Date: 2026-10-26
- Scope: `state/classifications/002-ext004-tree-based-overlap.jsonl` — 27
  overlap classifications, 120 evidence entries, 76 distinct KUs (50 of the 94
  ai-course KUs in batch 003 + 26 of the 30 master-ai tree KUs in batch 002),
  produced by task EXT-004
- Method (commands actually run, all from `/home/z/my-project/repo`):
  - `python3 /tmp/ext004review/check1_2.py` — Check 1 + Check 2: for every one
    of the 120 evidence entries, (a) substring test of the quote against the
    referenced KU's `excerpt` in the committed batches, (b) read the original
    source file (under `source-vaults/AI /AI Course/` and
    `source-vaults/AI /Master AI/`), slice lines, and locate the quote at the
    claimed 1-based line number (single-line and multi-line window search),
    (c) `source_path` equality with the KU's `source_path`; plus ku_id
    existence, vault resolution, and evidence-vs-`ku_ids` set equality.
  - `python3 /tmp/ext004review/check_extra.py` — for all 76 distinct cited
    KUs: excerpt == byte-exact slice of the original file at
    `line_start..line_end`; classification_id and ku_id-set uniqueness;
    overlap-type vocabulary check; disposition-field scan; rationale-presence
    scan; regex scan of all rationales for term-count evidence.
  - `python3 /tmp/ext004review/dump.py` + full manual reading of
    `/tmp/ext004review/full_records.txt` — all 27 records with the COMPLETE
    excerpts of every participating KU (Check 3 semantic audit, Check 4
    rationale fact-check).
  - `python3 /tmp/ext004review/check4_quotes{,2,3}.py` — mechanical
    verification of every quoted fragment inside `rationale` fields against
    the combined corpus (all 159 batch excerpts + the 4 original source
    files), with math/ellipsis normalization.
  - Check 5: parsed `reports/extraction/ext004-overlap-candidates.json`
    (95 topics, 64 cross-vault, 1056 confirmed term pairs); built a per-topic
    cited/uncited KU table; dumped and read all 44 uncited ai-course KUs and
    all 4 uncited master-ai tree KUs; `rg`/`sed` over both source files
    (code-fence counts, heading years, absence of pruning/OOB/stacking terms
    in master-ai, learning-rate ranges).
  - Check 6: field-level diff of
    `state/classifications/001-ext003-regression-overlap.jsonl` (14 records,
    67 quotes) against the EXT-004 file.
  - `git log`/`git status` — confirmed EXT-004 deliverables are uncommitted
    WIP on top of `da00710` (review happens pre-commit, as with EXT-003).

## Verdict: PASS-WITH-NOTES

All 27 assigned overlap types are defensible per the section-7 taxonomy (25
clean agreements, 2 defensible borderlines, 0 disagreements). All 120 evidence
quotes are byte-exact in both the committed excerpts and the original source
files at the claimed lines. Two items need repair before commit: one factual
error in a rationale (OC-ext004-0027's arXiv dating) and one genuine cross-vault
coverage gap (Random-Forest strengths / strong-baseline positioning).

## Check 1 — Byte-exact quote verification: 120/120 in excerpts, 120/120 at claimed source lines, 0 mismatches

- (a) 120/120 evidence quotes are byte-exact substrings of the referenced
  KU's `excerpt` field in the committed batches
  (`003-ext004-ai-course-03.7-tree-based-models.jsonl` /
  `002-ext002-master-ai-supervised-learning.jsonl`). 0 failures.
- (b) 120/120 quotes were also located in the ORIGINAL source markdown files.
  All 120 `lines` arrays are single-element; every quote appears on exactly
  its claimed 1-based line. 0 off-by-one, 0 not-found, 0 wrong-file cases.
  The 4 source files read: `01. Decision Trees - Splitting Criteria and Tree
  Construction.md`, `02. Random Forests and Bagging.md`,
  `03. Gradient Boosting and XGBoost.md` (ai-course 03.7), and
  `03 - Decision Trees and Gradient Boosting.md` (master-ai).
- (c) 120/120 evidence `source_path` values match the referenced KU's
  `source_path` exactly.
- Beyond the brief: all 76 distinct cited KUs' excerpts are byte-identical
  slices of the original files at their claimed `line_start..line_end` ranges
  (76/76, 0 mismatches), so no quote rests on a corrupted excerpt; all
  claimed evidence lines fall inside their KU's line span; evidence `ku_id`
  sets equal each record's `ku_ids` field for all 27 records.

## Check 2 — Cross-vault participation: 27/27, 0 violations

- Every record's `ku_ids` resolve to KUs in BOTH vaults (ai-course via
  `source_id` prefix `ai-course:`, master-ai via `master-ai:`): 27/27.
- Every cited ku_id exists in one of the two committed batches (0 dangling
  references).
- All 26 distinct cited master-ai KUs come from
  `03 - Machine Learning/Supervised Learning/03 - Decision Trees and Gradient
  Boosting.md` (0 citations from the linear/logistic-regression file).
- Composition: 50/94 ai-course batch KUs and 26/30 master-ai tree KUs
  participate. The 4 uncited master-ai KUs are: frontmatter (lines 1-6), the
  RF-baseline sentence at line 58 (see Check 5 — GAP), the XGBoost worked
  code block (lines 97-116, single-vault), and the See-Also link list
  (lines 164-167, structural).

## Check 3 — Semantic judgment audit: 25 AGREE, 2 AGREE-BORDERLINE, 0 DISAGREE

| ID | Topic | Assigned | Verdict |
|---|---|---|---|
| 0001 | DT as recursive feature-space partitioning | Semantic Duplicate | AGREE — same core claim both vaults; course's per-region prediction detail is elaboration |
| 0002 | Regression-tree criterion (variance/MSE) | Semantic Duplicate | AGREE — same claim; course adds formula + MSE-equivalence explanation |
| 0003 | Tree-construction stopping criteria | Semantic Duplicate | AGREE — same three-condition set (pure / max depth / min samples), wording only differs |
| 0004 | RF mechanism (bootstrap + feature randomness + aggregate) | Semantic Duplicate | AGREE-BORDERLINE — type defensible (course's full treatment does duplicate the mechanism), but the "three-part mechanism" is not fully evidenced on the course side: the random-feature-subset clause appears only in master-ai's cited KU; the course counterpart (KU-745a7060e76c4bac) is cited in OC-0017 instead |
| 0005 | Averaging reduces variance w/o increasing bias | Semantic Duplicate | AGREE — near-verbatim on both sides |
| 0006 | GB trains trees sequentially, each correcting previous | Semantic Duplicate | AGREE — near-verbatim definition duplicated |
| 0007 | Boosting = gradient descent in function space | Semantic Duplicate | AGREE — same deep insight; generality split off to OC-0018 |
| 0008 | Final boosting model formula (F_0 + ν·Σ trees) | Semantic Duplicate | AGREE — formula identity; notation-only difference (γ absorbed), consistent with the EXT-003 O(d^3)/O(m^3) precedent |
| 0009 | Shallow trees (depth 3-8) as weak learners | Semantic Duplicate | AGREE — same numeric range + same weak-learner rationale |
| 0010 | LR / n_estimators tradeoff + early stopping | Semantic Duplicate | AGREE — same tuning doctrine on both sides |
| 0011 | GBT SOTA for tabular data | Semantic Duplicate | AGREE — same claim + same adoption backing; master-ai era qualifier is an addition |
| 0012 | Single trees high variance | Semantic Duplicate | AGREE — near-verbatim |
| 0013 | Trees cannot extrapolate | Semantic Duplicate | AGREE — near-verbatim, same mechanism |
| 0014 | Classification split criteria (Gini/entropy/IG) | Partial Overlap | AGREE — name-only list vs full derivation; textbook partial case |
| 0015 | Decision-tree strengths | Partial Overlap | AGREE — 4 shared strengths, 2 course-only (no distributional assumptions, outlier robustness); rationale enumeration is garbled (see Check 4) |
| 0016 | Bagging mechanics | Partial Overlap | AGREE — one-clause reference vs full procedure + OOB quantification |
| 0017 | Feature randomness at splits | Partial Overlap | AGREE — one clause vs sqrt(d)/d/3 defaults + decorrelation rationale |
| 0018 | GB algorithm steps | Partial Overlap | AGREE — master-ai's MSE-only loop is a strict subset of the course's general-loss + per-leaf-γ formulation |
| 0019 | GB hyperparameters | Partial Overlap | AGREE — shared parameter set, different elaborations per side |
| 0020 | XGBoost innovations | Partial Overlap | AGREE — one line vs five-item list; year split off to OC-0027 |
| 0021 | LightGBM innovations | Partial Overlap | AGREE — one line vs four mechanisms + 3-10× quantification |
| 0022 | CatBoost innovations | Partial Overlap | AGREE — one line + production note vs three mechanisms; heading-only year difference correctly kept out of evidence and flagged for synthesis |
| 0023 | Why GB beats DL on tabular | Partial Overlap | AGREE — shared adoption claim; distinct non-shared halves (empirical/mechanistic vs thresholds/guidance) |
| 0024 | Feature importance + caveats | Partial Overlap | AGREE — shared capability + handle-with-care stance; different caveats and remedies per side |
| 0025 | Worked customer-purchase tree example | Partial Overlap | AGREE-BORDERLINE — sibling ASCII illustrations of the same concept (age/income/purchase); shared meaning is the pedagogical device rather than a claim, and Complementary is arguable, but Partial is defensible since neither example contains the other and the domain/structure genuinely coincide |
| 0026 | RF formalization (formula vs variance analysis) | Complementary Content | AGREE — different formal objects (estimator definition vs σ²/B analysis); neither contains the other's claim; both needed |
| 0027 | XGBoost era dating (2014 vs 2016) | Conflict or Historical Difference | AGREE on type — master-ai is internally inconsistent (2014 list vs 2016 citation) and the course's 2016-2019 era framing corroborates 2016; genuine date disagreement needing synthesis reconciliation. (The rationale's historical EXPLANATION is factually wrong — see Check 4; this does not change the type.) |

Distribution: 13 Semantic Duplicate, 12 Partial Overlap, 1 Complementary
Content, 1 Conflict or Historical Difference.

## Check 4 — Rationale fact-check

Mechanically verified every quoted fragment inside all 27 rationales against
the batch excerpts and original files (after stripping math `$…$` and
emphasis `**…**` markers); every content assertion was then checked manually
against the full excerpts. Findings:

1. **OC-ext004-0027 — factual error (REQUIRED REPAIR).** The rationale states
   "Historically, the paper first appeared on arXiv in 2014 and was published
   at KDD in 2016" and recommends citing "Chen & Guestrin (2016, KDD; arXiv
   2014)". The arXiv date is wrong: the XGBoost paper is
   arXiv:1603.02754 (the arXiv ID encodes 2016-03), posted March 2016, and
   published at KDD '16 (August 2016). What dates to 2014 is the initial
   release of the XGBoost library (Tianqi Chen's project). The correct
   reconciliation: master-ai's "(2014)" plausibly refers to the library's
   first release, "Chen & Guestrin (2016)" to the paper; the recommended
   citation should be "Chen & Guestrin (2016, KDD; arXiv 2016; library first
   released 2014)". The classification type is unaffected.
2. **OC-ext004-0004 — evidence-completeness nuance.** The rationale says the
   course "carries [all three parts] across its definition and the bagging
   step list". The two cited course KUs carry many-trees/averaging, bootstrap
   and aggregation, but NOT the random-feature-subset clause; that part is
   carried by KU-745a7060e76c4bac (cited in OC-0017). "A slightly different
   view of the data" gestures at it but does not state it. The
   three-part-mechanism claim is true of the course's full treatment but not
   of the cited evidence.
3. **OC-ext004-0006 — same pattern.** "The course adds … the bagging-vs-boosting
   contrast": the course's explicit contrast statements
   (KU-02ad70a78aa32e0a "Random Forests (bagging): … Each tree is a strong
   learner …; averaging reduces the variance" and KU-37e8d11c38215d07
   "Bagging: independent trees, strong learners, reduce variance. / Boosting:
   sequential trees, weak learners, reduce bias.") are in the batch but not
   cited; the cited course KU (KU-e7f3d1f5a04eff99) carries only the boosting
   half.
4. **OC-ext004-0019 — minor mislabeling.** "Stochastic gradient boosting" is
   presented as course-side non-overlapping content, but master-ai carries a
   compressed counterpart of the same claim ("`subsample`: fraction of data
   per tree (adds randomness, like bagging)" vs the course's "using
   `subsample < 1` and `colsample_bytree < 1` (like Random Forests' bootstrap
   and feature sampling) decorrelates the trees and improves generalization").
   The subsample parameter itself is already listed as shared, so the type is
   unaffected; the claim arguably belongs to the shared core.
5. **OC-ext004-0015 — garbled enumeration.** "Four shared strengths:
   interpretability, mixed/categorical+numerical data with no scaling,
   nonlinearities and interactions, and — within master-ai's … — the same
   data-type claim": the fourth item re-states the second. The substance
   (4 shared strengths; 2 course-only; 0 master-ai-only) is correct; the
   wording double-counts the data-type claim.
6. **OC-ext004-0003 — trivial elision.** The rationale quotes the course's
   stopping criterion as "(max depth, min samples per leaf)" dropping the
   source's trailing ", etc." — harmless paraphrase in a rationale (evidence
   quotes are unaffected), noted for completeness.
7. **Verified correct (spot examples):** OC-0004's "the course … four-step
   procedure with the ~37% out-of-bag quantification (classified separately
   …)" (OC-0016 exists as described); OC-0010's "its own prose (0.01-0.1)" —
   the course file line 41 does state "learning rate (typically 0.01–0.1)"
   (carried by uncited KU-287011e95e63c162), while the course table and
   summary say 0.01–0.3 and master-ai says 0.01–0.1; OC-0014's "pure/max-
   impurity boundary values, probabilistic interpretations" — present in the
   course batch (KU-04c78481e3d19ac6, KU-f5f86089e23914e2,
   KU-8e6e7a87a32e7ca2, KU-5b055de23cda4801, uncited but in-batch);
   OC-0019's "stochastic gradient boosting" (KU-0928cbcb2fa0fd04, in-batch);
   OC-0022's "master-ai dates CatBoost 2018; the course section heading dates
   it (Yandex, 2017), but headings are outside KU excerpts" — verified against
   the source files (heading `### CatBoost (Yandex, 2017)` at line 100; the
   excerpt itself contains no year); OC-0025's example specifics (Age > 30? /
   Income > 50K? / 85%-70%-90% probability leaves vs age > 35? / income >
   60k? / student? / buy-hold-sell) — all exact; OC-0027's term-evidence note
   (course heading `### XGBoost (Chen and Guestrin, 2016)` at line 79, outside
   the excerpt) — verified. All other rationale-quoted fragments matched the
   sources modulo `$`/`**` markup only.

## Check 5 — Coverage: 1 gap, 1 minor gap, 8 candidates confirmed covered or single-vault

Mapped all 64 cross-vault topics of the discovery report against the 27
records; read all 44 uncited ai-course KUs and all 4 uncited master-ai tree
KUs in full. Master-ai line 58 is the only non-structural master-ai content
line that participates in no classification.

| Candidate topic | Disposition |
|---|---|
| Bias-variance framing | Covered — OC-0005 (both vaults, qualitative claim); formalization pair split off as OC-0026 |
| DT strengths / DT cons lists | Covered — OC-0015 (strengths) and OC-0012/0013 (cons: high variance, overfitting, extrapolation) |
| RF weaknesses list (course) | Covered at claim level — extrapolation via OC-0013; "less accurate than boosting / boosting is SOTA" via OC-0011; "large model", "less interpretable than a single tree" single-vault (course) |
| **RF strengths / strong-baseline positioning** | **GAP — see below** |
| OOB error | Single-vault (course): master-ai contains no OOB content (grep-verified); acknowledged as course-unique in OC-0016's rationale. Correctly unclassified |
| Pruning | Shared part (stopping conditions) covered by OC-0003; pre-pruning detail, post-pruning/CART, and scikit-learn parameters are course-only (master-ai never uses the word "pruning" — grep-verified). No classification needed; optionally strengthen OC-0003 with KU-5515a2166a77ad42 |
| XGBoost worked code | Single-vault (master-ai): the three course tree files contain no code blocks (only the ASCII tree — verified). Correctly unclassified; its hyperparameter values are covered by OC-0019's shared parameter set |
| Production guidance | Overlapping elements covered: early stopping (OC-0010), default-to-GB (OC-0011/0023), CatBoost-for-categoricals (OC-0022), SHAP/interpretability + feature-importance care (OC-0024). Remaining items (Bayesian tuning/Optuna, drift monitoring, enterprise-ML framing, feature engineering) single-vault master-ai. No gap |
| Ensembling / stacking | Stacking XGBoost+NN is master-ai-only; the course's "ensembles dominate tabular ML" claim is covered by OC-0011. No gap |
| Bagging-vs-boosting contrast | Constituent claims covered (OC-0005 averaging/variance, OC-0006 sequential, OC-0009 weak learners), but the explicit contrast pair — course KU-02ad70a78aa32e0a / KU-37e8d11c38215d07 vs master-ai KU-bea36571e98b5c45 — has no record and the course contrast KUs are cited nowhere. MINOR GAP (see suggested repair 2) |
| sklearn usage | No shared claim: course notes sklearn defaults/parameters (folded into OC-0014's rationale as course-unique); master-ai uses sklearn imports inside the worked code. Correctly unclassified |
| "Which implementation?" guidance (course) | Covered piecewise by OC-0020/0021/0022 positioning claims |
| RF-as-baseline (course items) + master-ai line 58 | GAP (below) |

**Coverage GAP (required repair): Random-Forest strengths / strong-baseline
positioning.** Both vaults make the same claim cluster: the course
(KU-db11fc059424eabb, strengths list: "Strong default: works well
out-of-the-box with minimal tuning. Often the first algorithm to try on
tabular data."; KU-ffe5b19a4e9b1727 items 5-6: "Random Forests are a strong
default for tabular data — minimal tuning, robust, parallelizable" /
"typically less accurate than gradient boosting but easier to use and harder
to mess up"; KU-db4d196a7ae9cca3 item 3: "RFs are the 'strong baseline'") and
master-ai (KU-a3dac7cc037901e0, line 58: "Random forests are robust, fast,
and need little tuning. They're a great baseline for tabular data."). Shared
meaning: RFs are robust, need little tuning, and are the strong
default/baseline for tabular data; the course adds parallelizability and the
boosting comparison, master-ai adds speed. None of these KUs' baseline claims
participate in any of the 27 records (db4d196a7ae9cca3 is cited in OC-0013
for a different item). Recommended: add a 28th record, type Partial Overlap
(consistent with the OC-0015 list-vs-list convention), evidence
KU-db11fc059424eabb + KU-ffe5b19a4e9b1727 + KU-a3dac7cc037901e0 (+ optionally
KU-db4d196a7ae9cca3), topic "Random Forest as a strong, low-tuning baseline
for tabular data".

## Check 6 — Consistency with the EXT-003 precedent: consistent

- Identical record schema: the same 11 fields
  (`candidate_ref`, `classification_id`, `classified_by`, `date`, `evidence`,
  `ku_ids`, `method`, `overlap_type`, `rationale`, `task_id`, `topic`), byte-
  identical `method` string, same date (2026-10-26) and ID conventions
  (`OC-ext004-NNNN`), single-element `lines` arrays like EXT-003's.
- No `disposition` field on any classification record (dispositions remain
  separate per AGENTS.md §7.3); all batch KUs remain `Unaccounted` by design.
- Evidence standard identical: byte-exact quotes with per-quote `lines` +
  `source_path` (120/120 verified, Check 1); rationale present on all 27.
- No term-count evidence anywhere: no rationale or classification decision
  cites pair/term counts; the shared `candidate_ref` mentions batch sizes
  (94 + 30 KUs) only as provenance scope, matching the EXT-003 pattern.
- Vocabulary: EXT-004 legitimately introduces `Complementary Content` (once)
  and `Conflict or Historical Difference` (once) where EXT-003 used only
  Semantic/Partial — both are in the five-value section-7 taxonomy and both
  uses are justified by content (OC-0026, OC-0027).

## Overall verdict: PASS-WITH-NOTES

The classification file is mechanically clean and semantically sound; two
repairs are needed before commit/registry-apply.

Required repairs:

1. **OC-ext004-0027** — correct the rationale's historical claim: replace
   "the paper first appeared on arXiv in 2014 and was published at KDD in
   2016" (and the recommended citation "Chen & Guestrin (2016, KDD; arXiv
   2014)") with the accurate statement: the XGBoost library was first
   released in 2014; the paper (arXiv:1603.02754) was posted in March 2016
   and published at KDD '16 in August 2016. This record exists precisely to
   guide synthesis-time reconciliation, so the wrong arXiv year must not
   survive into the dossier.
2. **Coverage gap** — add a 28th classification (suggested `Partial Overlap`)
   for the Random-Forest strengths / strong-baseline topic, evidence
   KU-db11fc059424eabb + KU-ffe5b19a4e9b1727 (ai-course) and
   KU-a3dac7cc037901e0 (master-ai), optionally + KU-db4d196a7ae9cca3
   (course "strong baseline" item). Both vaults assert the same claim
   cluster (robust / minimal tuning / strong baseline for tabular data);
   currently master-ai line 58 participates in no record.

Suggested repairs (do not change any assigned type):

3. **OC-ext004-0004** — add KU-745a7060e76c4bac to the evidence (or reword
   the rationale to scope the shared claim to bootstrap+aggregation) so the
   "three-part mechanism" is fully evidenced on the course side.
4. **OC-ext004-0006** — add KU-02ad70a78aa32e0a and/or KU-37e8d11c38215d07
   to the evidence so "the course adds the bagging-vs-boosting contrast" is
   evidenced (currently only the boosting half is cited); this also closes
   the minor contrast-pair gap from Check 5.
5. **OC-ext004-0015** — reword the "Four shared strengths" enumeration; it
   currently double-counts the data-type claim (item 2 merges "no scaling"
   and item 4 restates item 2's claim).
6. **OC-ext004-0019** — note that master-ai's "subsample … adds randomness,
   like bagging" is a compressed counterpart of the course's
   stochastic-gradient-boosting claim (currently presented as purely
   course-side).
7. **OC-ext004-0010** — optionally add KU-287011e95e63c162 (course "typically
   0.01–0.1" prose) to the evidence, since the rationale's range comparison
   rests on it.
8. **OC-ext004-0003** — optionally mark the elision when quoting the course's
   stopping-criterion parenthetical (source has ", etc.").

## Limitations

- Check 1's line verification assumes the `lines` arrays are 1-based line
  numbers of the original files; this was confirmed empirically (120/120
  locate under 1-based indexing) but is an assumption about the producer's
  convention.
- The arXiv dating correction (OC-ext004-0027) is based on the arXiv
  identifier scheme (1603.02754 = 2016-03) and standard bibliographic
  knowledge; no network access was available to double-check against arXiv
  or the ACM DL.
- Check 3 verdicts are single-reviewer semantic judgments; the two
  AGREE-BORDERLINE calls (OC-0004, OC-0025) are arguable by construction.
- Check 5 coverage analysis is qualitative at topic-significance level: I
  mapped all 64 cross-vault discovery topics and read all uncited KUs in
  full, but "significant" is a judgment; thin single-sentence overlaps
  (e.g., incidental shared vocabulary such as "noise", "threshold",
  "validation") were deliberately not required to have records.
- I did not re-run `vu overlap-candidates` (reproducibility of the 1056-pair
  discovery is the orchestrator's responsibility, as in EXT-003), nor
  `validate-registry --classifications` (the registry apply step has not run
  yet); I reviewed only the classification JSONL, the two batches, the
  discovery report, the term map reference, and the source files.
- Git state during review: EXT-004 deliverables are untracked WIP on top of
  `da00710`; this review covers exactly the files listed in the scope.
