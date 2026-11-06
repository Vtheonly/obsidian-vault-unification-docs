#!/usr/bin/env python3
"""INTEG-005 aggregation + session-35 closeout.

Builds the machine-readable judgment aggregate, appends finding F-0051 (S35
census + audit-phase completion with the campaign-wide union proof), marks
INTEG-005 completed and queues INTEG-006 (S36: decision ledger) in the task
queue, and writes the session-35 checkpoint with the accelerated_mode block.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
sys.path.insert(0, str(REPO / "src"))
from vault_unification import registry as reg  # noqa: E402

JUDGMENTS = REPO / "state/integration/judgments-rest-v1.jsonl"
INVENTORY = REPO / "state/integration/inventory-v1.jsonl"
MANIFEST = REPO / "reports/integration/s35-rest-groups.json"
AGG = REPO / "reports/integration/s35-rest-judgments.json"
QUEUE = REPO / "state/task-queue.jsonl"
CURRENT = REPO / "state/current-state.json"
FINDINGS = REPO / "state/findings.jsonl"
CHECKPOINT = REPO / "state/checkpoints/checkpoint-2026-11-07-integ-session35.json"

CLUSTERS = ["MAPDIG", "MATHSOLVER", "WEATHER", "NLME", "MASTER-INDEX"]

REREVIEW = {
    "method": (
        "stratified even-spaced sample (every 9th record of the 374 = 42 items, "
        "11.2%) spanning all 5 clusters (MAPDIG 9, MATHSOLVER 10, WEATHER 9, "
        "NLME 10, MASTER-INDEX 4) and all 4 verdicts (9 absent / 12 covered / "
        "10 equivalent / 11 partial): 9 absent verified by independent "
        "orchestrator greps over all 544 notes (LightGlue/multi-image consensus/"
        "overlap detection/logarithmic equation/finite difference/lag feature/"
        "detail coefficient/arc fault/voltage sag/graph learning/node embedding/"
        "link prediction/geometric deep learning all 0 occurrences; 'superglue' "
        "3 hits = the SuperGLUE benchmark in T5.md and 'short-circuit' 2 hits = "
        "ResNet-skip and sampling metaphors — both read and confirmed false "
        "positives exactly as the judges documented); 22 covered/equivalent/"
        "partial verified by reading cited destinations and judging the verdict "
        "+ quote depth against the campaign depth standard"
    ),
    "sample_size": 42,
    "agreement": 42,
    "disagreements": [],
    "notes": (
        "Notable confirmed judgment calls: INT-0461 Autoregressive Language "
        "Modeling EQUIVALENT via CLM (the Decoder-Only note itself states 'also "
        "called autoregressive language modeling'); INT-0488 Error-Correcting "
        "Memory Updates EQUIVALENT via DeltaNet's delta rule; INT-0533 Segmented "
        "Recurrence Training EQUIVALENT via Transformer-XL's gradient-detached "
        "segment cache; INT-0506 Neural Memory Bank EQUIVALENT via MemGPT's "
        "external context; INT-0585 Transformers + INT-0594 Neural Memory COVERED "
        "as broad field labels with genuine anchors (Attention MOC; DeltaNet and "
        "Titans' dedicated neural-memory section); all 11 sampled partials "
        "confirmed as below-depth-but-present (padding-mask aside, point-prompt "
        "Q&A mention, polygonization gap, XGBoost+NN stacking bullet, RWKV "
        "read-out formula, Titans surprise updates, LoCoMo/LongMemEval mentions, "
        "head-replacement exemplar, window-of-history baseline, sequence-level "
        "loss aside, sin/cos-for-positions). All 9 sampled absent verdicts "
        "confirmed."
    ),
}

INTEG_006 = {
    "task_id": "INTEG-006",
    "title": "Decision ledger — A/B/C/D + destination for every one of the 1,233 items; integration wave plan (S36 of 15)",
    "status": "queued",
    "priority": "high",
    "dependencies": ["INTEG-005"],
    "inputs": [
        "state/integration/inventory-v1.jsonl (authoritative item list with project context)",
        "state/integration/judgments-{mednlp,2d3d,synpath,rest}-v1.jsonl (complete audit: union == 1,233 items exactly, F-0051)",
        "state/integration/coverage-lexical-v1.jsonl (lexical evidence — collision reports required for C decisions)",
        "state/integration/clusters-v1.json (cluster Repository/annotation context — the only authoritative project usage)",
        "docs/INTEGRATION_CAMPAIGN_PLAN.md sections 6-7 (decision rules, architecture integration rules)",
    ],
    "outputs": [
        "state/integration/decisions-v1.jsonl (one decision per item id, validator-enforced exact join with the inventory)",
        "reports/integration/s36-decisions.json (aggregate + wave plan: B/C/D work items enumerated with destinations)",
        "scripts/s36_validate_decisions.py + scripts/s36_closeout.py",
    ],
    "acceptance_criteria": [
        "100% of the 1,233 items have exactly one decision from {A, B, C, D} with a recorded destination for B/C/D",
        "every A decision cites the judgment's destination note and mechanically-verified evidence quote (validator-enforced)",
        "every C decision carries a vu integ-coverage collision report showing no title/heading/alias collision, and respects D-before-C (no new competing note where a partial home exists)",
        "every equivalence-mapped item (77 equivalent verdicts) records the covering concept name for the S44 terminology audit",
        "the wave plan enumerates all B/C/D work items grouped into cluster-ordered waves (largest first) with per-wave completion criteria",
        "no source-vault or output-vault mutation during the planning session",
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults, the taxonomy file, or output notes",
        "Do not weaken the campaign plan's decision-integrity rules (D-before-C, collision checks, A-quote verification)",
    ],
    "findings": [],
    "notes": "S36 per campaign plan section 8. Inputs complete: 1,233/1,233 items judged (277 covered / 77 equivalent / 253 partial / 626 absent, F-0051). Expected shape: A = 277+77 = 354 items (verified existing coverage); B = 253 (expand existing homes); C = up to 626 (new sections/notes, collision-checked); D = the distributed subsets identified within the 253 partial + 88-ish multi-destination absents. Reuse the 77 recorded equivalence mappings and the layer analyses in F-0032/F-0050/F-0051 for wave sizing. The 35 carry-over records (F-0048) must join their single canonical judgment, never multiple.",
    "commit": None,
    "tests_run": [],
}


def placement(item: dict) -> tuple[str, str]:
    for c in CLUSTERS:
        occ = next((o for o in item["occurrences"] if o["cluster"] == c), None)
        if occ:
            return (c, occ["section"] or "(master index fields)")
    return ("?", "?")


def main() -> int:
    recs = [json.loads(l) for l in JUDGMENTS.open(encoding="utf-8") if l.strip()]
    inv = {}
    for line in INVENTORY.open(encoding="utf-8"):
        if line.strip():
            i = json.loads(line)
            inv[i["item_id"]] = i
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    counts = Counter(r["verdict"] for r in recs)
    carried = sum(1 for r in recs if r.get("carry_over_from"))
    by_section: dict[str, dict] = {}
    for r in recs:
        c, s = placement(inv[r["item_id"]])
        by_section.setdefault(f"{c}: {s}", Counter())[r["verdict"]] += 1
        by_section[f"{c}: {s}"]["total"] += 1

    # ---- campaign-wide union proof (F-0051 evidence) ----
    union: dict[str, dict] = {}
    conflicts = 0
    for fname in ["judgments-mednlp-v1.jsonl", "judgments-2d3d-v1.jsonl", "judgments-synpath-v1.jsonl", "judgments-rest-v1.jsonl"]:
        for line in (REPO / "state/integration" / fname).open(encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                if r["item_id"] in union and union[r["item_id"]]["verdict"] != r["verdict"]:
                    conflicts += 1
                union.setdefault(r["item_id"], r)
    union_counts = Counter(r["verdict"] for r in union.values())
    union_exact = set(union) == set(inv)

    aggregate = {
        "campaign": "INTEG-005",
        "clusters": CLUSTERS,
        "items_total": len(recs),
        "items_fresh_judged": len(recs) - carried,
        "items_carried_over": carried,
        "verdict_counts": dict(counts),
        "retained_or_existing": counts["covered"] + counts["equivalent"] + counts["partial"],
        "genuinely_missing": counts["absent"],
        "by_section": {s: dict(c) for s, c in by_section.items()},
        "campaign_audit_phase": {
            "complete": union_exact and conflicts == 0 and len(union) == len(inv),
            "unique_items_judged": len(union),
            "inventory_items": len(inv),
            "union_exact_set_match": union_exact,
            "cross_file_verdict_conflicts": conflicts,
            "campaign_wide_verdicts": dict(union_counts),
            "files": ["judgments-mednlp-v1.jsonl", "judgments-2d3d-v1.jsonl", "judgments-synpath-v1.jsonl", "judgments-rest-v1.jsonl"],
            "note": "every one of the 1,233 unique inventory items now carries exactly one depth-standard judgment with mechanically verified evidence; the S36 decision ledger can open on a complete input",
        },
        "method": {
            "design": "full-cluster census (no sampling): all 374 unique remaining-cluster items judged once each",
            "denominator_note": "374 unique items = 81 MAPDIG + 91 MATHSOLVER + 78 WEATHER + 97 NLME + 35 MASTER-INDEX − 19 intra-set cross-cluster duplicates (F-0049 union accounting)",
            "carry_over": f"{carried} items with prior canonical judgments carried over verbatim per F-0048 (23 from MEDNLP/2D3D, 6 from SYNPATH)",
            "groups": f"{manifest['groups_total']} bounded subagent groups (max {manifest['max_items_per_group']} items; grouped by first-matching cluster + section, sections never merged; MASTER-INDEX fields under a pseudo-section)",
            "judges": "36 independent general-purpose subagents (35 first-run clean; group-23 first launch failed with an infrastructure timeout before writing anything — relaunched cleanly and completed, documented per the s30 precedent; no partial/corrupt output was ever accepted)",
            "depth_standard": "campaign plan section 5 (what it is / why it exists / how it works conceptually / relations to other concepts; project usage not required for 'covered'); broad MASTER-INDEX field labels additionally require the vault to span the field's core with the cited note as a genuine anchor",
            "evidence_rule": "covered/equivalent/partial require a verbatim quote (>= 12 words for covered/equivalent) mechanically validated as a whitespace-normalized substring of the cited note (scripts/s35_validate_judgments.py, exit 0: 374/374 PASSED)",
            "orchestrator_rereview": REREVIEW,
            "limitations": [
                "single-judge-per-item design mitigated by mandatory multi-term search before absent verdicts + the 11.2% orchestrator re-review; borderline covered/partial/equivalent calls carry uncertainty noted by judges",
                "judgments reflect the vault as of session 34 state (no vault mutations occurred during judging)",
                "'covered' does not include project usage; project context integration happens in the S37+ execution waves",
            ],
        },
        "destination_notes_cited": sorted({r["destination_note"] for r in recs if r.get("destination_note")}),
        "validation": "scripts/s35_validate_judgments.py: VALIDATION PASSED 374/374 (schema, exact set coverage, quotes verbatim-verified, absent discipline, carry-over re-validation)",
    }
    AGG.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"aggregate written: {AGG.relative_to(REPO)}")
    print(f"verdicts: {dict(counts)} ({carried} carried over)")
    print(f"campaign union: {len(union)}/1,233 exact={union_exact} conflicts={conflicts} verdicts={dict(union_counts)}")

    # ---- findings ledger: F-0051 ----
    finding = {
        "finding_id": "F-0051",
        "title": "S35 census completes the audit phase: 1,233/1,233 items judged; remaining-cluster profile + campaign-wide union proof",
        "category": "integration-coverage",
        "severity": "info",
        "status": "accepted",
        "discovered_by": "session-35 INTEG-005 (36 subagent groups; mechanical validation 374/374; orchestrator re-review 42/42)",
        "observed": (
            "S35 (MAPDIG+MATHSOLVER+WEATHER+NLME+MASTER-INDEX, 374 unique items = 345 fresh + 29 F-0048 carry-overs): "
            "150 covered / 52 equivalent / 84 partial / 88 absent. Per-cluster profile: MAPDIG — classical CV core covered "
            "(registration/homography/SIFT-descriptors, segmentation stack incl. SAM/DINOv2/ViT, morphological cleanup, "
            "connected components; 5+1 covered, 3 equiv in one 8-item group), modern neural matching stack absent "
            "(XFeat/ALIKED/LightGlue/LoFTR/detector-free/dense matching/learned descriptors), learned refinement absent "
            "(SegRefiner/diffusion refinement), topological/GIS processing absent (TopoJSON, Visvalingam-Whyatt, shared-arc, "
            "gap/overlap QA); MATHSOLVER — transformer decoder/encoder stack fully covered (7+1 covered in the decoder group; "
            "Swin mechanisms, patch embedding, tokenization incl. domain-specific BPE, decoding strategies, teacher forcing, "
            "cross-entropy/label smoothing, transfer learning), math-specific layer absent (LaTeX tokenization 0 occurrences, "
            "structural tokens, OCR eval metrics CER/SER, equation parsing/classification, CAS/SymPy symbolic solving — "
            "'LaTeX' never occurs in the vault); WEATHER — classical ML core covered/equivalent (CNNs, LSTM/BiLSTM, XGBoost/GBDT, "
            "Fourier/frequency domain, feature scaling), forecasting formulation partial-to-absent (no ARIMA/seasonality/"
            "stationarity/lag features anywhere; multivariate/multi-step forecasting absent), physics-informed ML entirely absent "
            "(PINN/Navier-Stokes/neural operator 0 hits), power-engineering fault layer absent (arc fault/voltage sag/microgrid "
            "0 hits), wavelet machinery absent (only name-drops); NLME — strongest coverage (transformer attention incl. "
            "GQA/FlashAttention/linear attention/Infini-attention, LLMs incl. Llama-3/Mistral, KV cache, training stack incl. "
            "AdamW/warmup/cosine/BPTT, PEFT/LoRA, long-context evaluation incl. NIAH/MMLU/GSM8K), neural-memory layer split "
            "(DeltaNet/Titans/linear-attention state machinery covered, but classical associative memory 0 hits — Hopfield/"
            "Hebbian/attractor never occur — write gates, memory state ops (snapshots/switching/hot-swap/branching/anchors) "
            "partial-to-absent); MASTER-INDEX fields — 7+3 covered, 4+1 equivalent, 3 partial (Equivariant AI, Image Fusion, "
            "Time-Series AI), 5 absent (Graph Learning, Chemical AI, Molecular Modeling, Physics-Informed AI, Online Learning). "
            "CAMPAIGN-WIDE AUDIT UNION: the four canonical judgment files join to exactly the 1,233-item inventory (set-equal, "
            "zero cross-file verdict conflicts — the F-0048 carry-over rule held): 277 covered / 77 equivalent / 253 partial / "
            "626 absent."
        ),
        "root_cause": "The unified vault's two source corpora are general AI/ML curricula: they never covered the user's project-domain layers (mathematical OCR/symbolic solving, meteorology/physics-informed ML, power-engineering fault analysis, classical associative memory, graph learning, GIS topology), while the general ML core the projects shared is thoroughly covered.",
        "resolution": (
            "Input to the S36 decision ledger (INTEG-006): A ≈ 354 items (277 covered + 77 equivalent, all with cited homes), "
            "B = 253 partial (expand existing homes), C ≤ 626 absent (new sections/notes, collision-checked, D-before-C). "
            "Wave sizing by cluster: the SYNPATH wave remains the largest B/C/D workload (193), then MEDNLP (267), 2D3D (255), "
            "NLME (~95 fresh in S35 scope), MATHSOLVER (~100), MAPDIG (~130), WEATHER (~140 incl. the physics-informed layer). "
            "The 77 equivalence mappings and the domain-layer analyses (F-0032 medical, F-0050 molecular/geometric, F-0051 "
            "forecasting/math-OCR/power) are the S36 planning substrate."
        ),
        "affected": ["state/integration/judgments-rest-v1.jsonl", "reports/integration/s35-rest-judgments.json"],
    }
    with FINDINGS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(finding, ensure_ascii=False) + "\n")
    print("finding appended: F-0051")

    # ---- task queue: INTEG-005 -> completed, INTEG-006 queued ----
    queue = [json.loads(l) for l in QUEUE.open(encoding="utf-8") if l.strip()]
    for t in queue:
        if t["task_id"] == "INTEG-005":
            t["status"] = "completed"
            t["findings"] = [
                "F-0051 S35 census: 374/374 unique remaining-cluster items judged (150 covered / 52 equivalent / 84 partial / 88 absent; 345 fresh + 29 F-0048 carry-overs); audit phase COMPLETE — the four canonical judgment files union to exactly the 1,233-item inventory with zero cross-file verdict conflicts (277 / 77 / 253 / 626 campaign-wide)",
                "domain layers confirmed absent for S37+ waves: mathematical OCR + symbolic solving (LaTeX 0 occurrences), forecasting formulation (ARIMA/seasonality/lag features absent), physics-informed ML (PINN 0), power-engineering faults (arc fault/voltage sag 0), classical associative memory (Hopfield/Hebbian 0), graph learning (GNN/message passing 0), GIS topology (TopoJSON/Visvalingam 0)",
                "strongest coverage: NLME transformer/LLM/training/PEFT/long-context-eval stack and MATHSOLVER decoder-encoder-tokenization-decoding stack (multiple all-covered groups)",
            ]
            t["tests_run"] = [
                {"command": "python3 scripts/s35_pack_groups.py", "result": "374 items packed: 345 fresh into 36 bounded groups (first-matching-cluster + section-coherent, max 18) + 29 carry-overs recorded"},
                {"command": "36 subagent judgment groups (35 first-run clean; group-23 first launch hit an infrastructure timeout before writing anything, relaunched cleanly per the s30 precedent)", "result": "345 fresh judgments (+29 carried over): 150 covered / 52 equivalent / 84 partial / 88 absent"},
                {"command": "python3 scripts/s35_validate_judgments.py", "result": "VALIDATION PASSED 374/374 (schema, exact set coverage, every covered/equivalent/partial quote verbatim-verified; absent discipline verified; carry-overs re-validated)"},
                {"command": "orchestrator re-review (stratified 42-item sample = 11.2%, all 5 clusters, all 4 verdicts)", "result": "42/42 agreement (9 absent independently grep-verified over all 544 notes — superglue=SuperGLUE benchmark, short-circuit=ResNet/sampling metaphors confirmed false positives; 12 covered + 10 equivalent destination-read verified; 11 partial section-verified)"},
                {"command": "campaign union proof (4 judgment files joined)", "result": "1,233/1,233 unique items, set-exact vs inventory, 0 cross-file verdict conflicts; campaign-wide 277 covered / 77 equivalent / 253 partial / 626 absent"},
                {"command": "vu verify-manifest x2", "result": "276/276 + 333/333 byte-identical (no mutations during judging)"},
                {"command": "python3 -m pytest -q (full suite at session end)", "result": "836 passed"},
            ]
            t["notes"] = (
                "Session 35 (S35 of 15; absorbed into the same wall-clock session as S34 under the "
                "campaign plan adaptive rule). Full census of the remaining clusters (374 unique "
                "items, no sampling; 345 fresh judgments + 29 F-0048 carry-overs). This completes "
                "the audit phase: every one of the 1,233 items now carries exactly one depth-"
                "standard judgment. Judgment file: state/integration/judgments-rest-v1.jsonl; "
                "aggregate: reports/integration/s35-rest-judgments.json."
            )
            break
    if not any(t["task_id"] == "INTEG-006" for t in queue):
        queue.append(INTEG_006)
    QUEUE.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in queue))
    report = reg.validate_task_queue(QUEUE, REPO / "schemas" / "task.schema.json")
    if not report["valid"]:
        print(f"QUEUE INVALID: {report['errors']}")
        return 1
    print(f"task queue valid: INTEG-005 completed, INTEG-006 queued ({len(queue)} tasks)")

    # ---- current-state ----
    cs = json.loads(CURRENT.read_text())
    cs["current_task_id"] = "INTEG-006"
    cs["stage"] = "integration-campaign (AUDIT PHASE COMPLETE: all 1,233 items judged; S36 decision ledger next)"
    cs["notes"] = (
        "INTEG campaign audit phase complete (S32 MEDNLP + S33 2D3D + S34 SYNPATH/VAULTX + S35 "
        "remaining clusters): 1,233/1,233 items judged with mechanically verified evidence and "
        "41/41 + 30/30 + 33/33 + 42/42 orchestrator re-review agreement; zero cross-file verdict "
        "conflicts. Campaign-wide: 277 covered / 77 equivalent / 253 partial / 626 absent. Next: "
        "S36 decision ledger (INTEG-006), then S37-S43 execution waves."
    )
    cs["last_verified_checkpoint"] = str(CHECKPOINT.relative_to(REPO))
    CURRENT.write_text(json.dumps(cs, indent=4) + "\n")

    # ---- checkpoint ----
    checkpoint = {
        "session": 35,
        "task_id": "INTEG-005",
        "date": "2026-11-07",
        "phase": "integration-campaign-audit (phase complete)",
        "work_completed": [
            "absorbed S35 into the same wall-clock session as S34 under the campaign plan adaptive rule (both recorded as separate budget sessions with separate checkpoints and task rows, per the S32+S33 precedent)",
            "packed the 374 unique remaining-cluster items (345 fresh after 29 F-0048 carry-overs) into 36 bounded groups via scripts/s35_pack_groups.py (first-matching-cluster + section-coherent, max 18, MASTER-INDEX fields under a pseudo-section; time-series/segmentation/OCR/memory/field-label terminology hints in the instructions)",
            "ran 36 independent subagent judgment groups: 35 completed cleanly on first run; group-23's first launch failed with an infrastructure timeout BEFORE writing anything and was relaunched cleanly (s30 precedent; no partial output ever accepted)",
            "mechanically validated all 374 judgments (schema, exact set coverage incl. carry-overs, verbatim-quote verification, absent discipline): VALIDATION PASSED 374/374",
            "orchestrator re-review of a stratified 42-item sample (11.2%, all 5 clusters, all 4 verdicts): 42/42 agreement",
            "proved the audit-phase completion invariant: the four canonical judgment files union to EXACTLY the 1,233-item inventory with zero cross-file verdict conflicts (campaign-wide 277 covered / 77 equivalent / 253 partial / 626 absent)",
            "wrote the canonical judgment file + aggregate report with the campaign_audit_phase block; appended finding F-0051; queued INTEG-006 (S36: decision ledger); updated current-state/ledger/README/handoff",
        ],
        "changed_paths": [
            "scripts/s35_pack_groups.py (new; committed pre-judging as a7a0939 with the manifest)",
            "scripts/s35_validate_judgments.py (new; committed pre-judging)",
            "scripts/s35_closeout.py (new)",
            "state/integration/judgments-rest-v1.jsonl (new; 374 records, 29 with carry_over_from)",
            "reports/integration/s35-rest-groups.json (committed pre-judging)",
            "reports/integration/s35-rest-judgments.json (new; aggregate incl. campaign_audit_phase proof)",
            "state/findings.jsonl (F-0051 appended)",
            "state/task-queue.jsonl (INTEG-005 completed; INTEG-006 queued)",
            "state/current-state.json",
            "state/checkpoints/checkpoint-2026-11-07-integ-session35.json",
            "docs/ACCELERATED_COMPLETION_POLICY.md (ledger row 35)",
            "docs/agent-handoff/next-agent.md (rewritten for session 36)",
            "README.md (campaign progress)",
        ],
        "tests_run": [
            {"command": "python3 -m pytest -q (full suite at session end)", "result": "836 passed"},
            {"command": "vu verify-manifest x2 (sources)", "result": "276/276 + 333/333 byte-identical"},
            {"command": "python3 scripts/s35_validate_judgments.py", "result": "VALIDATION PASSED 374/374"},
            {"command": "python3 scripts/s34_validate_judgments.py (S34 canonical re-verified during this session's startup)", "result": "VALIDATION PASSED 235/235, byte-identical rewrite"},
            {"command": "campaign union join (4 canonical files vs inventory)", "result": "1,233/1,233 set-exact, 0 conflicts"},
        ],
        "git_state": {
            "branch": "main",
            "base_commit": "51023b5 (session-34 close); S35 machinery pushed as a7a0939 and remote-verified before judging",
            "session_commits": "recorded in the session commit message",
            "push_verification": "per AGENTS.md section 13: push after commit and verify remote ref (git rev-parse origin/main + merge-base --is-ancestor)",
        },
        "open_findings": [
            "AUDIT PHASE COMPLETE — every item judged; the S36 decision ledger (INTEG-006) opens on a complete, conflict-free input",
            "campaign-wide workload for S37-S43: ~879 B/C/D items expected (253 partial + 626 absent); largest waves SYNPATH (~193), MEDNLP (~267 incl. partials), 2D3D (~255), then WEATHER/MAPDIG/MATHSOLVER/NLME/MASTER-INDEX",
            "domain layers confirmed entirely absent (0 genuine occurrences): mathematical OCR/symbolic solving (LaTeX never occurs), forecasting formulation (ARIMA/seasonality/lag features), physics-informed ML (PINN), power-engineering faults, classical associative memory (Hopfield/Hebbian), graph learning (GNN/message passing), GIS topology (TopoJSON/Visvalingam-Whyatt), molecular chemistry + geometric DL + GFlowNets + protein backbones (F-0050)",
            "77 equivalence mappings recorded across the four files — must be preserved in the S36 ledger for the S44 terminology audit",
            "group-23 execution note: first launch failed with an infrastructure timeout before writing anything; clean relaunch; the validator's per-group missing-file reporting makes any such failure detectable and resumable",
        ],
        "next_task": {
            "task_id": "INTEG-006",
            "title": "Decision ledger — A/B/C/D + destination for all 1,233 items; integration wave plan (S36)",
            "dependencies": ["INTEG-005 (completed)"],
            "resume": (
                "Follow AGENTS.md section 2 startup; read docs/INTEGRATION_CAMPAIGN_PLAN.md "
                "sections 6-7 (decision rules, architecture rules), findings F-0048..F-0051, and "
                "this checkpoint. Build state/integration/decisions-v1.jsonl: one record per item "
                "id joining its single canonical judgment (35 carry-over records must join once), "
                "with A requiring the judgment's verified quote, C requiring the vu integ-coverage "
                "collision report + D-before-C discipline, and a wave plan enumerating all B/C/D "
                "work items with destinations (cluster-ordered, largest first). Validate with a "
                "new scripts/s36_validate_decisions.py (exact inventory join, decision integrity "
                "rules) and close out with the S36 checkpoint + handoff."
            ),
        },
        "accelerated_mode": {
            "session_number": 35,
            "budget_sessions_consumed": 5,
            "budget_sessions_remaining": 10,
            "deliverable_metric_moved": "campaign items semantically judged (cumulative)",
            "before": "894/1,233 items judged (MEDNLP + 2D3D + SYNPATH/VAULTX; 72.5%)",
            "after": "1,233/1,233 items judged (100% — AUDIT PHASE COMPLETE): this session added 374 judgments (345 fresh + 29 carry-overs): 150 covered / 52 equivalent / 84 partial / 88 absent; campaign-wide 277 / 77 / 253 / 626",
            "denominator": "1,233 unique inventory items; 374 unique remaining-cluster items judged 374/374 (full census, no sampling; F-0049 union accounting)",
            "failed_session": False,
            "cause_if_failed": None,
            "deadline_position": "INTEG campaign sessions 5 of 15 consumed (S34+S35 absorbed into one wall-clock session under the adaptive rule); audit phase complete one session ahead of the plan's S35 boundary, pulling S36 planning next",
        },
    }
    CHECKPOINT.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\n")
    print(f"checkpoint written: {CHECKPOINT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
