#!/usr/bin/env python3
"""Session 18: feature analysis over the six dossier-extension pairs files."""
import json, collections

FNAME = {'regression':'regression','tree-based':'tree','evaluation':'evaluation','clustering':'clustering','generalization':'generalization','training-stability':'training-stability'}
DOMS = list(FNAME.keys())

part = {}
for d in DOMS:
    dz = json.load(open(f"state/dossiers/{d.replace('tree-based','tree-based')}-v1.json"))
    part[d] = set(dz['accounting']['participating_ku_ids'])

batchmap = {
 'regression': ['001-ext001-ai-course-03.1-regression','002-ext002-master-ai-supervised-learning'],
 'tree-based': ['002-ext002-master-ai-supervised-learning','003-ext004-ai-course-03.7-tree-based-models'],
 'evaluation': ['004-ext005-master-ai-evaluation','005-ext005-ai-course-03.6-model-evaluation'],
 'clustering': ['006-ext008-master-ai-unsupervised','007-ext008-ai-course-clustering-dimreduction'],
 'generalization': ['008-ext009-master-ai-generalization','009-ext009-ai-course-04.3-regularization'],
 'training-stability': ['010-ext010-master-ai-training-stability','011-ext010-ai-course-04.3-init-gradients'],
}
orig_files, orig_kus = {}, {}
for d, bl in batchmap.items():
    fs, ks = set(), set()
    for b in bl:
        for line in open(f'state/knowledge-units/{b}.jsonl'):
            r = json.loads(line)
            fs.add(r['source_id'].split(':',1)[1])
            ks.add(r['knowledge_unit_id'])
    orig_files[d], orig_kus[d] = fs, ks

folders = collections.Counter()
pair_kind = collections.Counter()
for d in DOMS:
    fn = FNAME[d]
    for line in open(f'scratch/dossier-ext-{fn}-pairs.jsonl'):
        p = json.loads(line)
        for side in ('ku_a','ku_b'):
            sp = p[side]['source_path']
            folders[(p[side]['vault'], sp.split('/')[0])] += 1
        # classify pair by membership
        a_in, b_in = p['ku_a']['ku_id'] in part[d], p['ku_b']['ku_id'] in part[d]
        a_orig = p['ku_a']['ku_id'] in orig_kus[d]
        b_orig = p['ku_b']['ku_id'] in orig_kus[d]
        if a_in and b_in: pair_kind[(d,'both-in-dossier')] += 1
        elif a_in or b_in: pair_kind[(d,'one-in-dossier')] += 1
        elif a_orig or b_orig: pair_kind[(d,'orig-batch-not-in-dossier')] += 1
        else: pair_kind[(d,'both-new')] += 1

print('=== Top-level folder distribution across all pairs ===')
for (v, f), c in sorted(folders.items(), key=lambda x:-x[1]):
    print(f'{v:12s} {f:60s} {c}')
print()
print('=== Pair membership classes per domain ===')
for d in DOMS:
    for k in ('both-in-dossier','one-in-dossier','orig-batch-not-in-dossier','both-new'):
        print(f'{d:20s} {k:30s} {pair_kind[(d,k)]}')
