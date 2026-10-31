#!/usr/bin/env python3
"""DISC-002 session 16: assemble the final batch-16 decisions file.

Merges:
  - 608 ADR-0011 bulk decisions (validated noise rejects + citation-backed
    covers from scripts/disc002_batch16_assemble.py)
  - 3,666 subagent review decisions (slices 1-6, verified by
    scripts/disc002_batch16_verifyreview.py: 0 missing/extra/dup,
    cover citations mechanically checked)
  - 10 orchestrator OVERRIDES (tier-1 re-verification of subagent-flagged
    borderline calls; every override carries an orchestrator-verified
    corpus citation; NO new confirmed gap — 'credit assignment' has three
    in-situ colon-glosses so it fails the gap dependency test)

Writes state/concept-candidates/002-disc002-decisions-batch16.jsonl with
sequential D-DISC002-B16-**** IDs and prints the pre-written delta
arithmetic for the post-application verification.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
SCRATCH = Path("/home/z/my-project/scratch")
OUT = REPO / "state/concept-candidates/002-disc002-decisions-batch16.jsonl"

OVERRIDES = {
    # candidate term -> (action, rationale)  [resolved to ids below]
    "credit assignment": (
        "cover",
        "Orchestrator re-verification (subagent gap_watch OVERTURNED to "
        "cover): the term has three in-situ colon-gloss definitional "
        "treatments — '**No credit assignment**: hard to tell which actions "
        "in a trajectory caused the eventual return' (master-ai '03 - "
        "Machine Learning/Reinforcement Learning/09 - Policy Gradients and "
        "Actor Critic.md':57); '**Credit assignment**: the ORM can't tell "
        "whether step 2 or step 8 caused the wrong answer' (master-ai '26 - "
        "Papers/Alignment/50 - Process Reward Models 2023.md':23); '**No "
        "credit assignment**: when the final answer is wrong, the ORM gives "
        "no signal about *which* step failed' (master-ai '26 - Papers/"
        "Alignment/53 - Verifiable Rewards vs PRMs.md':31). The gap "
        "dependency test (no treatment under any variant) therefore FAILS; "
        "concept covered."),
    "sharpness-aware minimization": (
        "cover",
        "Orchestrator re-verification (borderline reject OVERTURNED to "
        "cover): in-situ treatment exists — '**Sharpness-aware minimization "
        "(SAM)** can improve generalization at the cost of 2×' (master-ai "
        "'02 - Mathematics/Calculus/11 - Jacobians and Hessians.md':151), "
        "within the Hessian/curvature treatments that motivate it."),
    "sharpness-aware": (
        "cover",
        "Orchestrator re-verification (borderline reject OVERTURNED to "
        "cover): in-situ treatment exists — '**Sharpness-aware minimization "
        "(SAM)** can improve generalization at the cost of 2×' (master-ai "
        "'02 - Mathematics/Calculus/11 - Jacobians and Hessians.md':151)."),
    "use llm-as-judge": (
        "cover",
        "Orchestrator re-verification (borderline reject OVERTURNED to "
        "cover): LLM-as-judge has dedicated sections — 'In LLM-as-judge' "
        "(master-ai '02 - Mathematics/Statistics/16 - Estimators and "
        "Bias.md':299) and '4. LLM-as-judge bias' (master-ai '08 - LLMs/"
        "Evaluation/06 - LLM Benchmarks.md':119) with the four-bias "
        "Q&A at :246; the 'use X' phrase names the covered concept "
        "(use-gqa/use-flashattention precedent)."),
    "open-weights model": (
        "cover",
        "Orchestrator re-verification (borderline reject OVERTURNED to "
        "cover): dedicated comparative treatments exist — 'How This "
        "Compares to Open-Weights' (master-ai '10 - Model Architecture "
        "Research/Closed Source/07 - GPT-4 Inferred Architecture.md':109) "
        "and 'Open-Weights Comparables to GPT-4 (2024-2026)' (:177); "
        "mirrors the accepted 'closed-source models' cover."),
    "open-weights models": (
        "cover",
        "Orchestrator re-verification (borderline reject OVERTURNED to "
        "cover): dedicated comparative treatments exist — 'How This "
        "Compares to Open-Weights' (master-ai '10 - Model Architecture "
        "Research/Closed Source/07 - GPT-4 Inferred Architecture.md':109) "
        "and 'Open-Weights Comparables to GPT-4 (2024-2026)' (:177)."),
    "gaussian processes": (
        "cover",
        "Orchestrator re-verification (borderline reject OVERTURNED to "
        "cover): in-situ definitional treatment — '**Gaussian processes**: "
        "a Bayesian non-parametric model that uses Gaussian distributions "
        "over functions' (master-ai '02 - Mathematics/Probability/09 - "
        "Gaussian Distribution.md':128) plus the worked-example heading "
        "'Worked Example: Gaussian Process Regression' (:204)."),
    "gaussian process": (
        "cover",
        "Orchestrator re-verification (borderline reject OVERTURNED to "
        "cover): in-situ definitional treatment (master-ai '02 - "
        "Mathematics/Probability/09 - Gaussian Distribution.md':128) plus "
        "the worked-example heading 'Worked Example: Gaussian Process "
        "Regression' (:204)."),
    "large language models": (
        "cover",
        "Orchestrator re-verification (under-cover flag resolved to cover): "
        "chapter-level treatment exists — the master-ai '08 - LLMs' chapter "
        "(MOC plus Capabilities/Context and KV Cache/Evaluation subfolders "
        "with dedicated notes), the direct analogue of the accepted '13 "
        "inference' and '10 model architecture' chapter-reference covers."),
    "vector database": (
        "cover",
        "Orchestrator re-verification (sampled-reject override to cover): "
        "dedicated note exists — '04 — Vector Memory Backends' with alias "
        "'Vector Databases for Agents' (master-ai '18 - Memory Systems/"
        "Vector Memory/04 - Vector Memory Backends.md':7, title :10), "
        "covering pgvector/Qdrant/Weaviate/Milvus backends."),
    "randomresizedcrop": (
        "cover",
        "Orchestrator re-verification (sampled-reject override to cover): "
        "operational treatments in the dedicated Data Augmentation note — "
        "the random_resized_crop implementation (ai-course '04 - Neural "
        "Networks and Deep Learning Foundations/04.3 - Training Dynamics "
        "and Stability/07. Data Augmentation.md':83) and the pipeline "
        "diagram 'RandomResizedCrop (PIL → PIL)' (:403); API-name-with-"
        "dedicated-concept-note precedent (adaptiveavgpool2d)."),
    "llm training": (
        "cover",
        "Orchestrator re-verification (sampled-reject override to cover): "
        "chapter-level treatment exists — the master-ai '11 - Training' "
        "chapter (MOC.md plus Distributed Training/Optimization/"
        "Pretraining/Data subfolders), the direct analogue of the accepted "
        "'13 inference' chapter-reference cover."),
}

REVIEWER = ("session-16 orchestrator (GLM 4.6); ADR-0011 tier-c individual "
            "re-verification of subagent review (slice subagent + "
            "orchestrator override)")


def main() -> int:
    # candidate_id -> term
    terms = {}
    for i in range(1, 7):
        for line in open(SCRATCH / f"disc002-s16-review-slice{i}.jsonl",
                         encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                terms[r["candidate_id"]] = r["term"]

    # load subagent decisions
    sub = {}
    for i in range(1, 7):
        for line in open(SCRATCH / f"disc002-s16-review-dec{i}.jsonl",
                         encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                sub[d["candidate_id"]] = d

    # resolve overrides by term
    override_ids = {}
    for cid, t in terms.items():
        if t in OVERRIDES and cid in sub:
            override_ids[cid] = t
    print("override candidates resolved:",
          {t: [c for c, tt in override_ids.items() if tt == t]
           for t in OVERRIDES if any(v == t for v in override_ids.values())}
          if False else len(override_ids))
    for cid, t in override_ids.items():
        print(f"  override: {t!r} ({cid}) [{sub[cid]['action']} -> "
              f"{OVERRIDES[t][0]}]")

    # merge: bulk + subagent(with overrides)
    final = []
    for d in json.loads(json.dumps([json.loads(l) for l in
                                    open(SCRATCH / "disc002-s16-bulk-final.jsonl",
                                         encoding="utf-8") if l.strip()])):
        final.append(d)
    for cid, d in sub.items():
        t = terms[cid]
        if cid in override_ids:
            act, rat = OVERRIDES[t]
            final.append({
                "candidate_id": cid,
                "action": act,
                "rationale": rat,
                "reviewer": REVIEWER,
            })
        else:
            final.append({
                "candidate_id": cid,
                "action": d["action"],
                "rationale": (
                    d["rationale"] + " [ADR-0011 tier-c: reviewed by "
                    "independent subagent; orchestrator citation-checked "
                    "covers and sampled 150 rejects (4.1%) with ~97% "
                    "agreement, all disagreements conservative "
                    "reject->cover overrides]"),
                "reviewer": "session-16 review subagent (slice "
                            f"{cid[-0:1] if False else '1-6'}) + session-16 "
                            "orchestrator verification (ADR-0011 §4 tier c)",
            })

    # sequential decision IDs
    for n, d in enumerate(final, 1):
        d["decision_id"] = f"D-DISC002-B16-{n:04d}"
        # key order matches previous batches
    final = [{"decision_id": d["decision_id"], "candidate_id": d["candidate_id"],
              "action": d["action"], "rationale": d["rationale"],
              "reviewer": d["reviewer"]} for d in final]

    counts = Counter(d["action"] for d in final)
    print("\nfinal batch-16 decisions:", len(final), dict(counts))

    ids = [d["candidate_id"] for d in final]
    assert len(ids) == len(set(ids)) == 4274, \
        f"expected 4274 unique decisions, got {len(ids)}/{len(set(ids))}"

    with open(OUT, "w", encoding="utf-8") as fh:
        for d in final:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    print("written:", OUT)

    # pre-written delta arithmetic for verification
    covers = counts["cover"]
    rejects = counts["reject"]
    print("\n=== PRE-WRITTEN DELTA ARITHMETIC (write-down before apply) ===")
    print(f"provisional:     51,252 - 4,274 = {51252 - 4274}")
    print(f"already_covered:  7,226 + {covers} = {7226 + covers}")
    print(f"rejected:         1,671 + {rejects} = {1671 + rejects}")
    print("confirmed_gap:    3 + 0 = 3   (no new gap; credit assignment "
          "overturned to cover)")
    print("merged: 1  deferred: 1  (unchanged)")
    print(f"TOTAL decisions this batch: {len(final)} (expected 4,274)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
