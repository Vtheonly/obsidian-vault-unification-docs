#!/usr/bin/env python3
import json, random, sys
from pathlib import Path
random.seed(2026)
FNAME = {'regression':'regression','tree-based':'tree','evaluation':'evaluation','clustering':'clustering','generalization':'generalization','training-stability':'training-stability'}
pairs_by_tier = {'A': [], 'B': [], 'B3': []}
for d, fn in FNAME.items():
    for line in open(f'scratch/s18-tiers-{fn}.jsonl'):
        r = json.loads(line)
        if r['tier'] in pairs_by_tier:
            pairs_by_tier[r['tier']].append(r)
which = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
samp = random.sample(pairs_by_tier[which], min(n, len(pairs_by_tier[which])))
print(f"### {len(pairs_by_tier[which])} total {which}-pairs, sample {len(samp)}")
for r in samp:
    print(f"[{r['domain']}] topic={r['topic']}")
    for s in ('side_a','side_b'):
        side = r[s]
        print(f"   {s}: {side['source_path'][:72]}")
        print(f"        {side['reason'][:88]}")
