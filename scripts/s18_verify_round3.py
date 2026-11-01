#!/usr/bin/env python3
import json, sys
from pathlib import Path
def load_jsonl(p): return [json.loads(l) for l in open(p) if l.strip()]
problems = []
DELTA3 = {'evaluation': ('evaluation-delta3-bundle.json', ['evaluation-delta3-out.jsonl']),
          'generalization': ('generalization-delta3-bundle.json', ['generalization-delta3-out.jsonl']),
          'training-stability': ('training-stability-delta3-bundle.json', ['training-stability-delta3-out.jsonl'])}
ku_index = {}
for p in sorted(Path('state/knowledge-units').glob('0[1-7][0-9]-regen001-*.jsonl')):
    for r in load_jsonl(p): ku_index[r['knowledge_unit_id']] = r
for d, (bf, ofs) in DELTA3.items():
    bundle = json.load(open(f'scratch/s18-review/{bf}'))
    outputs = []
    for of in ofs: outputs.extend(load_jsonl(f'scratch/s18-review/{of}'))
    by_key = {(o['file'], o['term']): o for o in outputs}
    bkeys = {(c['file'], c['term']) for c in bundle['combos']}
    if set(by_key) != bkeys:
        problems.append(f'{d}: key mismatch missing={bkeys-set(by_key)} extra={set(by_key)-bkeys}')
    np = nr = 0
    for c in bundle['combos']:
        o = by_key.get((c['file'], c['term']))
        if not o: continue
        kids = [k['ku_id'] for k in c['kus']]
        vs = o.get('ku_verdicts', {})
        if set(vs) != set(kids):
            problems.append(f'{d}: ku mismatch {c["file"]}/{c["term"]}'); continue
        for kid in kids:
            if vs[kid] == 'participate': np += 1
            elif vs[kid] == 'reject': nr += 1
            else: problems.append(f'{d}: bad verdict')
    print(f'{d:20s} combos={len(bundle["combos"]):3d} lines={len(outputs):3d} accept={np:3d} reject={nr:3d}')
if problems:
    print('PROBLEMS:'); [print('  ', p) for p in problems[:20]]; sys.exit(1)
print('ROUND-3 VERIFICATION PASSED')
