# EXT-002 Independent Extraction Review

- **Task ID:** EXT-002-REVIEW (independent reviewer, read-only w.r.t. vaults and state)
- **Date (UTC):** 2026-10-25T22:02Z
- **Subject under review:** EXT-002 — structural KU extraction of Master AI folder `03 - Machine Learning/Supervised Learning` (2 files, 167 lines each) into `state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl` (65 records)
- **Reviewed artifacts:**
  - Source A: `source-vaults/AI /Master AI/03 - Machine Learning/Supervised Learning/02 - Linear and Logistic Regression.md` (sha256 `ee1cfd18…959a`, 167 lines)
  - Source B: `source-vaults/AI /Master AI/03 - Machine Learning/Supervised Learning/03 - Decision Trees and Gradient Boosting.md` (sha256 `ca947193…8f5c`, 167 lines)
  - Batch: `state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl` (65 records; file sha256 `e0ef12187b3792dbdc9e2868a31ff7a77f57eb4809fc3ad09aab6663d5871118` — matches the worklog determinism claim)
  - Coverage report: `reports/extraction/ext002-coverage.json`
  - Reference: `state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl` (298 records, AI Course vault)

## VERDICT: **PASS**

All acceptance criteria met: 32/32 rare details present with KU-id evidence (16 per file), 40/40 headings covered (counted independently via `mdextract`), 0 boundary anomalies, 65/65 records structurally pure, and a factual cross-vault topic-pair list produced (7 evidenced pairs). Details below.

## Method

All checks were executed by me with ad-hoc Python (`/home/z/my-project/review-scripts/ext002_review_checks.py` and `..._part2.py`; nothing under `/home/z/ovu/repo` was modified except this report). Heading detection and segmentation authority is the framework's own `vault_unification.mdextract.extract_structure_text` / `vault_unification.kuextract.segment_note` (imported from `/home/z/ovu/repo/src`), so my checks share one construct-detection authority with the extractor rather than a re-implementation that could disagree. Independent verifications performed on top of the mandated checks:

1. **Batch identity vs framework:** re-ran `kuextract.segment_note()` in memory on both source texts; the resulting 35 (A) + 30 (B) units are **identical** to the batch records in `unit_type`, `line_start`, `line_end`, `excerpt`, `excerpt_hash`, and `heading_path` — the batch is exactly the deterministic output of the framework extractor.
2. **Per-record fidelity (65/65):** every `excerpt` equals the byte-exact `"\n".join(source_lines[line_start-1:line_end])` slice; every `excerpt_hash` equals sha256 of the excerpt; every span is in range; every `source_file_hash` equals the on-disk file sha256 (both match the coverage report).
3. **Schema re-validation:** `validate_ku_file()` independently reports valid, 65/65 records valid, no errors, no cross-check failures.
4. **Type distribution** matches the worklog and coverage report exactly: prose 31, list 16, math_block 10, code_block 3, frontmatter 2, callout 2, table 1 (file A: 18/4/9/1/1/1/1; file B: 13/12/1/2/1/1/0).

## CHECK 1 — Rare-detail presence: **32/32 PASS** (16 from file A, 16 from file B; requirement ≥10, ≥5/file)

Each needle below was first confirmed present in the **source file** (so a miss in the batch would be a real finding, not a typo), then required to appear byte-exact in the excerpt of at least one batch record. All 32 pass.

