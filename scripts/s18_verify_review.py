#!/usr/bin/env python3
"""DISC-002 session 18: verify subagent Tier C review outputs (mechanical).

Checks per ADR-0011 subagent discipline:
  V1 completeness: every bundle combo has exactly one output line, every
     listed ku_id has exactly one verdict, verdicts in {participate, reject};
  V2 citation check: for every reviewed-ACCEPT verdict, the matched alias/
     matched_text must actually occur in the KU excerpt or match context (for
     hash topics, the KU excerpt must be non-empty);
  V3 stats + per-domain sampling frames for the orchestrator's personal 5%
     re-review (min 30) of rejects.

Exit code 1 on any V1/V2 failure.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REV = REPO / "scratch" / "s18-review"
random.seed(1818)

DOMAINS = ["regression", "tree-based", "evaluation", "clustering",
           "generalization", "training-stability"]
TS_PARTS = ["training-stability-out-p1.jsonl", "training-stability-out-p2.jsonl"]


def load_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.append(json.loads(line))
    return out


def build_ku_index() -> dict[str, dict]:
    idx: dict[str, dict] = {}
    for p in sorted((REPO / "state" / "knowledge-units").glob("0[1-7][0-9]-regen001-*.jsonl")):
        for r in load_jsonl(p):
            idx[r["knowledge_unit_id"]] = r
    return idx


def main() -> int:
    ku_index = build_ku_index()
    problems: list[str] = []
    stats = {}
    reject_frames = {}
    for domain in DOMAINS:
        bundle = json.loads((REV / f"{domain}-bundle.json").read_text())
        combos = bundle["combos"]
        out_files = ([REV / f"{domain}-out.jsonl"] if domain != "training-stability"
                     else [REV / f for f in TS_PARTS])
        outputs = []
        for f in out_files:
            if not f.exists():
                problems.append(f"V1[{domain}]: missing output file {f.name}")
                continue
            outputs.extend(load_jsonl(f))
        if problems:
            continue
        # V1 completeness
        out_by_key = {}
        for i, o in enumerate(outputs):
            key = (o.get("file"), o.get("term"))
            if key in out_by_key:
                problems.append(f"V1[{domain}]: duplicate output line for {key}")
            out_by_key[key] = o
        bundle_keys = {(c["file"], c["term"]) for c in combos}
        missing = bundle_keys - set(out_by_key)
        extra = set(out_by_key) - bundle_keys
        if missing:
            problems.append(f"V1[{domain}]: {len(missing)} combos without output "
                            f"(e.g. {sorted(missing)[:3]})")
        if extra:
            problems.append(f"V1[{domain}]: {len(extra)} extra output lines")
        n_p = n_r = 0
        accepts = []
        rejects = []
        for c in combos:
            o = out_by_key.get((c["file"], c["term"]))
            if o is None:
                continue
            ku_ids = [k["ku_id"] for k in c["kus"]]
            vs = o.get("ku_verdicts", {})
            if set(vs) != set(ku_ids):
                problems.append(f"V1[{domain}]: ku_id set mismatch for {c['file']} / {c['term']}")
                continue
            for k in ku_ids:
                v = vs[k]
                if v not in ("participate", "reject"):
                    problems.append(f"V1[{domain}]: invalid verdict {v!r}")
                    continue
                if v == "participate":
                    n_p += 1
                    accepts.append((c["file"], c["term"], k))
                else:
                    n_r += 1
                    rejects.append((c["file"], c["term"], k))
        # V2 citation check on accepts: the term, any term-map alias, or any
        # matched_text recorded in the bundle must occur in the KU excerpt or
        # in the KU's own match contexts (aliases like MAE/OLS/imbalanced are
        # valid citation anchors).
        tm_path = {"regression": "regression", "tree-based": "tree", "evaluation": "evaluation",
                   "clustering": "clustering", "generalization": "generalization",
                   "training-stability": "training-stability"}[domain]
        term_map = json.loads((REPO / "state" / "term-maps" / f"{tm_path}-domain-v1.json").read_text())
        combo_by_key = {(c["file"], c["term"]): c for c in combos}
        bad_cites = 0
        for f, term, kid in accepts:
            ku = ku_index.get(kid)
            excerpt = ((ku or {}).get("excerpt", "") or "").lower()
            if term in ("__exact_hash__", "__exact_normalized__"):
                if len(excerpt.strip()) < 10:
                    bad_cites += 1
                    problems.append(f"V2[{domain}]: hash-accept with empty excerpt {kid}")
                continue
            combo = combo_by_key[(f, term)]
            entry = next((k for k in combo["kus"] if k["ku_id"] == kid), None)
            ctxs = " ".join((m.get("context") or "") for m in (entry or {}).get("matches", [])).lower()
            needles = {term.lower()}
            needles.update(a.lower() for a in term_map.get(term, []) if isinstance(a, str))
            needles.update((m.get("matched_text") or "").lower()
                           for m in (entry or {}).get("matches", []))
            if not any(n and n in excerpt for n in needles) and not any(
                    n and n in ctxs for n in needles):
                bad_cites += 1
                problems.append(
                    f"V2[{domain}]: accept {kid} for term '{term}' — no term/alias/"
                    f"matched_text anchor in excerpt or match context")
        n_sample = max(30, round(0.05 * n_r))
        reject_frames[domain] = random.sample(rejects, min(n_sample, len(rejects))) if rejects else []
        stats[domain] = {"combos": len(combos), "output_lines": len(outputs),
                         "reviewed_accepts": n_p, "reviewed_rejects": n_r,
                         "citation_failures": bad_cites,
                         "reject_sample_size": len(reject_frames[domain])}
        print(f"{domain:20s} combos={len(combos):4d} lines={len(outputs):4d} "
              f"accept={n_p:4d} reject={n_r:4d} cite_fail={bad_cites} "
              f"sample={len(reject_frames[domain])}")
    if problems:
        print(f"\nVERIFICATION FAILED — {len(problems)} problems:")
        for p in problems[:30]:
            print("  ", p)
        (REV / "verify-problems.json").write_text(json.dumps(problems, indent=1))
        return 1
    (REV / "verify-summary.json").write_text(json.dumps(stats, indent=1) + "\n")
    with (REV / "reject-sample-frame.json").open("w") as fh:
        json.dump({d: [{"file": f, "term": t, "ku_id": k} for f, t, k in v]
                   for d, v in reject_frames.items()}, fh, indent=1)
    print("\nVERIFICATION PASSED (V1 completeness + V2 citations).")
    print("Reject sample frames written for orchestrator 5% re-review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
