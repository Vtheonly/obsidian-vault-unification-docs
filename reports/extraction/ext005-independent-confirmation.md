# EXT-005 Independent Confirmation + Push Retry Record (2026-10-27 session)

## What happened

A fresh session (2026-10-27) cloned the repository from `origin/main`
(7d9e65f, the EXT-004 state commit). Because the clone lacked the
EXT-005 commits (which are LOCAL-ONLY in `/home/z/my-project/repo` —
see the push blocker below), the session re-executed EXT-005 end-to-end
in the fresh clone BEFORE discovering the local-only commits via
`/home/z/my-project/worklog.md`. This report records the outcome of that
redundant execution as independent confirmation evidence, the push retry
results, and four candidate additional classification clusters found by
the re-derivation that are NOT in the committed classification file.

No source vault was modified at any point (verified in both working
copies). The committed artifacts are authoritative; nothing in this
report modifies them.

## 1. Independent re-derivation confirms the committed EXT-005 work

The fresh session executed, in a separate clone
(`/home/z/my-project/obsidian-vault-unification-docs`):

- Extraction batch 004 (master-ai Evaluation file): 43 KUs, 1/1 files,
  0 excluded/failed — **byte-identical** to the committed batch 004
  (verified by `cmp`; deterministic extraction reconfirmed).
- Extraction batch 005 (ai-course 03.6 folder): 275 KUs, 5/5 files,
  0 excluded/failed — **byte-identical** to the committed batch 005
  (verified by `cmp`).
- Double-run determinism for both batches: byte-identical.
- Fidelity (new both-batch checker, EXT-004 pattern): 43/43 + 275/275
  byte-exact excerpts, valid hashes, unique ids (including cross-batch),
  structural purity, 0 heading-crossing spans.
- Term map `evaluation-domain-v1.json` re-derived independently
  (123 terms / 90 aliases / 44 cross-vault, machine-verified in-scope;
  the committed map has 98 terms / 33 aliases / 40 cross-vault — same
  construction discipline, different pruning choices; both are
  content-verified).
- CAP-013 discovery over both batches: 318 KUs, 123 topics, 45
  cross-vault topics, 1927 term pairs, 0 hash duplicates (committed run:
  98/40/1604/0 — same method, larger term map; conclusions consistent).
- 29 evidence-based classifications generated with byte-exact quote
  verification (EXT-003/004 script pattern; schema + cross-checks valid;
  exit 0).

The re-derived classification set (21 SD + 7 PO + 1 CC) converges with
the committed set (23 SD + 5 PO + 1 CC) on all major clusters: accuracy
formula + imbalance trap, confusion-matrix table + derived-from claim,
precision/recall definitions, PR tradeoff, spam/cancer cost asymmetry,
F1 formula + harmonic-mean rationale, F-beta, macro/micro averaging, ROC
definition, AUC interpretation + properties + PR-AUC caveat, MSE/MAE/
RMSE/R^2/Huber, business-decision framing, sklearn code, MAP/mAP
(re-derived as Complementary Content; committed set uses SD 0023 + PO
0024 name-collision pair with finding F-0008 — a defensible reviewed
alternative treatment), calibration, CV/held-out discipline.

**Conclusion: the committed EXT-005 work is independently reproducible
from the same immutable sources.** The duplicate unreviewed artifacts
were NOT committed (they would be competing records; ADR-0009 discipline).
The re-derivation's unique findings are preserved below.

## 2. Push retry (2026-10-27) — all three PATs still rejected

