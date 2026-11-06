#!/usr/bin/env python3
"""Session 18: sample undecided sides that rule R would auto-reject."""
import json, random, sys
sys.path.insert(0, 'scripts')
from s18_defwindow_experiment import side_has_evidence, cfg
from pathlib import Path

REPO = Path('.')
FNAME = {"regression": "regression", "tree-based": "tree", "evaluation": "evaluation",
         "clustering": "clustering", "generalization": "generalization",
         "training-stability": "training-stability"}
random.seed(18)

def subfolder(p):
    parts = p.split("/")
    return "/".join(parts[:2]) if len(parts) >= 2 else "(root)/" + parts[0]

cleared = []
for domain, fn in FNAME.items():
    domf = set(cfg["domain_folders"][domain].get("ai-course", [])) | set(cfg["domain_folders"][domain].get("master-ai", []))
    for line in open(f'scratch/dossier-ext-{fn}-pairs.jsonl'):
        p = json.loads(line)
        for sk, mk in (("ku_a", "matches_a"), ("ku_b", "matches_b")):
            folder = subfolder(p[sk]["source_path"])
            if folder in domf or not p[mk]:
                continue
            if not side_has_evidence(p[sk], p[mk]):
                cleared.append((domain, p["topic"], p[sk]["source_path"],
                                p[mk][0].get("context", "")[:110] if p[mk] else ""))

print("R would clear (from ALL non-domain sides):", len(cleared))
for domain, topic, path, ctx in random.sample(cleared, 25):
    print(f"[{domain}] {topic}")
    print(f"    {path[:80]}")
    print(f"    ctx: {ctx}")
