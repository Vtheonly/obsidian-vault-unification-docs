#!/usr/bin/env python3
"""Session 18: subfolder + topic distributions per domain pairs file."""
import json, collections

FNAME = {'regression':'regression','tree-based':'tree','evaluation':'evaluation','clustering':'clustering','generalization':'generalization','training-stability':'training-stability'}

def subfolder(path):
    parts = path.split('/')
    if len(parts) >= 2: return '/'.join(parts[:2])
    return '(root) ' + parts[0]

for d, fn in FNAME.items():
    print(f'===== {d} =====')
    sf = collections.Counter(); tp = collections.Counter(); newkus = set()
    unconf = 0
    for line in open(f'scratch/dossier-ext-{fn}-pairs.jsonl'):
        p = json.loads(line)
        tp[p['topic']] += 1
        if p.get('unconfirmed_only'): unconf += 1
        for side in ('ku_a','ku_b'):
            sf[subfolder(p[side]['source_path'])] += 1
            newkus.add(p[side]['ku_id'])
    print('distinct new KUs:', len(newkus), '| unconfirmed_only pairs:', unconf)
    print('top 15 subfolders:')
    for s, c in sf.most_common(15): print(f'   {c:6d}  {s}')
    print('top 12 topics:')
    for t, c in tp.most_common(12): print(f'   {c:6d}  {t}')
    print()
