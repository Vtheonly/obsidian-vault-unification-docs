#!/usr/bin/env python3
"""EXT-010 (R1 repair): append finding F-0009 to state/findings.jsonl (idempotent).

F-0009 was surfaced by the EXT-010 classification work and verified at source
by EXT-010-REVIEW: the AI Course vault is internally inconsistent about the
PyTorch Conv2d default BIAS initialization (file 01 attributes zeros to the
Conv2d default while file 02 and file 01's own Linear section state the
uniform bound, which matches PyTorch's actual reset_parameters).
"""
import json
import sys

PATH = "state/findings.jsonl"

finding = {
    "finding_id": "F-0009",
    "title": "AI Course internally inconsistent on the PyTorch Conv2d default bias initialization (zeros vs uniform)",
    "category": "content-discrepancy",
    "severity": "medium",
    "status": "open",
    "discovered_by": "EXT-010 session (classification work); verified at source by EXT-010-REVIEW (read-only subagent)",
    "affected_source": (
        "source-vaults/AI /AI Course/04 - Neural Networks and Deep Learning "
        "Foundations/04.3 - Training Dynamics and Stability/01. Weight "
        "Initialization.md (L399-407 Conv2d defaults passage) vs 02. Weight "
        "Initialization Techniques.md (L68-70) and the same file 01 Linear "
        "section (L411-415)"
    ),
    "observed": (
        "Course file 01 states PyTorch initializes Conv2d weights with Kaiming "
        "Uniform (a = sqrt(5)) and then says 'Biases are initialized to zero.' "
        "(L407, inside the Kaiming-uniform-a=sqrt(5) passage). Course file 02 "
        "states 'The bias is initialized from a uniform distribution "
        "U(-1/sqrt(fan_in), 1/sqrt(fan_in))' for torch.nn.Conv2d (L68-70), and "
        "file 01's own Linear section says 'Fully-connected (Linear) layers "
        "use the same initialization as Conv2d' (L411) with biases "
        "'initialized using U(-1/sqrt(m), 1/sqrt(m))' (L415). File 01's "
        "verification code comment also hedges ('Should be zeros or small "
        "uniform'). The two statements about the Conv2d bias default "
        "contradict each other within the same vault."
    ),
    "evidence": (
        "state/knowledge-units/011-ext010-ai-course-04.3-init-gradients.jsonl "
        "(KU-f36687797fee3162 L407 'Biases are initialized to zero.'; "
        "KU-1324d50530a9206a L411 'the same initialization as Conv2d'; "
        "KU-6bceaf2675213e64 L415 uniform bias bound; KU-66b7f8b40fdcb24d "
        "L453 'zeros or small uniform' code comment; and from file 02: "
        "KU-e5251c5a48599a25 L68-70 uniform bound). Byte-exact quotes "
        "verified in OC-ext010-0033/0036 and independently at source by "
        "EXT-010-REVIEW (reports/extraction/ext010-review.md)."
    ),
    "expected_condition": (
        "At synthesis, the unified vault must state PyTorch's ACTUAL default "
        "for Conv2d/Linear biases: uniform on (-1/sqrt(fan_in), 1/sqrt(fan_in)) "
        "(reset_parameters uses kaiming_uniform_ with a=sqrt(5) for weights "
        "and a uniform bound for biases). Course file 01's L407 zero-bias "
        "attribution is the imprecise branch; the zero-bias statement may be "
        "kept as the manual-init RECOMMENDATION (consistent with master-ai's "
        "'Standard: zeros' bias guidance, OC-ext010-0036) but must not be "
        "presented as PyTorch's default."
    ),
    "repair_recommendation": (
        "Synthesis-time reconciliation in the weight-initialization and "
        "PyTorch-defaults notes; cross-reference from the synthesized note "
        "on initialization defaults. No action needed before synthesis; "
        "classification records OC-ext010-0033 and OC-ext010-0036 already "
        "carry the caveat in their rationales."
    ),
}

existing = [json.loads(l) for l in open(PATH, encoding="utf-8") if l.strip()]
if any(r.get("finding_id") == "F-0009" for r in existing):
    print("F-0009 already recorded; aborting append")
    sys.exit(1)

with open(PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(finding, ensure_ascii=False, sort_keys=True) + "\n")

print(f"appended F-0009; findings now has {len(existing) + 1} records")
