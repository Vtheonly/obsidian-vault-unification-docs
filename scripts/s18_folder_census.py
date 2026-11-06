#!/usr/bin/env python3
"""Session 18: complete subfolder census across all six pairs files."""
import json, collections

FNAME = {'regression':'regression','tree-based':'tree','evaluation':'evaluation','clustering':'clustering','generalization':'generalization','training-stability':'training-stability'}

def subfolder(path):
    parts = path.split('/')
    if len(parts) >= 2: return '/'.join(parts[:2])
    return '(root)/' + parts[0]

all_sf = collections.Counter()
for d, fn in FNAME.items():
    for line in open(f'scratch/dossier-ext-{fn}-pairs.jsonl'):
        p = json.loads(line)
        for side in ('ku_a','ku_b'):
            all_sf[(p[side]['vault'], subfolder(p[side]['source_path']))] += 1

print(f'{"vault":12s} {"subfolder":70s} {"pair-sides":>10s}')
for (v, s), c in sorted(all_sf.items(), key=lambda x: (x[0][0], -x[1])):
    print(f'{v:12s} {s:70s} {c:10d}')
print('TOTAL distinct subfolders:', len(all_sf))