The user re-supplied the same three PATs for this session ("one of them
should work"). Results, from `/home/z/my-project/repo` (HEAD 4f369bd):

| Check | Scheme / method | PAT 1 | PAT 2 | PAT 3 |
|---|---|---|---|---|
| `api.github.com/repos/...` | `Authorization: Bearer <T>` | 401 | 401 | 401 |
| `api.github.com/user` | `Authorization: token <T>` | 401 Bad credentials | 401 | 401 |
| `git push` | `https://x-access-token:<T>@github.com/...` | Invalid username or token | Invalid username or token | Invalid username or token |

Unauthenticated repo API access returns 403 (repo reachable; auth
required). Conclusion: **all three tokens are expired, revoked, or
otherwise invalid — the push remains blocked.** The EXT-005 commits
(4d77dff, 765774c, 4f369bd) plus this session's verification commit
remain local-only in `/home/z/my-project/repo` on branch `main`.
Fresh credentials (new PAT with `repo` scope for
`Vtheonly/obsidian-vault-unification-docs`) are required; then push
`7d9e65f..HEAD` to `origin/main`.

## 3. Candidate additional classification clusters (UNREVIEWED)

The re-derivation found four cross-vault clusters in the evaluation
domain that are NOT separate records in the committed
`003-ext005-evaluation-overlap.jsonl` (they may be partially folded
into existing rationales there). All quotes below were byte-exact-
verified inside the committed batch excerpts by the session's generator
script before recording. These are **candidates only** — they carry NO
independent review and must NOT be treated as classifications. If
adopted, they belong in a NEW append-only classification file under a
new task id with its own independent review (queued as EXT-007).

### C1. No single metric suffices; track multiple metrics — proposed Semantic Duplicate

- master-ai (batch 004, Production Implications list): "- **Track
  multiple metrics.** Accuracy alone hides precision/recall tradeoffs;
  F1 alone hides calibration."
- ai-course (batch 005, one-paragraph guide callout): "Always compute
  and report the full confusion matrix and classification report—no
  single number tells the whole story."
- ai-course (batch 005, summary): "The most important practice is to
  always look beyond accuracy and report a comprehensive set of metrics
  that reflects the true performance characteristics of your model."
- Relationship to committed set: closest committed record is
  OC-ext005-0026 (business decision); this cluster's core claim
  (report a comprehensive metric set) is not a separate committed
  record.

### C2. Degenerate majority-class model pattern transferred to pixel accuracy — proposed Partial Overlap

- master-ai (batch 004, accuracy section): "A spam filter that always
  says \"not spam\" gets 99% accuracy if 1% of emails are spam — and is
  useless." (also the anchor of committed OC-ext005-0002)
- ai-course (batch 005, pixel-accuracy pitfalls): "**Pitfalls:**
  Misleading for imbalanced classes. If 90% of the image is background,
  a model that always predicts \"background\" gets 90% pixel accuracy
  but is useless for the actual segmentation task."
- ai-course (batch 005, CV pitfalls section): "If 95% of pixels are
  background, pixel accuracy is dominated by background performance.
  Use mIoU (which weights all classes equally) or report per-class IoU."
- Relationship to committed set: committed OC-ext005-0002 covers the
  classification-accuracy trap; this record captures the same
  degenerate-model argument instantiated for a DIFFERENT metric (pixel
  accuracy), where master-ai has no segmentation counterpart.

### C3. Loss-vs-metric role distinction for regression metrics — proposed Partial Overlap

- master-ai (batch 004, MSE section): "Penalizes large errors heavily
  (quadratic). Sensitive to outliers. The default loss for regression."
- master-ai (batch 004, Huber section): "Often used in regression losses
  for deep learning."
- ai-course (batch 005, loss-relationship section): "MSE and MAE are
  both loss functions (used in training) and metrics (used in
  evaluation). But they are not always the same: you might train with
  MSE (for smooth gradients) but evaluate with MAE (for interpretability
  and robustness). This is fine — the loss determines what the model
  optimizes; the metric determines how you judge it."
- ai-course (batch 005, MAE pitfalls): "- The gradient is constant
  magnitude regardless of error size, which can make training harder
  (the model gets the same \"push\" from a small error as a large one).
  This is why MAE is rarely used as a training loss, even when it is
  the evaluation metric."
- Relationship to committed set: closest committed records are
  OC-ext005-0018 (MSE) and OC-ext005-0022 (Huber); the explicit
  loss-vs-metric distinction and the constant-gradient rationale are
  not a separate committed record.

### C4. For imbalanced data prefer PR-AUC AND macro-averaged metrics — proposed Semantic Duplicate

- master-ai (batch 004, production list): "- **For imbalanced data**:
  prefer PR-AUC and macro F1 over accuracy."
- ai-course (batch 005, one-paragraph guide): "For imbalanced datasets
  (>10:1 ratio), supplement with PR-AUC instead of ROC-AUC. For
  multi-class problems, report macro-averaged metrics alongside
  weighted-averaged metrics to reveal performance on rare classes."
- Relationship to committed set: committed OC-ext005-0015 covers the
  PR-AUC preference; the macro-F1-for-imbalance recommendation pairing
  is additionally present on both sides and could strengthen or extend
  that record's evidence rather than require a new record.

## Reproduction pointers

- Duplicate-pass working clone (kept, uncommitted):
  `/home/z/my-project/obsidian-vault-unification-docs` — contains
  `scripts/ext005_fidelity.py`, `scripts/ext005_term_map.py` (123-term
  variant), `scripts/ext005_term_probe.py`,
  `scripts/ext005_classifications.py` (29-record variant), and the
  re-derived (uncommitted) `state/` artifacts.
- Authoritative working copy: `/home/z/my-project/repo` (commits
  4d77dff, 765774c, 4f369bd local-only on main, on top of origin/main
  7d9e65f).

## Limitations

- The re-derivation was performed by the same model family (GLM 5.3) as
  the original EXT-005 work; it is an independent re-execution, not an
  independent reviewer for the candidate clusters in section 3.
- The byte-identical batch comparison covers the two new batches only
  (batches 001-003 were not re-extracted this session; they were
  verified via the registry rebuild).
- This session did not re-run the committed classification file's
  byte-exact verification (the EXT-005-REVIEW report already provides
  it: 105/105 quotes byte-exact including original-source lines).
