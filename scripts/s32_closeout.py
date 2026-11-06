#!/usr/bin/env python3
"""INTEG-002 aggregation + session-32 closeout.

Builds the machine-readable judgment aggregate (denominators, per-section
breakdown, method, re-review record), marks INTEG-002 completed and queues
INTEG-003 (S33: 2D3D cluster) in the task queue, and writes the session-32
checkpoint with the accelerated_mode block.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
sys.path.insert(0, str(REPO / "src"))
from vault_unification import registry as reg  # noqa: E402

JUDGMENTS = REPO / "state/integration/judgments-mednlp-v1.jsonl"
INVENTORY = REPO / "state/integration/inventory-v1.jsonl"
MANIFEST = REPO / "reports/integration/s32-mednlp-groups.json"
AGG = REPO / "reports/integration/s32-mednlp-judgments.json"
QUEUE = REPO / "state/task-queue.jsonl"
CURRENT = REPO / "state/current-state.json"
CHECKPOINT = REPO / "state/checkpoints/checkpoint-2026-11-06-integ-session32.json"

REREVIEW = {
    "method": "stratified even-spaced sample (every 9th record of the 368, 41 items = 11.1%): 23 absent verified by independent orchestrator greps of the agent search terms (all hits confirmed false positives: 'fluid' matching LUI, teacher-forcing 'instructor', image-anisotropy vs representation anisotropy, mermaid 'graph TD' declarations); 18 covered/partial/equivalent verified by reading the cited destination notes and judging the verdict + quote depth against the campaign depth standard",
    "sample_size": 41,
    "agreement": 41,
    "disagreements": [],
    "notes": "The 41-item sample spans all 18 MEDNLP sections and all four verdicts (12 covered / 4 partial / 2 equivalent / 23 absent). Notable confirmed judgment calls: Top-K Candidate Retrieval covered via the canonical retrieval-step explanation in Cosine Similarity.md; DAGs covered via the computational-graph treatment; Explainable AI equivalent under the vault's 'interpretability' terminology; Bootstrap Confidence Intervals equivalent under 'The bootstrap'; Graph Explainability absent (interpretability notes cover CNNs/LLMs, no graph-model explainability); Domain-Specific BERT partial (troubleshooting row only — BioBERT/ClinicalBERT family absent).",
}

INTEG_002_RESULT = {
    "covered": 0, "equivalent": 0, "partial": 0, "absent": 0,
}  # filled at runtime

INTEG_003 = {
    "task_id": "INTEG-003",
    "title": "Semantic coverage judgments — 2D3D cluster, 291 items (S33 of 15)",
    "status": "queued",
    "priority": "high",
    "dependencies": ["INTEG-002"],
    "inputs": [
        "state/integration/inventory-v1.jsonl (2D3D-cluster items; authoritative item list)",
        "state/integration/coverage-lexical-v1.jsonl (lexical evidence per item — substrate, never a decision)",
        "state/integration/clusters-v1.json (2D3D context records: 'Open the 2D3D project folder', group labels for architectural components / datasets / research directions)",
        "output/Unified-Vault/ (544 notes, read-only during judging)",
    ],
    "outputs": [
        "state/integration/judgments-2d3d-v1.jsonl (one judgment per 2D3D item)",
        "reports/integration/s33-2d3d-groups.json + s33-2d3d-judgments.json",
    ],
    "acceptance_criteria": [
        "every one of the 291 2D3D items receives exactly one judgment with a verdict from {covered, partial, absent, equivalent} at the campaign depth standard",
        "every covered/equivalent judgment cites a destination note and a verbatim evidence quote mechanically verified as a substring of that note",
        "the orchestrator independently re-reviews at least 10% of judgments and records agreement/disagreement",
        "no source-vault or output-vault mutation during the judgment phase",
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults, the taxonomy file, or output notes",
        "Do not skip items or batch-reason over groups of items without per-item records",
    ],
    "findings": [],
    "notes": "S33 per campaign plan section 8. 2D3D = computer vision and 3D reconstruction (291 items): the lexical none-band concentrated here in S31 (NeRF/3D reconstruction vocabulary absent from both source vaults); expect a high absent rate on 3D-specific items and covered/partial on general CV items.",
    "commit": None,
    "tests_run": [],
}


def main() -> int:
    recs = [json.loads(l) for l in JUDGMENTS.open(encoding="utf-8") if l.strip()]
    inv = {}
    for line in INVENTORY.open(encoding="utf-8"):
        if line.strip():
            i = json.loads(line)
            inv[i["item_id"]] = i
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def section_of(item_id: str) -> str:
        for occ in inv[item_id]["occurrences"]:
            if occ["cluster"] == "MEDNLP":
                return occ["section"]
        return "?"

    counts = Counter(r["verdict"] for r in recs)
    by_section: dict[str, dict] = {}
    for r in recs:
        s = section_of(r["item_id"])
        by_section.setdefault(s, Counter())[r["verdict"]] += 1
        by_section[s]["total"] += 1

    aggregate = {
        "campaign": "INTEG-002",
        "cluster": "MEDNLP",
        "items_total": len(recs),
        "verdict_counts": dict(counts),
        "retained_or_existing": counts["covered"] + counts["equivalent"] + counts["partial"],
        "genuinely_missing": counts["absent"],
        "by_section": {s: dict(c) for s, c in by_section.items()},
        "method": {
            "design": "full-cluster census (no sampling): all 368 MEDNLP items judged",
            "groups": f"{manifest['groups_total']} bounded subagent groups (max {manifest['max_items_per_group']} items; grouped by section, sections never merged)",
            "judges": "28 independent general-purpose subagents reading destination notes and grepping the vault for surface forms + alternative terminology before any absent verdict",
            "depth_standard": "campaign plan section 5 (what it is / why it exists / how it works conceptually / relations to other concepts; project usage not required for 'covered')",
            "evidence_rule": "covered/equivalent/partial require a verbatim quote (>= 12 words for covered/equivalent) mechanically validated as a whitespace-normalized substring of the cited note (scripts/s32_validate_judgments.py, exit 0: 368/368 PASSED)",
            "orchestrator_rereview": REREVIEW,
            "limitations": [
                "single-judge-per-item design mitigated by mandatory multi-term search before absent verdicts + the 11.1% orchestrator re-review; borderline covered/partial calls carry uncertainty noted by judges",
                "judgments reflect the vault as of session 31 state (no vault mutations occurred during judging)",
                "'covered' does not include project usage; project context integration happens in the S37+ execution waves",
            ],
        },
        "destination_notes_cited": sorted({r["destination_note"] for r in recs if r.get("destination_note")}),
        "validation": "scripts/s32_validate_judgments.py: VALIDATION PASSED 368/368 (schema, exact set coverage, quotes verbatim-verified, absent discipline)",
    }
    AGG.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"aggregate written: {AGG.relative_to(REPO)}")
    print(f"verdicts: {dict(counts)}")

    # ---- task queue: INTEG-002 -> completed (fill result), INTEG-003 queued ----
    queue = [json.loads(l) for l in QUEUE.open(encoding="utf-8") if l.strip()]
    for t in queue:
        if t["task_id"] == "INTEG-002":
            t["status"] = "completed"
            t["commit"] = None
            t["findings"] = [
                "MEDNLP cluster is ~54% genuinely missing (197/368 absent): the entire medical-terminology layer (UMLS/SNOMED/ICD/RxNorm/LOINC/MeSH/HGNC/OMIM/MONDO/HPO/Orphanet: 0 vault occurrences), the diseases/phenotypes/drugs named-entity layer, clinical IE (negation/assertion/temporality/experiencer/certainty), clinical BERT family, RDF/OWL/SKOS ontology stack, triple stores, GNN/KG-embedding family, and ontology-based similarity — the vault's sources never covered medical NLP",
                "general-ML items are largely covered (89 covered + 12 equivalent): attention/transformer mechanics, tokenization, embeddings + vector math, retrieval/ANN index family, evaluation metrics, sampling/decoding; 70 partial items have a right home but below-depth explanations (e.g. Domain-Specific BERT, ranking-metric family, Concept Drift, LLM-based IE, FAISS/NetworkX as libraries)",
                "terminology-equivalence detections: Explainable AI≡interpretability, Bootstrap CIs≡The bootstrap, Retrieve-then-Rank/Candidate Ranking≡Reranking, Deterministic Generation≡greedy decoding, Neural Ranker≡cross-encoder reranker, Structured Generation≡constrained decoding — the D/A decision rules will reuse these mappings",
            ]
            t["tests_run"] = [
                {"command": "python3 scripts/s32_pack_groups.py", "result": "368 MEDNLP items packed into 28 bounded groups (by section, max 18)"},
                {"command": "28 subagent judgment groups (general-purpose agents, all 28 completed cleanly on first run)", "result": "368 judgments: 89 covered / 12 equivalent / 70 partial / 197 absent"},
                {"command": "python3 scripts/s32_validate_judgments.py", "result": "VALIDATION PASSED 368/368 (schema, exact set coverage, every covered/equivalent/partial quote verbatim-verified as whitespace-normalized substring of its cited note; absent discipline verified)"},
                {"command": "orchestrator re-review (stratified 41-item sample = 11.1%)", "result": "41/41 agreement (23 absent independently grep-verified; 18 covered/partial/equivalent destination-read verified)"},
                {"command": "vu verify-manifest x2", "result": "276/276 + 333/333 byte-identical (no mutations during judging)"},
                {"command": "python3 -m pytest -q (full suite)", "result": "836 passed (unchanged code since the session-31 green run; re-run as session-end evidence)"},
            ]
            t["notes"] = (
                "Session 32 (S32 of 15). Full-cluster census of MEDNLP (368 items, no sampling). "
                "Result feeds the S36 decision ledger: covered/equivalent -> decision A candidates; "
                "partial -> decision B (expand existing note); absent -> decision C/D (integrate; "
                "medical-domain items will anchor new cluster-domain notes per plan section 7). "
                "Judgment file: state/integration/judgments-mednlp-v1.jsonl; aggregate: "
                "reports/integration/s32-mednlp-judgments.json."
            )
        if t["task_id"] == "INTEG-003" and t["status"] == "queued":
            break
    else:
        queue.append(INTEG_003)
    QUEUE.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in queue))
    report = reg.validate_task_queue(QUEUE, REPO / "schemas" / "task.schema.json")
    if not report["valid"]:
        print(f"QUEUE INVALID: {report['errors']}")
        return 1
    print(f"task queue valid: INTEG-002 completed, INTEG-003 queued ({len(queue)} tasks)")

    # ---- current-state ----
    cs = json.loads(CURRENT.read_text())
    cs["current_task_id"] = "INTEG-003"
    cs["stage"] = "integration-campaign (S32 MEDNLP judgments complete; S33 2D3D next)"
    cs["notes"] = (
        "INTEG campaign S32 complete: MEDNLP cluster fully judged (368/368, no sampling) — "
        "89 covered / 12 equivalent / 70 partial / 197 absent; all quotes mechanically "
        "verified; 11.1% orchestrator re-review 41/41 agreement. Next: S33 2D3D cluster "
        "(291 items), then S34 SYNPATH+VAULTX, S35 rest, S36 decisions."
    )
    cs["last_verified_checkpoint"] = str(CHECKPOINT.relative_to(REPO))
    CURRENT.write_text(json.dumps(cs, indent=4) + "\n")

    # ---- checkpoint ----
    checkpoint = {
        "session": 32,
        "task_id": "INTEG-002",
        "date": "2026-11-06",
        "phase": "integration-campaign-audit",
        "work_completed": [
            "packed the 368 MEDNLP items into 28 bounded judgment groups (section-coherent, max 18 items; lexical hints attached) via scripts/s32_pack_groups.py",
            "ran 28 independent subagent judgment groups (all completed cleanly on first run): each judge read candidate notes and grepped the vault for surface + alternative terminology before any absent verdict",
            "mechanically validated all 368 judgments (schema, exact set coverage, verbatim-quote verification, absent discipline): VALIDATION PASSED 368/368",
            "orchestrator re-review of a stratified 41-item sample (11.1%): 41/41 agreement",
            "wrote the canonical judgment file + aggregate report; queued INTEG-003 (S33: 2D3D); updated ledger/handoff/README",
        ],
        "changed_paths": [
            "scripts/s32_pack_groups.py (new)",
            "scripts/s32_validate_judgments.py (new)",
            "state/integration/judgments-mednlp-v1.jsonl (new; 368 records)",
            "reports/integration/s32-mednlp-groups.json (new; committed manifest)",
            "reports/integration/s32-mednlp-judgments.json (new; aggregate)",
            "state/task-queue.jsonl (INTEG-002 completed; INTEG-003 queued)",
            "state/current-state.json",
            "state/checkpoints/checkpoint-2026-11-06-integ-session32.json",
            "docs/ACCELERATED_COMPLETION_POLICY.md (ledger row 32)",
            "docs/agent-handoff/next-agent.md (rewritten for session 33)",
            "README.md (campaign progress)",
        ],
        "tests_run": [
            {"command": "python3 -m pytest -q (full suite at session end)", "result": "836 passed"},
            {"command": "vu verify-manifest x2 (sources)", "result": "276/276 + 333/333 byte-identical"},
            {"command": "python3 scripts/s32_validate_judgments.py", "result": "VALIDATION PASSED 368/368"},
        ],
        "git_state": {
            "branch": "main",
            "base_commit": "b451679 (session-31 close)",
            "session_commits": "recorded in the session commit message",
            "push_verification": "per AGENTS.md section 13: push after commit and verify remote ref",
        },
        "open_findings": [
            "MEDNLP absent-rate 54% (197/368) confirms the campaign premise: the medical-domain layer must be built almost from scratch as cluster-domain notes (decision C/D) in the S37+ waves",
            "70 partial items define the decision-B expansion workload for MEDNLP destinations (e.g. ranking-metric prose, FAISS/NetworkX library intros, Domain-Specific BERT concept)",
            "12 equivalence mappings recorded for terminology consistency in the S36 decision ledger",
        ],
        "next_task": {
            "task_id": "INTEG-003",
            "title": "Semantic coverage judgments — 2D3D cluster (291 items)",
            "dependencies": ["INTEG-002 (completed)"],
            "resume": (
                "Follow AGENTS.md section 2 startup; read docs/INTEGRATION_CAMPAIGN_PLAN.md and this "
                "checkpoint; reuse the S32 machinery: adapt scripts/s32_pack_groups.py to the 2D3D "
                "cluster (291 items), run bounded judgment groups, validate with the same mechanical "
                "checks, re-review >=10%, aggregate, and queue INTEG-004 (S34: SYNPATH+VAULTX)."
            ),
        },
        "accelerated_mode": {
            "session_number": 32,
            "budget_sessions_consumed": 2,
            "budget_sessions_remaining": 13,
            "deliverable_metric_moved": "campaign items semantically judged (cumulative)",
            "before": "0/1,233 items judged (S31 produced lexical evidence only)",
            "after": "368/1,233 items judged at the depth standard (MEDNLP cluster complete; 29.8% of the inventory) — 89 covered / 12 equivalent / 70 partial / 197 absent",
            "denominator": "1,233 unique inventory items; 368 MEDNLP items judged 368/368 (full census, no sampling)",
            "failed_session": False,
            "cause_if_failed": None,
            "deadline_position": "INTEG campaign session 2 of 15 (S31-S45); on plan (S32 objective met within its session)",
        },
    }
    CHECKPOINT.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\n")
    print(f"checkpoint written: {CHECKPOINT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
