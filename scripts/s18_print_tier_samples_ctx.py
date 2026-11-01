#!/usr/bin/env python3
import json, random, sys
from pathlib import Path
random.seed(2026)
FNAME = {'regression':'regression','tree-based':'tree','evaluation':'evaluation','clustering':'clustering','generalization':'generalization','training-stability':'training-stability'}
pairs_by_id = {}
for d, fn in FNAME.items():
    for line in open(f'scratch/dossier-ext-{fn}-pairs.jsonl'):
        r = json.loads(line)
        pairs_by_id[r['candidate_id']] = r
tiers_by_tier = {'A': [], 'B': [], 'B3': []}
for d, fn in FNAME.items():
    for line in open(f'scratch/s18-tiers-{fn}.jsonl'):
        r = json.loads(line)
        if r['tier'] in tiers_by_tier:
            tiers_by_tier[r['tier']].append(r)
which = sys.argv[1]; n = int(sys.argv[2])
samp = random.sample(tiers_by_tier[which], min(n, len(tiers_by_tier[which])))
for r in samp:
    p = pairs_by_id[r['candidate_id']]
    print(f"[{r['domain']}] topic={r['topic']}  confirmed={p['confirmed']}")
    for sk, mk in (('ku_a','matches_a'),('ku_b','matches_b')):
        side = r['side_a' if sk == 'ku_a' else 'side_b']
        ms = p.get(mk, [])
        print(f"   {sk}: {side['source_path'][:70]}")
        for m in ms[:2]:
            print(f"        ctx: {(m.get('context') or '')[:135]}")
