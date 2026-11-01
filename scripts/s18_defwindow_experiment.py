#!/usr/bin/env python3
"""Session 18: calibration experiment for a heading/def-window evidence rule.

Proposed side rule R (ADR-0011 binding-2 evidence class, session-16 precedent):
  auto_reject if (side outside domain folders) AND (NO match on the side is a
  heading hit or a definition-window hit for its matched alias)
  heading hit   : alias occurs (case-insensitive) in the side's heading path
  def-window hit: within the match context, the 70 chars after the match end
                  contain a gloss marker (":", " - ", " — ", " is ", " are ",
                  " means ", " refers to", " defines", " ="), or the 40 chars
                  before the match contain "define", "definition", "called".

Tested against the six ORIGINAL pair pools: R must reject ZERO sides of
dossier-participating KUs (ADR-0011 zero-counter-example requirement).
Also reports how many EXTENSION undecided sides R would clear.
"""
import json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
cfg = json.loads((REPO / "state/term-maps/dext-tier-config-v1.json").read_text())

GLOSS_AFTER = re.compile(r"(:|\s-\s|\s—\s|\sis\s|\sare\s|\smeans\s|\srefers to\s|\sdefines\s|\s=)")
GLOSS_BEFORE = re.compile(r"(define|definition|defined as|called|denoted)", re.I)

def evidence_hit(heading_path: list[str], match: dict) -> bool:
    alias = match.get("alias") or match.get("matched_text", "")
    hay = " > ".join(heading_path).lower()
    if alias and alias.lower() in hay:
        return True
    # char_span indexes the ORIGINAL line; the context string marks the match
    # with ⟦...⟧ instead -> locate the marked span inside the context.
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
    return any(evidence_hit(side.get("heading_path", []), m) for m in matches)

ORIG = {"regression": "ext003", "tree-based": "ext004", "evaluation": "ext005",
        "clustering": "ext008", "generalization": "ext009", "training-stability": "ext010"}
DOSSIER = {"regression": "regression-v1.json", "tree-based": "tree-based-v1.json",
           "evaluation": "evaluation-v1.json", "clustering": "clustering-v1.json",
           "generalization": "generalization-v1.json", "training-stability": "training-stability-v1.json"}

def subfolder(p):
    parts = p.split("/")
    return "/".join(parts[:2]) if len(parts) >= 2 else "(root)/" + parts[0]

violations = []
for domain, tag in ORIG.items():
    domf = set(cfg["domain_folders"][domain].get("ai-course", [])) | set(cfg["domain_folders"][domain].get("master-ai", []))
    broad = set(cfg["broad_terms"][domain])
    dossier = json.loads((REPO / "state/dossiers" / DOSSIER[domain]).read_text())
    participants = set(dossier["accounting"]["participating_ku_ids"])
    for line in open(REPO / f"reports/extraction/{tag}-overlap-candidates-pairs.jsonl"):
        p = json.loads(line)
        for sk, mk in (("ku_a", "matches_a"), ("ku_b", "matches_b")):
            if p[sk]["ku_id"] not in participants:
                continue
            folder = subfolder(p[sk]["source_path"])
            if folder in domf:
                continue  # R only fires outside domain folders; originals are in-domain
            if not side_has_evidence(p[sk], p[mk]) and p[mk]:
                violations.append((domain, p[sk]["ku_id"], p["topic"]))

print("C2b violations (R rejects a participating-KU side):", len(violations))
for v in violations[:15]:
    print("   ", v)

# now: how many extension undecided sides would R clear?
FNAME = {"regression": "regression", "tree-based": "tree", "evaluation": "evaluation",
         "clustering": "clustering", "generalization": "generalization",
         "training-stability": "training-stability"}
cleared = kept = 0
for domain, fn in FNAME.items():
    domf = set(cfg["domain_folders"][domain].get("ai-course", [])) | set(cfg["domain_folders"][domain].get("master-ai", []))
    for line in open(REPO / f"scratch/dossier-ext-{fn}-pairs.jsonl"):
        p = json.loads(line)
        for sk, mk in (("ku_a", "matches_a"), ("ku_b", "matches_b")):
            folder = subfolder(p[sk]["source_path"])
            if folder in domf:
                continue
            if p[mk] and not side_has_evidence(p[sk], p[mk]):
                cleared += 1
            else:
                kept += 1
print("extension non-domain sides: R would clear", cleared, "| keep for review", kept)
