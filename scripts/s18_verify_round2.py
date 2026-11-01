#!/usr/bin/env python3
"""Session 18: verify round-2 (delta) review outputs — V1 completeness + V2 citations."""
import json, random, sys
from pathlib import Path
REPO = Path('.')
random.seed(2828)

def load_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]

problems = []
stats = {}
ku_index = {}
for p in sorted(Path('state/knowledge-units').glob('0[1-7][0-9]-regen001-*.jsonl')):
    for r in load_jsonl(p):
        ku_index[r['knowledge_unit_id']] = r

DELTA = {
 'regression': ['regression-delta-bundle.json', ['regression-delta-out.jsonl']],
 'tree-based': ['tree-based-delta-bundle.json', ['tree-based-delta-out.jsonl']],
 'evaluation': ['evaluation-delta-bundle.json', ['evaluation-delta-out.jsonl']],
 'clustering': ['clustering-delta-bundle.json', ['clustering-delta-out.jsonl']],
 'generalization': ['generalization-delta-bundle.json', ['generalization-delta-out.jsonl']],
 'training-stability': ['training-stability-delta-bundle.json',
                        ['training-stability-delta-out-p1.jsonl', 'training-stability-delta-out-p2.jsonl']],
}
TM = {'regression':'regression','tree-based':'tree','evaluation':'evaluation','clustering':'clustering','generalization':'generalization','training-stability':'training-stability'}
for d, (bf, ofs) in DELTA.items():
    bundle = json.load(open(f'scratch/s18-review/{bf}'))
    outputs = []
    for of in ofs:
        outputs.extend(load_jsonl(f'scratch/s18-review/{of}'))
    by_key = {}
    for o in outputs:
        key = (o['file'], o['term'])
        if key in by_key: problems.append(f'V1[{d}]: duplicate {key}')
        by_key[key] = o
    bkeys = {(c['file'], c['term']) for c in bundle['combos']}
    miss, extra = bkeys - set(by_key), set(by_key) - bkeys
    if miss: problems.append(f'V1[{d}]: {len(miss)} missing (e.g. {sorted(miss)[:2]})')
    if extra: problems.append(f'V1[{d}]: {len(extra)} extra')
    tm = json.load(open(f'state/term-maps/{TM[d]}-domain-v1.json'))
    np = nr = bad = 0
    for c in bundle['combos']:
        o = by_key.get((c['file'], c['term']))
        if not o: continue
        kids = [k['ku_id'] for k in c['kus']]
        vs = o.get('ku_verdicts', {})
        if set(vs) != set(kids):
            problems.append(f'V1[{d}]: ku set mismatch {c["file"]}/{c["term"]}')
            continue
        for kid in kids:
            if vs[kid] == 'participate':
                np += 1
                ku = ku_index.get(kid, {})
                exc = (ku.get('excerpt','') or '').lower()
                entry = next((k for k in c['kus'] if k['ku_id']==kid), None)
                ctxs = ' '.join((m.get('context') or '') for m in (entry or {}).get('matches', [])).lower()
                term = c['term']
                if term.startswith('__'): 
                    if len(exc.strip()) < 10: bad += 1; problems.append(f'V2[{d}]: hash-accept empty {kid}')
                    continue
                needles = {term.lower()} | {a.lower() for a in tm.get(term, [])} | {(m.get('matched_text') or '').lower() for m in (entry or {}).get('matches', [])}
                if not any(n and n in exc for n in needles) and not any(n and n in ctxs for n in needles):
                    bad += 1
                    problems.append(f'V2[{d}]: accept {kid} term {term!r} no anchor')
            elif vs[kid] == 'reject':
                nr += 1
            else:
                problems.append(f'V1[{d}]: bad verdict {vs[kid]!r}')
    stats[d] = {'combos': len(bundle['combos']), 'lines': len(outputs), 'accepts': np, 'rejects': nr, 'cite_fail': bad}
    print(f'{d:20s} combos={len(bundle["combos"]):4d} lines={len(outputs):4d} accept={np:4d} reject={nr:4d} cite_fail={bad}')
if problems:
    print('PROBLEMS:'); [print('  ', p) for p in problems[:25]]
    sys.exit(1)
json.dump(stats, open('scratch/s18-review/verify-round2-summary.json','w'), indent=1)
print('ROUND-2 VERIFICATION PASSED')
