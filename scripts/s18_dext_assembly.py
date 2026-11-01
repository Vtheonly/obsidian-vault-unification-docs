#!/usr/bin/env python3
"""DISC-002 session 18: FINAL dossier-extension assembly.

Resolves every one of the 69,185 pairs to a final decision:
  side verdict = reviewed verdict (rounds 1-3 + orchestrator overrides) when
                 one exists for (domain, file, topic, ku_id), else the
                 mechanical auto verdict (A1/A2 participate, B1/B2/nav reject);
  pair decision = participate iff BOTH sides participate, else reject-pair.
  KU participant set (per domain) = KUs with >= 1 participate side verdict.

Committed outputs:
  state/classifications/008-disc002-dext-review-verdicts.jsonl
      consolidated irreplaceable review decisions (round provenance kept)
  state/classifications/009..014-disc002-dext-<domain>-extension.jsonl
      term-level dossier-extension classification records (dossier-v2 input)
Derived outputs (scratch, replayable from committed inputs + this script):
  scratch/s18-final-pair-decisions-<domain>.jsonl
Reports:
  reports/dossier-ext/s18-dext-final-report.json

Assertions (delta-verification, pre-written arithmetic):
  - every C-tier side has a review verdict (0 unresolved 'undecided')
  - per-domain pair counts sum to exactly 69,185
    (9,211 + 10,833 + 10,603 + 6,672 + 11,275 + 20,591)
  - every pair gets exactly one decision
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FNAME = {"regression": "regression", "tree-based": "tree", "evaluation": "evaluation",
         "clustering": "clustering", "generalization": "generalization",
         "training-stability": "training-stability"}
EXPECTED_PAIRS = {"regression": 9211, "tree-based": 10833, "evaluation": 10603,
                  "clustering": 6672, "generalization": 11275,
                  "training-stability": 20591}
REVIEW_FILES = {
    "regression": [("regression-out.jsonl", 1), ("regression-delta-out.jsonl", 2)],
    "tree-based": [("tree-based-out.jsonl", 1), ("tree-based-delta-out.jsonl", 2)],
    "evaluation": [("evaluation-out.jsonl", 1), ("evaluation-delta-out.jsonl", 2),
                   ("evaluation-delta3-out.jsonl", 3)],
    "clustering": [("clustering-out.jsonl", 1), ("clustering-delta-out.jsonl", 2)],
    "generalization": [("generalization-out.jsonl", 1),
                       ("generalization-delta-out.jsonl", 2),
                       ("generalization-delta3-out.jsonl", 3)],
    "training-stability": [("training-stability-out-p1.jsonl", 1),
                           ("training-stability-out-p2.jsonl", 1),
                           ("training-stability-delta-out-p1.jsonl", 2),
                           ("training-stability-delta-out-p2.jsonl", 2),
                           ("training-stability-delta3-out.jsonl", 3)],
    # round 4: KU-level gap fill after the calibration iterations (one file,
    # mixed domains; round provenance is 4 for every record in it)
    "_round4": [("round4-out.jsonl", 4)],
}
# Orchestrator overrides from personal sample re-review (conservative
# reject->participate direction, session-16 precedent):
OVERRIDES = [
    {"domain": "regression", "file": "02 - Mathematics/Statistics/16 - Estimators and Bias.md",
     "term": "prior", "ku_id": "KU-55b0bfae0efe783e", "verdict": "participate",
     "rationale": "orchestrator override (5%-sample disagreement): 'MAP extends MLE by "
                  "incorporating a prior over the parameters' is genuine MAP-estimation "
                  "concept content (regression scope), not an incidental mention"},
    {"domain": "evaluation",
     "file": "02 - Mathematics/Information Theory/15 - Entropy Cross-Entropy KL.md",
     "term": "cross-entropy", "ku_id": "KU-89730bb977d4ced3", "verdict": "participate",
     "rationale": "orchestrator override (B3-sample disagreement): 'The cross-entropy "
                  "between two distributions p and q' is a real definition of the "
                  "log-loss metric; prose definitions without colon-gloss markers must "
                  "not be auto-rejected by rule B2"},
]
EXT_FILE_SEQ = {"regression": "009", "tree-based": "010", "evaluation": "011",
                "clustering": "012", "generalization": "013",
                "training-stability": "014"}
VERDICTS_OUT = REPO / "state" / "classifications" / "008-disc002-dext-review-verdicts.jsonl"
REPORT_OUT = REPO / "reports" / "dossier-ext" / "s18-dext-final-report.json"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def main() -> int:
    # ---- load review verdicts (round provenance preserved) ------------------
    verdicts: dict[tuple, dict] = {}   # (domain, file, term, ku) -> record
    verdict_records: list[dict] = []
    for r in load_jsonl(REPO / "scratch" / "s18-review" / "round4-out.jsonl"):
        for kid, v in r["ku_verdicts"].items():
            key = (r["domain"], r["file"], r["term"], kid)
            rec = {"domain": r["domain"], "file": r["file"], "term": r["term"],
                   "ku_id": kid, "verdict": v, "round": 4,
                   "rationale": r.get("rationale", ""),
                   "source": "scratch/s18-review/round4-out.jsonl"}
            verdicts[key] = rec
            verdict_records.append(rec)
    for domain, files in REVIEW_FILES.items():
        if domain == "_round4":
            continue
        for fname, rnd in files:
            for r in load_jsonl(REPO / "scratch" / "s18-review" / fname):
                for kid, v in r["ku_verdicts"].items():
                    key = (domain, r["file"], r["term"], kid)
                    rec = {"domain": domain, "file": r["file"], "term": r["term"],
                           "ku_id": kid, "verdict": v, "round": rnd,
                           "rationale": r.get("rationale", ""),
                           "source": f"scratch/s18-review/{fname}"}
                    if key in verdicts and verdicts[key]["verdict"] != v:
                        print(f"WARNING: round conflict for {key}: "
                              f"{verdicts[key]['verdict']} (r{verdicts[key]['round']})"
                              f" vs {v} (r{rnd}) — later round wins")
                    verdicts[key] = rec
                    verdict_records.append(rec)
    for o in OVERRIDES:
        key = (o["domain"], o["file"], o["term"], o["ku_id"])
        verdicts[key] = {"domain": o["domain"], "file": o["file"], "term": o["term"],
                         "ku_id": o["ku_id"], "verdict": o["verdict"],
                         "round": "orchestrator-override",
                         "rationale": o["rationale"],
                         "source": "scripts/s18_dext_assembly.py OVERRIDES"}
        verdict_records.append(verdicts[key])
    print(f"review verdicts loaded: {len(verdicts)} distinct (domain,file,term,ku)")

    # ---- resolve pairs -------------------------------------------------------
    report = {"command": "s18_dext_assembly",
              "method": ("side verdicts: review (rounds 1-3 + orchestrator overrides) "
                         "override mechanical auto verdicts; pair participates iff both "
                         "sides participate; KU joins the domain extension set iff >= 1 "
                         "participate side verdict"),
              "domains": {}}
    grand_pairs = grand_part = grand_rej = 0
    ku_participants: dict[str, set] = {}
    pair_decision_files = {}
    for domain, fn in FNAME.items():
        tiers = load_jsonl(REPO / "scratch" / f"s18-tiers-{fn}.jsonl")
        assert len(tiers) == EXPECTED_PAIRS[domain], \
            f"{domain}: pair count {len(tiers)} != expected {EXPECTED_PAIRS[domain]}"
        unresolved = 0
        tier_final = Counter()
        participants: set = set()
        auto_used = reviewed_used = 0
        out = REPO / "scratch" / f"s18-final-pair-decisions-{fn}.jsonl"
        with out.open("w", encoding="utf-8") as fh:
            for p in tiers:
                side_final = {}
                for s in ("side_a", "side_b"):
                    side = p[s]
                    v = side["verdict"]
                    if v == "undecided":
                        key = (domain, side["source_path"], p["topic"], side["ku_id"])
                        rv = verdicts.get(key)
                        if rv is None:
                            unresolved += 1
                            side_final[s] = "undecided"
                            continue
                        side_final[s] = rv["verdict"]
                        reviewed_used += 1
                    else:
                        side_final[s] = "participate" if v == "auto_participate" else "reject"
                        # review still overrides auto decisions where it exists
                        key = (domain, side["source_path"], p["topic"], side["ku_id"])
                        rv = verdicts.get(key)
                        if rv is not None:
                            side_final[s] = rv["verdict"]
                            reviewed_used += 1
                        else:
                            auto_used += 1
                    if side_final[s] == "participate":
                        participants.add(side["ku_id"])
                decision = ("participate" if side_final["side_a"] == "participate"
                            and side_final["side_b"] == "participate" else "reject-pair")
                tier_final[decision] += 1
                fh.write(json.dumps({
                    "candidate_id": p["candidate_id"], "domain": domain,
                    "topic": p["topic"], "tier": p["tier"],
                    "decision": decision,
                    "side_a": {"ku_id": p["side_a"]["ku_id"], "final": side_final["side_a"]},
                    "side_b": {"ku_id": p["side_b"]["ku_id"], "final": side_final["side_b"]},
                }, ensure_ascii=False) + "\n")
        if unresolved:
            print(f"ASSEMBLY FAILURE [{domain}]: {unresolved} unresolved undecided sides")
            return 1
        ku_participants[domain] = participants
        grand_pairs += len(tiers)
        grand_part += tier_final["participate"]
        grand_rej += tier_final["reject-pair"]
        pair_decision_files[domain] = str(out.relative_to(REPO))
        report["domains"][domain] = {
            "pairs": len(tiers),
            "tier_counts": dict(Counter(p["tier"] for p in tiers)),
            "pair_decisions": dict(tier_final),
            "side_verdict_sources": {"reviewed": reviewed_used, "auto": auto_used},
            "extension_participant_kus": len(participants),
        }
        print(f"{domain:20s} pairs={len(tiers):6d} participate={tier_final['participate']:5d} "
              f"reject-pair={tier_final['reject-pair']:5d} "
              f"participants={len(participants):4d} "
              f"(sides: reviewed={reviewed_used} auto={auto_used})")

    # ---- write consolidated review verdicts (committed decision record) ------
    # write only the EFFECTIVE verdict per key (the verdicts dict value), so
    # orchestrator overrides replace the round verdict they supersede
    effective = sorted(verdicts.values(),
                       key=lambda r: (r["domain"], r["file"], r["term"], r["ku_id"]))
    with VERDICTS_OUT.open("w", encoding="utf-8") as fh:
        for r in effective:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ---- write extension classification records per domain ------------------
    ext_summary = {}
    for domain, fn in FNAME.items():
        # participating KUs grouped by the term whose review/auto evidence admitted them
        by_term: dict[str, set] = {}
        for key, r in verdicts.items():
            if key[0] == domain and r["verdict"] == "participate":
                by_term.setdefault(key[2], set()).add(key[3])
        # auto-accepted sides (A1/A2) that were never reviewed: derive from tiers
        for p in load_jsonl(REPO / "scratch" / f"s18-tiers-{fn}.jsonl"):
            for s in ("side_a", "side_b"):
                side = p[s]
                if side["verdict"] == "auto_participate":
                    key = (domain, side["source_path"], p["topic"], side["ku_id"])
                    if key not in verdicts:
                        by_term.setdefault(p["topic"], set()).add(side["ku_id"])
        # KU metadata for evidence quotes
        ku_meta = {}
        for p in sorted((REPO / "state" / "knowledge-units").glob("*.jsonl")):
            for r in load_jsonl(p):
                if r["knowledge_unit_id"] in ku_participants[domain]:
                    ku_meta[r["knowledge_unit_id"]] = r
        records = []
        for i, term in enumerate(sorted(by_term), start=1):
            kids = sorted(by_term[term])
            evidence = []
            for kid in kids:
                m = ku_meta.get(kid, {})
                evidence.append({
                    "ku_id": kid,
                    "source_path": m.get("source_path", ""),
                    "lines": list(range(m.get("line_start", 0),
                                        m.get("line_end", -1) + 1)),
                    "quote": m.get("excerpt", "") or "",
                })
            records.append({
                "candidate_ref": ("dossier-extension pair pool: scratch/dossier-ext-"
                                  f"{fn}-pairs.jsonl regenerated via the command in "
                                  f"reports/dossier-ext/disc002-dext-{fn}-overlap-run.json; "
                                  "tiering by scripts/s18_dext_tiering.py with "
                                  "state/term-maps/dext-tier-config-v1.json"),
                "classification_id": f"DX-disc002-s18-{fn}-{i:04d}",
                "classified_by": ("DISC-002 session 18 orchestrator (Z AI / GLM 5.3) "
                                  "with 15 tiered review subagents + orchestrator "
                                  "verification (ADR-0011 tiered mode, ADR-0012)"),
                "date": "2026-11-01",
                "evidence": evidence,
                "ku_ids": kids,
                "method": ("ADR-0011 tiered dossier-extension classification: Tier A "
                           "auto-participate (domain folder or heading/definition-window "
                           "evidence via strong alias), Tier B auto-reject (navigation, "
                           "broad-term-only non-domain, or no-gloss non-domain), Tier C "
                           "subagent review of every undecided (file,term) combo with "
                           "orchestrator mechanical verification + 5% sample re-review "
                           "(~99.4% agreement, disagreements overridden conservatively)"),
                "overlap_type": "Complementary Content",
                "rationale": (f"Corpus-extension evidence for the '{term}' concept family "
                              f"of the {domain} domain: {len(kids)} KUs across non-dossier "
                              "corpus locations judged to carry domain concept content "
                              "(definitions/math/mechanics/examples/code/applications/"
                              "interview/historical/distinctions) by the tiered pipeline; "
                              "complements the original dossier concepts for synthesis."),
                "task_id": "DISC-002",
                "topic": f"{term} — corpus extension evidence",
            })
        seq = EXT_FILE_SEQ[domain]
        out = REPO / "state" / "classifications" / f"{seq}-disc002-dext-{fn}-extension.jsonl"
        with out.open("w", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        n_kus = sum(len(r["ku_ids"]) for r in records)
        # sanity: extension KU set equals participant set
        rec_kus = {k for r in records for k in r["ku_ids"]}
        assert rec_kus == ku_participants[domain], \
            f"{domain}: extension record KUs != participant set"
        ext_summary[domain] = {"file": str(out.relative_to(REPO)),
                               "records": len(records), "kus": n_kus}
        print(f"{domain:20s} extension records={len(records):3d} kus={n_kus:4d} -> {out.name}")

    # ---- final report --------------------------------------------------------
    report["grand_total"] = {
        "pairs": grand_pairs, "participate": grand_part, "reject_pair": grand_rej,
        "expected_pairs": 69185,
        "arithmetic_check": grand_pairs == 69185 and grand_part + grand_rej == grand_pairs,
        "extension_participant_kus_total": sum(len(v) for v in ku_participants.values()),
    }
    report["review_verdicts_file"] = str(VERDICTS_OUT.relative_to(REPO))
    report["review_verdicts_count"] = len(verdicts)
    report["extension_records"] = ext_summary
    report["pair_decision_files_scratch"] = pair_decision_files
    report["orchestrator_overrides"] = OVERRIDES
    REPORT_OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    ok = report["grand_total"]["arithmetic_check"]
    print(f"\nGRAND: pairs={grand_pairs} participate={grand_part} reject-pair={grand_rej} "
          f"participants={report['grand_total']['extension_participant_kus_total']}")
    print("ARITHMETIC CHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
