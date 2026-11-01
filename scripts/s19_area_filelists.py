#!/usr/bin/env python3
"""DISP-001 session 19: build the canonical-structure backbone + area file lists.

Derives (deterministically, from the committed KU batches) the per-area source
file lists that the mapping subagents consume, and the unified backbone area
definitions (designed by the orchestrator, documented in
state/synthesis/canonical-structure-v1.json once mappings are integrated).

Usage:
  python3 scripts/s19_area_filelists.py     # writes scratch/s19-mapping/*.txt
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRATCH = REPO / "scratch" / "s19-mapping"

# Unified backbone: canonical area -> source areas it unifies (vault:top-folder)
BACKBONE = {
    "01 - Foundations": [
        ("ai-course", "01 - Foundations and Overview"),
        ("master-ai", "01 - AI Foundations"),
    ],
    "02 - Mathematics": [
        ("master-ai", "02 - Mathematics"),
    ],
    "03 - Python and Data Tooling": [
        ("ai-course", "02 - Python and Data Tooling"),
    ],
    "04 - Machine Learning": [
        ("ai-course", "03 - Machine Learning"),
        ("master-ai", "03 - Machine Learning"),
    ],
    "05 - Neural Network Foundations": [
        ("ai-course", "04 - Neural Networks and Deep Learning Foundations"),
        ("master-ai", "04 - Neural Networks"),
    ],
    "06 - Computer Vision": [
        ("ai-course", "05 - Convolutional Neural Networks (CNN)"),
        ("ai-course", "06 - Image Processing"),
    ],
    "07 - Sequence Models": [
        ("ai-course", "07 - Sequence Models and RNNs"),
    ],
    "08 - Attention and Transformers": [
        ("ai-course", "08 - Attention and Transformers"),
        ("master-ai", "06 - Attention Mechanisms"),
        ("master-ai", "07 - Transformers"),
    ],
    "09 - NLP and Language Models": [
        ("master-ai", "05 - NLP Fundamentals"),
    ],
    "10 - Large Language Models": [
        ("master-ai", "08 - LLMs"),
    ],
    "11 - Foundation Models and Multimodal": [
        ("master-ai", "09 - Foundation Models"),
        ("master-ai", "23 - Multimodal AI"),
    ],
    "12 - Generative Models": [
        ("ai-course", "10 - Generative Models"),
    ],
    "13 - Training and Adaptation": [
        ("master-ai", "11 - Training"),
        ("master-ai", "12 - Fine-Tuning"),
    ],
    "14 - Inference and Production": [
        ("master-ai", "13 - Inference"),
        ("master-ai", "20 - AI Infrastructure"),
        ("master-ai", "21 - LLMOps and MLOps"),
        ("master-ai", "22 - Production AI"),
    ],
    "15 - Agents and Tooling": [
        ("master-ai", "15 - AI Agents"),
        ("master-ai", "16 - Multi-Agent Systems"),
        ("master-ai", "17 - RAG"),
        ("master-ai", "18 - Memory Systems"),
        ("master-ai", "19 - MCP"),
        ("master-ai", "25 - Frameworks and Tools"),
    ],
    "16 - Interpretability and Research": [
        ("master-ai", "14 - Interpretability"),
        ("master-ai", "24 - Research Frontiers"),
        ("master-ai", "10 - Model Architecture Research"),
    ],
    "17 - Papers": [
        ("master-ai", "26 - Papers"),
    ],
    "18 - Projects": [
        ("master-ai", "27 - Projects"),
    ],
    "19 - Reference and Practice": [
        ("ai-course", "09 - Quizzes and Question Banks"),
        ("master-ai", "28 - Glossary"),
        ("master-ai", "29 - Interview Prep"),
    ],
    "20 - Vault and Project Context": [
        ("master-ai", "00 - Vault Management"),
        ("master-ai", "(root)"),
        ("ai-course", "(root)"),
    ],
}


def main() -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    # inventory: all source files with sizes (from the vault trees, read-only)
    files: dict[tuple[str, str], list[tuple[str, int]]] = {}
    for vault, root in [("ai-course", REPO / "source-vaults/AI /AI Course"),
                        ("master-ai", REPO / "source-vaults/AI /Master AI")]:
        for p in sorted(root.rglob("*.md")):
            rel = p.relative_to(root).as_posix()
            top = rel.split("/")[0] if "/" in rel else "(root)"
            files.setdefault((vault, top), []).append((rel, p.stat().st_size))

    total = sum(len(v) for v in files.values())
    print(f"indexed {total} source files across {len(files)} source areas")

    manifest = {"backbone": {}, "source_areas": {}}
    for area, sources in BACKBONE.items():
        area_files = []
        for key in sources:
            fl = files.get(key, [])
            area_files.extend((key[0], rel, size) for rel, size in fl)
            manifest["source_areas"][f"{key[0]}:{key[1]}"] = len(fl)
        manifest["backbone"][area] = {
            "unifies": [f"{v}:{t}" for v, t in sources],
            "file_count": len(area_files),
        }
        out = SCRATCH / (area.replace(" ", "-").replace("/", "-") + ".txt")
        with out.open("w", encoding="utf-8") as fh:
            for vault, rel, size in area_files:
                fh.write(f"{vault}\t{rel}\t{size}\n")
        print(f"{area:45s} {len(area_files):4d} files -> {out.name}")

    # every source area must be consumed exactly once
    consumed = [k for sources in BACKBONE.values() for k in sources]
    missing = [k for k in files if k not in consumed]
    extra = [k for k in consumed if k not in files]
    assert not missing, f"unassigned source areas: {missing}"
    assert not extra, f"backbone references nonexistent areas: {extra}"
    assert sum(len(v) for v in files.values()) == 609, total
    (SCRATCH / "backbone.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("backbone covers all 609 files; wrote scratch/s19-mapping/backbone.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
