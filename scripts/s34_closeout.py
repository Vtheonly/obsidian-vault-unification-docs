#!/usr/bin/env python3
"""INTEG-004 aggregation + session-34 closeout.

Builds the machine-readable judgment aggregate (denominators, per-section
breakdown, method, re-review record), appends findings F-0048..F-0050, marks
INTEG-004 completed and queues INTEG-005 (S35: remaining clusters) in the
task queue, and writes the session-34 checkpoint with the accelerated_mode
block.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
sys.path.insert(0, str(REPO / "src"))
from vault_unification import registry as reg  # noqa: E402

JUDGMENTS = REPO / "state/integration/judgments-synpath-v1.jsonl"
INVENTORY = REPO / "state/integration/inventory-v1.jsonl"
MANIFEST = REPO / "reports/integration/s34-synpath-groups.json"
AGG = REPO / "reports/integration/s34-synpath-judgments.json"
QUEUE = REPO / "state/task-queue.jsonl"
CURRENT = REPO / "state/current-state.json"
FINDINGS = REPO / "state/findings.jsonl"
CHECKPOINT = REPO / "state/checkpoints/checkpoint-2026-11-07-integ-session34.json"

REREVIEW = {
    "method": (
        "stratified even-spaced sample (every 8th record of the 235 = 30 items, "
        "12.8%) plus 3 added equivalent-verdict items (the trickiest class) = 33 "
        "items (14.0%): 20 absent verified by independent orchestrator greps over "
        "all 544 notes of the item names, the judges' search terms, and "
        "orchestrator-chosen alternatives (all 544-note scans: PaiNN/SchNet/GemNet/"
        "EGNN/synthon/retrosynthesis/torsion/dihedral/chemoselectiv*/deprotect*/"
        "resonance/heavy-atom/drug-like/Lipinski/QED/ligand/SE(3)/conformer/"
        "stereochem*/SMILES/invariant-point all 0 occurrences; every nonzero hit "
        "independently read and confirmed a false positive: 'receptor' = retinal "
        "photoreceptors, 'graph neural' x3 = bare name-drops in other contexts, "
        "'message passing' x2 = multi-agent homonym, 'e(3)' x2 = np.eye(3)/range(3) "
        "code); 6 covered + 3 equivalent verified by reading the cited destination "
        "notes and judging verdict + quote depth against the campaign depth "
        "standard; 4 partial verified by reading the cited sections and confirming "
        "the below-depth-but-present characterization"
    ),
    "sample_size": 33,
    "agreement": 33,
    "disagreements": [],
    "notes": (
        "Sample spans all 14 sections and all 4 verdict classes. Notable confirmed "
        "judgment calls: INT-0033 QKV covered (dedicated Queries Keys and Values "
        "note: database analogy, matrix form, three roles); INT-0041 Softmax "
        "Attention covered (dedicated Scaled Dot-Product Attention note + Linear "
        "Attention baseline framing + MiniMax-01 hybrid analysis — consistent with "
        "the prior MEDNLP judgment of INT-0031, the same underlying mechanism); "
        "INT-0209 Checkpoint Recovery covered via the capstone's dedicated "
        "Sharded-checkpointing + Recovery-from-failures sections; INT-0053 "
        "Distance-Based Attention Bias EQUIVALENT via ALiBi (full-depth additive "
        "score bias by distance); INT-0103 Conditional Probability Factorization "
        "EQUIVALENT via the chain-rule-of-probability treatment (formula + LM "
        "training + generation connections); INT-0207 Gradient Stability EQUIVALENT "
        "via the gradient-flow concept in Vanishing and Exploding Gradients. All 20 "
        "sampled absent verdicts confirmed: the molecular-chemistry / geometric-RL "
        "vocabulary has zero genuine vault occurrences."
    ),
}

INTEG_005 = {
    "task_id": "INTEG-005",
    "title": "Semantic coverage judgments — MAPDIG + MATHSOLVER + WEATHER + NLME + MASTER-INDEX clusters, 374 unique items (S35 of 15)",
    "status": "queued",
    "priority": "high",
    "dependencies": ["INTEG-004"],
    "inputs": [
        "state/integration/inventory-v1.jsonl (MAPDIG/MATHSOLVER/WEATHER/NLME/MASTER-INDEX items; authoritative item list)",
        "state/integration/coverage-lexical-v1.jsonl (lexical evidence per item — substrate, never a decision)",
        "state/integration/clusters-v1.json (cluster contexts and Repository annotations)",
        "output/Unified-Vault/ (544 notes, read-only during judging)",
        "state/integration/judgments-{mednlp,2d3d,synpath}-v1.jsonl (carry-over source for the 29 pre-judged overlapping items)",
    ],
    "outputs": [
        "state/integration/judgments-rest-v1.jsonl (one judgment per remaining-cluster item)",
        "reports/integration/s35-rest-groups.json + s35-rest-judgments.json",
    ],
    "acceptance_criteria": [
        "every one of the 374 unique remaining-cluster items receives exactly one judgment with a verdict from {covered, partial, absent, equivalent} at the campaign depth standard (374 = 81 MAPDIG + 91 MATHSOLVER + 78 WEATHER + 97 NLME + 35 MASTER-INDEX − 19 cross-cluster duplicates within the set, per the F-0049 union accounting)",
        "the 29 items already judged in prior canonical files are carried over per the F-0048 carry-over rule (verdict/destination/quote preserved verbatim with carry_over_from provenance), leaving 345 fresh judgments",
        "every covered/equivalent judgment cites a destination note and a verbatim evidence quote mechanically verified as a substring of that note",
        "the orchestrator independently re-reviews at least 10% of judgments and records agreement/disagreement",
        "no source-vault or output-vault mutation during the judgment phase",
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults, the taxonomy file, or output notes",
        "Do not skip items or batch-reason over groups of items without per-item records",
    ],
    "findings": [],
    "notes": "S35 per campaign plan section 8; completes the audit phase (after S32 MEDNLP, S33 2D3D, S34 SYNPATH+VAULTX). Expected profile from S31 lexical evidence: MAPDIG time-series/geospatial vocabulary, WEATHER meteorology, MATHSOLVER OCR/document parsing, NLME long-context/memory architectures — likely covered on the general-ML core (attention, transformers, normalization) and absent on the domain-specific layers. Reuse the S34 machinery end-to-end including the carry-over rule (F-0048): 23 of the 374 items already have MEDNLP/2D3D judgments and 6 more will have SYNPATH judgments after S34 (29 total).",
    "commit": None,
    "tests_run": [],
}


def section_of(item: dict) -> str:
    for cluster in ("SYNPATH", "VAULTX"):
        for occ in item["occurrences"]:
            if occ["cluster"] == cluster:
                return f"{cluster}: {occ['section']}"
    return "?"


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
        s = section_of(inv[r["item_id"]])
        by_section.setdefault(s, Counter())[r["verdict"]] += 1
        by_section[s]["total"] += 1

    aggregate = {
        "campaign": "INTEG-004",
        "clusters": ["SYNPATH", "VAULTX"],
        "items_total": len(recs),
        "items_fresh_judged": len(recs) - carried,
        "items_carried_over": carried,
        "verdict_counts": dict(counts),
        "retained_or_existing": counts["covered"] + counts["equivalent"] + counts["partial"],
        "genuinely_missing": counts["absent"],
        "by_section": {s: dict(c) for s, c in by_section.items()},
        "method": {
            "design": "full-cluster census (no sampling): all 235 unique SYNPATH+VAULTX items judged once each",
            "denominator_note": (
                "235 unique items = 209 SYNPATH + 28 VAULTX − 2 dual-cluster items "
                "(INT-0052 Spatial Distance Bias, INT-0202 Vector-Jacobian Products) "
                "counted once; the plan's '237' arithmetic double-counted them (F-0049)"
            ),
            "carry_over": (
                "6 items with prior canonical judgments (INT-0031/0032/0046/0047 from "
                "MEDNLP, INT-0187/0192 from 2D3D) carried over verbatim with "
                "carry_over_from provenance per the one-item-one-judgment rule (F-0048)"
            ),
            "groups": f"{manifest['groups_total']} bounded subagent groups (max {manifest['max_items_per_group']} items; grouped by cluster+section, sections never merged)",
            "judges": "17 independent general-purpose subagents reading destination notes and grepping the vault for surface forms + alternative terminology before any absent verdict (chemistry/equivariance/RL terminology hints added to the S34 judging instructions)",
            "depth_standard": "campaign plan section 5 (what it is / why it exists / how it works conceptually / relations to other concepts; project usage not required for 'covered')",
            "evidence_rule": "covered/equivalent/partial require a verbatim quote (>= 12 words for covered/equivalent) mechanically validated as a whitespace-normalized substring of the cited note (scripts/s34_validate_judgments.py, exit 0: 235/235 PASSED)",
            "orchestrator_rereview": REREVIEW,
            "limitations": [
                "single-judge-per-item design mitigated by mandatory multi-term search before absent verdicts + the 14.0% orchestrator re-review; borderline covered/partial calls carry uncertainty noted by judges",
                "judgments reflect the vault as of session 33 state (no vault mutations occurred during judging)",
                "'covered' does not include project usage; project context integration happens in the S37+ execution waves",
            ],
        },
        "destination_notes_cited": sorted({r["destination_note"] for r in recs if r.get("destination_note")}),
        "validation": "scripts/s34_validate_judgments.py: VALIDATION PASSED 235/235 (schema, exact set coverage, quotes verbatim-verified, absent discipline, carry-over re-validated against current vault state)",
    }
    AGG.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"aggregate written: {AGG.relative_to(REPO)}")
    print(f"verdicts: {dict(counts)} ({carried} carried over)")

    # ---- findings ledger: F-0048, F-0049, F-0050 ----
    new_findings = [
        {
            "finding_id": "F-0048",
            "title": "INTEG carry-over rule: one item = one judgment across clusters (first cross-cluster item overlap, S34)",
            "category": "campaign-methodology",
            "severity": "info",
            "status": "accepted",
            "discovered_by": "session-34 INTEG-004 (SYNPATH+VAULTX packing: 6 of the target items already had canonical judgments)",
            "observed": (
                "The campaign's first three audit clusters (MEDNLP, 2D3D) had zero item overlap, but SYNPATH+VAULTX shares 6 items with them (INT-0031 Scaled Dot-Product Attention, INT-0032 Multi-Head Attention, INT-0046 Attention Masking, INT-0047 Padding Masking — MEDNLP; INT-0187 Curriculum Learning, INT-0192 Data Augmentation — 2D3D). Multi-cluster membership is intrinsic to the taxonomy (14 SYNPATH/VAULTX items belong to 2+ clusters; S35's 374 items include 29 already judged)."
            ),
            "root_cause": "Cluster-scoped judgment files vs item-keyed decision ledger: the S36 ledger is keyed by item id, so an item must carry exactly one judgment.",
            "resolution": (
                "Binding rule recorded in the S34 manifest and applied: items already judged in a prior canonical judgment file are carried over verbatim (verdict, destination, quote, rationale preserved; carry_over_from provenance added), NOT re-judged. Justification: the vault is byte-identical since those judgments (verified every session), so the verdict cannot legitimately change, and re-judging risks conflicting verdicts for the same item. The validator re-validates every carried-over quote against the current vault state and enforces exact set coverage. S35 must apply the same rule (29 carry-overs expected)."
            ),
            "affected": ["state/integration/judgments-synpath-v1.jsonl", "reports/integration/s34-synpath-groups.json", "scripts/s34_validate_judgments.py"],
        },
        {
            "finding_id": "F-0049",
            "title": "Plan arithmetic correction: SYNPATH+VAULTX = 235 unique items, not 237 (dual-cluster items double-counted)",
            "category": "campaign-methodology",
            "severity": "info",
            "status": "fixed",
            "discovered_by": "session-34 INTEG-004 packing (deterministic union of SYNPATH ∪ VAULTX inventory items)",
            "observed": "The campaign plan S34 row and the INTEG-004 task row state '237 items (209 + 28)', but 2 items (INT-0052 Spatial Distance Bias, INT-0202 Vector-Jacobian Products) belong to BOTH clusters and are single inventory items judged once each: the unique-item denominator is 235. The campaign's coverage formula counts unique inventory items (1,233 total), so no item is lost or skipped — the '237' figure was set arithmetic, not a coverage gap.",
            "root_cause": "Plan/session-33 task text summed per-cluster counts without deduplicating cross-cluster items.",
            "resolution": "Denominator corrected to 235 in the S34 manifest, aggregate report, task queue, and checkpoint. Each dual-cluster item is judged once, in its first-occurrence cluster section (both placed in SYNPATH sections; their VAULTX occurrences are recorded on the item records). INTEG-005 (S35) uses the same union accounting: 374 unique items, not the naive 382.",
            "affected": ["docs/INTEGRATION_CAMPAIGN_PLAN.md (S34/S35 session rows — arithmetic noted, structure unchanged)", "state/task-queue.jsonl (INTEG-004 acceptance criteria; INTEG-005 title)"],
        },
        {
            "finding_id": "F-0050",
            "title": "SYNPATH+VAULTX census: molecular-chemistry and geometric-deep-learning layers ~65% missing; general training/attention core covered",
            "category": "integration-coverage",
            "severity": "info",
            "status": "accepted",
            "discovered_by": "session-34 INTEG-004 (17 subagent groups; mechanical validation 235/235; orchestrator re-review 33/33)",
            "observed": (
                "235 items: 36 covered / 6 equivalent / 41 partial / 152 absent (64.7% absent). The vault has ZERO molecular-chemistry content (synthon/retrosynthesis/torsion/dihedral/conformer/stereochem*/SMILES/chemoselect*/deprotect*/resonance/heavy-atom/ligand/drug-like/Lipinski/QED/pharmacophore: 0 occurrences in all 544 notes), ZERO geometric-deep-learning content (geometric deep learning/PaiNN/SchNet/GemNet/EGNN/SE(3)/message passing in the graph sense: 0; 'graph neural' appears only as 3 bare name-drops), ZERO GFlowNet content (GFlowNet/trajectory balance/forward-backward policy: 0), and ZERO protein-backbone content (Equiformer/invariant point attention/receptor/pocket in the molecular sense: 0). Covered/equivalent/partial concentrate in the general layers: attention mechanisms (QKV, cross-attention, softmax attention, log-softmax, pre-norm, residual attention: covered), training/optimization (autodiff, gradient clipping, activation checkpointing, mixed precision incl. FP32 baseline, NaN detection, checkpoint recovery, numerical stability, gradient-flow ≡ gradient stability: covered), supervised learning, MDP-based generation, self-supervised pretraining, Gaussian RBF (kernel-trait treatment), relative position encoding, additive distance bias ≡ ALiBi, chain-rule factorization ≡ conditional probability factorization. 41 partial items = decision-B workload: generic mechanism covered, molecular/geometric instantiation missing (equivariance = CNN translation only, distance encodings absent, action sampling mentioned not explained, coordinate jittering = pixel noise only, geometric attention = Swin 2D positional bias only, MLM/denoising present but residue/coordinate forms absent)."
            ),
            "root_cause": "The unified vault's sources (two AI-curriculum vaults) never covered computational chemistry, geometric DL, or protein modeling; only the user's project taxonomy references them.",
            "resolution": "Input to the S36 decision ledger: ~193 B/C/D work items expected from this cluster pair (152 absent + 41 partial; 6 equivalents map to named vault concepts). The SYNPATH wave (largest, first in S37+ ordering) must build cluster-domain notes for geometric deep learning + equivariant architectures (area 05/11 per plan §7), molecular generation + GFlowNets + reaction learning (new chemistry cluster-domain notes), protein backbones (VAULTX), with the general concepts anchored to existing notes (attention masking taxonomy, distance-bias family, training core).",
            "affected": ["state/integration/judgments-synpath-v1.jsonl", "reports/integration/s34-synpath-judgments.json"],
        },
    ]
    with FINDINGS.open("a", encoding="utf-8") as f:
        for fd in new_findings:
            f.write(json.dumps(fd, ensure_ascii=False) + "\n")
    print("findings appended: F-0048, F-0049, F-0050")

    # ---- task queue: INTEG-004 -> completed, INTEG-005 queued ----
    queue = [json.loads(l) for l in QUEUE.open(encoding="utf-8") if l.strip()]
    for t in queue:
        if t["task_id"] == "INTEG-004":
            t["status"] = "completed"
            t["findings"] = [
                "F-0048 carry-over rule established (one item = one judgment; 6 prior-judged items carried over verbatim with provenance; binding for S35's 29 carry-overs)",
                "F-0049 denominator correction: 235 unique SYNPATH+VAULTX items, not 237 (INT-0052/INT-0202 dual-cluster items were double-counted by plan arithmetic; no coverage gap — every item judged exactly once)",
                "F-0050 census result: 36 covered / 6 equivalent / 41 partial / 152 absent (64.7% absent) — zero molecular-chemistry, geometric-deep-learning, GFlowNet, or protein-backbone content in the vault; general attention/training core covered; ~193 B/C/D work items expected for the S36 ledger",
            ]
            t["tests_run"] = [
                {"command": "python3 scripts/s34_pack_groups.py", "result": "235 items packed: 229 fresh into 17 bounded groups (cluster+section-coherent, max 18) + 6 carry-overs recorded"},
                {"command": "17 subagent judgment groups (general-purpose agents, all 17 completed cleanly on first run)", "result": "229 fresh judgments (+6 carried over): 36 covered / 6 equivalent / 41 partial / 152 absent"},
                {"command": "python3 scripts/s34_validate_judgments.py", "result": "VALIDATION PASSED 235/235 (schema, exact set coverage, every covered/equivalent/partial quote verbatim-verified as whitespace-normalized substring of its cited note; absent discipline verified; carry-overs re-validated)"},
                {"command": "orchestrator re-review (stratified 33-item sample = 14.0%)", "result": "33/33 agreement (20 absent independently grep-verified over all 544 notes — all hits false positives; 6 covered + 3 equivalent destination-read verified; 4 partial section-verified)"},
                {"command": "vu verify-manifest x2", "result": "276/276 + 333/333 byte-identical (no mutations during judging)"},
                {"command": "python3 -m pytest -q (full suite)", "result": "836 passed (no framework code changes; re-run as session-end evidence)"},
            ]
            t["notes"] = (
                "Session 34 (S34 of 15). Full-cluster census of SYNPATH+VAULTX (235 unique "
                "items, no sampling; 229 fresh judgments + 6 F-0048 carry-overs). Result "
                "feeds the S36 decision ledger. Judgment file: "
                "state/integration/judgments-synpath-v1.jsonl; aggregate: "
                "reports/integration/s34-synpath-judgments.json."
            )
            break
    if not any(t["task_id"] == "INTEG-005" for t in queue):
        queue.append(INTEG_005)
    QUEUE.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in queue))
    report = reg.validate_task_queue(QUEUE, REPO / "schemas" / "task.schema.json")
    if not report["valid"]:
        print(f"QUEUE INVALID: {report['errors']}")
        return 1
    print(f"task queue valid: INTEG-004 completed, INTEG-005 queued ({len(queue)} tasks)")

    # ---- current-state ----
    cs = json.loads(CURRENT.read_text())
    cs["current_task_id"] = "INTEG-005"
    cs["stage"] = "integration-campaign (S32 MEDNLP + S33 2D3D + S34 SYNPATH/VAULTX judgments complete; S35 remaining clusters next)"
    cs["notes"] = (
        "INTEG campaign S34 complete: SYNPATH+VAULTX 235/235 judged (36 covered / "
        "6 equivalent / 41 partial / 152 absent) with mechanically verified quotes and "
        "33/33 orchestrator re-review agreement. 894/1,233 items judged (72.5%). "
        "F-0048 carry-over rule + F-0049 denominator correction established. Next: "
        "S35 (remaining clusters, 374 unique items / 345 fresh), then S36 decisions."
    )
    cs["last_verified_checkpoint"] = str(CHECKPOINT.relative_to(REPO))
    CURRENT.write_text(json.dumps(cs, indent=4) + "\n")

    # ---- checkpoint ----
    checkpoint = {
        "session": 34,
        "task_id": "INTEG-004",
        "date": "2026-11-07",
        "phase": "integration-campaign-audit",
        "work_completed": [
            "startup verification independently reproduced the session-33 baseline: 836/836 tests, sources 276/276 + 333/333 byte-identical (verify-manifest 0 changed/added/removed), HEAD == origin/main at bc7f6e9",
            "s33 + s32 validators re-run from reconstructed scratch (canonical files byte-identical after rewrite): VALIDATION PASSED 291/291 and 368/368 with verdict counts matching the handoff claims",
            "packed the 235 unique SYNPATH+VAULTX items into 17 bounded judgment groups (cluster+section-coherent, max 18; lexical hints attached; chemistry/equivariance/RL alternative-terminology hints added to the judging instructions) via scripts/s34_pack_groups.py; 6 pre-judged items carried over per the F-0048 rule instead of re-judged",
            "ran 17 independent subagent judgment groups (all completed cleanly on first run): each judge read candidate notes and grepped the vault for surface + alternative terminology before any absent verdict",
            "mechanically validated all 235 judgments (schema, exact set coverage incl. carry-overs, verbatim-quote verification, absent discipline): VALIDATION PASSED 235/235",
            "orchestrator re-review of a stratified 33-item sample (14.0%): 33/33 agreement (20 absent grep-verified; 9 covered/equivalent destination-read verified; 4 partial section-verified)",
            "wrote the canonical judgment file + aggregate report; appended findings F-0048/F-0049/F-0050; queued INTEG-005 (S35: remaining clusters); updated current-state/ledger/README/handoff",
        ],
        "changed_paths": [
            "scripts/s34_pack_groups.py (new)",
            "scripts/s34_validate_judgments.py (new)",
            "scripts/s34_closeout.py (new)",
            "state/integration/judgments-synpath-v1.jsonl (new; 235 records, 6 with carry_over_from)",
            "reports/integration/s34-synpath-groups.json (new; committed manifest with carry-over meta)",
            "reports/integration/s34-synpath-judgments.json (new; aggregate)",
            "state/findings.jsonl (F-0048, F-0049, F-0050 appended)",
            "state/task-queue.jsonl (INTEG-004 completed; INTEG-005 queued)",
            "state/current-state.json",
            "state/checkpoints/checkpoint-2026-11-07-integ-session34.json",
            "docs/ACCELERATED_COMPLETION_POLICY.md (ledger row 34)",
            "docs/agent-handoff/next-agent.md (rewritten for session 35)",
            "README.md (campaign progress)",
        ],
        "tests_run": [
            {"command": "python3 -m pytest -q (full suite at session end)", "result": "836 passed"},
            {"command": "vu verify-manifest x2 (sources)", "result": "276/276 + 333/333 byte-identical"},
            {"command": "python3 scripts/s34_validate_judgments.py", "result": "VALIDATION PASSED 235/235"},
            {"command": "python3 scripts/s33_validate_judgments.py (startup re-verification)", "result": "VALIDATION PASSED 291/291, canonical file byte-identical"},
            {"command": "python3 scripts/s32_validate_judgments.py (startup re-verification)", "result": "VALIDATION PASSED 368/368, canonical file byte-identical"},
        ],
        "git_state": {
            "branch": "main",
            "base_commit": "bc7f6e9 (session-33 close); machinery unit pushed as 6b62e66 and remote-verified before judging",
            "session_commits": "recorded in the session commit message",
            "push_verification": "per AGENTS.md section 13: push after commit and verify remote ref (git rev-parse origin/main + merge-base --is-ancestor)",
        },
        "open_findings": [
            "SYNPATH+VAULTX absent rate 64.7% (152/235): the molecular-chemistry layer (synthons, retrosynthesis, reaction templates, SMARTS, torsions, stereochemistry, force fields, drug-likeness scoring), the geometric-deep-learning layer (GNNs, message passing, PaiNN/SchNet/GemNet/EGNN, SE(3) equivariance), the GFlowNet stack, and the protein-backbone layer (Equiformer, IPA, receptor ensembles) must be built as cluster-domain notes (decision C/D) in the S37+ waves — SYNPATH is the largest wave and runs first",
            "41 partial items: the generic mechanisms exist (attention masking, distance biases, autodiff/checkpointing/stability, MDP/sampling, MLM/denoising, equivariance in the CNN sense) but the molecular/geometric instantiations are missing — decision B expansions",
            "6 equivalence mappings recorded this session (Distance-Based Attention Bias≡ALiBi, Additive Distance Bias≡ALiBi, Conditional Probability Factorization≡chain rule of probability, Gradient Stability≡gradient flow, Categorical Action Mask≡choice-constrained decoding, plus carried-over equivalences) — reuse in the S36 ledger",
            "S35 must apply the F-0048 carry-over rule (29 pre-judged items among its 374) and the F-0049 union accounting",
        ],
        "next_task": {
            "task_id": "INTEG-005",
            "title": "Semantic coverage judgments — remaining clusters MAPDIG+MATHSOLVER+WEATHER+NLME+MASTER-INDEX (374 unique items, 345 fresh)",
            "dependencies": ["INTEG-004 (completed)"],
            "resume": (
                "Follow AGENTS.md section 2 startup; read docs/INTEGRATION_CAMPAIGN_PLAN.md, "
                "the F-0048/F-0049 findings, and this checkpoint; reuse the S34 machinery: "
                "adapt scripts/s34_pack_groups.py to the remaining clusters (374 unique "
                "items, 345 fresh after 29 F-0048 carry-overs), run bounded judgment "
                "groups, validate mechanically, re-review >=10%, aggregate, and open "
                "INTEG-006 (S36: decision ledger for all 1,233 items)."
            ),
        },
        "accelerated_mode": {
            "session_number": 34,
            "budget_sessions_consumed": 4,
            "budget_sessions_remaining": 11,
            "deliverable_metric_moved": "campaign items semantically judged (cumulative)",
            "before": "659/1,233 items judged (MEDNLP + 2D3D complete; 53.4%)",
            "after": "894/1,233 items judged (MEDNLP + 2D3D + SYNPATH/VAULTX complete; 72.5%) — this session added 235 judgments: 36 covered / 6 equivalent / 41 partial / 152 absent",
            "denominator": "1,233 unique inventory items; 235 unique SYNPATH+VAULTX items judged 235/235 (full census, no sampling; F-0049 corrected the plan's 237 arithmetic)",
            "failed_session": False,
            "cause_if_failed": None,
            "deadline_position": "INTEG campaign session 4 of 15 (S31-S45); on plan (S34 objective completed within its budgeted session)",
        },
    }
    CHECKPOINT.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\n")
    print(f"checkpoint written: {CHECKPOINT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
