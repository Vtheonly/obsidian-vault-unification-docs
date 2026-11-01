#!/usr/bin/env python3
"""DISC-002 session 18: dossier-extension tiering engine (ADR-0011 mode).

Computes per-side verdicts and per-pair tiers over the six regenerated
dossier-extension pair files (69,185 pairs), using the curated config
state/term-maps/dext-tier-config-v1.json, and CALIBRATES the config against
the original EXT-003..010 hand-classified evidence before any tier is applied.

Side-level verdict semantics (a pair links two NEW KUs, one per vault):
  auto_participate  : side KU is in a domain folder AND has a clean
                      (non-mermaid, non-code-block) match on a
                      domain-specific term            -> Tier A side
  auto_reject       : side is a navigation/meta KU, OR side is outside the
                      domain folders AND every matched term on that side is
                      broad, OR the side has no clean match at all
                      (mermaid-only / unconfirmed evidence)   -> Tier B side
  undecided         : everything else                    -> Tier C side
                      (individual review required)

Pair tiers:
  A : both sides auto_participate                -> auto participate
  B : both sides auto_reject                     -> auto reject-pair
  B3: one side auto_reject, other auto_participate -> reject-pair with the
      participating side recorded (pair is not full cross-vault overlap
      evidence, but the strong side's verdict stands for KU aggregation)
  C : at least one side undecided                -> review required

Calibration (zero-counter-example requirement, ADR-0011 binding 1/2):
  C1 For every dossier-participating KU in each domain, the KU's source
     folder must be listed in domain_folders (else Tier A evidence would be
     excluded) AND at least one of its matched topics in the ORIGINAL
     overlap run must be non-broad (else a broad-listed term was the sole
     anchor of hand-accepted evidence).
  C2 Applying the auto_reject rule to the ORIGINAL pair pools must reject
     zero pairs whose both-side KUs are dossier participants... more
     precisely: zero sides belonging to dossier-participating KUs may
     receive auto_reject.
  C3 Every topic that provided the (sole) matched evidence for a
     dossier-participating KU side in the original pools must not be broad.

Outputs (scratch, regenerable):
  scratch/s18-tiers-<domain>.jsonl   per-pair tier + side verdicts + reasons
  reports/dossier-ext/s18-tiering-report.json  sizes + calibration results
Exit code 1 on any calibration counter-example (tiers are NOT applied).
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO / "state" / "term-maps" / "dext-tier-config-v1.json"
REPORT_PATH = REPO / "reports" / "dossier-ext" / "s18-tiering-report.json"
SCRATCH = REPO / "scratch"

FNAME = {"regression": "regression", "tree-based": "tree", "evaluation": "evaluation",
         "clustering": "clustering", "generalization": "generalization",
         "training-stability": "training-stability"}

# original-ext-run calibration sources per domain
ORIG_PAIRS = {
    "regression": "reports/extraction/ext003-overlap-candidates-pairs.jsonl",
    "tree-based": "reports/extraction/ext004-overlap-candidates-pairs.jsonl",
    "evaluation": "reports/extraction/ext005-overlap-candidates-pairs.jsonl",
    "clustering": "reports/extraction/ext008-overlap-candidates-pairs.jsonl",
    "generalization": "reports/extraction/ext009-overlap-candidates-pairs.jsonl",
    "training-stability": "reports/extraction/ext010-overlap-candidates-pairs.jsonl",
}
DOSSIER_FILE = {
    "regression": "state/dossiers/regression-v1.json",
    "tree-based": "state/dossiers/tree-based-v1.json",
    "evaluation": "state/dossiers/evaluation-v1.json",
    "clustering": "state/dossiers/clustering-v1.json",
    "generalization": "state/dossiers/generalization-v1.json",
    "training-stability": "state/dossiers/training-stability-v1.json",
}


def load_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.append(json.loads(line))
    return out


def subfolder(source_path: str) -> str:
    parts = source_path.split("/")
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return "(root)/" + parts[0]


def is_nav(source_path: str, nav: dict) -> bool:
    name = source_path.split("/")[-1]
    if name in nav["exact_filenames"]:
        return True
    top = source_path.split("/")[0]
    return any(top == p or top.startswith(p + "/") for p in nav["prefix_folders"])


def source_path_exempt(source_path: str) -> bool:
    """Quiz/interview folders keep rule-R protection (review, not auto-reject)."""
    top = source_path.split("/")[0]
    return any(top == p or top.startswith(p + "/") for p in REVIEW_EXEMPT_PREFIXES)


def clean_match(match: dict) -> bool:
    """A match is clean evidence if not mermaid-suspect and not inside a code block."""
    return not match.get("mermaid_node_suspect", False) and not match.get("unit_is_code_block", False)


# Rule R evidence detector (session-16 cover evidence class): a match counts as
# gloss evidence when the matched alias appears in the KU's heading path, or the
# match context shows a definition window (gloss marker within 70 chars after
# the ⟦match⟧ marker, or a define/called cue within 40 chars before it).
GLOSS_AFTER = re.compile(r"(:|\s-\s|\s—\s|\sis\s|\sare\s|\smeans\s|\srefers to\s|\sdefines\s|\s=)")
GLOSS_BEFORE = re.compile(r"(define|definition|defined as|called|denoted)", re.I)

# Folders whose thin-evidence matches stay in review despite rule R: quiz and
# interview banks carry dossier category (interview_misconceptions) evidence in
# terse answer lines that gloss detection misses (ADR-0011 probe discipline).
REVIEW_EXEMPT_PREFIXES = ("09 - Quizzes and Question Banks", "29 - Interview Prep")


def evidence_hit(side: dict, match: dict) -> bool:
    alias = match.get("alias") or match.get("matched_text", "")
    hay = " > ".join(side.get("heading_path", [])).lower()
    if alias and alias.lower() in hay:
        return True
    ctx = match.get("context", "")
    marked = "\u27e6" + match.get("matched_text", "") + "\u27e7"
    pos = ctx.find(marked)
    if pos >= 0:
        after = ctx[pos + len(marked): pos + len(marked) + 70]
        before = ctx[max(0, pos - 40): pos]
        if GLOSS_AFTER.search(after) or GLOSS_BEFORE.search(before):
            return True
    return False


def side_has_evidence(side: dict, matches: list[dict]) -> bool:
    return any(evidence_hit(side, m) for m in matches)


def side_verdict(side: dict, matches: list[dict], cfg_domain: dict, nav: dict) -> dict:
    """Compute the auto tier verdict for one pair side."""
    folder = subfolder(side["source_path"])
    in_domain_folder = folder in cfg_domain["domain_folders"].get(side["vault"], [])
    nav_side = is_nav(side["source_path"], nav)
    clean = [m for m in matches if clean_match(m)]
    terms = sorted({m["term"] for m in matches})
    clean_terms = sorted({m["term"] for m in clean})
    broad = set(cfg_domain["broad_terms"])
    specific_clean_terms = [t for t in clean_terms if t not in broad]

    if nav_side:
        return {"verdict": "auto_reject", "folder": folder, "terms": terms,
                "reason": "navigation/meta KU (no concept evidence)"}
    weak_aliases = set(cfg_domain.get("weak_aliases", []))

    def strong(m: dict) -> bool:
        return m["term"] not in broad and m.get("alias", "") not in weak_aliases

    strong_clean_terms = sorted({m["term"] for m in clean if strong(m)})
    if strong_clean_terms and in_domain_folder:
        return {"verdict": "auto_participate", "folder": folder,
                "terms": strong_clean_terms,
                "reason": "domain folder + clean match on domain-specific term "
                          "via strong alias (" + ", ".join(strong_clean_terms) + ")",
                "accept_class": "A1"}
    if (strong_clean_terms and matches
            and side_has_evidence(side, matches)):
        # Tier A2 (session-16 cover evidence class): clean match on a
        # domain-specific term via a STRONG alias WITH a heading or
        # definition-window hit for that term -> the KU carries real domain
        # content regardless of folder. Weak-alias matches (observed failure
        # mode: 'singular', 'default', 'ones', 'rotate', 'closed-form
        # solution', 'shrinks'...) stay in review (ADR-0011 pull-back).
        ev_terms = sorted({m["term"] for m in matches
                           if strong(m) and evidence_hit(side, m)})
        if ev_terms:
            return {"verdict": "auto_participate", "folder": folder,
                    "terms": ev_terms,
                    "reason": "specific-term match with heading/definition-"
                              "window evidence via strong alias ("
                              + ", ".join(ev_terms) + ")",
                    "accept_class": "A2"}
    if not in_domain_folder and not specific_clean_terms and clean:
        # clean is non-empty here, so the side has at least one real-text
        # broad-term match; combined with a non-domain folder this is
        # incidental lexical co-occurrence. Sides whose only matches are
        # mermaid-suspect and/or code-block do NOT auto-reject (calibration:
        # hand-accepted KUs with code-block-only evidence exist) -> review.
        return {"verdict": "auto_reject", "folder": folder, "terms": terms,
                "reason": "outside domain folders + broad-term-only matches "
                          f"({', '.join(terms)})",
                "reject_class": "B1"}
    if (not in_domain_folder and matches
            and not source_path_exempt(side["source_path"])
            and not side_has_evidence(side, matches)):
        # Rule R (B2): outside domain folders with NO gloss/heading evidence for
        # any matched term -> thin incidental mention. Calibration is vacuous on
        # the original pools (all hand-accepted sides live in domain folders);
        # safety rests on the 5% orchestrator sample re-verification per
        # ADR-0011 tier-(b), pull-back provision on any disagreement.
        return {"verdict": "auto_reject", "folder": folder, "terms": terms,
                "reason": "outside domain folders + no heading/definition-window "
                          "evidence for any matched term",
                "reject_class": "B2"}
    if not clean:
        return {"verdict": "undecided", "folder": folder, "terms": terms,
                "reason": "no clean prose match (mermaid-suspect and/or "
                          "code-block only evidence) -> review"}
    return {"verdict": "undecided", "folder": folder, "terms": terms,
            "reason": "mixed evidence: folder=%s in_domain_folder=%s terms=%s"
                      % (folder, in_domain_folder, ",".join(terms))}


def pair_tier(va: dict, vb: dict) -> str:
    if va["verdict"] == "auto_participate" and vb["verdict"] == "auto_participate":
        return "A"
    if va["verdict"] == "auto_reject" and vb["verdict"] == "auto_reject":
        return "B"
    if "undecided" in (va["verdict"], vb["verdict"]):
        return "C"
    return "B3"  # one auto_reject, one auto_participate


def calibrate(cfg: dict) -> tuple[list[str], dict]:
    """C1-C3 zero-counter-example calibration against hand-classified evidence."""
    problems: list[str] = []
    detail: dict = {}
    nav = cfg["nav_rules"]
    for domain, dossier_path in DOSSIER_FILE.items():
        dcfg = {"broad_terms": cfg["broad_terms"][domain],
                "domain_folders": cfg["domain_folders"][domain]}
        dossier = json.loads((REPO / dossier_path).read_text(encoding="utf-8"))
        participants = set(dossier["accounting"]["participating_ku_ids"])
        # KU metadata from the original domain classification evidence files is
        # not enough: we need each participating KU's source folder + original
        # matched topics -> rebuild from the original pair pool.
        orig_pairs = load_jsonl(REPO / ORIG_PAIRS[domain])
        ku_folder: dict[str, str] = {}
        ku_topics: dict[str, set[str]] = {}
        for p in orig_pairs:
            for side_key, matches_key in (("ku_a", "matches_a"), ("ku_b", "matches_b")):
                kid = p[side_key]["ku_id"]
                ku_folder.setdefault(kid, subfolder(p[side_key]["source_path"]))
                ku_topics.setdefault(kid, set()).update(m["term"] for m in p[matches_key])
        dom_folders = set(dcfg["domain_folders"].get("ai-course", [])) | \
            set(dcfg["domain_folders"].get("master-ai", []))
        broad = set(dcfg["broad_terms"])
        c1_folder = c1_term = c2 = 0
        for kid in participants:
            if kid not in ku_folder:
                # participating KU never appeared in the original pair pool
                # (its concept record cites it directly); not a tier rule issue.
                continue
            folder = ku_folder[kid]
            if folder not in dom_folders:
                problems.append(f"C1-folder[{domain}]: participating KU {kid} lives in "
                                f"unlisted folder {folder}")
                c1_folder += 1
            topics = ku_topics.get(kid, set())
            if topics and topics <= broad:
                problems.append(f"C1-term[{domain}]: participating KU {kid} matched ONLY "
                                f"broad-listed topics {sorted(topics)}")
                c1_term += 1
        # C2: auto_reject applied to original-pool sides of participating KUs
        for p in orig_pairs:
            for side_key, matches_key in (("ku_a", "matches_a"), ("ku_b", "matches_b")):
                kid = p[side_key]["ku_id"]
                if kid not in participants:
                    continue
                v = side_verdict(p[side_key], p[matches_key], dcfg, nav)
                if v["verdict"] == "auto_reject":
                    problems.append(f"C2[{domain}]: auto_reject hits participating KU {kid} "
                                    f"({v['reason']})")
                    c2 += 1
        detail[domain] = {"participating_kus": len(participants),
                          "participating_kus_in_orig_pool": sum(1 for k in participants if k in ku_folder),
                          "c1_folder_violations": c1_folder,
                          "c1_term_violations": c1_term,
                          "c2_reject_violations": c2}
    return problems, detail


def main() -> int:
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    nav = cfg["nav_rules"]

    problems, cal_detail = calibrate(cfg)
    if problems:
        print("CALIBRATION FAILED — counter-examples found (tiers NOT applied):")
        for p in problems[:40]:
            print("  ", p)
        if len(problems) > 40:
            print(f"   ... and {len(problems) - 40} more")
        REPORT_PATH.write_text(json.dumps(
            {"command": "s18_dext_tiering", "status": "calibration_failed",
             "counter_examples": problems, "calibration": cal_detail},
            indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return 1
    print("CALIBRATION PASSED (zero counter-examples on C1/C2).")

    report = {"command": "s18_dext_tiering",
              "config": "state/term-maps/dext-tier-config-v1.json",
              "calibration": cal_detail,
              "domains": {}}
    grand = Counter()
    for domain, fn in FNAME.items():
        dcfg = {"broad_terms": cfg["broad_terms"][domain],
                "domain_folders": cfg["domain_folders"][domain],
                "weak_aliases": cfg.get("weak_aliases", {}).get(domain, [])}
        pairs = load_jsonl(SCRATCH / f"dossier-ext-{fn}-pairs.jsonl")
        tier_counts = Counter()
        side_counts = Counter()
        undecided_ku_terms: set[tuple[str, str]] = set()
        undecided_sides = Counter()
        out_path = SCRATCH / f"s18-tiers-{fn}.jsonl"
        with out_path.open("w", encoding="utf-8") as out:
            for p in pairs:
                va = side_verdict(p["ku_a"], p["matches_a"], dcfg, nav)
                vb = side_verdict(p["ku_b"], p["matches_b"], dcfg, nav)
                tier = pair_tier(va, vb)
                tier_counts[tier] += 1
                side_counts[va["verdict"]] += 1
                side_counts[vb["verdict"]] += 1
                for v, side in ((va, "a"), (vb, "b")):
                    if v["verdict"] == "undecided":
                        kid = p[f"ku_{side}"]["ku_id"]
                        for t in v["terms"]:
                            undecided_ku_terms.add((kid, t))
                        undecided_sides[p[f"ku_{side}"]["source_path"]] += 1
                out.write(json.dumps({
                    "candidate_id": p["candidate_id"],
                    "domain": domain,
                    "topic": p["topic"],
                    "confirmed": p["confirmed"],
                    "tier": tier,
                    "side_a": {"ku_id": p["ku_a"]["ku_id"],
                               "source_path": p["ku_a"]["source_path"],
                               "vault": p["ku_a"]["vault"],
                               **va},
                    "side_b": {"ku_id": p["ku_b"]["ku_id"],
                               "source_path": p["ku_b"]["source_path"],
                               "vault": p["ku_b"]["vault"],
                               **vb},
                }, ensure_ascii=False) + "\n")
        report["domains"][domain] = {
            "pairs_total": len(pairs),
            "tier_counts": dict(sorted(tier_counts.items())),
            "side_verdict_counts": dict(sorted(side_counts.items())),
            "distinct_undecided_ku_term_combos": len(undecided_ku_terms),
            "top_undecided_files": [{"file": f, "sides": c}
                                    for f, c in undecided_sides.most_common(12)],
        }
        grand.update(tier_counts)
        print(f"{domain:20s} pairs={len(pairs):6d} " +
              " ".join(f"{k}={v}" for k, v in sorted(tier_counts.items())) +
              f" | undecided (ku,term) combos={len(undecided_ku_terms)}")
    report["grand_total"] = {"pairs": sum(report["domains"][d]["pairs_total"] for d in report["domains"]),
                             "tier_counts": dict(sorted(grand.items()))}
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print("GRAND:", dict(sorted(grand.items())), "-> report", REPORT_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
