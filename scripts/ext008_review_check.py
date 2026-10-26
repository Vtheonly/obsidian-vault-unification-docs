#!/usr/bin/env python3
"""EXT-008-REVIEW mechanical verification of 005-ext008-clustering-dimreduction-overlap.jsonl.

Independent, read-only re-verification (EXT-005/EXT-007-REVIEW precedent, adapted):

  CHECK 1  every evidence quote is a byte-exact substring of the referenced
           KU's excerpt in the batches 006 + 007.
  CHECK 2  every evidence quote appears byte-exact at its stated line(s) in the
           ORIGINAL source file (roots 'source-vaults/AI /Master AI' and
           'source-vaults/AI /AI Course'; note the space in 'AI '). Exact line
           required (off-by-one reported separately); for multi-line quotes the
           joined slice from stated lines[0] to lines[-1] must contain the
           quote. Also verifies every stated line falls inside the citing KU's
           own [line_start, line_end] span.
  CHECK 3  structural: required schema fields present; evidence ku_ids ==
           record ku_ids (exact set equality); every record cross-vault
           (master-ai + ai-course in ku_ids AND in evidence); ids unique and
           sequential OC-ext008-0001..0027; no duplicate quotes within a record
           or across the file; jsonschema validation against
           schemas/overlap-classification.schema.json.
  CHECK 6  append-only discipline: committed classification files
           001-ext003, 002-ext004, 003-ext005, 004-ext007 are byte-identical
           to their git HEAD versions (sha256 of working copy vs
           `git show HEAD:<path>`); `git status --short` reports no modified
           tracked files (only legitimately-new untracked EXT-008 artifacts).

Writes NOTHING to state/ (only stdout).
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLS_PATH = REPO / "state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl"
BATCHES = [
    REPO / "state/knowledge-units/006-ext008-master-ai-unsupervised.jsonl",
    REPO / "state/knowledge-units/007-ext008-ai-course-clustering-dimreduction.jsonl",
]
ROOTS = [
    REPO / "source-vaults/AI /Master AI",
    REPO / "source-vaults/AI /AI Course",
]
SCHEMA = REPO / "schemas/overlap-classification.schema.json"
COMMITTED_CLS = [
    "state/classifications/001-ext003-regression-overlap.jsonl",
    "state/classifications/002-ext004-tree-based-overlap.jsonl",
    "state/classifications/003-ext005-evaluation-overlap.jsonl",
    "state/classifications/004-ext007-evaluation-addendum.jsonl",
]
ALLOWED_UNTRACKED_PREFIXES = (
    "reports/extraction/ext008-",
    "scripts/ext008_",
    "state/classifications/005-ext008-",
    "state/knowledge-units/006-ext008-",
    "state/knowledge-units/007-ext008-",
    "state/term-maps/clustering-domain-v1.json",
)

failures: list[str] = []
notes: list[str] = []

records = [json.loads(l) for l in CLS_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]

kus: dict[str, dict] = {}
for path in BATCHES:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            ku = json.loads(line)
            kus[ku["knowledge_unit_id"]] = ku

counts = {"quotes": 0, "byte_exact": 0, "line_exact": 0, "line_off_by_one": 0,
          "line_fail": 0, "span_violations": 0, "multiline": 0}

# ---------------- CHECK 1 + CHECK 2 ----------------
for rec in records:
    cid = rec["classification_id"]
    for ev in rec.get("evidence", []):
        counts["quotes"] += 1
        ku = kus.get(ev["ku_id"])
        if ku is None:
            failures.append(f"{cid}: evidence ku_id {ev['ku_id']} not found in batches 006/007")
            continue
        if ev["source_path"] != ku["source_path"]:
            failures.append(
                f"{cid}: evidence source_path {ev['source_path']!r} != KU source_path {ku['source_path']!r}")
        q = ev["quote"]
        if q in ku["excerpt"]:
            counts["byte_exact"] += 1
        else:
            failures.append(f"{cid}: CHECK1 FAIL quote not byte-exact in excerpt of {ev['ku_id']}: {q[:120]!r}")

        # original source file
        src = None
        for root in ROOTS:
            cand = root / ev["source_path"]
            if cand.exists():
                src = cand
                break
        if src is None:
            failures.append(f"{cid}: source file not found for {ev['source_path']!r}")
            continue
        src_lines = src.read_text(encoding="utf-8").splitlines()
        joined = "\n".join(src_lines)

        stated_lines = ev["lines"]
        if len(stated_lines) > 1:
            counts["multiline"] += 1
        # every stated line must be inside the KU's own span
        for ln in stated_lines:
            if not (ku["line_start"] <= ln <= ku["line_end"]):
                counts["span_violations"] += 1
                failures.append(
                    f"{cid}: stated line {ln} outside KU {ev['ku_id']} span "
                    f"[{ku['line_start']},{ku['line_end']}]")
            if not (1 <= ln <= len(src_lines)):
                failures.append(f"{cid}: stated line {ln} beyond file length {len(src_lines)}")

        # multi-line quotes: joined slice from stated lines must contain quote
        if len(stated_lines) > 1:
            lo, hi = stated_lines[0], stated_lines[-1]
            if 1 <= lo <= hi <= len(src_lines):
                slice_txt = "\n".join(src_lines[lo - 1:hi])
                if q not in slice_txt:
                    failures.append(
                        f"{cid}: CHECK2 FAIL multi-line quote not contained in joined "
                        f"slice L{lo}-L{hi} of {ev['source_path']!r}: {q[:100]!r}")

        # exact-position verification: find every occurrence of the quote,
        # compute the 1-based line of each occurrence start; pass iff some
        # occurrence starts at the stated first line.
        first_line = stated_lines[0]
        occ_lines = []
        start = 0
        while True:
            pos = joined.find(q, start)
            if pos < 0:
                break
            occ_lines.append(joined[:pos].count("\n") + 1)
            start = pos + 1
        if not occ_lines:
            counts["line_fail"] += 1
            failures.append(
                f"{cid}: CHECK2 FAIL quote text not found in ORIGINAL source "
                f"{ev['source_path']!r} (KU {ev['ku_id']}): {q[:100]!r}")
        elif first_line in occ_lines:
            counts["line_exact"] += 1
            if len(occ_lines) > 1:
                notes.append(
                    f"{cid}: quote occurs at multiple source lines {occ_lines}; "
                    f"stated {first_line} is among them (ambiguous but correct)")
        else:
            nearest = min(occ_lines, key=lambda x: abs(x - first_line))
            if abs(nearest - first_line) == 1:
                counts["line_off_by_one"] += 1
                failures.append(
                    f"{cid}: CHECK2 FAIL off-by-one: stated line {first_line}, "
                    f"quote found at {nearest} ({ev['ku_id']})")
            else:
                counts["line_fail"] += 1
                failures.append(
                    f"{cid}: CHECK2 FAIL stated line {first_line}, quote found at "
                    f"{occ_lines} ({ev['ku_id']})")

# ---------------- CHECK 3: structural ----------------
struct_fail: list[str] = []
required_fields = ["classification_id", "task_id", "topic", "overlap_type",
                   "ku_ids", "rationale", "evidence", "classified_by", "date"]
valid_types = {"Exact Duplicate", "Semantic Duplicate", "Partial Overlap",
               "Complementary Content", "Conflict or Historical Difference"}

cross_vault_ok = 0
type_census: dict[str, int] = {}
for rec in records:
    cid = rec["classification_id"]
    for f in required_fields:
        if f not in rec:
            struct_fail.append(f"{cid}: missing required field {f}")
    if rec.get("overlap_type") not in valid_types:
        struct_fail.append(f"{cid}: invalid overlap_type {rec.get('overlap_type')!r}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", rec.get("date", "")):
        struct_fail.append(f"{cid}: bad date {rec.get('date')!r}")
    if rec.get("task_id") != "EXT-008":
        struct_fail.append(f"{cid}: unexpected task_id {rec.get('task_id')!r}")

    # evidence ku_ids == record ku_ids (EXACT set equality)
    ev_ids = {ev["ku_id"] for ev in rec.get("evidence", [])}
    if ev_ids != set(rec["ku_ids"]):
        struct_fail.append(
            f"{cid}: evidence ku_ids != record ku_ids "
            f"(evidence-only={sorted(ev_ids - set(rec['ku_ids']))}, "
            f"record-only={sorted(set(rec['ku_ids']) - ev_ids)})")

    # every ku_id exists in the batches
    for kid in rec["ku_ids"]:
        if kid not in kus:
            struct_fail.append(f"{cid}: ku_id {kid} not in batches 006/007")

    # cross-vault: both prefixes in ku_ids AND in evidence
    prefixes = {kus[k]["source_id"].split(":", 1)[0] for k in rec["ku_ids"] if k in kus}
    ev_prefixes = {kus[e["ku_id"]]["source_id"].split(":", 1)[0]
                   for e in rec.get("evidence", []) if e["ku_id"] in kus}
    if prefixes == {"master-ai", "ai-course"}:
        cross_vault_ok += 1
    else:
        struct_fail.append(f"{cid}: ku_ids not cross-vault: {sorted(prefixes)}")
    if not {"master-ai", "ai-course"} <= ev_prefixes:
        struct_fail.append(f"{cid}: evidence does not quote both vaults: {sorted(ev_prefixes)}")

    type_census[rec["overlap_type"]] = type_census.get(rec["overlap_type"], 0) + 1

# ids unique + sequential
ids = [r["classification_id"] for r in records]
expected = [f"OC-ext008-{i:04d}" for i in range(1, len(records) + 1)]
if len(ids) != len(set(ids)):
    struct_fail.append(f"duplicate classification ids: {ids}")
if ids != expected:
    struct_fail.append(f"id sequence mismatch: expected {expected}, got {ids}")

# no duplicate quotes within a record or across the file
all_quotes = [ev["quote"] for r in records for ev in r["evidence"]]
if len(all_quotes) != len(set(all_quotes)):
    from collections import Counter
    for q, n in Counter(all_quotes).items():
        if n > 1:
            struct_fail.append(f"duplicate quote across file ({n}x): {q[:90]!r}")
for r in records:
    rq = [ev["quote"] for ev in r["evidence"]]
    if len(rq) != len(set(rq)):
        struct_fail.append(f"{r['classification_id']}: duplicate quotes inside record")

# schema validation
try:
    import jsonschema
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for rec in records:
        for err in validator.iter_errors(rec):
            struct_fail.append(f"{rec['classification_id']}: schema: {err.message} "
                               f"at {list(err.absolute_path)}")
except ImportError:
    notes.append("jsonschema not available — schema validation skipped in script "
                 "(validate separately)")

# duplicate-each-other check: no two records with identical ku_id SETS
seen_sets: dict[tuple, str] = {}
for rec in records:
    key = tuple(sorted(rec["ku_ids"]))
    if key in seen_sets:
        notes.append(f"{rec['classification_id']} shares the exact ku_id set with "
                     f"{seen_sets[key]} — distinct claims on same units (check semantics)")
    else:
        seen_sets[key] = rec["classification_id"]

# ---------------- CHECK 6: append-only discipline ----------------
appendonly_fail: list[str] = []
for rel in COMMITTED_CLS:
    try:
        head = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO,
                              capture_output=True, check=True).stdout
        work = (REPO / rel).read_bytes()
        hs, ws = hashlib.sha256(head).hexdigest(), hashlib.sha256(work).hexdigest()
        if hs != ws:
            appendonly_fail.append(f"{rel}: working copy ({ws}) differs from HEAD ({hs})")
        else:
            notes.append(f"{rel} byte-unchanged vs HEAD: sha256 {ws}")
    except subprocess.CalledProcessError as e:
        appendonly_fail.append(f"git show failed for {rel}: {e}")

# git status: no modified tracked files; untracked only in EXT-008 namespaces
status = subprocess.run(["git", "status", "--short"], cwd=REPO,
                        capture_output=True, check=True).stdout.decode()
for line in status.splitlines():
    code, _, path = line.partition(" ")
    path = path.strip().strip('"')
    if "R" in code or "M" in code or "D" in code or "C" in code:
        appendonly_fail.append(f"git status shows modified/deleted tracked file: {line}")
    elif code == "??":
        if not any(path.startswith(p) or path == p for p in ALLOWED_UNTRACKED_PREFIXES):
            appendonly_fail.append(f"git status shows unexpected untracked path: {line}")
        else:
            notes.append(f"untracked (expected EXT-008 artifact): {path}")

# ---------------- report ----------------
print(f"records: {len(records)}  type census: {type_census}")
print(f"CHECK1 quotes: {counts['quotes']} checked, {counts['byte_exact']} byte-exact "
      f"in KU excerpts, {counts['quotes'] - counts['byte_exact']} FAILED")
print(f"CHECK2 quotes: {counts['line_exact']} at EXACTLY the stated source line, "
      f"{counts['line_off_by_one']} off-by-one, {counts['line_fail']} not found/other; "
      f"{counts['multiline']} multi-line quotes slice-verified; "
      f"{counts['span_violations']} stated lines outside KU span")
print(f"CHECK3 cross-vault records: {cross_vault_ok}/{len(records)}; "
      f"structural failures: {len(struct_fail)}")
for f in struct_fail:
    print("  STRUCT-FAIL:", f)
print(f"CHECK6 append-only failures: {len(appendonly_fail)}")
for f in appendonly_fail:
    print("  APPENDONLY-FAIL:", f)
if notes:
    print("notes:")
    for n in notes:
        print("  -", n)
print(f"evidence/quote failures: {len(failures)}")
for f in failures:
    print("  FAIL:", f)

participating = sorted({k for r in records for k in r["ku_ids"]})
ma = sum(1 for k in participating if kus[k]["source_id"].startswith("master-ai:"))
co = sum(1 for k in participating if kus[k]["source_id"].startswith("ai-course:"))
print(f"participating KUs: {len(participating)} (master-ai {ma}, ai-course {co})")
print(f"batch-coverage: {len(participating)}/{len(kus)} KUs of batches 006+007 participate; "
      f"non-participating: {sorted(set(kus) - set(participating))}")

total_fail = len(failures) + len(struct_fail) + len(appendonly_fail)
print(f"TOTAL FAILURES: {total_fail}")
sys.exit(1 if total_fail else 0)
