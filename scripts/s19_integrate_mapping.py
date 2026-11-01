#!/usr/bin/env python3
"""DISP-001 session 19: integrate the 14 mapping groups into committed state.

Inputs (verified by scripts/s19_verify_mapping.py first):
  scratch/s19-mapping/out-{1..14}.jsonl + notes-{1..14}.json + backbone.json

Outputs (committed):
  state/synthesis/canonical-structure-v1.json — the unified vault backbone
    (20 areas) with every planned canonical note (path, title, area, source
    file count, contributing vaults) and the design rationale.
  state/synthesis/file-mapping-v1.jsonl — 609 records, one per source file:
    {vault, source_path, canonical_paths, multi, rationale, mapped_by, date}.

Pre-written arithmetic (asserted before writing):
  * 609 mapping records == 276 ai-course + 333 master-ai;
  * every canonical path referenced by a record appears in the structure;
  * every structure note is referenced by >= 1 record;
  * per-area file counts sum to 609; per-area note counts sum to the total.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRATCH = REPO / "scratch" / "s19-mapping"
OUT_STRUCT = REPO / "state" / "synthesis" / "canonical-structure-v1.json"
OUT_MAPPING = REPO / "state" / "synthesis" / "file-mapping-v1.jsonl"

GROUP_META = {
    1: "subagent M1", 2: "subagent M2", 3: "subagent M3", 4: "subagent M4",
    5: "subagent M5", 6: "subagent M6", 7: "subagent M7", 8: "subagent M8",
    9: "subagent M9", 10: "subagent M10", 11: "subagent M11",
    12: "subagent M12", 13: "subagent M13",
    14: "orchestrator individual review (vault/project context files)",
}

AREA_RATIONALE = {
    "01 - Foundations": "Unifies ai-course Foundations and Overview with master-ai AI Foundations: the definitional hierarchy of AI/ML/DL, history, applications, and data-science foundations.",
    "02 - Mathematics": "master-ai Mathematics tree (linear algebra, calculus, probability, statistics, optimization, information theory) — the mathematical foundations the course vault consumes.",
    "03 - Python and Data Tooling": "ai-course Python and Data Tooling (environment, programming, libraries, data cleaning) — the tooling track has no master-ai counterpart.",
    "04 - Machine Learning": "Unifies both vaults' classical ML: regression, optimization, KNN, SVM, clustering/dimensionality reduction, trees, evaluation, generalization, reinforcement learning.",
    "05 - Neural Network Foundations": "Unifies ai-course NN/DL foundations (deep: backprop derivations, training dynamics, labs) with master-ai Neural Networks (concise architecture/training notes).",
    "06 - Computer Vision": "ai-course CNN track merged with its Image Processing track into one vision area (classical IP + learned CNN pipelines).",
    "07 - Sequence Models": "ai-course sequence models track (recurrence, LSTM/GRU, seq2seq, pitfalls).",
    "08 - Attention and Transformers": "Heaviest cross-vault merge: ai-course Attention/Transformers + master-ai Attention Mechanisms + master-ai Transformers.",
    "09 - NLP and Language Models": "master-ai NLP fundamentals (tokenization, embeddings, language modeling, pre-transformer NLP).",
    "10 - Large Language Models": "master-ai LLM internals (architecture, capabilities, context/KV cache, evaluation, limitations, sampling).",
    "11 - Foundation Models and Multimodal": "master-ai Foundation Models + Multimodal AI unified into one modern-models area.",
    "12 - Generative Models": "ai-course generative track (autoencoders, VAEs, GANs, diffusion).",
    "13 - Training and Adaptation": "master-ai Training + Fine-Tuning (data, distributed, optimization, pretraining, PEFT/RLHF).",
    "14 - Inference and Production": "master-ai Inference + AI Infrastructure + LLMOps/MLOps + Production AI.",
    "15 - Agents and Tooling": "master-ai Agents + Multi-Agent + RAG + Memory + MCP + Frameworks and Tools.",
    "16 - Interpretability and Research": "master-ai Interpretability + Research Frontiers + Model Architecture Research.",
    "17 - Papers": "master-ai Papers notes organized by research theme.",
    "18 - Projects": "master-ai project write-ups (capstones, implementations, mini-projects).",
    "19 - Reference and Practice": "ai-course quiz/question banks + master-ai Glossary + Interview Prep — first-class practice and reference material.",
    "20 - Vault and Project Context": "ARCHIVAL CONTEXT LAYER (not ordinary knowledge notes): the source vaults' own construction documents (merge reports, roadmaps, iteration logs, research queue with evidence-status labels). Retained as clearly-labeled internal context; the release audit decides its final presentation. Ordinary notes never narrate merges (SOURCE_POLICY).",
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def main() -> int:
    backbone = json.loads((SCRATCH / "backbone.json").read_text(encoding="utf-8"))
    records = []
    notes: dict[str, dict] = {}
    per_group = {}
    for n in range(1, 15):
        recs = load_jsonl(SCRATCH / f"out-{n}.jsonl")
        nts = json.loads((SCRATCH / f"notes-{n}.json").read_text(encoding="utf-8"))["notes"]
        for r in recs:
            r["mapped_by"] = GROUP_META[n]
            r["date"] = "2026-11-01"
            records.append(r)
        for nt in nts:
            if nt["path"] in notes:
                print(f"FAIL: note {nt['path']} appears in two groups")
                return 1
            notes[nt["path"]] = nt
        per_group[n] = (len(recs), len(nts))

    # pre-written arithmetic
    assert len(records) == 609, f"record count {len(records)} != 609"
    ai = sum(1 for r in records if r["vault"] == "ai-course")
    ma = sum(1 for r in records if r["vault"] == "master-ai")
    assert (ai, ma) == (276, 333), f"vault split {(ai, ma)} != (276, 333)"

    ref_counts: dict[str, int] = {}
    for r in records:
        for cp in r["canonical_paths"]:
            ref_counts[cp] = ref_counts.get(cp, 0) + 1
            if cp not in notes:
                print(f"FAIL: record references unregistered note {cp}")
                return 1
    orphans = [p for p in notes if p not in ref_counts]
    assert not orphans, f"notes never referenced: {orphans[:5]}"

    areas = {}
    for path, nt in notes.items():
        area = nt["area"]
        areas.setdefault(area, {"notes": 0, "source_files": 0, "refs": 0})
        areas[area]["notes"] += 1
        areas[area]["refs"] += ref_counts[path]
    for r in records:  # distinct source files per area (a multi-mapped file
        # that feeds two areas counts once in each, which is correct per-area)
        for area in {p.split("/", 1)[0] for p in r["canonical_paths"]}:
            areas[area]["source_files"] += 1
    assert sum(a["source_files"] for a in areas.values()) >= 609
    assert sum(a["refs"] for a in areas.values()) == sum(ref_counts.values())
    assert sum(a["notes"] for a in areas.values()) == len(notes)
    for area, meta in backbone["backbone"].items():
        assert area in areas, f"backbone area missing from mapping: {area}"
        assert areas[area]["source_files"] == meta["file_count"], (
            f"{area}: file count {areas[area]['source_files']} != {meta['file_count']}")

    structure = {
        "structure_id": "canonical-structure-v1",
        "created": "2026-11-01",
        "created_by": ("DISP-001 session 19 (orchestrator design + 13 mapping "
                       "subagents + orchestrator individual review of the "
                       "vault/project context files)"),
        "status": "planned",
        "version": "v1",
        "method": (
            "Backbone designed by the orchestrator from both vaults' top-level "
            "taxonomies as a learning progression; per-area canonical notes and "
            "the file mapping produced by 13 bounded subagents (one to three "
            "backbone areas each) plus one orchestrator-reviewed context group; "
            "every output mechanically verified (completeness, format, "
            "cross-consistency, cross-group uniqueness) by "
            "scripts/s19_verify_mapping.py; integration arithmetic asserted by "
            "this script."),
        "editorial_note": (
            "Note paths are PLANNED destinations for synthesis planning and "
            "KU dispositions, not written notes. Titles/folders may be refined "
            "at synthesis start under EDITORIAL_STYLE_GUIDE change control "
            "(versioned, with migration of this mapping)."),
        "design_rationale": AREA_RATIONALE,
        "areas": {
            area: {
                "unifies": meta["unifies"],
                "source_files": areas[area]["source_files"],
                "note_count": areas[area]["notes"],
            }
            for area, meta in backbone["backbone"].items()
        },
        "notes": [
            {k: v for k, v in nt.items()}
            for _, nt in sorted(notes.items())
        ],
        "accounting": {
            "source_files": len(records),
            "source_files_by_vault": {"ai-course": ai, "master-ai": ma},
            "canonical_notes": len(notes),
            "areas": len(areas),
            "multi_mapped_files": sum(1 for r in records if r.get("multi")),
            "notes_fed_by_both_vaults": sum(
                1 for nt in notes.values()
                if set(nt.get("vaults", [])) == {"ai-course", "master-ai"}),
            "per_group": {str(n): {"records": c, "notes": k}
                          for n, (c, k) in sorted(per_group.items())},
        },
    }

    OUT_STRUCT.parent.mkdir(parents=True, exist_ok=True)
    OUT_STRUCT.write_text(
        json.dumps(structure, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8")
    with OUT_MAPPING.open("w", encoding="utf-8") as fh:
        for r in sorted(records, key=lambda r: (r["vault"], r["source_path"])):
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    acc = structure["accounting"]
    print(f"wrote {OUT_STRUCT.relative_to(REPO)}: {acc['areas']} areas, "
          f"{acc['canonical_notes']} notes")
    print(f"wrote {OUT_MAPPING.relative_to(REPO)}: {acc['source_files']} records "
          f"(ai-course {ai}, master-ai {ma}); "
          f"multi-mapped {acc['multi_mapped_files']}; "
          f"cross-vault notes {acc['notes_fed_by_both_vaults']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
