# EXT-003 Independent Review (EXT-003-REVIEW)

- Reviewer: independent review subagent (read-only; no files modified; scratch
  scripts confined to /tmp/ext003_review/)
- Scope: `state/classifications/001-ext003-regression-overlap.jsonl` (14
  overlap classifications over batches 001+002, 363 KUs) — the project's
  first semantic (overlap_type) judgments
- Method: Python-assisted byte-exact verification against the committed
  batches AND the original source files, plus full-excerpt reading of every
  referenced KU for semantic judgment, rationale fact-checking, and
  candidate-vs-classification coverage analysis
- Date: 2026-10-26

## Verdict: PASS-WITH-NOTES

All 14 assigned overlap types are defensible per the §7 taxonomy. Notes
(three rationale-wording inaccuracies + one evidence addition) were repaired
by the orchestrator before commit; no label changed.

## Check 1 — Evidence fidelity: 66/66 byte-exact, 0 mismatches

Every evidence quote is an exact substring of the referenced KU's excerpt in
the committed batches. Additionally verified beyond the brief:

- All referenced KUs' excerpts are byte-identical slices of the original
  source files at their claimed line ranges (0 mismatches).
- All quotes appear on exactly their claimed source line in the original
  files (0 off-by-one).
- `excerpt_hash` self-consistent for all referenced KUs; evidence
  `source_path` fields match; evidence line numbers fall inside KU spans.
- All records validate against `schemas/overlap-classification.schema.json`.

## Check 2 — Vault span: 14/14 cross-vault

Every classification references KUs from both `ai-course:` and `master-ai:`
source prefixes.

## Check 3 — Semantic judgment audit: 14/14 agree

| ID | Topic | Assigned | Verdict |
|---|---|---|---|
| 0001 | LR model form | Semantic Duplicate | Agree |
| 0002 | MSE cost | Semantic Duplicate | Agree |
| 0003 | Normal equations | Semantic Duplicate | Agree (rationale wording fixed pre-commit) |
| 0004 | O(d^3)/O(m^3) | Semantic Duplicate | Agree |
| 0005 | closed-form vs GD | Semantic Duplicate | Agree (borderline, defensible) |
| 0006 | GD scalable method | Partial Overlap | Agree |
| 0007 | Logistic sigmoid | Semantic Duplicate | Agree (borderline, defensible) |
| 0008 | BCE / log loss | Semantic Duplicate | Agree (borderline, defensible; wording fixed) |
| 0009 | Softmax output layer | Partial Overlap | Agree |
| 0010 | NN building blocks | Partial Overlap | Agree |
| 0011 | sklearn workflow | Partial Overlap | Agree |
| 0012 | Multicollinearity | Partial Overlap | Agree |
| 0013 | Linear decision boundary | Partial Overlap | Agree |
| 0014 | Feature scaling | Partial Overlap | Agree (borderline, defensible; evidence extended) |

## Check 4 — Rationale factual claims

Verified accurate: OC-0004's O(d^3)/O(m^3) quotes (including the correction
of the EXT-002-REVIEW Check 5 "Master-AI-only" claim — justified: d vs m is
pure notation); OC-0011's `# C = 1/lambda` comment; OC-0007's note that
master-ai never uses the word "sigmoid" (grep-verified, 0 matches);
OC-0003's "Normal Equation" heading-only observation; OC-0002/0008's
course-unique motivation/derivation claims; OC-0009's claim that the course
never states the softmax formula (verified across all 298 course KUs).

Inaccuracies found and repaired by the orchestrator before commit (labels
unchanged):

1. OC-0003 (moderate): rationale said "both describe it as ... obtained by
   setting the derivative of the MSE to zero" — master-ai contains no
   derivative text at all; corrected to attribute the derivation description
   to the course side only.
2. OC-0008 (minor): "both present it via a piecewise y=1/y=0 construction"
   misdescribed master-ai's example→batch construction; corrected to
   "stepwise".
3. OC-0014 (minor): "penalty fairness" was classifier gloss, not quoted
   master-ai evidence; corrected (master-ai states the practice without an
   explicit motivation).

## Check 5 — Coverage sanity: no major gaps

- All 7 hypothesized cross-vault topic pairs from EXT-002-REVIEW Check 5 are
  covered (MSE→0002, normal equations→0003, gradient descent→0005+0006,
  sigmoid→0007, BCE→0008, softmax→0009, sklearn→0011).
- Single-vault topics correctly received NO classification: ridge/L2,
  lasso/L1, MAP/prior, calibration/temperature scaling (independently
  re-verified — the course batch's apparent hits are the English word
  "bridge", mermaid node labels, and literal temperature prediction);
  also MLE interpretations, odds/logit, R^2, and the trees/boosting file.
- The 614 confirmed pairs not inside a classification are generic-term
  residue ("neural network" x132, "logistic regression" x115, "MSE" x85,
  ...) plus two defensible-omission clusters (XGBoost `learning_rate`
  hyperparameter vs GD learning rate; regression-vs-NN table vs MNIST
  train/test explanation — different contexts, no shared core claim).
- No confirmed cross-vault candidate pair that required classification is
  missing.
- Grounding observation: 6 of 14 classifications (0001, 0002, 0003, 0006,
  0007, 0008) have no confirmed candidate pair linking their KUs — they rest
  on orchestrator semantic judgment (formula-level identity invisible to
  word-boundary matching). This is consistent with the declared method and
  the underlying evidence was independently verified as real; the rationales
  for 0003 and 0007 transparently flag exactly this.

## Reviewer-recommended repairs (all applied by the orchestrator)

1. Correct OC-0003 rationale derivative attribution — DONE (regenerated).
2. Fix OC-0008/OC-0014 wording — DONE (regenerated).
3. Add KU-169259731978f5ae (MNIST pixel normalization) to OC-0014 evidence —
   DONE (OC-0014 now 5 ku_ids / 5 evidence; kus_participating 60 → 61).

## Limitations of this review

- Did not re-run or audit the CAP-013 discovery algorithm itself (lookaround
  correctness, mermaid-flag logic) — covered separately by tests/test_overlap.py
  (F-0006 regression cases) and the orchestrator's reproducibility check
  (byte-identical re-run).
- Excerpt-vs-source verification covered the 60 referenced KUs only, not all
  363 (full-batch fidelity was EXT-001/EXT-002 review scope).
- The four borderline agreements (0005, 0007, 0008, 0014) are judgment calls;
  a stricter reading could defensibly relabel 0005/0007/0008 as Partial
  Overlap.
- Did not audit the registry DB contents or dispositions (all still
  Unaccounted — downstream by design).
