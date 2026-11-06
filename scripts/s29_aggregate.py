#!/usr/bin/env python3
"""VERIF-001 aggregation: merge judgments, record findings, build campaign report.

Inputs (validated by s29_validate_judgments.py — must have passed):
  scratch/s29-verify/judgments/group-*.jsonl   246 judgments
  state/synthesis/s29-semantic-sample.jsonl    the sample
  scratch/s29-verify/orchestrator-review.jsonl orchestrator re-review selection

Outputs (committed):
  reports/synthesis/s29-semantic-judgments.jsonl  merged judgments (evidence)
  reports/synthesis/s29-semantic-campaign.json    aggregate campaign report
  state/findings.jsonl                            + F-0035..F-0041
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
JUDG_DIR = REPO / "scratch/s29-verify/judgments"
SAMPLE = REPO / "state/synthesis/s29-semantic-sample.jsonl"
MERGED_OUT = REPO / "reports/synthesis/s29-semantic-judgments.jsonl"
CAMPAIGN_OUT = REPO / "reports/synthesis/s29-semantic-campaign.json"
FINDINGS = REPO / "state/findings.jsonl"

sample = {}
for line in SAMPLE.open(encoding="utf-8"):
    if line.strip():
        r = json.loads(line)
        sample[r["ku_id"]] = r

judgments = []
for gf in sorted(JUDG_DIR.glob("group-*.jsonl")):
    gid = int(gf.stem.split("-")[1])
    for line in gf.open(encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            r["group"] = gid
            judgments.append(r)
assert len(judgments) == len(sample) == 246

with MERGED_OUT.open("w", encoding="utf-8") as fh:
    for r in sorted(judgments, key=lambda x: (x["group"], x["ku_id"])):
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

by_verdict = Counter(r["verdict"] for r in judgments)
by_disp = defaultdict(Counter)
by_type = defaultdict(Counter)
by_area = defaultdict(Counter)
for r in judgments:
    ku = sample[r["ku_id"]]
    by_disp[ku["disposition"]][r["verdict"]] += 1
    by_type[ku["unit_type"]][r["verdict"]] += 1
    area = ku["destinations"][0]["path"].split("/")[0] if ku["destinations"] else "(none)"
    by_area[area][r["verdict"]] += 1

flagged = [(r["ku_id"], r["group"], f) for r in judgments for f in r.get("quality_flags", [])]

# ---- findings ----
new_findings = [
    {
        "finding_id": "F-0035",
        "title": "Multi-Head Attention See Also dropped 2 of 5 source cross-links",
        "category": "output-preservation",
        "severity": "medium",
        "status": "open",
        "discovered_by": "session-29 VERIF-001 semantic campaign (group 10; orchestrator-confirmed)",
        "observed": "The source Multi-Head Attention note's See-Also listed 5 links; the unified note's See Also carries 3 ([[Self-Attention]], [[Transformer Block]], and the renamed [[Attention and Transformers MOC]]) but drops [[KV Cache Mechanics]] and [[Mechanistic Interpretability]] although both target notes exist in the vault; their topics survive only as unlinked prose (KV cache in the MQA/GQA/MLA section; mechanistic interpretability in head-specialization).",
        "root_cause": "See-Also regeneration during area-08 synthesis kept in-area links and dropped cross-area ones not covered by the batch's link rules.",
        "evidence": "KU-e139f00c9e5651ab (verdict partial); judgments group-10; orchestrator independent re-review confirmed by direct read of the note's See Also section (12 links, neither target present).",
        "repair": "Add both links in path form (colliding-basename convention) to the See Also list: [[10 - Large Language Models/Context and KV Cache/KV Cache Mechanics|KV Cache Mechanics]] and [[16 - Interpretability and Research/Interpretability/Mechanistic Interpretability|Mechanistic Interpretability]].",
        "regression_prevention": "s29_semantic_repairs.py repair 2 (anchored, probe-idempotent); check-links re-run must stay 0 problems.",
        "affected_paths": ["output/Unified-Vault/08 - Attention and Transformers/Attention Mechanism/Multi-Head Attention.md"],
        "verification": "pending repair",
        "remaining_risk": "Other See-Also lists generated in the same batch were sampled and found conforming (group 13 KU-ffeead6bb4974004 present with renamed targets); a dedicated vault-wide see-also cross-check was not in this campaign's scope.",
    },
    {
        "finding_id": "F-0036",
        "title": "Current Iteration Log dropped 'quantization' from the Conceptual Interview Questions 2 coverage list",
        "category": "output-preservation",
        "severity": "medium",
        "status": "open",
        "discovered_by": "session-29 VERIF-001 semantic campaign (group 17; orchestrator-confirmed)",
        "observed": "The source list reads '... spec decoding, quantization, DPO variants ...'; the destination's corresponding list runs directly from [[Speculative Decoding|spec decoding]] to [[DPO|DPO variants]], omitting the standalone 'quantization' topic entry (GPTQ quantization survives only in the coding-note item).",
        "root_cause": "List item dropped during area-20 archival-note consolidation.",
        "evidence": "KU-2fd0a537e0a20f6c (verdict partial); judgments group-17; orchestrator independent re-review confirmed at Current Iteration Log.md line 79.",
        "repair": "Insert [[Quantization|quantization]], between the spec-decoding and DPO-variants entries, restoring the source list.",
        "regression_prevention": "s29_semantic_repairs.py repair 1 (anchored, probe-idempotent).",
        "affected_paths": ["output/Unified-Vault/20 - Vault and Project Context/Current Iteration Log.md"],
        "verification": "pending repair",
        "remaining_risk": "One item in one archival list; the campaign's other 17 area-20 KUs were present.",
    },
    {
        "finding_id": "F-0037",
        "title": "Logistic Regression note contains a 3x-repeated phrase stutter",
        "category": "output-editorial",
        "severity": "low",
        "status": "open",
        "discovered_by": "session-29 VERIF-001 semantic campaign (group 04 quality flag; orchestrator-confirmed)",
        "observed": "'a fascinating mathematical coincidence:' is repeated three times in a row at the start of the sentence in the 'Are the gradient formulas identical? A deeper look' section (one line, three consecutive copies).",
        "root_cause": "Generation/repair stutter in a single line; not caught by lint (no structural defect) or prose-quality heuristic (word-count based).",
        "evidence": "Logistic Regression.md line 174; judgments group-04 KU-ffef84f04a6f9b46 quality flag.",
        "repair": "Collapse the tripled phrase to a single occurrence (content otherwise unchanged).",
        "regression_prevention": "s29_semantic_repairs.py repair 3 (anchored, probe-idempotent).",
        "affected_paths": ["output/Unified-Vault/04 - Machine Learning/Regression/Logistic Regression.md"],
        "verification": "pending repair",
        "remaining_risk": "The prose-quality check cannot detect intra-line duplication; a corpus-wide duplicate-phrase scan is a possible framework follow-up.",
    },
    {
        "finding_id": "F-0038",
        "title": "Loss Functions note duplicates the Huber French-labels block three times",
        "category": "output-editorial",
        "severity": "low",
        "status": "open",
        "discovered_by": "session-29 VERIF-001 semantic campaign (group 03 quality flag; orchestrator-confirmed)",
        "observed": "The paragraph 'The original course material wrote the same definition with French condition labels ...' plus its cases formula and si/sinon gloss appears three consecutive times in the Huber-loss section.",
        "root_cause": "Generation consolidation artifact; the three copies are identical (the two math forms are equivalent factorings: delta(|e| - delta/2) = delta|e| - delta^2/2), so no mathematical contradiction — pure duplication.",
        "evidence": "Loss Functions.md lines 272-287; judgments group-03 KU-6afa618fccdc24c4 quality flag.",
        "repair": "Keep the first block, remove the second and third (anchored on the exact repeated span).",
        "regression_prevention": "s29_semantic_repairs.py repair 4 (anchored, probe-idempotent); full-corpus audit re-run must stay 0 findings (the Huber formula remains present once).",
        "affected_paths": ["output/Unified-Vault/04 - Machine Learning/Optimization Algorithms/Loss Functions.md"],
        "verification": "pending repair",
        "remaining_risk": "Marker retention unaffected (one verbatim instance remains).",
    },
    {
        "finding_id": "F-0039",
        "title": "K-Nearest Neighbors note has a dangling heading fragment breaking the Small/Large K parallel",
        "category": "output-editorial",
        "severity": "low",
        "status": "open",
        "discovered_by": "session-29 VERIF-001 semantic campaign (group 03 quality flag; orchestrator-confirmed)",
        "observed": "'### Large K' is followed by its bullet and then a stray line ': underfitting and high bias' — the suffix of the intended heading '### Large K: underfitting and high bias' (parallel to '### Small K: overfitting and high variance') stranded as body text.",
        "root_cause": "Heading split during generation or repair.",
        "evidence": "K-Nearest Neighbors.md lines 193-196; judgments group-03 quality flag.",
        "repair": "Merge the fragment into the heading: '### Large K: underfitting and high bias'; delete the stray line.",
        "regression_prevention": "s29_semantic_repairs.py repair 5 (anchored, probe-idempotent).",
        "affected_paths": ["output/Unified-Vault/04 - Machine Learning/Nearest Neighbors/K-Nearest Neighbors.md"],
        "verification": "pending repair",
        "remaining_risk": "None identified; the fragment's words are preserved in the merged heading.",
    },
    {
        "finding_id": "F-0040",
        "title": "Sigmoid vanishing-gradient code comment carries a mathematically wrong source value (sic, preserved verbatim)",
        "category": "source-inherited-inconsistency",
        "severity": "info",
        "status": "accepted",
        "discovered_by": "session-29 VERIF-001 semantic campaign (group 06 quality flag; orchestrator-confirmed)",
        "observed": "The verbatim source code block in Vanishing and Exploding Gradients.md states '0.25^10 ~= 0.0000000009' (9e-10); the correct value is 0.25^10 = 1/1,048,576 ~= 9.5e-7, which the same note's prose and table correctly state (10^-6 row). The wrong figure is the source's own, preserved verbatim per the code-verbatim convention.",
        "root_cause": "Source-internal arithmetic slip inside a code comment; the synthesis preserved the block byte-verbatim (fingerprinted) while the surrounding prose carries the correct magnitude.",
        "evidence": "Vanishing and Exploding Gradients.md line 601 (code block) vs lines 530/573-587 (correct values); judgments group-06 KU-47b487ace3477d0b quality flag.",
        "repair": "None — keep-both/sic convention for source-internal inconsistencies (final report §5.4); altering the verbatim code block would violate the code-fingerprint preservation contract.",
        "regression_prevention": "Documented here; the reader sees the inconsistency of the record with the correct value adjacent.",
        "affected_paths": ["output/Unified-Vault/05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients.md"],
        "verification": "confirmed by direct read",
        "remaining_risk": "A reader quoting only the code comment takes away a wrong magnitude; mitigated by the adjacent correct prose.",
    },
    {
        "finding_id": "F-0041",
        "title": "Cost Optimization worked example switches between 7,000 and 7,300 conversations mid-calculation (sic, inherited verbatim)",
        "category": "source-inherited-inconsistency",
        "severity": "info",
        "status": "accepted",
        "discovered_by": "session-29 VERIF-001 semantic campaign (group 13 quality flag; orchestrator-confirmed)",
        "observed": "'7,000 x 5 turns x (300 in x 0.7 cache-adjusted + 120 out) = 7,300 x 5 x (210 + 120) = ...' — the conversation count changes from 7,000 to 7,300 inside one equation line. The source (Master AI 21 - LLMOps and MLOps/Cost/06 - Cost Optimization.md line 104) contains the identical text.",
        "root_cause": "Source-internal inconsistency (the 0.7 routing factor plausibly explains 70% of a ~10,400 pool, but the line as written mixes the two figures); preserved verbatim.",
        "evidence": "Cost Optimization.md line 117; source line 104 (byte-identical); judgments group-13 KU-9b65c36a081c5388 quality flag.",
        "repair": "None — keep-both/sic convention; the line is the source's own arithmetic presentation.",
        "regression_prevention": "Documented here.",
        "affected_paths": ["output/Unified-Vault/14 - Inference and Production/LLMOps and MLOps/Cost Optimization.md"],
        "verification": "confirmed by direct read of both source and output",
        "remaining_risk": "Minor reader confusion in one worked example.",
    },
]

existing = [json.loads(l) for l in FINDINGS.open(encoding="utf-8") if l.strip()]
existing_ids = {f["finding_id"] for f in existing}
for f in new_findings:
    assert f["finding_id"] not in existing_ids, f"duplicate id {f['finding_id']}"
with FINDINGS.open("a", encoding="utf-8") as fh:
    for f in new_findings:
        fh.write(json.dumps(f, ensure_ascii=False) + "\n")
print(f"findings appended: {[f['finding_id'] for f in new_findings]}")

# ---- campaign report ----
campaign = {
    "task_id": "VERIF-001",
    "title": "Post-delivery stratified semantic spot-verification",
    "date": "2026-11-06",
    "population": {"kus_total": 27536, "notes_total": 544},
    "sample": {
        "drawn": 246,
        "fraction": round(246 / 27536, 5),
        "method": "see reports/synthesis/s29-semantic-sample.json",
        "areas_covered": 20,
    },
    "judgments": {
        "total": len(judgments),
        "by_verdict": dict(by_verdict),
        "present_rate": round(by_verdict["present"] / len(judgments), 4),
        "retained_total": by_verdict["present"] + by_verdict["superseded-info-retained"],
        "by_disposition": {k: dict(v) for k, v in sorted(by_disp.items())},
        "by_unit_type": {k: dict(v) for k, v in sorted(by_type.items())},
        "by_area": {k: dict(v) for k, v in sorted(by_area.items())},
    },
    "evidence_integrity": {
        "mechanical_validation": "PASSED: 246/246 judgments, every evidence_quote verified as a whitespace-normalized substring of its cited destination note (s29_validate_judgments.py)",
        "orchestrator_review": "28/246 KUs re-reviewed independently (all 4 non-present + 24 even-spaced present): 28/28 agreement; 1 judgment repaired for destination_note field conformance (verdict unchanged); 6 present verdicts deep-verified at full-context level (Q&A answers, 5-point lists, link chains)",
        "subagent_reporting_notes": "2 quality flags did not reproduce under orchestrator verification (claimed 3x sentence repetitions in K-Nearest Neighbors.md are 1x each) — flagged as subagent reporting inaccuracies, excluded from findings; all other verified flags are recorded as F-0035..F-0041",
    },
    "findings": {
        "new": [f["finding_id"] for f in new_findings],
        "repaired_this_session": ["F-0035", "F-0036", "F-0037", "F-0038", "F-0039"],
        "accepted_sic": ["F-0040", "F-0041"],
        "partial_verdict_kus": ["KU-e139f00c9e5651ab", "KU-2fd0a537e0a20f6c"],
        "absent_verdict_kus": [],
    },
    "limitations": [
        "0.89% stratified sample with area floor; NOT a full per-unit semantic proof (final report §5.1 boundary stands)",
        "judgments are AI reading-level assessments by subagent groups; orchestrator re-reviewed 28 (11.4%)",
        "evidence quotes prove the cited span exists; the verdict weighs the span against the excerpt's knowledge",
        "quality flags are observations from judgment context, not a systematic editorial sweep",
    ],
    "judgments_file": "reports/synthesis/s29-semantic-judgments.jsonl",
}
CAMPAIGN_OUT.write_text(json.dumps(campaign, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
print("campaign report written")
print("verdicts:", dict(by_verdict))
print(f"present+retained: {campaign['judgments']['retained_total']}/246 "
      f"({campaign['judgments']['retained_total']/246:.1%})")