| # | Detail (source lines) | Proving KU-id |
|---|---|---|
| A1 | Ridge closed form with the λI term: `\hat{\mathbf{w}} = (\mathbf{X}^T \mathbf{X} + \lambda \mathbf{I})^{-1} \mathbf{X}^T \mathbf{y}` (L47, inline math) | KU-d45e836332e307c8 |
| A2 | "makes the inverse always well-defined (no singularity)" + "shrinks weights toward zero" (L47) | KU-d45e836332e307c8 |
| A3 | Ridge = "**MAP under a Gaussian prior**" (L47) | KU-d45e836332e307c8 |
| A4 | Lasso L1 penalty: `L_{\text{lasso}} = \text{MSE} + \lambda \|\mathbf{w}\|_1` (L53–55) | KU-2527b6bd210c0858 |
| A5 | Lasso "many weights become exactly zero" + "MAP under a Laplace prior" (L57) | KU-5ff2005fbd8be171 |
| A6 | Softmax formula `p(y = k \mid \mathbf{x}) = \frac{\exp(\mathbf{w}_k \cdot \mathbf{x})}{\sum_j \exp(\mathbf{w}_j \cdot \mathbf{x})}` (L89–91) | KU-74814e20d567d124 |
| A7 | Batch binary cross-entropy `L = -\frac{1}{N} \sum_i [y_i \log \hat{p}_i + (1-y_i) \log(1 - \hat{p}_i)]` (L77–79) | KU-1a3b5288448131a4 |
| A8 | O(d³) remark: "the matrix inverse is $O(d^3)$" (L33) | KU-e158377d31fa3fbe |
| A9 | sklearn `LogisticRegression(C=1.0).fit(X, y_cls)  # C = 1/lambda` incl. the two-space comment (L127) | KU-0b46cce8095bdcf5 |
| A10 | Calibration contrast: "produces **calibrated probabilities** by construction" / "post-hoc temperature scaling to calibrate" (L104) | KU-5338f2ffd7e9ef14 |
| A11 | Imbalanced classes: "biased toward the majority class" / "Use class weighting or resampling" (L154) | KU-3ad6be7f5fea1a73 |
| A12 | Further reading: ESL "Chapter 3 (regression) and 4 (classification)" + Murphy "Chapter 10–11" with en-dash (L159–160) | KU-1cd8f06cb4ceeb66 |
| A13 | Frontmatter `tags: [ml, supervised, regression, logistic]`, `iteration: 2`, `aliases: [Linear and Logistic Regression]` (L1–6) | KU-9ed3590ee6ad925a |
| A14 | Wikilink `[[02 - Mathematics/Probability/09 - Gaussian Distribution|Gaussian Distribution]]` (L37) | KU-7cbf7e7d7b7d6f4d |
| A15 | Table cells "Tabular data, small dataset (<10k rows)", "Need calibrated probabilities out of the box", "Willing to add temperature scaling" (L133–139) | KU-af74852cfc1d5771 |
| A16 | "**MSE = MLE under Gaussian noise**" (L37) | KU-7cbf7e7d7b7d6f4d |
| B1 | Random forest averaging: `\hat{f}_{\text{RF}}(\mathbf{x}) = \frac{1}{N} \sum_{i=1}^{N} T_i(\mathbf{x})` (L52–54) | KU-29957f0636ae66d8 |
| B2 | "Cannot extrapolate (predictions are constant in each leaf)." (L46) | KU-2738bc0226d67be7 |
| B3 | "gradient boosting is still SOTA in 2026" (L11, TL;DR callout) | KU-5c20f9686292a5bb |
| B4 | Split criteria "Gini impurity, information gain (entropy)." (L32) | KU-28152a3138f78aa9 |
| B5 | "variance reduction, MSE." for regression splits (L33) | KU-28152a3138f78aa9 |
| B6 | ASCII decision-tree diagram — "age > 35?", "income > 60k?", `"buy"      "hold"   "buy"   "sell"` with exact spacing (L17–27 code block) | KU-9ba16a24268005b4 |
| B7 | Boosting update rule `F_m(\mathbf{x}) = F_{m-1}(\mathbf{x}) + \nu \cdot T_m(\mathbf{x})` (L70) | KU-b5889f96e8d2229d |
| B8 | Final model `F_M(\mathbf{x}) = F_0(\mathbf{x}) + \nu \sum_{m=1}^M T_m(\mathbf{x})` (L72) | KU-8ba911106098b781 |
| B9 | "**XGBoost** (2014)" + "second-order gradients" (L80) | KU-79844cd275d4b9d3 |
| B10 | "Empirical studies (e.g., Grinsztajn et al. 2022) consistently show tree-based models beat deep learning on tabular data." (L122) | KU-8646a36bf0fd301a |
| B11 | Further reading: ESL "Chapter 9 (additive models, trees), Chapter 10 (boosting)" + "Chen & Guestrin (2016), *XGBoost: A Scalable Tree Boosting System*" (L158–159) | KU-0d1295e4ec08ef9b |
| B12 | XGBoost example params `n_estimators=500`, `learning_rate=0.05`, `early_stopping_rounds=20`, `eval_metric='logloss'` (L97–116 code block) | KU-e6e067290d111471 |
| B13 | Frontmatter `tags: [ml, supervised, trees, gradient-boosting, xgboost]`, `iteration: 2`, `aliases: [Decision Trees and Gradient Boosting]` (L1–6) | KU-9fcede9ed3a6ec99 |
| B14 | "Typical: 0.01–0.1." learning-rate range with en-dash (L89) | KU-81d7fb11dd97fc42 |
| B15 | "residual = negative gradient of MSE" + "functional gradient descent in function space" (L76) | KU-72848b7c09a02821 |
| B16 | "use `scale_pos_weight` or sampling" (L153) | KU-f675ce70e488dfc4 |

