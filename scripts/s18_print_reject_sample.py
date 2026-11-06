#!/usr/bin/env python3
import json, sys
from pathlib import Path
REPO = Path('.')
frame = json.load(open('scratch/s18-review/reject-sample-frame.json'))
ku_index = {}
for p in sorted(Path('state/knowledge-units').glob('0[1-7][0-9]-regen001-*.jsonl')):
    for line in open(p):
        if line.strip():
            r = json.loads(line)
            ku_index[r['knowledge_unit_id']] = r
start = int(sys.argv[1]); end = int(sys.argv[2])
n = 0
for domain, items in frame.items():
    for it in items:
        n += 1
        if n < start or n > end: continue
        ku = ku_index.get(it['ku_id'], {})
        exc = (ku.get('excerpt','') or '').replace('\n',' ')[:230]
        hp = ' > '.join(ku.get('heading_path', []))[:60]
        print(f"#{n} [{domain}] term={it['term']}")
        print(f"   {it['file'][:78]}")
        print(f"   h: {hp}")
        print(f"   e: {exc}")
        print()
