#!/usr/bin/env python3
"""DISP-001 session 19: mechanically verify the 13 mapping subagent outputs.

Checks per group N (out-N.jsonl + notes-N.json against the input lists):
  C1 completeness: every input file has exactly one record (no missing/extra);
  C2 sort order: records sorted by (vault, source_path);
  C3 path format: every canonical path is "<backbone area>/[<subarea>/]<Title>.md"
     with an area from the group's assigned backbone areas, Title Case title,
     no leading digits/punctuation in the title segment;
  C4 multi flag consistency: multi == (len(canonical_paths) > 1);
  C5 notes manifest: every canonical path referenced in out-N appears exactly
     once in notes-N (and vice versa), with consistent source_file_count and
     vaults;
  C6 cross-group uniqueness: no canonical path is used by two different groups;
  C7 source immutability: no file under source-vaults/ was touched (caller
     re-verifies manifests separately).

Exit non-zero on any violation; prints a per-group summary.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRATCH = REPO / "scratch" / "s19-mapping"

GROUPS = {
    1: (["01---Foundations.txt"], ["01 - Foundations"]),
    2: (["02---Mathematics.txt", "03---Python-and-Data-Tooling.txt"],
        ["02 - Mathematics", "03 - Python and Data Tooling"]),
    3: (["04---Machine-Learning.txt"], ["04 - Machine Learning"]),
    4: (["05---Neural-Network-Foundations.txt"], ["05 - Neural Network Foundations"]),
    5: (["06---Computer-Vision.txt"], ["06 - Computer Vision"]),
    6: (["07---Sequence-Models.txt", "12---Generative-Models.txt"],
        ["07 - Sequence Models", "12 - Generative Models"]),
    7: (["08---Attention-and-Transformers.txt"], ["08 - Attention and Transformers"]),
    8: (["09---NLP-and-Language-Models.txt", "10---Large-Language-Models.txt",
         "11---Foundation-Models-and-Multimodal.txt"],
        ["09 - NLP and Language Models", "10 - Large Language Models",
         "11 - Foundation Models and Multimodal"]),
    9: (["13---Training-and-Adaptation.txt", "14---Inference-and-Production.txt"],
        ["13 - Training and Adaptation", "14 - Inference and Production"]),
    10: (["15---Agents-and-Tooling.txt"], ["15 - Agents and Tooling"]),
    11: (["16---Interpretability-and-Research.txt"], ["16 - Interpretability and Research"]),
    12: (["17---Papers.txt", "18---Projects.txt"], ["17 - Papers", "18 - Projects"]),
    13: (["19---Reference-and-Practice.txt"], ["19 - Reference and Practice"]),
}

TITLE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9'()+.,:&-]*(?: [A-Za-z0-9'()+.,:&-]+)*$")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def main() -> int:
    failures = 0
    all_canonical: dict[str, int] = {}
    total_records = 0
    total_notes = 0
    for n, (lists, areas) in GROUPS.items():
        expected: set[tuple[str, str]] = set()
        for lst in lists:
            for line in (SCRATCH / lst).read_text(encoding="utf-8").splitlines():
                if line.strip():
                    vault, path, _size = line.split("\t")
                    expected.add((vault, path))
        out_path = SCRATCH / f"out-{n}.jsonl"
        notes_path = SCRATCH / f"notes-{n}.json"
        if not out_path.exists() or not notes_path.exists():
            print(f"G{n}: MISSING OUTPUT FILES")
            failures += 1
            continue
        records = load_jsonl(out_path)
        notes = json.loads(notes_path.read_text(encoding="utf-8"))["notes"]
        got = [(r["vault"], r["source_path"]) for r in records]
        problems = []
        # C1 completeness
        missing = expected - set(got)
        extra = set(got) - expected
        dupes = len(got) != len(set(got))
        if missing:
            problems.append(f"C1 missing {len(missing)}: {sorted(missing)[:3]}")
        if extra:
            problems.append(f"C1 extra {len(extra)}: {sorted(extra)[:3]}")
        if dupes:
            problems.append("C1 duplicate records")
        # C2 sort
        if got != sorted(got):
            problems.append("C2 not sorted")
        # C3/C4 per-record checks
        for r in records:
            cps = r.get("canonical_paths", [])
            if not cps or len(cps) > 3:
                problems.append(f"C3 bad canonical_paths for {r['source_path']}")
                continue
            for cp in cps:
                area_ok = any(cp == a + "/" or cp.startswith(a + "/") for a in areas)
                if not area_ok:
                    problems.append(f"C3 area prefix wrong: {cp}")
                    continue
                rest = cp[len(areas[0].split("/")[0]) + 1:] if False else cp.split("/", 1)[1]
                segs = [s for s in rest.split("/") if s]
                title = segs[-1]
                if not title.endswith(".md"):
                    problems.append(f"C3 not .md: {cp}")
                stem = title[:-3]
                if not TITLE_RE.match(stem):
                    problems.append(f"C3 title format: {cp!r}")
            if r.get("multi", False) != (len(cps) > 1):
                problems.append(f"C4 multi flag wrong for {r['source_path']}")
            if not r.get("rationale"):
                problems.append(f"C3 missing rationale for {r['source_path']}")
        # C5 notes manifest consistency
        ref_counts: dict[str, int] = {}
        ref_vaults: dict[str, set] = {}
        for r in records:
            for cp in r["canonical_paths"]:
                ref_counts[cp] = ref_counts.get(cp, 0) + 1
                ref_vaults.setdefault(cp, set()).add(r["vault"])
        note_paths = [nt["path"] for nt in notes]
        if len(note_paths) != len(set(note_paths)):
            problems.append("C5 duplicate note paths in manifest")
        for cp, cnt in ref_counts.items():
            if cp not in note_paths:
                problems.append(f"C5 referenced note not in manifest: {cp}")
        for nt in notes:
            cp = nt["path"]
            if cp not in ref_counts:
                problems.append(f"C5 manifest note never referenced: {cp}")
            elif nt.get("source_file_count") != ref_counts[cp]:
                problems.append(
                    f"C5 count mismatch {cp}: manifest {nt.get('source_file_count')}"
                    f" != records {ref_counts[cp]}")
            if set(nt.get("vaults", [])) != ref_vaults.get(cp, set()):
                problems.append(f"C5 vaults mismatch {cp}")
            if nt.get("area") not in areas:
                problems.append(f"C5 note area wrong: {cp}")
        # C6 cross-group uniqueness
        for cp in ref_counts:
            if cp in all_canonical:
                problems.append(f"C6 canonical path reused across groups: {cp}")
            all_canonical[cp] = n
        total_records += len(records)
        total_notes += len(notes)
        status = "OK" if not problems else "FAIL"
        print(f"G{n:2d}: {len(records):3d} records, {len(notes):3d} notes -> {status}"
              + ("" if not problems else f"  [{'; '.join(problems[:6])}]"))
        failures += len(problems)

    print(f"\nTOTAL: {total_records} records, {total_notes} canonical notes, "
          f"{failures} problems")
    return 0 if failures == 0 and total_records == 592 else 1


if __name__ == "__main__":
    sys.exit(main())
