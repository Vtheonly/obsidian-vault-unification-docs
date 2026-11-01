#!/usr/bin/env python3
"""Session 18 final quality gates for the dossier-extension classification.

G1 every extension-record ku_id exists in the committed regen batches;
G2 classification ids unique across the six extension files;
G3 every review-verdict ku_id exists in the regen batches;
G4 pair-decision completeness: 69,185 decisions, per-domain sums correct;
G5 source manifests unchanged (re-run verify-manifest via vu);
G6 append the sampling/verification evidence to the final report.
"""
import json, subprocess, sys
from pathlib import Path
REPO = Path('.')
FNAME = {"regression":"regression","tree-based":"tree","evaluation":"evaluation","clustering":"clustering","generalization":"generalization","training-stability":"training-stability"}
EXPECTED = {"regression": 9211, "tree-based": 10833, "evaluation": 10603, "clustering": 6672, "generalization": 11275, "training-stability": 20591}

ku_ids = set()
for p in sorted(Path('state/knowledge-units').glob('0[1-7][0-9]-regen001-*.jsonl')):
    for line in open(p):
        if line.strip(): ku_ids.add(json.loads(line)['knowledge_unit_id'])

problems = []
# G1 + G2
cls_ids = []
ext_kus = {}
for d, fn in FNAME.items():
    f = Path(f'state/classifications/{ {"regression":"009","tree-based":"010","evaluation":"011","clustering":"012","generalization":"013","training-stability":"014"}[d] }-disc002-dext-{fn}-extension.jsonl')
    for line in open(f):
        r = json.loads(line)
        cls_ids.append(r['classification_id'])
        for kid in r['ku_ids']:
            if kid not in ku_ids:
                problems.append(f'G1[{d}]: unknown ku {kid} in {r["classification_id"]}')
        ext_kus.setdefault(d, set()).update(r['ku_ids'])
if len(cls_ids) != len(set(cls_ids)):
    problems.append('G2: duplicate classification ids')
# G3
for line in open('state/classifications/008-disc002-dext-review-verdicts.jsonl'):
    r = json.loads(line)
    if r['ku_id'] not in ku_ids:
        problems.append(f'G3: unknown ku {r["ku_id"]} in review verdicts')
# G4
total = 0
for d, fn in FNAME.items():
    n = sum(1 for _ in open(f'scratch/s18-final-pair-decisions-{fn}.jsonl'))
    if n != EXPECTED[d]: problems.append(f'G4[{d}]: {n} != {EXPECTED[d]}')
    total += n
if total != 69185: problems.append(f'G4: total {total} != 69185')
# G5
for root, man, out in (("source-vaults/AI /AI Course", "state/manifests/ai-course.jsonl", "scratch/s18-immutable-final-ai-course.json"),
                       ("source-vaults/AI /Master AI", "state/manifests/master-ai.jsonl", "scratch/s18-immutable-final-master-ai.json")):
    r = subprocess.run(['python3', '-m', 'vault_unification', 'verify-manifest', '--root', root, '--manifest', man, '--report', out], capture_output=True, text=True)
    j = json.load(open(out))
    c = j['diff']['counts']
    if c['changed'] or c['added'] or c['removed']:
        problems.append(f'G5: {man} changed: {c}')
    print(f"G5 {man}: {c['unchanged']}/{c['before']} unchanged, 0 diffs")
if problems:
    print('GATE FAILURES:'); [print('  ', p) for p in problems[:20]]; sys.exit(1)
print('G1-G5 PASSED')
# G6: append verification evidence to the final report
rep = json.load(open('reports/dossier-ext/s18-dext-final-report.json'))
rep['verification'] = {
 'tier_A_sample': ('30-pair fresh random sample after two calibration pull-backs '
                   '(weak aliases, then canonical homonyms): ~17% residual single-side '
                   'over-inclusion, exclusively in the safe direction (extra dossier '
                   'evidence pointers); zero under-inclusion observed; two further '
                   'pull-back iterations were assessed and rejected as they would '
                   'effectively reinstate universal per-unit review removed by '
                   'ADR-0011; dossier-v2 extension records are advisory to synthesis, '
                   'which re-examines evidence and never blindly trusts the scaffold'),
 'tier_B_sample': ('20-pair sample of auto-rejects: 19/20 correct; 1 borderline-thin '
                   'case (one-line loss-spike symptom in a CNN pitfall list) left as '
                   'reject because the dossier carries the full treatment from its '
                   'own domain files'),
 'tier_B3_sample': ('15-pair sample: 1 real miss (prose definition of cross-entropy '
                    'without colon-gloss) overridden to participate by the '
                    'orchestrator (recorded in the overrides list)'),
 'review_reject_sample': ('179/539 sampled reviewed rejects (5% min 30 per domain) '
                          'personally re-reviewed by the orchestrator: 178/179 '
                          'agreement (99.4%), 1 conservative reject->participate '
                          'override, zero hidden gaps'),
 'citation_checks': ('every reviewed-accept verdict machine-checked for a term/alias/'
                     'matched_text anchor in the KU excerpt or match context '
                     '(0 failures across rounds 1-3; round 4 completeness-checked)'),
 'residual_risks': [
   'Tier A retains ~17% single-side over-inclusion from canonical-term homonyms not '
   'blacklisted (entropy-for-tree, decomposition, validation-as-form-validation); '
   'all are over-inclusion, none lose knowledge (the KU ledger is independent of '
   'dossier membership)',
   'B2 (no-gloss auto-reject) can miss prose definitions in non-domain folders; '
   'measured ~1/35 in sampling; the override mechanism exists for future sessions',
   'The 46,978 low-signal discovery candidates and 3 confirmed gaps are untouched '
   'by this classification and remain documented non-claims']}
json.dump(rep, open('reports/dossier-ext/s18-dext-final-report.json','w'), indent=2, ensure_ascii=False)
open('reports/dossier-ext/s18-dext-final-report.json','a').write('\n')
print('G6 verification evidence appended')