Bonus (not counted): both "See Also" wikilink lists are intact as list units at L164–167 (KU-2c8a3e043adbfea3 for file A, KU-b685a6343a93e0b1 for file B), and the `[[03 - Decision Trees and Gradient Boosting]]` cross-link at L141 is present in its prose unit.

## CHECK 2 — Heading coverage: **40/40 PASS** (A: 22/22, B: 18/18)

Headings were detected with `mdextract.extract_structure_text` (ATX lines starting with `#` **outside code fences** — important here, because file A's python block contains `# Linear regression`, `# Ridge (L2)`, `# Logistic regression` comment lines that a naive matcher would misread as headings; mdextract correctly ignores them). Every heading text appears in the `heading_path` chains of the batch records:

- **File A — 22 headings (1×H1, 9×H2, 12×H3):** `02 - Linear and Logistic Regression` (L8); `Linear Regression` (13); `Loss: Mean Squared Error (MSE)` (21); `Closed-form solution (Normal Equations)` (27); `Probabilistic interpretation: MLE = MSE` (35); `Ridge regression (L2 regularization)` (39); `Lasso (L1 regularization)` (49); `Logistic Regression` (59); `Loss: Binary Cross-Entropy` (67); `Probabilistic interpretation: MLE = cross-entropy` (81); `Multiclass: Softmax Regression` (85); `Why These Models Matter` (95); `1. They're the building blocks of neural networks` (97); `2. Strong baselines` (100); `3. Calibration` (103); `4. The math generalizes` (106); `Worked Example` (109); `When to Use Classical Regression vs Neural Networks` (131); `Production Implications` (143); `Common Pitfalls` (150); `Further Reading` (157); `See Also` (162). **22/22 covered.**
- **File B — 18 headings (1×H1, 10×H2, 7×H3):** `03 - Decision Trees and Gradient Boosting` (L8); `Decision Trees` (13); `Training` (29); `Pros` (37); `Cons` (43); `Random Forests` (48); `Gradient Boosting` (60); `Algorithm` (64); `Why it works` (74); `Modern implementations` (78); `Key hyperparameters` (86); `Worked Example (XGBoost)` (95); `Why Gradient Boosting Beats Deep Learning on Tabular Data` (120); `Why This Matters for AI` (132); `Production Implications` (139); `Common Pitfalls` (148); `Further Reading` (156); `See Also` (162). **18/18 covered.**

No `heading_path` component exists that does not correspond to a real heading (zero phantom headings). Stronger sub-check: for **all 65 records**, `heading_path` equals the independent recomputation `mdextract.heading_path(headings, line_start)` (0 mismatches) — chains are not just present but correct. The coverage report's `heading_context` buckets (22 and 18) match my independently counted headings.

## CHECK 3 — Boundary anomalies: **0 found**

(a) **Span overlaps: 0.** For each file, records sorted by `(line_start, line_end)` show no pair with `u.line_end >= v.line_start`. Independent proof of no double-counting: sum of span lengths == size of the union of span lines (A: 93 == 93; B: 105 == 105). The extractor design (`kuextract.segment_note`) is a linear scan with disjoint "occupied" construct spans from mdextract, so nesting is impossible by construction — and none occurs. No reliance on the nested-construct exemption was needed; there are no nested constructs.

(b) **Heading-line crossings: 0.** No unit span `[line_start, line_end]` contains any real heading line in either file (headings live in their own accounting bucket, as designed). Note there are no `empty_section` units in this batch (every section has content), so no span even coincides with a heading line.

(c) **Unit-type sanity: 0 violations.** All 65 records verified against their content:
- `frontmatter` (2): both span L1–6, first and last excerpt lines are exactly `---`, matching `mdextract.frontmatter_span`.
- `math_block` (10): all excerpts contain `$$` and start with a `$$` delimiter line (9 in file A: L17–19, 23–25, 29–31, 43–45, 53–55, 63–65, 71–73, 77–79, 89–91; 1 in file B: L52–54).
- `code_block` (3): all fenced — `​```python` L111–129 (file A), bare ` ``` ` ASCII-tree L17–27 and `​```python` L97–116 (file B); last lines are closing fences.
- `table` (1): L133–139, all lines start with `|` and include the `---` header separator row.
- `callout` (2): L10–11 in each file, first line matches `> [!info] TL;DR` (Obsidian callout tag).
- `quote` (0): none — correct, since both blockquote constructs are callouts.
- `list` (16): every excerpt's first line matches the list-item marker grammar (`-`/`*`/`+`/`N.`/`N)` + space) and continuation lines are either items or indented (e.g. file B's numbered `Algorithm` list L66–70 with indented sub-bullets is correctly one `list` unit).
- `prose` (31): no prose unit starts with `>`, `|`, `$$`, a fence, or a list marker, and no prose span contains a `$$` block-start line.

Additional boundary facts: no blank line occurs inside any non-code/math unit (blank-inside-unit lines: 4 in file A, 2 in file B — all six are inside python code fences, where they are legitimate unit content, not lost lines). Independent line accounting from records + mdextract headings: file A = 93 unit + 22 heading + 52 excluded-blank = **167/167**; file B = 105 + 18 + 44 = **167/167** — both `consistent`, matching the coverage report buckets exactly. (Transparency note: my first accounting pass naively counted all 56/46 blank lines in the files as "excluded", producing a spurious 171/169; the discrepancy was my script's bug — fence-interior blanks belong to unit spans — and disappears once blanks are partitioned correctly. The framework's accounting was right.)

## CHECK 4 — Structural purity: **65/65 PASS**

Every one of the 65 records has:
- `disposition` exactly `"Unaccounted"` (65/65);
- **no `overlap_type` field at all** (the key is absent, so no semantic value is set); likewise no `concept_ids` or `destinations`, and no unexpected keys of any kind beyond the 13 schema fields;
- `source_id` prefixed `master-ai:` (65/65) — `master-ai:03 - Machine Learning/Supervised Learning/02 - Linear and Logistic Regression.md` (35) and `master-ai:03 - Machine Learning/Supervised Learning/03 - Decision Trees and Gradient Boosting.md` (30);
- `verification_status` exactly `{accounting: pending, editorial: pending, semantic: pending, technical: pending, extraction: machine-segmented}` (65/65);
- `unit_type` within the structural vocabulary (65/65).

No semantic or overlap claims anywhere in the batch. Independent schema re-validation: valid, 0 errors.

## CHECK 5 — Cross-vault readiness observation (PROSE ONLY — no classification assigned)

For the linear/logistic-regression domain, these topics are present **both** in this Master AI batch (file A) and in the AI Course EXT-001 batch (`001-ext001-ai-course-03.1-regression.jsonl`, 298 records, 6 files). One KU-id per side as evidence:

| Topic | AI Course (EXT-001) evidence | Master AI (EXT-002) evidence |
|---|---|---|
| MSE / squared-error loss | KU-d34b1ad0162dc662 (prose, "We use the **Mean Squared Error (MSE)**") | KU-327a42f377f78038 (math_block, `L(\mathbf{w}, b) = \frac{1}{N}\sum (y_i - \hat{y}_i)^2`) |
| Normal equations / closed-form solution | KU-64d87f0278acada9 (math_block, `W = (X^T X)^{-1} X^T Y`) and KU-afad28616fcebe08 ("This is the **Normal Equation**") | KU-8da5462c28a9111a (math_block, `\hat{\mathbf{w}} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}`) |
| Gradient descent as the large-problem alternative | KU-6c357e4ff4ab9221 (prose, "**Gradient Descent** is the algorithm for 'walking down the hill.'") | KU-e158377d31fa3fbe (prose, "use gradient descent (or SGD) instead; the matrix inverse is $O(d^3)$") |
| Logistic sigmoid | KU-3bdaae307ccf2517 (prose, "**Key properties of the Sigmoid:**") / KU-37365ca5a1071a9b | KU-f1a9690f30690f3f (math_block, `p(y=1\mid\mathbf{x}) = \sigma(\mathbf{w}\cdot\mathbf{x}+b) = \frac{1}{1+e^{-(...)}}`) |
| Binary cross-entropy / log loss | KU-deeee89749d932bf (prose, "we _must_ use **Binary Cross-Entropy (Log Loss)**") | KU-1a3b5288448131a4 (math_block, batch BCE formula) / KU-37ff602bc236ac91 (Bernoulli MLE = BCE) |
| Softmax (multiclass output) | KU-d758cb4d3ebb7e4d (code_block, keras `layers.Dense(10, activation='softmax')`, MNIST lab) | KU-74814e20d567d124 (math_block, softmax formula) / KU-70ae26c22fefe5f8 |
| sklearn linear-model usage | KU-bca783756b65c8f9 (code_block, `from sklearn.linear_model import LinearRegression`) | KU-0b46cce8095bdcf5 (code_block, `LinearRegression, LogisticRegression, Ridge` + `C = 1/lambda`) |

Observational asymmetries relevant to EXT-003+ planning (facts, not classifications):
- **Master-AI-only in this domain pairing:** ridge/L2 and lasso/L1 regularization (word-boundary searches for "ridge", "lasso", "L1/L2 regularization", "regularization" over all 298 EXT-001 excerpts return **zero** genuine hits — the only apparent hits were the word "bridge" and a mermaid node label `L2[Equation: y = ax + b]`), the MAP/Bayesian-prior interpretations, calibration/temperature-scaling, and the O(d³) caveat.
- **Course-side-only in this batch:** from-scratch gradient-descent implementation code, the French MNIST deep-learning lab, and the DL-perspective framing.
- **Methodological caution for the next session:** naive substring matching produces false positives here ("bridge" ⊃ "ridge"; mermaid `L1[...]`/`L2[...]` labels). Overlap-classification tooling should use word-boundary/regex matching and human confirmation against excerpts, not raw substring counts. My pair list above is keyword-evidence only; **no overlap classification is assigned or implied by this review.**

## Acceptance criteria mapping

| Criterion | Required | Found | Status |
|---|---|---|---|
| Rare details with KU-id evidence | ≥10 (≥5/file) | 32/32 (16+16) | PASS |
| Heading coverage (counted by reviewer) | N/N | 40/40 (22+18) | PASS |
| Boundary anomalies | 0 or documented design | 0 | PASS |
| Structurally pure records | 65/65 | 65/65 | PASS |
| Cross-vault topic-pair list | factual | 7 pairs with KU evidence | PASS |

## Concerns / notes for the orchestrator (none blocking)

1. **Extraction quality is genuinely high.** The batch is byte-identical to an independent re-run of the framework extractor, every excerpt is a byte-exact source slice, and all 334 lines of both files are accounted for with a consistent partition. I found nothing to fix.
2. **Heading-detection hazard confirmed:** file A's worked example contains `#`-prefixed python comments that defeat naive heading matchers (the orchestrator hit this too and switched to mdextract). Any future tooling that touches these files must use mdextract, not naive regex.
3. **Determinism claim verified:** current batch file sha256 `e0ef1218…1118` equals the worklog's second-run hash; my in-memory re-segmentation reproduces the batch exactly.
4. **Course-batch keyword false positives** (bridge/mermaid) as detailed in Check 5 — worth carrying into EXT-003's method notes.
5. Minor observation, no action needed: the two source files each end with a wikilink list at L164–167; these are captured as `list` units with correct heading_path `[…, "See Also"]`, so link-graph work later can rely on them.
