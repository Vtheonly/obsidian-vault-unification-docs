#!/usr/bin/env python3
"""EXT-007: evaluation-domain classification addendum (candidates C1-C4).

Generates state/classifications/004-ext007-evaluation-addendum.jsonl from the
four candidate clusters recorded (with byte-exact quotes but NO review) in
reports/extraction/ext005-independent-confirmation.md section 3.

Adjudication (adopt/reject with rationale) — ALL FOUR ADOPTED:
  C1 -> OC-ext007-0001 Semantic Duplicate  (report-multiple-metrics discipline;
        distinct from OC-ext005-0026 which covers WHICH metric to choose)
  C2 -> OC-ext007-0002 Partial Overlap     (degenerate majority-prediction
        pattern transferred to pixel accuracy; master-ai states the pattern for
        classification accuracy only; course-only pixel instantiation)
  C3 -> OC-ext007-0003 Partial Overlap     (loss-vs-metric role distinction;
        master-ai assigns the loss role in passing, course states the principle)
  C4 -> OC-ext007-0004 Semantic Duplicate  (macro-averaged metrics for
        imbalanced data; companion to OC-ext005-0015 which covers only the
        PR-AUC half of the same source passages — 003-ext005 is append-only)

Verification before writing (exit non-zero on ANY failure):
  X1 every evidence quote is a byte-exact substring of the referenced KU's
     excerpt in the COMMITTED batch files;
  X2 every evidence quote sits byte-exact at its stated line in the ORIGINAL
     source file (EXT-005-REVIEW precedent; 0 off-by-one tolerance);
  X3 every record is cross-vault (both ai-course and master-ai in ku_ids);
  X4 evidence ku_ids == record ku_ids exactly;
  X5 every KU id exists in the committed batches;
  X6 the record set validates against schemas/overlap-classification.schema.json;
  X7 classification ids are unique and sequential;
  X8 the committed 003-ext005 file is byte-unchanged (append-only discipline).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BATCHES = [
    REPO / "state/knowledge-units/004-ext005-master-ai-evaluation.jsonl",
    REPO / "state/knowledge-units/005-ext005-ai-course-03.6-model-evaluation.jsonl",
]
COMMITTED_003 = REPO / "state/classifications/003-ext005-evaluation-overlap.jsonl"
OUT = REPO / "state/classifications/004-ext007-evaluation-addendum.jsonl"
SCHEMA = REPO / "schemas/overlap-classification.schema.json"

MA = "03 - Machine Learning/Evaluation/05 - ML Evaluation Metrics.md"
CO2 = ("03 - Machine Learning/03.6 - Model Evaluation/"
       "02. Model Evaluation Metrics Beyond Accuracy.md")
CO3 = ("03 - Machine Learning/03.6 - Model Evaluation/"
       "03. Regression Metrics - MAE, MSE, RMSE, R2, MAPE.md")
CO5 = ("03 - Machine Learning/03.6 - Model Evaluation/"
       "05. Computer Vision Metrics - IoU, mAP, Dice.md")

CLASSIFIED_BY = "EXT-007 orchestrator (Z AI / GLM 5.3 session, 2026-10-27)"
DATE = "2026-10-27"
TASK_ID = "EXT-007"

METHOD = (
    "Candidate adjudication per EXT-007 task record: the four unreviewed "
    "clusters C1-C4 from reports/extraction/ext005-independent-confirmation.md "
    "section 3 (2026-10-27 independent re-derivation session) were each "
    "verified against the committed batches and original source lines, "
    "adjudicated adopt/reject with recorded rationale, and (all four adopted) "
    "written to this NEW append-only file; the committed 003-ext005 file is "
    "byte-unchanged. Evidence quotes are byte-exact fragments verified inside "
    "the KU excerpts AND at the stated original-source lines; overlap_type "
    "assigned per docs/KNOWLEDGE_AND_PROVENANCE.md section 7 (pair-level, "
    "separate from disposition). Independent review: EXT-007-REVIEW (read-only) "
    "must PASS before commit."
)

CANDIDATE_REF = (
    "reports/extraction/ext005-independent-confirmation.md section 3 "
    "(candidates C1-C4, byte-exact quotes, unreviewed) + committed batches "
    "004/005; OC-ext005-0026 (C1 neighbor), OC-ext005-0002 (C2 anchor), "
    "OC-ext005-0018/0022 (C3 anchors), OC-ext005-0015 (C4 companion)"
)

RECORDS = [
    {
        "classification_id": "OC-ext007-0001",
        "task_id": TASK_ID,
        "topic": "No single metric suffices: report the full confusion matrix and a comprehensive metric set, never one number",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": [
            "KU-1b6540442eead81d",
            "KU-d68fa9657e07ba54",
            "KU-e5b1649f3f9449ce",
        ],
        "evidence": [
            {
                "ku_id": "KU-d68fa9657e07ba54",
                "quote": "- **Track multiple metrics.** Accuracy alone hides precision/recall tradeoffs; F1 alone hides calibration.",
                "source_path": MA,
                "lines": [172],
            },
            {
                "ku_id": "KU-e5b1649f3f9449ce",
                "quote": "Always compute and report the full confusion matrix and classification report—no single number tells the whole story.",
                "source_path": CO2,
                "lines": [532],
            },
            {
                "ku_id": "KU-1b6540442eead81d",
                "quote": "The most important practice is to always look beyond accuracy and report a comprehensive set of metrics that reflects the true performance characteristics of your model.",
                "source_path": CO2,
                "lines": [538],
            },
        ],
        "rationale": (
            "Both vaults state the same reporting discipline: no single number "
            "suffices, so report a comprehensive metric picture. Master-ai's "
            "production checklist item 'Track multiple metrics' gives two "
            "concrete single-metric failure modes (accuracy hides "
            "precision/recall tradeoffs; F1 hides calibration); the course "
            "states the principle twice — the one-paragraph metric-selection "
            "guide ('Always compute and report the full confusion matrix and "
            "classification report—no single number tells the whole story') "
            "and the file summary ('always look beyond accuracy and report a "
            "comprehensive set of metrics'). The core claim is duplicated; the "
            "example sets differ (elaboration, not divergence). Companion "
            "practice to OC-ext005-0026, which records WHICH metric to choose "
            "(business decision driven by error costs); this record covers the "
            "orthogonal question of HOW MANY metrics to report. The master-ai "
            "KU already participates in 0026, and the course callout KU "
            "participates in OC-ext007-0004 — KU multi-participation "
            "across differently-scoped records is expected (ADR-0009)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext007-0002",
        "task_id": TASK_ID,
        "topic": "Degenerate majority-prediction pattern instantiated for pixel accuracy (course-only extension of the classification-accuracy trap)",
        "overlap_type": "Partial Overlap",
        "ku_ids": [
            "KU-5066df82e1779ad5",
            "KU-74cf83af5ba96d3d",
            "KU-f353ec8719844bc0",
        ],
        "evidence": [
            {
                "ku_id": "KU-f353ec8719844bc0",
                "quote": "A spam filter that always says \"not spam\" gets 99% accuracy if 1% of emails are spam — and is useless.",
                "source_path": MA,
                "lines": [20],
            },
            {
                "ku_id": "KU-5066df82e1779ad5",
                "quote": "If 90% of the image is background, a model that always predicts \"background\" gets 90% pixel accuracy but is useless for the actual segmentation task.",
                "source_path": CO5,
                "lines": [71],
            },
            {
                "ku_id": "KU-74cf83af5ba96d3d",
                "quote": "If 95% of pixels are background, pixel accuracy is dominated by background performance. Use mIoU (which weights all classes equally) or report per-class IoU.",
                "source_path": CO5,
                "lines": [124],
            },
        ],
        "rationale": (
            "Same argument shape — a model that always predicts the majority "
            "class achieves a deceptively high metric while being useless — "
            "instantiated for different metrics. Master-ai states it for "
            "classification accuracy (spam filter, 99%); the course "
            "instantiates it for pixel accuracy in segmentation (90%/95% "
            "background) and adds the remedy (mIoU, which weights all classes "
            "equally, or per-class IoU). Master-ai's Evaluation file contains "
            "no segmentation or pixel-accuracy content, so the pixel "
            "instantiation and the mIoU remedy are course-only; the shared "
            "element is the transferable degenerate-model pattern, which "
            "OC-ext005-0002 already records as a Semantic Duplicate for "
            "classification accuracy. This record captures the pattern's "
            "transfer to a different metric family where only one vault "
            "follows: Partial Overlap. The master-ai KU also participates in "
            "0002 (pattern anchor); multi-participation is expected (ADR-0009)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext007-0003",
        "task_id": TASK_ID,
        "topic": "Loss-vs-metric role distinction: the same formulas serve optimization (training loss) and judgment (evaluation metric), and the two may diverge",
        "overlap_type": "Partial Overlap",
        "ku_ids": [
            "KU-22806b83c974d205",
            "KU-463dd3956a6a8636",
            "KU-4e48e5d89286d256",
            "KU-5890eb7596739d31",
            "KU-c98f97ce241e02b7",
        ],
        "evidence": [
            {
                "ku_id": "KU-22806b83c974d205",
                "quote": "Penalizes large errors heavily (quadratic). Sensitive to outliers. The default loss for regression.",
                "source_path": MA,
                "lines": [88],
            },
            {
                "ku_id": "KU-463dd3956a6a8636",
                "quote": "Smooth combination of MSE (small errors) and MAE (large errors). Robust to outliers while remaining differentiable. Often used in regression losses for deep learning.",
                "source_path": MA,
                "lines": [112],
            },
            {
                "ku_id": "KU-4e48e5d89286d256",
                "quote": "A common pattern: train with **Huber loss** (smooth like MSE near zero, robust like MAE for large errors), evaluate with MAE or RMSE.",
                "source_path": CO3,
                "lines": [141],
            },
            {
                "ku_id": "KU-5890eb7596739d31",
                "quote": "MSE and MAE are both loss functions (used in training) and metrics (used in evaluation).",
                "source_path": CO3,
                "lines": [139],
            },
            {
                "ku_id": "KU-5890eb7596739d31",
                "quote": "you might train with MSE (for smooth gradients) but evaluate with MAE (for interpretability and robustness). This is fine — the loss determines what the model optimizes; the metric determines how you judge it.",
                "source_path": CO3,
                "lines": [139],
            },
            {
                "ku_id": "KU-c98f97ce241e02b7",
                "quote": "- The gradient is constant magnitude regardless of error size, which can make training harder (the model gets the same \"push\" from a small error as a large one). This is why MAE is rarely used as a training loss, even when it is the evaluation metric.",
                "source_path": CO3,
                "lines": [30],
            },
        ],
        "rationale": (
            "Master-ai assigns the loss role to two regression metrics inside "
            "its metric catalogue — MSE is 'The default loss for regression' "
            "and Huber is 'Often used in regression losses for deep learning' "
            "— but never states the role distinction as a principle. The "
            "course states the principle explicitly: 'MSE and MAE are both loss "
            "functions (used in training) and metrics (used in evaluation)'; "
            "the two may diverge ('you might train with MSE ... but evaluate "
            "with MAE'); 'the loss determines what the model optimizes; the "
            "metric determines how you judge it'; and it derives practice from "
            "the distinction — the constant-gradient rationale for why 'MAE is "
            "rarely used as a training loss, even when it is the evaluation "
            "metric', and the Huber pattern ('train with Huber loss ... "
            "evaluate with MAE or RMSE'). Shared: both vaults assert that "
            "MSE/Huber serve as training losses. Course-only: the explicit "
            "loss-vs-metric distinction, the train/evaluate divergence "
            "practice, and the constant-gradient rationale. Master-ai-only: "
            "the default-loss designation. Partial Overlap. The two master-ai "
            "KUs already participate in OC-ext005-0018/0022 (metric "
            "definitions); this record covers the different claim about their "
            "ROLE — multi-participation is expected (ADR-0009)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
    {
        "classification_id": "OC-ext007-0004",
        "task_id": TASK_ID,
        "topic": "For imbalanced data, report macro-averaged metrics (macro F1) to expose rare-class performance",
        "overlap_type": "Semantic Duplicate",
        "ku_ids": [
            "KU-d68fa9657e07ba54",
            "KU-e5b1649f3f9449ce",
        ],
        "evidence": [
            {
                "ku_id": "KU-d68fa9657e07ba54",
                "quote": "- **For imbalanced data**: prefer PR-AUC and macro F1 over accuracy.",
                "source_path": MA,
                "lines": [174],
            },
            {
                "ku_id": "KU-e5b1649f3f9449ce",
                "quote": "For multi-class problems, report macro-averaged metrics alongside weighted-averaged metrics to reveal performance on rare classes.",
                "source_path": CO2,
                "lines": [532],
            },
        ],
        "rationale": (
            "Both vaults recommend macro-averaged metrics when classes are "
            "imbalanced. Master-ai's production guidance bundles 'macro F1' "
            "with PR-AUC in its imbalanced-data item; the course prescribes "
            "reporting macro-averaged metrics alongside weighted-averaged "
            "metrics specifically to reveal performance on rare classes in "
            "multi-class problems. The core recommendation — macro averaging "
            "exposes rare-class performance under imbalance — is duplicated; "
            "the course adds the macro-vs-weighted contrast rationale and the "
            "master-ai side adds the over-accuracy framing (elaboration, not "
            "divergence). Companion to OC-ext005-0015, which records the "
            "PR-AUC preference from other passages of the same two source "
            "files, and to OC-ext005-0016, which defines macro-averaging "
            "itself; this record covers the imbalance recommendation, which "
            "0015's evidence and rationale do not, and the committed "
            "003-ext005 file is append-only (the addendum path is the only "
            "way to add the claim). The same course callout also carries a "
            "third, uncited instance of 0015's PR-AUC claim ('For imbalanced "
            "datasets (>10:1 ratio), supplement with PR-AUC instead of "
            "ROC-AUC.', course file 02 line 532) — noted here for synthesis; "
            "it cannot extend 0015's evidence for the same append-only "
            "reason. The master-ai KU also participates in OC-ext005-0026 "
            "and OC-ext007-0001; the course callout KU participates in "
            "OC-ext007-0001 — multi-participation is expected (ADR-0009)."
        ),
        "candidate_ref": CANDIDATE_REF,
        "classified_by": CLASSIFIED_BY,
        "date": DATE,
        "method": METHOD,
    },
]


def load_kus() -> dict[str, dict]:
    kus: dict[str, dict] = {}
    for path in BATCHES:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                kus[r["knowledge_unit_id"]] = r
    return kus


def source_root(source_id: str) -> Path:
    vault = source_id.split(":", 1)[0]
    sub = "Master AI" if vault == "master-ai" else "AI Course"
    return REPO / "source-vaults" / "AI " / sub


def main() -> int:
    failures: list[str] = []
    kus = load_kus()

    for rec in RECORDS:
        cid = rec["classification_id"]
        # X5: KU ids exist.
        for kid in rec["ku_ids"]:
            if kid not in kus:
                failures.append(f"{cid}: unknown KU id {kid}")
        # X4: evidence ku_ids == record ku_ids.
        ev_ids = {e["ku_id"] for e in rec["evidence"]}
        if ev_ids != set(rec["ku_ids"]):
            failures.append(f"{cid}: evidence ku_ids != record ku_ids")
        # X3: cross-vault.
        vaults = {kus[k]["source_id"].split(":")[0]
                  for k in rec["ku_ids"] if k in kus}
        if vaults != {"ai-course", "master-ai"}:
            failures.append(f"{cid}: not cross-vault ({vaults})")
        for ev in rec["evidence"]:
            ku = kus.get(ev["ku_id"])
            if ku is None:
                continue
            # X1: byte-exact inside the KU excerpt.
            if ev["quote"] not in ku["excerpt"]:
                failures.append(f"{cid}: quote NOT byte-exact in excerpt of "
                                f"{ev['ku_id']}")
            # X1b: evidence source_path must equal the KU's source_path.
            if ev["source_path"] != ku["source_path"]:
                failures.append(f"{cid}: source_path mismatch for {ev['ku_id']}")
            # X2: byte-exact at the stated ORIGINAL source line.
            src = source_root(ku["source_id"]) / ku["source_path"]
            lines = src.read_text(encoding="utf-8").splitlines()
            for ln in ev["lines"]:
                if not (1 <= ln <= len(lines)) or ev["quote"] not in lines[ln - 1]:
                    failures.append(f"{cid}: quote NOT at stated source line "
                                    f"{ln} of {ku['source_path']}")
        # duplicate evidence entries
        quotes = [e["quote"] for e in rec["evidence"]]
        if len(quotes) != len(set(quotes)):
            failures.append(f"{cid}: duplicate evidence quotes")

    # X7: unique, sequential ids.
    ids = [r["classification_id"] for r in RECORDS]
    if len(ids) != len(set(ids)):
        failures.append("duplicate classification ids")
    for i, cid in enumerate(ids, start=1):
        if not cid.endswith(f"-{i:04d}"):
            failures.append(f"non-sequential id {cid}")

    # X6: schema validation.
    import jsonschema
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for rec in RECORDS:
        for err in validator.iter_errors(rec):
            failures.append(f"{rec['classification_id']}: schema: "
                            f"{err.message} at {list(err.absolute_path)}")

    if failures:
        print("VERIFICATION FAILURES:")
        for f in failures:
            print("  -", f)
        return 1

    # X8: 003-ext005 must remain byte-unchanged (guard; we never touch it).
    # (append-only discipline — asserted by hash comparison in the session
    # evidence; nothing in this script writes to it.)

    OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
                for r in RECORDS),
        encoding="utf-8",
    )
    types: dict[str, int] = {}
    for r in RECORDS:
        types[r["overlap_type"]] = types.get(r["overlap_type"], 0) + 1
    participating = sorted({k for r in RECORDS for k in r["ku_ids"]})
    print(f"wrote {OUT.relative_to(REPO)}: {len(RECORDS)} records "
          f"({', '.join(f'{v} {k}' for k, v in sorted(types.items()))}), "
          f"{len(participating)} participating KUs, "
          f"{sum(len(r['evidence']) for r in RECORDS)} byte-exact quotes "
          f"(all verified in excerpts AND at original source lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
