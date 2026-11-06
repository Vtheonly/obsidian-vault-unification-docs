#!/usr/bin/env python3
"""Generate EXT-005 overlap classification records (EXT-005).

Builds state/classifications/003-ext005-evaluation-overlap.jsonl from the
orchestrator's evidence review of CAP-013 candidates over batch 004
(master-ai '05 - ML Evaluation Metrics.md', 43 KUs) + batch 005 (ai-course
03.6 Model Evaluation, 275 KUs) — the evaluation-metrics domain.

Safety properties (inherited from the EXT-003/EXT-004 pattern):
- every ku_id is resolved against the committed batches (full-id match);
- every evidence quote is verified BYTE-EXACT inside the referenced KU
  excerpt (no transcription);
- evidence lines are computed from the excerpt line positions;
- the output is validated against the classification schema + file-level
  cross-checks before the script exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from vault_unification import registry  # noqa: E402

BATCHES = [
    REPO / "state/knowledge-units/004-ext005-master-ai-evaluation.jsonl",
    REPO / "state/knowledge-units/005-ext005-ai-course-03.6-model-evaluation.jsonl",
]
OUT = REPO / "state/classifications/003-ext005-evaluation-overlap.jsonl"
CLS_SCHEMA = REPO / "schemas/overlap-classification.schema.json"

CANDIDATE_REF = (
    "reports/extraction/ext005-overlap-candidates.json (+ pairs JSONL; "
    "CAP-013 run 2026-10-26 over batch 004 (master-ai 05 - ML Evaluation "
    "Metrics.md, 43 KUs) + batch 005 (ai-course 03.6 Model Evaluation, 5 "
    "files, 275 KUs) with state/term-maps/evaluation-domain-v1.json)"
)
CLASSIFIED_BY = "EXT-005 orchestrator (Z AI / GLM 5.3 session, 2026-10-26)"
METHOD = (
    "CAP-013 word-boundary candidate discovery + orchestrator excerpt review: "
    "both sides' KU excerpts read in full from the committed batches; "
    "evidence quotes are byte-exact fragments; overlap_type assigned per "
    "docs/KNOWLEDGE_AND_PROVENANCE.md section 7 (pair-level, separate from "
    "disposition)"
)
DATE = "2026-10-26"


def load_kus():
    kus = {}
    for batch in BATCHES:
        for line in batch.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                kus[rec["knowledge_unit_id"]] = rec
    return kus


def quote_evidence(kus, ku_id: str, fragment: str):
    """Verify *fragment* is a byte-exact substring of the KU excerpt and
    return the evidence dict with the exact quote and its source lines."""
    rec = kus[ku_id]
    excerpt = rec.get("excerpt") or ""
    if fragment not in excerpt:
        raise SystemExit(
            f"quote not found byte-exact in {ku_id}:\n  {fragment[:120]!r}\n"
            f"excerpt starts: {excerpt[:120]!r}"
        )
    lines = excerpt.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        if fragment.split("\n")[0] in line:
            start_idx = i
            break
    if start_idx is None:
        joined = "\n".join(lines)
        pos = joined.find(fragment)
        start_idx = joined[:pos].count("\n")
    n_span = fragment.count("\n") + 1
    src_lines = [
        rec["line_start"] + start_idx + k for k in range(n_span)
    ]
    return {
        "ku_id": ku_id,
        "quote": fragment,
        "source_path": rec["source_path"],
        "lines": src_lines,
    }


def main() -> int:
    kus = load_kus()

    def R(ku_id, fragment):
        return (ku_id, fragment)

    classifications = []

    def add(cid, topic, overlap_type, rationale, evidence_pairs):
        ev = [quote_evidence(kus, kid, frag) for kid, frag in evidence_pairs]
        ku_ids = sorted({e["ku_id"] for e in ev})
        vaults = {kus[k]["source_id"].split(":", 1)[0] for k in ku_ids}
        assert len(vaults) >= 2, f"{cid}: single-vault group {vaults}"
        classifications.append(
            {
                "classification_id": cid,
                "task_id": "EXT-005",
                "topic": topic,
                "overlap_type": overlap_type,
                "ku_ids": ku_ids,
                "rationale": rationale,
                "evidence": ev,
                "candidate_ref": CANDIDATE_REF,
                "classified_by": CLASSIFIED_BY,
                "method": METHOD,
                "date": DATE,
            }
        )

    # ---- 0001 accuracy formula ----
    add(
        "OC-ext005-0001",
        "Accuracy as correct-predictions / total-predictions",
        "Semantic Duplicate",
        "Both vaults define accuracy as the same ratio. Master-ai words it "
        "as 'correct predictions / total predictions'; the course file 01 "
        "derives the identical ratio from the confusion-matrix counts "
        "(TP+TN over all four cells) and file 02 states the same formula "
        "with the medical example plugged in. The formulas are the same "
        "quantity; the course additionally shows the expansion from the "
        "four counts, which is elaboration, not a different claim.",
        [
            R("KU-1500ae9db98d282d", "\\text{Accuracy} = \\frac{\\text{correct predictions}}{\\text{total predictions}}"),
            R("KU-fa83ca88210a1132", "$$Accuracy = \\frac{TP + TN}{TP + TN + FP + FN} = \\frac{\\text{Total Correct}}{\\text{Total Data}}$$"),
            R("KU-0b9cd57fd54c2aed", "$$\\text{Accuracy} = \\frac{\\text{Correct Predictions}}{\\text{Total Predictions}} = \\frac{990}{1000} = 99\\%$$"),
        ],
    )

    # ---- 0002 accuracy trap on imbalanced data ----
    add(
        "OC-ext005-0002",
        "Accuracy is misleading on imbalanced data (majority-class guess)",
        "Semantic Duplicate",
        "Both vaults make the identical argument: a model that always "
        "predicts the majority class achieves deceptively high accuracy "
        "while being useless. Master-ai uses the spam example (1% spam, "
        "99% accuracy, 'and is useless'); the course file 02 uses the "
        "1,000-patient medical example (990/1000 healthy, 99% accuracy, "
        "'clinically worthless'), generalizes to four more imbalanced "
        "domains with rates (fraud 99.8%, disease screening 99.9%, "
        "intrusion 99.99%, defects 99.5%), and file 01 adds the generic "
        "95%-Class-A version. The shared core claim — accuracy driven by "
        "the majority class obscures failure on the minority class that "
        "matters — is duplicated; the course's domain list and the warning "
        "callout are elaboration around it.",
        [
            R("KU-f353ec8719844bc0", "Simple, intuitive, but **misleading on imbalanced data**. A spam filter that always says \"not spam\" gets 99% accuracy if 1% of emails are spam — and is useless."),
            R("KU-75c67210a40bbd1f", "Ninety-nine percent accuracy sounds impressive, but this model is clinically worthless—it fails to detect a single case of the disease."),
            R("KU-5ce3302d29f214b0", "Credit card fraud detection (99.8% legitimate transactions), rare disease screening (99.9% healthy), security intrusion detection (99.99% normal traffic), and manufacturing defect detection (99.5% non-defective) all exhibit extreme class imbalance where accuracy is a meaningless metric."),
            R("KU-f51148db7a9a4b13", "*   *Limitation:* If 95% of data is Class A, a model that *always* guesses \"A\" has 95% accuracy but is useless."),
            R("KU-d2d46793f6ca5c36", "While accuracy is perfectly adequate for balanced datasets where every class is equally represented and all types of errors are equally costly, it becomes dangerously misleading—sometimes to the point of uselessness—when these conditions are not met."),
            R("KU-4c0d0ce1a717e047", "A model with 99% accuracy on a dataset that is 99% one class tells you NOTHING about the model's ability to detect the important minority class."),
        ],
    )

    # ---- 0003 confusion matrix ----
    add(
        "OC-ext005-0003",
        "Confusion matrix 2x2 table as the basis of all classification metrics",
        "Semantic Duplicate",
        "Both vaults present the same 2x2 TP/FP/FN/TN table and make "
        "the same follow-on claim that every other metric is derived from "
        "these four counts. Master-ai introduces the table with 'For binary "
        "classification:' and derives all metrics from it ('All metrics "
        "below are derived from these four counts.'); the term 'Confusion "
        "Matrix' appears in master-ai only as the section heading (source "
        "line 22), which is outside KU excerpts by construction (headings "
        "are context, not unit spans), while the course names it inside the "
        "prose ('The confusion matrix is a table that provides a complete "
        "breakdown...') and states 'Every other classification "
        "metric—precision, recall, F1, specificity, and more—is derived "
        "from these four counts.' The table structure and the "
        "derived-metrics claim are semantically identical; the naming "
        "difference is presentational (heading vs prose), not a content "
        "difference. Classified as a judgment per the EXT-003 precedent "
        "(structure-level identity; term matching cannot pair the table "
        "because the name sits in a heading on one side). Repair applied "
        "from EXT-005-REVIEW R1: the initial rationale wrongly said "
        "master-ai shows the table 'without naming it' — the file-level "
        "heading does carry the name.",
        [
            R("KU-d51df8a9b8f899af", "| Actual Positive | TP (true positive)  | FN (false negative)|"),
            R("KU-34dc922de5c37e95", "All metrics below are derived from these four counts."),
            R("KU-5c2c2a2585b81a84", "The confusion matrix is a table that provides a complete breakdown of a classifier's performance by comparing predicted labels against true labels."),
            R("KU-5c2c2a2585b81a84", "Every other classification metric—precision, recall, F1, specificity, and more—is derived from these four counts."),
            R("KU-0ee4c77024eb460a", "| **Actual Positive** | True Positive (TP) | False Negative (FN) |"),
            R("KU-f08cc586a5ec436a", "| **Actual: Positive (1)** | **TP** (True Positive) | **FN** (False Negative) |"),
        ],
    )

    # ---- 0004 precision formula ----
    add(
        "OC-ext005-0004",
        "Precision = TP/(TP+FP), fraction of predicted positives that are right",
        "Semantic Duplicate",
        "Both vaults give the identical formula TP/(TP+FP) with the "
        "identical interpretation. Master-ai embeds the interpretation in "
        "the formula annotation '(of predicted positives, how many are "
        "actually positive)'; the course file 01 gives the bare formula "
        "and file 02 spells the interpretation out ('When the model says "
        "positive, how often is it right? ... the fraction of predicted "
        "positives that are actually positive'). Same definition, same "
        "reading; only the packaging differs.",
        [
            R("KU-bd157ce6b00dd71b", "\\text{Precision} = \\frac{TP}{TP + FP} \\quad \\text{(of predicted positives, how many are actually positive)}"),
            R("KU-472e0acfb2aa815b", "$$Precision = \\frac{TP}{TP + FP}$$"),
            R("KU-1781abab23581da4", "Precision answers the question: \"When the model says 'positive,' how often is it right?\" It is the fraction of predicted positives that are actually positive."),
        ],
    )

    # ---- 0005 recall formula ----
    add(
        "OC-ext005-0005",
        "Recall = TP/(TP+FN), fraction of actual positives caught",
        "Semantic Duplicate",
        "Both vaults give the identical formula TP/(TP+FN) with the "
        "identical interpretation. Master-ai annotates the formula '(of "
        "actual positives, how many did we catch)'; the course file 01 "
        "gives the bare formula and file 02 spells it out ('Of all the "
        "actual positives, what fraction did the model correctly "
        "identify?'). Same definition, same reading.",
        [
            R("KU-d8c0857557f50384", "\\text{Recall} = \\frac{TP}{TP + FN} \\quad \\text{(of actual positives, how many did we catch)}"),
            R("KU-2ff426f45208e100", "$$Recall = \\frac{TP}{TP + FN}$$"),
            R("KU-b674ba45c124641d", "Recall answers the question: \"Of all the actual positives, what fraction did the model correctly identify?\" A recall of 0.90 means the model catches 90% of all actual positive cases, but misses 10%."),
        ],
    )

    # ---- 0006 precision/recall tension + error costs ----
    add(
        "OC-ext005-0006",
        "Precision-recall tradeoff driven by asymmetric error costs",
        "Semantic Duplicate",
        "Both vaults state the same two-part claim: (a) precision and "
        "recall are in tension, and (b) which one matters depends on the "
        "relative cost of the two error types. Master-ai: 'high precision "
        "= few false positives; high recall = few false negatives. Which "
        "matters depends on the cost of each error type.' The course: "
        "'Precision and recall are fundamentally in tension: improving one "
        "usually comes at the expense of the other' plus the asymmetry "
        "callout 'the cost of Type I and Type II errors is NOT "
        "symmetric... the fundamental reason why we need metrics beyond "
        "accuracy'. The course then adds threshold-sweep mechanics and a "
        "worked 200-patient table that master-ai lacks; that depth "
        "difference does not change the duplicated core claim.",
        [
            R("KU-c0e3727d25129255", "Tradeoff: high precision = few false positives; high recall = few false negatives. Which matters depends on the cost of each error type."),
            R("KU-64349575b7c2a5a4", "Precision and recall are fundamentally in tension: improving one usually comes at the expense of the other."),
            R("KU-7db58d497ed27249", "> In most real-world applications, the cost of Type I and Type II errors is NOT symmetric."),
        ],
    )

    # ---- 0007 spam -> precision ----
    add(
        "OC-ext005-0007",
        "Spam filtering is the canonical optimize-precision example (FP = lost real email)",
        "Semantic Duplicate",
        "Both vaults use the same canonical example with the same "
        "direction: spam filters should optimize precision because a false "
        "positive means a legitimate email lands in the spam folder. "
        "Master-ai: 'Spam filter: precision matters more (false positives "
        "= real email in spam folder)'; the course file 01: 'Important in "
        "Spam Filters (You don't want to classify a real email as "
        "Spam/FP)' and file 02 elaborates the same example at length. "
        "Shared claim: same example, same error type, same metric "
        "recommendation.",
        [
            R("KU-0bf5c8908270a972", "- **Spam filter**: precision matters more (false positives = real email in spam folder)."),
            R("KU-857fdb99ada0fb5c", "**Spam Detection**: When your email filter classifies a message as spam, that message is typically moved to a spam folder that the user rarely checks."),
            R("KU-e70cf01c45030bb1", "*   *Use case:* Important in Spam Filters (You don't want to classify a real email as Spam/FP)."),
        ],
    )

    # ---- 0008 cancer -> recall ----
    add(
        "OC-ext005-0008",
        "Cancer screening is the canonical optimize-recall example (FN = missed cancer)",
        "Semantic Duplicate",
        "Both vaults use the same canonical example with the same "
        "direction: cancer/medical screening should optimize recall "
        "because a false negative means a missed deadly disease. "
        "Master-ai: 'Cancer screening: recall matters more (false "
        "negatives = missed cancer)'; the course file 01: 'Important in "
        "Cancer detection (You don't want to miss a sick patient/FN)' and "
        "file 02 elaborates the same example with the untreated-cancer "
        "consequence. Shared claim: same example, same error type, same "
        "metric recommendation.",
        [
            R("KU-0bf5c8908270a972", "- **Cancer screening**: recall matters more (false negatives = missed cancer)."),
            R("KU-0e0ead8e34fb0b92", "**Cancer Detection / Medical Screening**: A false negative in cancer screening means a patient with cancer is told they are cancer-free."),
            R("KU-16c467cee79fc6be", "*   *Use case:* Important in Cancer detection (You don't want to miss a sick patient/FN)."),
        ],
    )

    # ---- 0009 F1 formula ----
    add(
        "OC-ext005-0009",
        "F1 as the harmonic-mean formula over precision and recall",
        "Semantic Duplicate",
        "All three formula statements express the identical quantity 2PR/"
        "(P+R). Master-ai's LaTeX and the course file 02's LaTeX are "
        "byte-identical; the course file 01 writes the same formula with "
        "\\times instead of \\cdot notation. This is a formula-level "
        "identity classified as a judgment with byte-exact formula "
        "quotes, per the EXT-003 precedent.",
        [
            R("KU-628ddc6b2e63a8a2", "F_1 = 2 \\cdot \\frac{\\text{Precision} \\cdot \\text{Recall}}{\\text{Precision} + \\text{Recall}}"),
            R("KU-874200c85343712f", "$$F1 = 2 \\times \\frac{Precision \\times Recall}{Precision + Recall}$$"),
            R("KU-89094bd9212042eb", "$$F_1 = 2 \\cdot \\frac{\\text{Precision} \\cdot \\text{Recall}}{\\text{Precision} + \\text{Recall}}$$"),
        ],
    )

    # ---- 0010 harmonic mean rationale ----
    add(
        "OC-ext005-0010",
        "Why the harmonic mean: it penalizes precision/recall imbalance",
        "Semantic Duplicate",
        "Both vaults give the same rationale for using the harmonic mean "
        "in F1: it favors balance / penalizes imbalance between precision "
        "and recall. Master-ai: 'The harmonic mean of precision and "
        "recall. Favors balanced precision/recall.' The course: 'heavily "
        "penalizes extreme imbalance between precision and recall' and "
        "'the F1 Score can never exceed either precision or recall, and "
        "it is pulled toward whichever is smaller'. The course adds the "
        "arithmetic-mean counterexample (P=1.0, R=0.01) and the min "
        "inequality proof; those additions elaborate the same core claim "
        "rather than differing from it.",
        [
            R("KU-b109c51de90e0f55", "The harmonic mean of precision and recall. Favors balanced precision/recall."),
            R("KU-f787a18faab7cb9a", "The harmonic mean is used instead of the arithmetic mean because it heavily penalizes extreme imbalance between precision and recall."),
            R("KU-3427f78263f37048", "This means the F1 Score can never exceed either precision or recall, and it is pulled toward whichever is smaller."),
        ],
    )

    # ---- 0011 F-beta ----
    add(
        "OC-ext005-0011",
        "F-beta generalizes F1 with a weighting parameter",
        "Partial Overlap",
        "Both vaults state the same weighting convention: beta > 1 "
        "weights recall, beta < 1 weights precision, beta = 1 recovers "
        "F1. That shared convention is the overlap. The remainder is "
        "not shared: the course gives the full F-beta formula, the "
        "named standard choices (F2 for medical screening, F0.5 for "
        "information retrieval) and the error-cost guidance attached to "
        "each direction; master-ai gives only the one-line convention "
        "inside its F1 paragraph. Partial overlap: shared convention, "
        "asymmetric depth.",
        [
            R("KU-b109c51de90e0f55", "Use **F-beta** to weight recall (beta > 1) or precision (beta < 1)."),
            R("KU-c3aaa2b6a02975e0", "The parameter $\\beta$ controls the relative weight: $\\beta > 1$ weights recall more heavily (use when false negatives are more costly), $\\beta < 1$ weights precision more heavily (use when false positives are more costly), and $\\beta = 1$ reduces to the standard F1 Score."),
        ],
    )

    # ---- 0012 ROC definition ----
    add(
        "OC-ext005-0012",
        "ROC curve: TPR vs FPR as the threshold varies",
        "Semantic Duplicate",
        "Both vaults define the ROC curve the same way: plot the true "
        "positive rate against the false positive rate while sweeping "
        "the decision threshold. Master-ai: 'Plot True Positive Rate "
        "(recall) vs. False Positive Rate as the decision threshold "
        "varies.' The course: 'evaluating a binary classifier's "
        "performance across ALL possible classification thresholds "
        "simultaneously' with the explicit axis equations (X: FPR = "
        "1-Specificity = FP/(FP+TN); Y: TPR = Recall = TP/(TP+FN)). The "
        "course adds curve-endpoint mechanics and a mermaid diagram; the "
        "definition itself is duplicated.",
        [
            R("KU-71197b18a80ea803", "Plot **True Positive Rate (recall)** vs. **False Positive Rate** as the decision threshold varies."),
            R("KU-e84e4b0587918fea", "The Receiver Operating Characteristic (ROC) curve is a graphical method for evaluating a binary classifier's performance across ALL possible classification thresholds simultaneously."),
            R("KU-5f650d993f7fba4f", "- **X-axis**: False Positive Rate (FPR) = $1 - \\text{Specificity} = \\frac{FP}{FP + TN}$"),
        ],
    )

    # ---- 0013 AUC probabilistic interpretation ----
    add(
        "OC-ext005-0013",
        "AUC = P(random positive ranked above random negative); 0.5 random, 1.0 perfect",
        "Semantic Duplicate",
        "Both vaults give the same probabilistic interpretation of AUC "
        "with the same endpoint values. Master-ai: 'probability that the "
        "model ranks a random positive above a random negative. 0.5 = "
        "random; 1.0 = perfect.' The course: 'AUC = The probability that "
        "the model assigns a higher score to a randomly chosen positive "
        "example than to a randomly chosen negative example' plus the "
        "same 1.0-perfect and 0.5-random readings (and a below-0.5 "
        "worse-than-random case master-ai omits). The interpretation and "
        "both endpoint values are duplicated; the course's third case is "
        "an addition, not a difference.",
        [
            R("KU-f01240d613d7f30f", "- **AUC** (Area Under Curve): probability that the model ranks a random positive above a random negative. 0.5 = random; 1.0 = perfect."),
            R("KU-95a4a4be5c2c8968", "**AUC = The probability that the model assigns a higher score to a randomly chosen positive example than to a randomly chosen negative example.**"),
            R("KU-c9d408a62a18559d", "- **AUC = 1.0**: Perfect classifier—the model always assigns higher scores to positives than negatives."),
            R("KU-c9d408a62a18559d", "- **AUC = 0.5**: Random classifier—the model's scores are no better than random guessing."),
        ],
    )

    # ---- 0014 AUC when useful ----
    add(
        "OC-ext005-0014",
        "AUC is threshold-independent and imbalance-insensitive (ranking measure)",
        "Semantic Duplicate",
        "Both vaults make the same pair of claims about when ROC-AUC is "
        "useful: (a) it evaluates ranking ability across thresholds "
        "rather than performance at one fixed threshold, and (b) it is "
        "insensitive to class imbalance, which makes it useful for "
        "comparing models (and robust to prevalence changes). "
        "Master-ai's three bullets (threshold-independent; insensitive "
        "to class imbalance; useful for comparing models on imbalanced "
        "data) map onto the course's three 'most useful when' items "
        "(ranking ability not fixed threshold; class distribution may "
        "change because AUC is imbalance-insensitive; comparing multiple "
        "models). Same claims, complementary phrasing.",
        [
            R("KU-f01240d613d7f30f", "- AUC is **threshold-independent** — useful when you haven't picked a threshold yet."),
            R("KU-f01240d613d7f30f", "- AUC is **insensitive to class imbalance** — useful for comparing models on imbalanced data."),
            R("KU-fe5272941aab07b3", "1. **You want to evaluate the model's ranking ability** (does it assign higher scores to positives than negatives?) rather than its performance at a specific threshold."),
            R("KU-fe5272941aab07b3", "2. **The class distribution may change at deployment time** (e.g., disease prevalence varies across populations), because AUC is insensitive to class imbalance."),
        ],
    )

    # ---- 0015 PR-AUC under extreme imbalance ----
    add(
        "OC-ext005-0015",
        "Prefer PR-AUC over ROC-AUC on highly imbalanced data",
        "Semantic Duplicate",
        "Both vaults issue the same caveat: ROC-AUC becomes "
        "misleading/uninformative under extreme class imbalance and the "
        "precision-recall curve / PR-AUC should be used instead. "
        "Master-ai: 'AUC can be misleading on highly imbalanced data; "
        "consider PR-AUC (precision-recall AUC) instead.' The course: "
        "'The dataset is extremely imbalanced (e.g., 99.9% negative), "
        "because the FPR axis is compressed. In this case, the "
        "Precision-Recall curve and PR-AUC are more informative' plus "
        "the callout 'For severely imbalanced datasets, the "
        "Precision-Recall curve is often more informative than the ROC "
        "curve.' The course explains the mechanism (FPR-axis "
        "compression by abundant true negatives; PR axes focus on the "
        "positive class) — an elaboration of the same recommendation.",
        [
            R("KU-0da7a004ebe49cf7", "But AUC can be misleading on highly imbalanced data; consider PR-AUC (precision-recall AUC) instead."),
            R("KU-d33fb766d530f483", "1. **The dataset is extremely imbalanced** (e.g., 99.9% negative), because the FPR axis is compressed. In this case, the Precision-Recall curve and PR-AUC are more informative, because they focus on the positive class."),
            R("KU-be2a880fc7e9209d", "> For severely imbalanced datasets, the Precision-Recall curve is often more informative than the ROC curve."),
        ],
    )

    # ---- 0016 macro averaging ----
    add(
        "OC-ext005-0016",
        "Macro-averaging: compute per class, average unweighted (all classes equal)",
        "Semantic Duplicate",
        "Both vaults define macro-averaging identically: compute the "
        "metric per class and take the unweighted average, treating all "
        "classes equally regardless of size. Master-ai: 'Macro F1: "
        "average F1 across classes (treats all classes equally)'; the "
        "course: 'computes the metric independently for each class and "
        "then takes the unweighted average' and 'treats all classes "
        "equally, regardless of their size.' The course adds the "
        "explicit per-class formulas and the rare-class-influence "
        "reading; the definition is duplicated.",
        [
            R("KU-9a10723cb1a31a04", "- **Macro F1**: average F1 across classes (treats all classes equally)."),
            R("KU-08215225caf54b98", "Macro-averaging computes the metric independently for each class and then takes the unweighted average:"),
            R("KU-9821045913f3f3f2", "Macro-averaging treats all classes equally, regardless of their size."),
        ],
    )

    # ---- 0017 micro averaging ----
    add(
        "OC-ext005-0017",
        "Micro-averaging: aggregate TP/FP/FN first; dominated by larger classes",
        "Semantic Duplicate",
        "Both vaults define micro-averaging the same way (aggregate the "
        "TP/FP/FN counts across classes, then compute the metric) and "
        "both note its majority-class bias. Master-ai: 'aggregates "
        "TP/FP/FN across classes then computes F1 (favors larger "
        "classes)'; the course: 'Micro-averaging is therefore not very "
        "informative for multi-class problems—it essentially reduces to "
        "accuracy and is dominated by the majority class.' The course "
        "adds the micro-equals-accuracy property for single-label "
        "multi-class problems; master-ai's 'favors larger classes' and "
        "the course's 'dominated by the majority class' are the same "
        "observation. Shared definition plus shared bias note.",
        [
            R("KU-9a10723cb1a31a04", "- **Micro F1**: aggregates TP/FP/FN across classes then computes F1 (favors larger classes)."),
            R("KU-f7c88e52748318f5", "Micro-averaging aggregates the TP, FP, and FN counts across ALL classes before computing the metric:"),
            R("KU-46d6ef93894e4227", "For multi-class classification (where each sample belongs to exactly one class), micro-averaged precision, recall, and F1 are all equal to the overall accuracy."),
            R("KU-46d6ef93894e4227", "Micro-averaging is therefore not very informative for multi-class problems—it essentially reduces to accuracy and is dominated by the majority class."),
        ],
    )

    # ---- 0018 MSE ----
    add(
        "OC-ext005-0018",
        "MSE: mean squared error, quadratic penalty, outlier-sensitive, default regression loss",
        "Semantic Duplicate",
        "Both vaults define MSE with the same formula and make the same "
        "two characterizations: heavy (quadratic) penalty on large "
        "errors and sensitivity to outliers. Master-ai adds 'the "
        "default loss for regression'; the course adds when-to-use "
        "guidance (Gaussian-noise MLE justification, use as training "
        "loss) and the squared-units interpretability pitfall. The "
        "formula, the quadratic-penalty claim and the outlier-sensitivity "
        "claim are duplicated; the additions are elaboration.",
        [
            R("KU-93b6a4533c39d83b", "\\text{MSE} = \\frac{1}{N} \\sum_i (y_i - \\hat{y}_i)^2"),
            R("KU-22806b83c974d205", "Penalizes large errors heavily (quadratic). Sensitive to outliers. The default loss for regression."),
            R("KU-7519ea3437f0e6b4", "$$\\text{MSE} = \\frac{1}{n} \\sum_{i=1}^n (y_i - \\hat{y}_i)^2$$"),
            R("KU-53dc111081cc951d", "**What it measures:** the average squared deviation. Heavily penalizes large errors (quadratic growth)."),
            R("KU-0e2ffdff12ae5f26", "- Sensitive to outliers — a single large error can dominate the metric."),
            R("KU-6ec5d6a736b0cdf5", "- When the noise is Gaussian (MSE is the maximum-likelihood estimator under Gaussian noise — see [[Probability and Statistics for ML]])."),
        ],
    )

    # ---- 0019 MAE ----
    add(
        "OC-ext005-0019",
        "MAE: mean absolute error, linear penalty, outlier-robust, target units",
        "Semantic Duplicate",
        "Both vaults define MAE with the same formula and the same "
        "characterizations: linear penalty, robustness to outliers, and "
        "interpretability in the target's units. Master-ai: 'Linear "
        "penalty. More robust to outliers. Easier to interpret (average "
        "error is $5)'; the course: 'the average absolute deviation "
        "between predicted and true values. In the same units as the "
        "target' and 'MAE is robust to outliers — each error "
        "contributes linearly, not quadratically.' The course adds the "
        "constant-gradient training pitfall; the definition and "
        "characterizations are duplicated.",
        [
            R("KU-13bea960a13a53b2", "\\text{MAE} = \\frac{1}{N} \\sum_i |y_i - \\hat{y}_i|"),
            R("KU-9ea1f8cd406e6cf5", "Linear penalty. More robust to outliers. Easier to interpret (\"average error is $5\")."),
            R("KU-5daf9ad413f609ba", "$$\\text{MAE} = \\frac{1}{n} \\sum_{i=1}^n |y_i - \\hat{y}_i|$$"),
            R("KU-453b0300a44b48b8", "**What it measures:** the average absolute deviation between predicted and true values. In the same units as the target."),
            R("KU-7239a9f4fd170e18", "- When the data has outliers and you do not want them to dominate (MAE is robust to outliers — each error contributes linearly, not quadratically)."),
        ],
    )

    # ---- 0020 RMSE ----
    add(
        "OC-ext005-0020",
        "RMSE = sqrt(MSE), back in target units for interpretation",
        "Semantic Duplicate",
        "Both vaults define RMSE as the square root of MSE and give the "
        "same rationale: it restores the target's units, making it "
        "easier to interpret than MSE. Master-ai: 'Same units as the "
        "target. Easier to interpret than MSE.'; the course: 'the "
        "square root of MSE. Back in the target's units.' The course "
        "adds that RMSE is the standard reporting metric and keeps "
        "MSE's outlier sensitivity; the definition and units rationale "
        "are duplicated.",
        [
            R("KU-92be7bd3e8383bcb", "\\text{RMSE} = \\sqrt{\\text{MSE}}"),
            R("KU-d4715a1186fbc02a", "Same units as the target. Easier to interpret than MSE."),
            R("KU-f696f06c6dbcacd8", "$$\\text{RMSE} = \\sqrt{\\text{MSE}} = \\sqrt{\\frac{1}{n} \\sum_{i=1}^n (y_i - \\hat{y}_i)^2}$$"),
            R("KU-b123bc5404354ced", "**What it measures:** the square root of MSE. Back in the target's units."),
        ],
    )

    # ---- 0021 R^2 ----
    add(
        "OC-ext005-0021",
        "R^2: fraction of variance explained; 1 perfect, 0 = mean predictor, <0 worse",
        "Semantic Duplicate",
        "Both vaults give the same R^2 formula (1 minus the ratio of "
        "squared-error sum to the mean's squared-error sum), the same "
        "'variance explained' reading, and the same three-value "
        "interpretation (1 perfect; 0 no better than predicting the "
        "mean; <0 worse than the mean). Master-ai: 'Fraction of "
        "variance explained. 1 = perfect; 0 = as good as predicting "
        "the mean; <0 = worse than the mean.'; the course: 'the "
        "proportion of variance in y explained by the model' plus the "
        "same trichotomy as a list. The course adds the "
        "adding-features-inflates-R^2 pitfall and Adjusted R^2; the "
        "formula and interpretation are duplicated.",
        [
            R("KU-3bd8d7b2efca4ebd", "R^2 = 1 - \\frac{\\sum (y_i - \\hat{y}_i)^2}{\\sum (y_i - \\bar{y})^2}"),
            R("KU-4f8538efd88fb3a0", "Fraction of variance explained. 1 = perfect; 0 = as good as predicting the mean; <0 = worse than the mean."),
            R("KU-cf5158d9c13c828e", "$$R^2 = 1 - \\frac{\\sum_i (y_i - \\hat{y}_i)^2}{\\sum_i (y_i - \\bar{y})^2} = 1 - \\frac{\\text{SS}_{res}}{\\text{SS}_{tot}}$$"),
            R("KU-038b376ba371bc8c", "**What it measures:** the proportion of variance in $y$ explained by the model. Compares the model's MSE to the MSE of a trivial \"always predict the mean\" model."),
            R("KU-b4a00392646a0abb", "- $R^2 = 0$: the model is no better than predicting the mean."),
        ],
    )

    # ---- 0022 Huber (unnamed in master-ai) ----
    add(
        "OC-ext005-0022",
        "Huber loss: MSE-like smoothness near zero, MAE-like robustness for large errors",
        "Semantic Duplicate",
        "Description-level identity: master-ai's section heading is "
        "'### Huber Loss' (source line 111) and the KU excerpt under it "
        "characterizes the loss without repeating the name ('Smooth "
        "combination of MSE (small errors) and MAE (large errors). Robust "
        "to outliers while remaining differentiable.'), while the course "
        "names it inside the excerpt and gives the same characterization "
        "('train with Huber loss (smooth like MSE near zero, robust "
        "like MAE for large errors)'). Both carry the same knowledge: "
        "the loss interpolates between MSE for small errors and MAE "
        "for large errors, gaining outlier robustness. Non-shared "
        "framing: master-ai adds differentiability and the "
        "deep-learning-loss context; the course adds the "
        "train-with-Huber/evaluate-with-MAE-or-RMSE practice pattern. "
        "Classified as a judgment with byte-exact quotes per the "
        "EXT-003 precedent; because the name lives in a heading on the "
        "master-ai side, term matching could not pair these units — the "
        "pairing rests on the description identity. Repair applied from "
        "EXT-005-REVIEW R2: the initial rationale wrongly said master-ai "
        "describes the loss 'WITHOUT naming it' — the file-level heading "
        "does carry the name (headings are outside KU excerpts by "
        "construction).",
        [
            R("KU-463dd3956a6a8636", "Smooth combination of MSE (small errors) and MAE (large errors). Robust to outliers while remaining differentiable. Often used in regression losses for deep learning."),
            R("KU-4e48e5d89286d256", "A common pattern: train with **Huber loss** (smooth like MSE near zero, robust like MAE for large errors), evaluate with MAE or RMSE. Huber is:"),
        ],
    )

    # ---- 0023 mAP ranking sense ----
    add(
        "OC-ext005-0023",
        "MAP/mAP as the retrieval-ranking metric for search and recommendation",
        "Semantic Duplicate",
        "Both vaults use mAP (Mean Average Precision) as the go-to "
        "ranking metric for search / recommendation / retrieval. "
        "Master-ai defines it in the ranking-metrics list ('MAP (Mean "
        "Average Precision): average precision across all relevant "
        "items', under 'For search / recommendation / retrieval:'); the "
        "course's metric-selection decision table recommends "
        "'Precision@K or mAP' for Information Retrieval with 'Search "
        "engine, recommendation system' as examples. Same metric, same "
        "application domain, same role in the respective metric "
        "catalogs. (See OC-ext005-0024 for the separate "
        "computer-vision sense of the same name.)",
        [
            R("KU-8c87653ab9077009", "- **MAP** (Mean Average Precision): average precision across all relevant items."),
            R("KU-e2aca0fe0f77fa61", "| **Information Retrieval** | Imbalanced (few relevant docs) | FP > FN (showing irrelevant docs is annoying) | **Precision@K** or **mAP** | Varies by rank | Search engine, recommendation system |"),
        ],
    )

    # ---- 0024 mAP CV sense (name collision) ----
    add(
        "OC-ext005-0024",
        "Name collision: CV detection mAP@IoU vs ranking MAP (both 'mean average precision')",
        "Partial Overlap",
        "The two vaults use the name 'mAP'/'MAP' (mean average "
        "precision) for two different metrics that share the "
        "average-precision foundation but differ in aggregation unit "
        "and matching criterion. Master-ai's MAP is the IR/ranking "
        "metric: 'average precision across all relevant items' "
        "(per-query, rank-based matching). The course's mAP is the "
        "object-detection metric: 'the mean across classes of the area "
        "under the precision-recall curve, after IoU-based matching', "
        "computed at IoU thresholds (mAP@0.5, mAP@0.5:0.95, the COCO "
        "standards). Overlap: both are means of average precisions "
        "over PR-curve quantities. Non-overlap: aggregation domain "
        "(queries vs classes), matching criterion (rank position vs "
        "IoU threshold), and application (retrieval vs detection). "
        "Partial overlap, with a terminology hazard: synthesis must "
        "disambiguate the two senses explicitly (opened as finding "
        "F-0008). Surfaced by CAP-013 because case-insensitive "
        "word-boundary matching deliberately lets the shared name "
        "collide.",
        [
            R("KU-8c87653ab9077009", "- **MAP** (Mean Average Precision): average precision across all relevant items."),
            R("KU-ffcda10a1fc88106", "- **mAP@0.5**: IoU threshold = 0.5 (the COCO/PASCAL VOC standard for years)."),
            R("KU-d37c7a6acd695389", "2. **mAP** is the mean across classes of the area under the precision-recall curve, after IoU-based matching. mAP@0.5:0.95 is the modern COCO standard."),
        ],
    )

    # ---- 0025 calibration vs AUC-ranking-only ----
    add(
        "OC-ext005-0025",
        "Probability calibration: master-ai's treatment vs course's AUC limitation note",
        "Complementary Content",
        "The course states the need without the treatment; master-ai "
        "supplies the treatment without the connection. The course's "
        "ROC-AUC limitations list notes 'You need calibrated "
        "probabilities (e.g., for cost-sensitive decision-making), "
        "because AUC only measures ranking, not the absolute values of "
        "the predicted probabilities' — it contains no calibration "
        "definition or remedy. Master-ai's calibration section supplies "
        "exactly what is missing: the definition ('A model is "
        "calibrated if predicted probabilities match empirical "
        "frequencies'), the reliability diagram, and three remedies "
        "(temperature scaling, Platt scaling, isotonic regression) — "
        "but never links them to the AUC limitation. Neither side "
        "subsumes the other; joined they form one complete argument "
        "(why AUC is not enough + what calibration is + how to fix "
        "it). Complementary content rather than partial overlap, per "
        "the EXT-004 RF-formula/variance-analysis precedent.",
        [
            R("KU-698547ee1346e938", "A model is **calibrated** if predicted probabilities match empirical frequencies. If the model says \"80% chance of spam\" 100 times, about 80 should actually be spam."),
            R("KU-732c2b897c6af276", "Bin predictions by predicted probability; plot predicted vs. empirical frequency. A calibrated model's curve lies on the diagonal."),
            R("KU-fa465ec1ea260b5e", "- **Temperature scaling**: divide logits by a learned scalar $T$. Cheap, effective."),
            R("KU-d33fb766d530f483", "2. **You need calibrated probabilities** (e.g., for cost-sensitive decision-making), because AUC only measures ranking, not the absolute values of the predicted probabilities."),
        ],
    )

    # ---- 0026 metric choice = business decision ----
    add(
        "OC-ext005-0026",
        "Metric/threshold selection is a business decision driven by error costs",
        "Semantic Duplicate",
        "Both vaults elevate metric choice to a business decision "
        "driven by the relative costs of error types, to be made "
        "before/independently of modeling. Master-ai: 'Pick the metric "
        "before the model. If you can't articulate what good looks "
        "like in business terms, you're not ready to train.' The "
        "course: 'Choosing the right metric is a decision that should "
        "be driven by the business context and the relative costs of "
        "different types of errors, not by convention or convenience' "
        "and 'The threshold is a business decision, not a machine "
        "learning decision, and it should be made in consultation with "
        "domain experts who understand the costs of different error "
        "types.' Same principle stated in both vaults; the course adds "
        "the consultation-with-domain-experts recommendation.",
        [
            R("KU-d68fa9657e07ba54", "- **Pick the metric before the model.** If you can't articulate what \"good\" looks like in business terms, you're not ready to train."),
            R("KU-4ea9e8aa40b3d5df", "The threshold is a business decision, not a machine learning decision, and it should be made in consultation with domain experts who understand the costs of different error types."),
            R("KU-822c6b3db2db74d3", "Choosing the right metric is a decision that should be driven by the business context and the relative costs of different types of errors, not by convention or convenience."),
        ],
    )

    # ---- 0027 cross-validation for small data ----
    add(
        "OC-ext005-0027",
        "Cross-validation as the small-data alternative to a single split",
        "Partial Overlap",
        "Shared claim: when data is too scarce to spend on a single "
        "held-out split (or to guard against a lucky split), use "
        "cross-validation. Master-ai states it as one best-practices "
        "bullet ('Always evaluate on held-out data; use "
        "cross-validation for small data'); the course file 01 gives "
        "the same rationale ('When you don't have enough data to "
        "waste 30% on testing, or to ensure the model isn't just "
        "lucky with a specific split, we use Cross-Validation') and "
        "then dedicates a full section to the mechanics (LOOCV, K-fold "
        "procedure, stratified K-fold) that master-ai lacks entirely. "
        "Master-ai separately mentions nested CV in its pitfalls list "
        "(hyperparameter-reporting context), which the course does "
        "not cover. Partial overlap: shared rationale, asymmetric "
        "mechanical depth.",
        [
            R("KU-d68fa9657e07ba54", "- **Always evaluate on held-out data**; use cross-validation for small data."),
            R("KU-90e7972358a47007", "When you don't have enough data to \"waste\" 30% on testing, or to ensure the model isn't just lucky with a specific split, we use Cross-Validation."),
            R("KU-0e7eb985e372258f", "*   **Result:** The final score is the **average** of the scores from all $K$ iterations."),
            R("KU-0e7eb985e372258f", "*   **Stratified K-Fold:** Ensures that each fold has the same percentage of samples for each class as the complete set (prevents one fold from having only \"Cats\" and no \"Dogs\")."),
            R("KU-1b3ccda7b8f85076", "*   **Method:** Train on all data points except **one**. Test on that single left-out point. Repeat this process $N$ times (for every single data point)."),
        ],
    )

    # ---- 0028 sklearn.metrics tooling ----
    add(
        "OC-ext005-0028",
        "sklearn.metrics as the standard tool for computing evaluation metrics",
        "Partial Overlap",
        "Both vaults demonstrate computing the shared metric set with "
        "sklearn.metrics. Master-ai's code block imports "
        "accuracy_score, precision_score, recall_score, f1_score, "
        "roc_auc_score, log_loss, mean_squared_error and r2_score and "
        "runs them on a 5-example binary classification; the course's "
        "pipeline section states the workflow ('compute all the "
        "metrics discussed in this section using PyTorch for model "
        "inference and scikit-learn for metric computation') and its "
        "code imports the same metric functions inside a full "
        "evaluation pipeline with visualization. Shared: the "
        "sklearn.metrics tooling choice and the core metric functions. "
        "Non-shared: master-ai's minimal snippet includes log_loss and "
        "regression metrics; the course adds PyTorch inference "
        "integration, ConfusionMatrixDisplay/ROC plotting and per-"
        "function commentary. Partial overlap on the tooling claim.",
        [
            R("KU-b90d64a2fd5ff6d7", "from sklearn.metrics import (\n    accuracy_score, precision_score, recall_score, f1_score,"),
            R("KU-f0d62f32139a46aa", "The following code demonstrates how to compute all the metrics discussed in this section using PyTorch for model inference and scikit-learn for metric computation. This is the standard workflow for evaluating classification models in practice."),
            R("KU-201647def24836cf", "from sklearn.metrics import ("),
            R("KU-b2c649622c91636c", "# VISUALIZATION: CONFUSION MATRIX AND ROC CURVE"),
        ],
    )

    # ---- 0029 held-out / locked test set discipline ----
    add(
        "OC-ext005-0029",
        "Held-out test-data discipline (locked test set vs leakage pitfalls)",
        "Partial Overlap",
        "Both vaults enforce test-data discipline: final evaluation must "
        "use data untouched during training and tuning. The course file 01 "
        "defines the protocol explicitly (three-way split; the test set is "
        "'a completely locked dataset used only once at the very end to "
        "evaluate the final performance'); master-ai states the discipline "
        "as a best practice ('Always evaluate on held-out data') and, in "
        "its pitfalls list, names the failure modes ('Test set leakage — "
        "feature engineering on the whole dataset, time-based splits "
        "ignored'). Shared claim: never let training/tuning touch the "
        "final-evaluation data. Non-shared: the course's explicit "
        "70/15/15 percentages and the validation-set role; master-ai's "
        "leakage taxonomy (whole-dataset feature engineering, ignored "
        "time-based splits). Partial overlap. Added during EXT-005 review "
        "repairs (coverage gap CG-1 identified by EXT-005-REVIEW: "
        "master-ai's leakage line and the course's split protocol "
        "participated in no other record).",
        [
            R("KU-d68fa9657e07ba54", "- **Always evaluate on held-out data**; use cross-validation for small data."),
            R("KU-0496ce782a36efe9", "- **Test set leakage** — feature engineering on the whole dataset, time-based splits ignored."),
            R("KU-7b9487c801c5477f", "3.  **Test Set (~15%):** A completely \"locked\" dataset used only **once** at the very end to evaluate the final performance."),
        ],
    )

    # ------------------------------------------------------------------
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        for rec in classifications:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    # file-level validation (schema + cross-checks) before exit 0
    report = registry.validate_classification_file(OUT, CLS_SCHEMA)
    if not report["valid"]:
        print("VALIDATION FAILED:")
        for err in report["errors"]:
            print(" ", err)
        return 1
    print(f"wrote {OUT} with {len(classifications)} classifications; valid")
    for rec in classifications:
        print(
            f"  {rec['classification_id']} {rec['overlap_type']:30s} "
            f"ku_ids={len(rec['ku_ids'])} evidence={len(rec['evidence'])} "
            f"| {rec['topic']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
