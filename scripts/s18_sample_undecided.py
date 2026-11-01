#!/usr/bin/env python3
"""Session 18: sample undecided combos with evidence for review-bundle design."""
import json, collections, random
random.seed(42)

FNAME = {'regression':'regression','tree-based':'tree','evaluation':'evaluation','clustering':'clustering','generalization':'generalization','training-stability':'training-stability'}

# breakdown of 'mixed evidence' into sub-classes
sub = collections.Counter()
samples = []
for d, fn in FNAME.items():
    cfg = json.load(open('state/term-maps/dext-tier-config-v1.json'))
    broad = set(cfg['broad_terms'][d])
    domf = set(cfg['domain_folders'].get('ai-course', [])) | set(cfg['domain_folders'].get('master-ai', []))
    for line in open(f'scratch/s18-tiers-{fn}.jsonl'):
        r = json.loads(line)
        if r['tier'] != 'C': continue
        for side in ('side_a','side_b'):
            s = r[side]
            if s['verdict'] != 'undecided': continue
            if not s['reason'].startswith('mixed'): continue
            folder = s['folder']
            in_dom = folder in domf
            has_spec = any(t not in broad for t in s['terms'])
            if in_dom and has_spec: k = 'domain-folder+specific(code/mermaid-only)'
            elif in_dom: k = 'domain-folder+broad-only'
            elif has_spec: k = 'non-domain+specific'
            else: k = 'non-domain+broad-only(undecided bug?)'
            sub[k] += 1
            if k == 'non-domain+specific' and len(samples) < 8:
                samples.append((d, s['source_path'], s['terms']))
print('mixed-evidence sub-classes:', dict(sub.most_common()))
print()
for d, path, terms in samples:
    print(f'[{d}] {path}  terms={terms}')
