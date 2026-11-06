#!/usr/bin/env python3
"""INTEG-003 aggregation + session-33 closeout.

Builds the machine-readable judgment aggregate (denominators, per-section
breakdown, method, re-review record), marks INTEG-003 completed and queues
INTEG-003 (S33: 2D3D cluster) in the task queue, and writes the session-33
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

JUDGMENTS = REPO / "state/integration/judgments-2d3d-v1.jsonl"
INVENTORY = REPO / "state/integration/inventory-v1.jsonl"
MANIFEST = REPO / "reports/integration/s33-2d3d-groups.json"
AGG = REPO / "reports/integration/s33-2d3d-judgments.json"
QUEUE = REPO / "state/task-queue.jsonl"
CURRENT = REPO / "state/current-state.json"
CHECKPOINT = REPO / "state/checkpoints/checkpoint-2026-11-06-integ-session33.json"

REREVIEW = {
    "method": "stratified even-spaced sample (every 10th record of the 291, 30 items = 10.3%): 20 absent verified by independent orchestrator greps of the agent search terms (all hits confirmed false positives: 'an 8-point improvement' in Process Reward Models is an accuracy delta not the epipolar algorithm; 'roof' hits are 'Proofread'/'proof' substrings); 10 partial/equivalent verified by reading the cited destination notes and judging the verdict + quote depth against the campaign depth standard",
    "sample_size": 30,
    "agreement": 30,
    "disagreements": [],
    "notes": "The 30-item sample spans 2D3D sections and the partial/equivalent/absent verdicts (0 covered in sample). Notable confirmed judgment calls: Image Pair Mapping EQUIVALENT via the keypoint-matching treatment (Lowe's ratio test, RANSAC verification) in the Feature Descriptors note; Shared-Weight CNN EQUIVALENT via parameter sharing in Local Connectivity and Parameter Sharing; Curriculum Learning PARTIAL (project-note recipe, not a dedicated concept explanation); Coordinate Systems PARTIAL (2D image-vs-math origins explained, no world/camera 3D chain); Latent Slots PARTIAL via the Perceiver latent-array machinery (slot semantics absent); Computational Feasibility PARTIAL (worked FLOPs-to-wall-clock estimates never framed as a concept). All 20 sampled absent verdicts confirmed: pinhole/undistortion/eight-point/SuperPoint/surface normals/depth foundation models/monocular depth/ECA-Net/watertight/alpha compositing/CUDA rasterization/scene parsing/floorplan/DeepFloorplan have zero genuine vault occurrences.",
}

INTEG_003_RESULT = {
    "covered": 0, "equivalent": 0, "partial": 0, "absent": 0,
}  # filled at runtime

INTEG_004 = {
    "task_id": "INTEG-004",
    "title": "Semantic coverage judgments — SYNPATH + VAULTX clusters, 237 items (S34 of 15)",
    "status": "queued",
    "priority": "high",
    "dependencies": ["INTEG-003"],
    "inputs": [
        "state/integration/inventory-v1.jsonl (SYNPATH + VAULTX items; authoritative item list)",
        "state/integration/coverage-lexical-v1.jsonl (lexical evidence per item — substrate, never a decision)",
        "state/integration/clusters-v1.json (SYNPATH context: Repository '3d-syntree / 3d-synV2'; VAULTX context: additional AI-concepts section)",
        "output/Unified-Vault/ (544 notes, read-only during judging)",
    ],
    "outputs": [
        "state/integration/judgments-synpath-v1.jsonl (one judgment per SYNPATH+VAULTX item)",
        "reports/integration/s34-synpath-groups.json + s34-synpath-judgments.json",
    ],
    "acceptance_criteria": [
        "every one of the 237 SYNPATH+VAULTX items receives exactly one judgment with a verdict from {covered, partial, absent, equivalent} at the campaign depth standard",
        "every covered/equivalent judgment cites a destination note and a verbatim evidence quote mechanically verified as a substring of that note",
        "the orchestrator independently re-reviews at least 10% of judgments and records agreement/disagreement",
        "no source-vault or output-vault mutation during the judgment phase",
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults, the taxonomy file, or output notes",
        "Do not skip items or batch-reason over groups of items without per-item records",
    ],
    "findings": [],
    "notes": "S34 per campaign plan section 8. SYNPATH (209 items) = geometric deep learning, equivariant architectures (PaiNN/Equiformer), molecular generation, GFlowNets, protein representation; VAULTX (28 items) = additional AI concepts from the user's projects vault. S31 lexical evidence showed the geometric-deep-learning vocabulary is absent from the vault (no GNN note); expect a high absent rate on geometric/equivariant items and covered/partial on general deep-learning items (attention, normalization, optimizers).",
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
            if occ["cluster"] == "2D3D":
                return occ["section"]
        return "?"

    counts = Counter(r["verdict"] for r in recs)
    by_section: dict[str, dict] = {}
    for r in recs:
        s = section_of(r["item_id"])
        by_section.setdefault(s, Counter())[r["verdict"]] += 1
        by_section[s]["total"] += 1

    aggregate = {
        "campaign": "INTEG-003",
        "cluster": "2D3D",
        "items_total": len(recs),
        "verdict_counts": dict(counts),
        "retained_or_existing": counts["covered"] + counts["equivalent"] + counts["partial"],
        "genuinely_missing": counts["absent"],
        "by_section": {s: dict(c) for s, c in by_section.items()},
        "method": {
            "design": "full-cluster census (no sampling): all 291 2D3D items judged",
            "groups": f"{manifest['groups_total']} bounded subagent groups (max {manifest['max_items_per_group']} items; grouped by section, sections never merged)",
            "judges": "24 independent general-purpose subagents reading destination notes and grepping the vault for surface forms + alternative terminology before any absent verdict",
            "depth_standard": "campaign plan section 5 (what it is / why it exists / how it works conceptually / relations to other concepts; project usage not required for 'covered')",
            "evidence_rule": "covered/equivalent/partial require a verbatim quote (>= 12 words for covered/equivalent) mechanically validated as a whitespace-normalized substring of the cited note (scripts/s33_validate_judgments.py, exit 0: 291/291 PASSED)",
            "orchestrator_rereview": REREVIEW,
            "limitations": [
                "single-judge-per-item design mitigated by mandatory multi-term search before absent verdicts + the 10.3% orchestrator re-review; borderline covered/partial calls carry uncertainty noted by judges",
                "judgments reflect the vault as of session 32 state (no vault mutations occurred during judging)",
                "'covered' does not include project usage; project context integration happens in the S37+ execution waves",
            ],
        },
        "destination_notes_cited": sorted({r["destination_note"] for r in recs if r.get("destination_note")}),
        "validation": "scripts/s33_validate_judgments.py: VALIDATION PASSED 291/291 (schema, exact set coverage, quotes verbatim-verified, absent discipline)",
    }
    AGG.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"aggregate written: {AGG.relative_to(REPO)}")
    print(f"verdicts: {dict(counts)}")

    # ---- task queue: INTEG-003 -> completed (fill result), INTEG-004 queued ----
    queue = [json.loads(l) for l in QUEUE.open(encoding="utf-8") if l.strip()]
    for t in queue:
        if t["task_id"] == "INTEG-003":
            t["status"] = "completed"
            t["commit"] = None
            t["findings"] = [
                "2D3D cluster is ~66% genuinely missing (191/291 absent): the vault has no 3D-reconstruction layer at all — camera models/intrinsics/calibration (pinhole, focal length, checkerboard: 0 occurrences), epipolar + multi-view geometry (epipolar/essential matrix/fundamental matrix/eight-point/stereo: 0 occurrences), MVS/cost volumes/plane sweep, bundle adjustment + NLLS machinery (Levenberg-Marquardt/Gauss-Newton/COLMAP/Ceres: 0), point clouds + triangulation, neural depth estimation (monocular/MiDaS/Depth Anything/DPT: 0), depth fusion/TSDF/volumetric integration, mesh processing (marching cubes/decimation/QEM/watertight: 0), NeRF/3DGS rendering stack (radiance/volume rendering/ray marching/splatting: 'radiance' literally never occurs), building decomposition (scene parsing/floorplan/scene graphs: 0), and primitive/disentangled 3D representations — its own Foundation Models MOC concedes NeRF/3DGS have no dedicated note yet",
                "general-CV/deep-learning items within 2D3D are covered or near-covered: SIFT/ORB feature descriptors + matching (the strongest single note: 8 covered in group-06), ViT/CNN, Group Norm/LeakyReLU/Softmax/ResNet blocks, gradient descent + Jacobians, semantic segmentation, data augmentation, homogeneous coordinates (2D scope), plus 8 equivalence mappings (Image Pair Matching≡keypoint matching, Shared-Weight CNN≡parameter sharing, Feature Extraction≡hierarchical feature extraction, Feature Pyramids≡FPN, Geometric Correspondence≡keypoint correspondence, Frame Resizing≡image scaling+interpolation, System Orchestrator≡multi-agent orchestrator, Backward Warping≡inverse mapping)",
                "64 partial items define the decision-B expansion workload: the math/2D core exists but the 3D framing is missing (RANSAC one-liner, perspective projection 2D-only, coordinate systems 2D-only, NCC/SAD in non-MVS contexts, voxel grids as CNN input, NeRF/3DGS bare roadmap name-drops, Perceiver latent machinery for slot attention, curriculum learning + synthetic data + computational feasibility as project-note recipes)",
            ]
            t["tests_run"] = [
                {"command": "python3 scripts/s33_pack_groups.py", "result": "291 2D3D items packed into 24 bounded groups (by section, max 18)"},
                {"command": "24 subagent judgment groups (general-purpose agents, all 24 completed cleanly on first run)", "result": "291 judgments: 28 covered / 8 equivalent / 64 partial / 191 absent"},
                {"command": "python3 scripts/s33_validate_judgments.py", "result": "VALIDATION PASSED 291/291 (schema, exact set coverage, every covered/equivalent/partial quote verbatim-verified as whitespace-normalized substring of its cited note; absent discipline verified)"},
                {"command": "orchestrator re-review (stratified 30-item sample = 10.3%)", "result": "30/30 agreement (20 absent independently grep-verified — all hits confirmed false positives; 10 partial/equivalent destination-read verified)"},
                {"command": "vu verify-manifest x2", "result": "276/276 + 333/333 byte-identical (no mutations during judging)"},
                {"command": "python3 -m pytest -q (full suite)", "result": "836 passed (no code changes this session; re-run as session-end evidence)"},
            ]
            t["notes"] = (
                "Session 33 (S33 of 15; executed within the same wall-clock session as S32 per the "
                "campaign plan's adaptive rule that audit sessions may absorb the next cluster when "
                "throughput allows). Full-cluster census of 2D3D (291 items, no sampling). Result "
                "feeds the S36 decision ledger. Judgment file: state/integration/judgments-2d3d-v1.jsonl; "
                "aggregate: reports/integration/s33-2d3d-judgments.json."
            )
            break
    for t in queue:
        if t["task_id"] == "INTEG-004" and t["status"] == "queued":
            break
    else:
        queue.append(INTEG_004)
    QUEUE.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in queue))
    report = reg.validate_task_queue(QUEUE, REPO / "schemas" / "task.schema.json")
    if not report["valid"]:
        print(f"QUEUE INVALID: {report['errors']}")
        return 1
    print(f"task queue valid: INTEG-003 completed, INTEG-004 queued ({len(queue)} tasks)")

    # ---- current-state ----
    cs = json.loads(CURRENT.read_text())
    cs["current_task_id"] = "INTEG-004"
    cs["stage"] = "integration-campaign (S32 MEDNLP + S33 2D3D judgments complete; S34 SYNPATH+VAULTX next)"
    cs["notes"] = (
        "INTEG campaign S32+S33 complete (both executed in this wall-clock session): MEDNLP "
        "(368/368: 89 covered / 12 equivalent / 70 partial / 197 absent) and 2D3D (291/291: "
        "28 covered / 8 equivalent / 64 partial / 191 absent) fully judged with mechanically "
        "verified quotes and 41/41 + 30/30 orchestrator re-review agreement. 659/1,233 items "
        "judged (53.4%). Next: S34 SYNPATH+VAULTX (237 items), S35 rest, S36 decisions."
    )
    cs["last_verified_checkpoint"] = str(CHECKPOINT.relative_to(REPO))
    CURRENT.write_text(json.dumps(cs, indent=4) + "\n")

    # ---- checkpoint ----
    checkpoint = {
        "session": 33,
        "task_id": "INTEG-003",
        "date": "2026-11-06",
        "phase": "integration-campaign-audit",
        "work_completed": [
            "packed the 291 2D3D items into 24 bounded judgment groups (section-coherent, max 18 items; lexical hints attached) via scripts/s33_pack_groups.py",
            "ran 24 independent subagent judgment groups (all completed cleanly on first run): each judge read candidate notes and grepped the vault for surface + alternative terminology before any absent verdict",
            "mechanically validated all 291 judgments (schema, exact set coverage, verbatim-quote verification, absent discipline): VALIDATION PASSED 291/291",
            "orchestrator re-review of a stratified 30-item sample (10.3%): 30/30 agreement",
            "wrote the canonical judgment file + aggregate report; queued INTEG-004 (S34: SYNPATH+VAULTX); updated ledger/handoff/README",
            "note: S32 and S33 were executed within the same wall-clock session under the campaign plan's adaptive rule (audit sessions may absorb the next cluster when throughput allows); both are recorded as separate budget sessions with separate checkpoints and task rows",
        ],
        "changed_paths": [
            "scripts/s33_pack_groups.py (new)",
            "scripts/s33_validate_judgments.py (new)",
            "scripts/s33_closeout.py (new)",
            "state/integration/judgments-2d3d-v1.jsonl (new; 291 records)",
            "reports/integration/s33-2d3d-groups.json (new; committed manifest)",
            "reports/integration/s33-2d3d-judgments.json (new; aggregate)",
            "state/task-queue.jsonl (INTEG-003 completed; INTEG-004 queued)",
            "state/current-state.json",
            "state/checkpoints/checkpoint-2026-11-06-integ-session33.json",
            "docs/ACCELERATED_COMPLETION_POLICY.md (ledger row 33)",
            "docs/agent-handoff/next-agent.md (rewritten for session 34)",
            "README.md (campaign progress)",
        ],
        "tests_run": [
            {"command": "python3 -m pytest -q (full suite at session end)", "result": "836 passed"},
            {"command": "vu verify-manifest x2 (sources)", "result": "276/276 + 333/333 byte-identical"},
            {"command": "python3 scripts/s33_validate_judgments.py", "result": "VALIDATION PASSED 291/291"},
        ],
        "git_state": {
            "branch": "main",
            "base_commit": "1616e7a (session-32 close)",
            "session_commits": "recorded in the session commit message",
            "push_verification": "per AGENTS.md section 13: push after commit and verify remote ref",
        },
        "open_findings": [
            "2D3D absent-rate 66% (191/291): the 3D-reconstruction layer (camera geometry, epipolar/multi-view, MVS, bundle adjustment, point clouds, depth, fusion, meshes, NeRF/3DGS, building decomposition, primitives) must be built as cluster-domain notes (decision C/D) in the S37+ waves",
            "64 partial items: the 2D/math core exists (RANSAC one-liner, homogeneous coordinates 2D-scope, NCC/SAD in non-MVS contexts, voxel grids as CNN input, Perceiver latents) — decision B expansions bridge 2D->3D",
            "8 equivalence mappings recorded (Image Pair Matching≡keypoint matching, Shared-Weight CNN≡parameter sharing, Feature Pyramids≡FPN, Geometric Correspondence≡keypoint correspondence, Frame Resizing≡image scaling, Backward Warping≡inverse mapping, System Orchestrator≡multi-agent orchestrator, Feature Extraction≡hierarchical feature extraction)",
        ],
        "next_task": {
            "task_id": "INTEG-004",
            "title": "Semantic coverage judgments — SYNPATH + VAULTX clusters (237 items)",
            "dependencies": ["INTEG-003 (completed)"],
            "resume": (
                "Follow AGENTS.md section 2 startup; read docs/INTEGRATION_CAMPAIGN_PLAN.md and this "
                "checkpoint; reuse the S32/S33 machinery: adapt scripts/s33_pack_groups.py to the "
                "SYNPATH+VAULTX clusters (237 items), run bounded judgment groups, validate with the "
                "same mechanical checks, re-review >=10%, aggregate, and queue INTEG-005 (S35: the "
                "remaining clusters MAPDIG+MATHSOLVER+WEATHER+NLME+MASTER-INDEX, 382 items)."
            ),
        },
        "accelerated_mode": {
            "session_number": 33,
            "budget_sessions_consumed": 3,
            "budget_sessions_remaining": 12,
            "deliverable_metric_moved": "campaign items semantically judged (cumulative)",
            "before": "368/1,233 items judged (MEDNLP complete; 29.8%)",
            "after": "659/1,233 items judged (MEDNLP + 2D3D complete; 53.4%) — this session added 291 2D3D judgments: 28 covered / 8 equivalent / 64 partial / 191 absent",
            "denominator": "1,233 unique inventory items; 291 2D3D items judged 291/291 (full census, no sampling)",
            "failed_session": False,
            "cause_if_failed": None,
            "deadline_position": "INTEG campaign session 3 of 15 (S31-S45); ahead of plan (two audit clusters completed in one wall-clock session under the adaptive rule)",
        },
    }
    CHECKPOINT.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\n")
    print(f"checkpoint written: {CHECKPOINT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
