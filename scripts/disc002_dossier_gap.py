#!/usr/bin/env python3
"""DISC-002: dossier reconciliation gap report.

The six committed dossiers were built from the pre-restart classification
overlays (11 batches, 514 participating KUs). The full corpus now holds
27,536 KUs across 70 batches. This script quantifies, per domain, how many
KUs in the 59 REGEN batches (012-070) match the domain's committed term map
(word-boundary, alias-aware) — i.e. the evidence a dossier EXTENSION must
absorb. It does not modify any dossier; it produces the precise, quantified
work order for the extension task.

Writes reports/discovery/disc002-dossier-reconciliation-gap.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from vault_unification.search import boundary_pattern  # noqa: E402

REPO = Path(".")
DOSSIER_DIR = REPO / "state" / "dossiers"
TERM_MAPS = {
    "regression": "state/term-maps/regression-domain-v1.json",
    "tree-based": "state/term-maps/tree-domain-v1.json",
    "evaluation": "state/term-maps/evaluation-domain-v1.json",
    "clustering": "state/term-maps/clustering-domain-v1.json",
    "generalization": "state/term-maps/generalization-domain-v1.json",
    "training-stability": "state/term-maps/training-stability-domain-v1.json",
}
REGEN_BATCHES = sorted(
    (REPO / "state" / "knowledge-units").glob("0??-regen001-*.jsonl")
)
OLD_BATCH_PREFIXES = (
    "001-", "002-", "003-", "004-", "005-", "006-",
    "007-", "008-", "009-", "010-", "011-",
)


def load_terms(term_map_path: Path) -> dict[str, list[str]]:
    data = json.loads(term_map_path.read_text(encoding="utf-8"))
    out: dict[str, list[str]] = {}
    for canon, aliases in data.items():
        if canon.startswith("_"):
            continue
        variants = [canon] + list(aliases or [])
        out[canon] = [v for v in variants if v]
    return out


def main() -> int:
    # load regen KUs once
    regen_kus = []
    for path in REGEN_BATCHES:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                regen_kus.append(json.loads(line))
    print(f"regen KUs loaded: {len(regen_kus)} from {len(REGEN_BATCHES)} batches")

    report: dict = {
        "task": "DISC-002 dossier reconciliation gap",
        "regen_kus": len(regen_kus),
        "regen_batches": len(REGEN_BATCHES),
        "interpretation": (
            "regen_kus_matching_terms is an UPPER BOUND funnel number, NOT a "
            "work order size: domain term maps contain broadly-occurring terms "
            "(e.g. 'gradient descent', 'learning rate'), so a term hit alone is "
            "not evidence of domain participation. Dossier extension MUST go "
            "through the same discipline the dossiers were built with: "
            "overlap-candidates (CAP-013) between the new KUs and each domain's "
            "existing concept KU sets, then semantic classification, then "
            "dossier regeneration with the ext006 rule set. The committed "
            "dossiers regenerate byte-identically from their inputs "
            "(scripts/ext006_dossiers.py --check, exit 0, 2026-10-28)."
        ),
        "domains": {},
    }
    for domain, tm_path in TERM_MAPS.items():
        terms = load_terms(Path(tm_path))
        # precompile pattern per canonical term (any variant)
        variants = [v for vs in terms.values() for v in vs]
        pats = [boundary_pattern(v) for v in variants]
        dossier = json.loads(
            (DOSSIER_DIR / f"{domain}-v1.json").read_text(encoding="utf-8")
        )
        participating = set()
        for concept in dossier.get("concepts", []):
            participating.update(concept.get("ku_ids", []))
        matches = []
        for ku in regen_kus:
            hay = ku.get("excerpt", "") + " " + " ".join(
                ku.get("heading_path", [])
            )
            if any(p.search(hay) for p in pats):
                matches.append(ku["knowledge_unit_id"])
        new_matches = [k for k in matches if k not in participating]
        report["domains"][domain] = {
            "term_map": tm_path,
            "canonical_terms": len(terms),
            "dossier_concepts": len(dossier.get("concepts", [])),
            "dossier_participating_kus": len(participating),
            "regen_kus_matching_terms_upper_bound": len(matches),
            "new_kus_beyond_dossier_upper_bound": len(new_matches),
            "sample_new_kus": new_matches[:10],
            "next_action": (
                "run vu overlap-candidates between this domain's existing "
                "participating KUs and the regen KUs, then classify and extend "
                "the dossier (bounded batches); do NOT bulk-absorb term matches"
            ),
        }
        print(
            f"{domain}: concepts={len(dossier.get('concepts', []))} "
            f"participating={len(participating)} regen_matches={len(matches)} "
            f"new={len(new_matches)}"
        )

    out = REPO / "reports" / "discovery" / "disc002-dossier-reconciliation-gap.json"
    out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(f"report -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
