#!/usr/bin/env python3
"""DISC-002 session 16: verify subagent review decisions (ADR-0011 §4).

1. Schema/completeness: every review candidate has exactly one decision.
2. Citation check for EVERY cover (subagent + bulk P): each
   (vault 'path':line) citation in the rationale must resolve to a real
   file, and the term (or a normalized token overlap) must appear within
   +-4 lines of the cited line.
3. Emit a verification report; covers failing the citation check are
   downgraded to a re-review queue.

The single gap_watch candidate is handled separately by the orchestrator.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
SCRATCH = Path("/home/z/my-project/scratch")
VAULTS = {
    "master-ai": REPO / "source-vaults/AI /Master AI",
    "ai-course": REPO / "source-vaults/AI /AI Course",
}

CITE = re.compile(r"\((master-ai|ai-course) '([^']+)':(\d+)\)")


def norm(s: str) -> str:
    return " ".join(s.lower().replace("-", " ").replace("_", " ").split())


def tokens(s: str) -> set:
    return set(norm(s).split())


def main() -> int:
    # load bundle + decisions
    bundle = {}
    order = []
    for i in range(1, 7):
        for line in open(SCRATCH / f"disc002-s16-review-slice{i}.jsonl",
                         encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                bundle[r["candidate_id"]] = r
                order.append(r["candidate_id"])
    decs = {}
    for i in range(1, 7):
        for line in open(SCRATCH / f"disc002-s16-review-dec{i}.jsonl",
                         encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                decs[d["candidate_id"]] = d

    print("bundle:", len(bundle), "decisions:", len(decs))
    missing = [c for c in bundle if c not in decs]
    extra = [c for c in decs if c not in bundle]
    dup = len(order) - len(bundle)
    print("missing decisions:", len(missing), "extra:", len(extra),
          "dups:", dup)
    actions = Counter(d["action"] for d in decs.values())
    print("actions:", dict(actions))

    # id/term agreement
    mism = [d["candidate_id"] for d in decs.values()
            if bundle[d["candidate_id"]]["term"] != d.get("term")]
    print("term mismatches:", len(mism))

    # --- citation check for every cover ---
    filecache = {}

    def get_lines(vault, rel):
        key = (vault, rel)
        if key not in filecache:
            p = VAULTS[vault] / rel
            try:
                filecache[key] = p.read_text(encoding="utf-8",
                                             errors="replace").split("\n")
            except OSError:
                filecache[key] = None
        return filecache[key]

    cover_fail, cover_ok = [], 0
    for cid, d in decs.items():
        if d["action"] != "cover":
            continue
        cits = CITE.findall(d["rationale"])
        if not cits:
            cover_fail.append((cid, d, "NO_CITATION"))
            continue
        term_toks = tokens(bundle[cid]["term"])
        ok_any = False
        reason = "NO_TERM_NEAR_CITE"
        for vault, rel, line in cits:
            lines = get_lines(vault, rel)
            if lines is None:
                reason = "FILE_NOT_FOUND"
                continue
            ln = int(line)
            window = " ".join(lines[max(0, ln - 5): ln + 5])
            wt = set(norm(window).replace("(", " ").replace(")", " ")
                     .replace(",", " ").replace(".", " ").split())
            # citation is valid if ANY meaningful term token (len>3 or the
            # full normalized term) appears in the +-4-line window
            if norm(bundle[cid]["term"]) in norm(window) or \
                    any(t in wt for t in term_toks if len(t) > 4):
                ok_any = True
                break
        if ok_any:
            cover_ok += 1
        else:
            cover_fail.append((cid, d, reason))

    print(f"\ncover citation check: OK={cover_ok}  FAIL={len(cover_fail)}")
    for cid, d, why in cover_fail[:25]:
        print(f"  FAIL[{why}] {bundle[cid]['term']!r} :: "
              f"{d['rationale'][:130]}")

    # --- sample of rejects for orchestrator re-review ---
    import random
    random.seed(2026)
    rejects = [d for d in decs.values() if d["action"] == "reject"]
    sample = random.sample(rejects, min(150, len(rejects)))
    with open(SCRATCH / "disc002-s16-reject-sample.jsonl", "w",
              encoding="utf-8") as fh:
        for d in sample:
            b = bundle[d["candidate_id"]]
            fh.write(json.dumps({
                "candidate_id": d["candidate_id"],
                "term": b["term"], "kind": b["kind"], "score": b["score"],
                "contexts": b["contexts"],
                "evidence_quote": (b["evidence"][0].get("quote", "")
                                   if b["evidence"] else "")[:220],
                "subagent_action": "reject",
                "subagent_rationale": d["rationale"],
            }, ensure_ascii=False) + "\n")
    print("reject sample written: 150")

    # --- gap_watch list ---
    gaps = [d for d in decs.values() if d["action"] == "gap_watch"]
    for d in gaps:
        print("\nGAP_WATCH:", json.dumps(d, indent=1)[:500])

    (SCRATCH / "disc002-s16-verify-report.json").write_text(json.dumps({
        "bundle": len(bundle), "decisions": len(decs),
        "missing": len(missing), "extra": len(extra),
        "actions": dict(actions), "term_mismatches": len(mism),
        "cover_citation_ok": cover_ok, "cover_citation_fail": len(cover_fail),
        "cover_fail_ids": [c for c, _, _ in cover_fail],
        "gap_watch": [d["candidate_id"] for d in gaps],
    }, indent=1) + "\n")
    print("\nverification report saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
