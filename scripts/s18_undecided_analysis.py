#!/usr/bin/env python3
"""Session 18: analyze undecided (Tier C) composition at file/term granularity."""
import json, collections
from pathlib import Path

FNAME = {'regression':'regression','tree-based':'tree','evaluation':'evaluation','clustering':'clustering','generalization':'generalization','training-stability':'training-stability'}

reasons = collections.Counter()
file_term = {}  # domain -> set of (file, term)
for d, fn in FNAME.items():
    ft = set()
    for line in open(f'scratch/s18-tiers-{fn}.jsonl'):
        r = json.loads(line)
        if r['tier'] != 'C': continue
        for side in ('side_a','side_b'):
            s = r[side]
            if s['verdict'] != 'undecided': continue
            reasons[s['reason'].split(':')[0]] += 1
            for t in s['terms']:
                ft.add((s['source_path'], t))
    file_term[d] = ft
    print(f'{d:20s} undecided (file,term) combos: {len(ft)}')
total = sum(len(v) for v in file_term.values())
print('TOTAL (file,term) combos:', total)
print()
print('undecided side reasons:', dict(reasons.most_common()))
