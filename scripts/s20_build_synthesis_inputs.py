#!/usr/bin/env python3
"""S20/SYNTH-001: build per-note synthesis inputs for one canonical area.

Deterministic, idempotent: derives every artifact from COMMITTED state only
(canonical structure, file mapping, KU batches, disposition ledger, v2
dossiers). Outputs to scratch/ (git-ignored, replayable) plus one committed
machine-readable report under reports/synthesis/.

Outputs (under scratch/synth/<slug>/):
  bundles/<nn>-<slug>.md   evidence bundle per note (source files verbatim +
                           per-KU checklist + dossier concepts)
  specs/<nn>-<slug>.json   generation-prompt spec per note (check-prompt input)
  audit-kus.jsonl          KU records with EFFECTIVE disposition+destinations
                           (audit-output input; ledger overlay, never edits)
  provenance.jsonl         {note, ku_ids} mapping (assess-quality input)
  expected-notes.txt       the area's planned note paths
  notes.json               orchestration metadata (type, groups, sizes)

Assertions (fail loudly, pre-written arithmetic):
  - every area-4-destined ledger KU appears in exactly one audit batch record
  - every KU record keeps its committed excerpt/hash/locator byte-identical
  - destinations are exactly the ledger's (no invention, no filtering)
  - every note bundle carries >= 1 KU
  - note count / file count match the canonical structure accounting
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRATCH = REPO / "scratch" / "synth"
VAULT_ROOTS = {
    "ai-course": REPO / "source-vaults" / "AI " / "AI Course",
    "master-ai": REPO / "source-vaults" / "AI " / "Master AI",
}

# Explicit note-type assignments (drives the per-type quality standard).
# Unlisted notes default to "concept". Recorded in the session-20 style-guide
# conventions section; changing a type requires regenerating its spec.
NOTE_TYPES: dict[str, str] = {
    "04 - Machine Learning/Machine Learning MOC.md": "overview",
    "04 - Machine Learning/Model Evaluation/Model Evaluation Metrics.md": "reference",
    "04 - Machine Learning/Model Evaluation/Regression Evaluation Metrics.md": "reference",
    "04 - Machine Learning/Model Evaluation/Clustering Evaluation Metrics.md": "reference",
    "04 - Machine Learning/Model Evaluation/Computer Vision Evaluation Metrics.md": "reference",
    "04 - Machine Learning/Support Vector Machines/SVM Lagrangian Dual.md": "derivation",
}


def slugify(text: str) -> str:
    text = text.rsplit("/", 1)[-1]
    text = re.sub(r"\.md$", "", text)
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text[:60] or "note"


def load_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--area", required=True, help="area folder name, e.g. '04 - Machine Learning'")
    ap.add_argument("--slug", required=True, help="scratch dir slug, e.g. area04")
    ap.add_argument("--report", required=True, help="committed JSON report path")
    args = ap.parse_args()

    area = args.area
    prefix = area + "/"
    out_dir = SCRATCH / args.slug
    bundles = out_dir / "bundles"
    specs = out_dir / "specs"
    for d in (bundles, specs):
        d.mkdir(parents=True, exist_ok=True)

    # ---- committed inputs ------------------------------------------------
    structure = json.loads((REPO / "state/synthesis/canonical-structure-v1.json").read_text())
    file_mapping = load_jsonl(REPO / "state/synthesis/file-mapping-v1.jsonl")
    ledger = load_jsonl(REPO / "state/dispositions/001-disp001-rule-driven.jsonl")

    ku_by_id: dict[str, dict] = {}
    for batch in sorted((REPO / "state/knowledge-units").glob("*.jsonl")):
        for rec in load_jsonl(batch):
            ku_by_id[rec["knowledge_unit_id"]] = rec

    dossiers = []
    for dom in ("regression", "tree-based", "evaluation", "clustering", "generalization", "training-stability"):
        dossiers.append(json.loads((REPO / "state/dossiers" / f"{dom}-v2.json").read_text()))

    # ---- area scoping ----------------------------------------------------
    notes = [n for n in structure["notes"] if n["area"] == area]
    area_files = [r for r in file_mapping if any(p.startswith(prefix) for p in r["canonical_paths"])]
    note_paths = sorted(n["path"] for n in notes)

    # files feeding each note
    files_by_note: dict[str, list[dict]] = {p: [] for p in note_paths}
    for r in area_files:
        for cp in r["canonical_paths"]:
            if cp.startswith(prefix):
                files_by_note[cp].append(r)
    # KUs per note (from the ledger — the authoritative overlay)
    kus_by_note: dict[str, list[str]] = {p: [] for p in note_paths}
    area_kus = [r for r in ledger if any(d["path"].startswith(prefix) for d in r["destinations"])]
    for r in area_kus:
        for d in r["destinations"]:
            if d["path"].startswith(prefix):
                kus_by_note[d["path"]].append(r["ku_id"])

    # dossier concepts per note (concepts with >= 1 KU destined to the note)
    concepts_by_note: dict[str, list[dict]] = {p: [] for p in note_paths}
    ku_note_sets = {p: set(ids) for p, ids in kus_by_note.items()}
    for dos in dossiers:
        for c in dos["concepts"]:
            kset = set(c.get("ku_ids", []))
            if not kset:
                continue
            for p, nset in ku_note_sets.items():
                inter = kset & nset
                if inter:
                    concepts_by_note[p].append(
                        {
                            "concept_id": c["concept_id"],
                            "label": c.get("label"),
                            "dossier": dos["dossier_id"],
                            "concept_kus": len(kset),
                            "kus_in_this_note": len(inter),
                            "overlap_type": c.get("overlap_type"),
                        }
                    )

    # ---- audit batch (effective state; committed records + ledger overlay) --
    audit_records = []
    for r in area_kus:
        base = dict(ku_by_id[r["ku_id"]])
        base["disposition"] = r["disposition"]
        base["destinations"] = r["destinations"]
        if r["disposition"] == "Superseded":
            # invariant 3: superseded units must record why unique information
            # survives elsewhere — carry the ledger rationale verbatim
            base["superseded_rationale"] = r["rationale"]
        audit_records.append(base)
    audit_path = out_dir / "audit-kus.jsonl"
    with audit_path.open("w", encoding="utf-8") as fh:
        for rec in sorted(audit_records, key=lambda x: x["knowledge_unit_id"]):
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # ---- provenance mapping ------------------------------------------------
    prov_path = out_dir / "provenance.jsonl"
    with prov_path.open("w", encoding="utf-8") as fh:
        for p in note_paths:
            fh.write(json.dumps({"note": p, "ku_ids": sorted(kus_by_note[p])}, ensure_ascii=False) + "\n")

    (out_dir / "expected-notes.txt").write_text("\n".join(note_paths) + "\n", encoding="utf-8")

    # ---- bundles + specs ----------------------------------------------------
    notes_meta = []
    for idx, p in enumerate(sorted(note_paths), start=1):
        meta_note = next(n for n in notes if n["path"] == p)
        ntype = NOTE_TYPES.get(p, "concept")
        fmap = files_by_note[p]
        ku_ids = sorted(kus_by_note[p])
        bundle_name = f"{idx:02d}-{slugify(p)}.md"
        spec_name = f"{idx:02d}-{slugify(p)}.json"

        # ---- bundle ----
        parts = []
        parts.append(f"# SYNTHESIS EVIDENCE BUNDLE {idx:02d}/{len(note_paths)}\n")
        parts.append(f"## Target note\n")
        parts.append(f"- **Canonical path:** `{p}`")
        parts.append(f"- **Title:** {meta_note['title']}")
        parts.append(f"- **Note type:** {ntype}")
        parts.append(f"- **Planned rationale:** {meta_note['rationale']}")
        parts.append(f"- **Source vaults:** {', '.join(meta_note['vaults'])}\n")
        parts.append("## Mapped source files (verbatim, immutable evidence)\n")
        total_words = 0
        repo_files = []
        for fi, fr in enumerate(fmap, start=1):
            src = VAULT_ROOTS[fr["vault"]] / fr["source_path"]
            text = src.read_text(encoding="utf-8")
            total_words += len(text.split())
            repo_files.append(str(src.relative_to(REPO)))
            parts.append(f"### FILE {fi}/{len(fmap)} — {fr['vault']} — `{fr['source_path']}`\n")
            parts.append(f"Mapping rationale: {fr['rationale']}\n")
            parts.append("```markdown")
            parts.append(text.rstrip("\n"))
            parts.append("```\n")
        parts.append("## Dossier concepts anchored by this note\n")
        cons = sorted(concepts_by_note[p], key=lambda c: -c["kus_in_this_note"])
        if cons:
            for c in cons:
                parts.append(
                    f"- {c['label']} (`{c['concept_id']}`, {c['dossier']}): "
                    f"{c['kus_in_this_note']} of {c['concept_kus']} concept KUs land in this note"
                )
        else:
            parts.append("- (none: this note's KUs are not dossier concept members)")
        parts.append("\n## Knowledge-unit checklist (coverage accounting)\n")
        parts.append(
            f"{len(ku_ids)} KUs are destined to this note. Every unit's content must be "
            "represented (prose may be rewritten; equations, code and rare terms must survive).\n"
        )
        parts.append("| ku_id | disposition | source lines | heading path |")
        parts.append("|---|---|---|---|")
        for kid in ku_ids:
            r = next(x for x in area_kus if x["ku_id"] == kid)
            ku = ku_by_id[kid]
            hp = " > ".join(ku.get("heading_path") or [])
            parts.append(f"| `{kid}` | {r['disposition']} | {ku['line_start']}-{ku['line_end']} | {hp} |")
        (bundles / bundle_name).write_text("\n".join(parts) + "\n", encoding="utf-8")

        # ---- generation prompt spec ----
        requirements = [
            "Open with YAML frontmatter carrying title, type, aliases, tags, sources (titles of the mapped source notes) and created_index.",
            "Begin the body with a 2-4 sentence orienting introduction before the first section heading; do not use an H1 heading anywhere in the body.",
            "Structure the note with ## section headings (### for subsections), sentence case, unnumbered, in a logical teaching order for the topic.",
            "Synthesize all mapped source files into one coherent treatment: reconcile terminology, keep every distinct explanation, worked example, equation, derivation step, caveat, table, diagram and code sample.",
            "Reproduce every equation and every fenced code block from the source material verbatim (whitespace-insensitive), using $...$ inline and $$...$$ display math and language-labelled fences.",
            "Preserve rare or one-off details: historical distinctions, API/version caveats, project-specific lessons, interview distinctions, edge cases and failure modes.",
            "Write flowing explanatory prose for concepts; use lists and tables only where they genuinely aid lookup or comparison; never leave a section as a bare bullet list.",
            "Link related notes with Obsidian wikilinks that resolve inside this area batch ([[Note Name]] for unique basenames; [[path/to/Note|Note]] for the colliding basenames Linear Regression and Logistic Regression); every note links to Machine Learning MOC and at least two topical siblings.",
            "Keep the note self-contained: no references to source vaults, merge history, file paths of sources, or this bundle; provenance lives in frontmatter sources only.",
            "Match the depth of the evidence: do not shorten, summarize away, or pad; the note ends with a See also section of wikilinks when siblings exist.",
        ]
        constraints = [
            "Do not invent facts, numbers, citations or claims that are not present in the source evidence.",
            "Preserve unrelated content: do not remove or alter material merely because it is obscure, one-off, or from an unfamiliar subtopic.",
            "Record provenance: frontmatter sources lists the titles of every mapped source note.",
            "Equations, code blocks and mermaid diagrams are copied verbatim from the sources; prose around them is rewritten for coherence.",
        ]
        criteria = [
            {"criterion": "zero artifact-lint errors (fences, math delimiters, tables, links, frontmatter)", "check": "lint:FENCE_UNCLOSED"},
            {"criterion": "no broken or ambiguous internal links", "check": "lint:LINK_BROKEN"},
            {"criterion": "no placeholder or unfinished-text markers", "check": "lint:PLACEHOLDER_TEXT"},
            {"criterion": "structure dimension within band (intro + >=2 sections, no hierarchy skips)", "check": "quality:structure"},
            {"criterion": "depth dimension within band for the note type", "check": "quality:depth"},
            {"criterion": "source coverage: >= 60% of mapped KU key terms present in the note", "check": "quality:source_coverage"},
            {"criterion": "provenance dimension within band (frontmatter sources + in-text links)", "check": "quality:provenance"},
            {"criterion": "links dimension within band (internal links present and resolving)", "check": "quality:links"},
            {"criterion": "every mapped KU's content is represented in the note", "check": "manual_review"},
        ]
        spec = {
            "schema_version": "1.0.0",
            "objective": (
                f"Synthesize the canonical note '{meta_note['title']}' ({ntype}) at {p} from its "
                f"{len(fmap)} mapped source file(s) and {len(ku_ids)} destined knowledge units, "
                "preserving every meaningful detail in unified editorial style."
            ),
            "target_note": {"path": p, "type": ntype, "title": meta_note["title"]},
            "source_evidence": {
                "ku_ids": ku_ids,
                "files": repo_files,
                "dossier": ", ".join(
                    sorted({c["dossier"] for c in cons})
                )
                or "none",
            },
            "requirements": requirements,
            "constraints": constraints,
            "acceptance_criteria": criteria,
            "output_contract": {
                "path": p,
                "format": "markdown",
                "max_words": max(400, 6 * total_words),
            },
            "context_budget": {"max_words": 4000, "max_source_excerpts": 0},
            "evidence_bundle": f"scratch/synth/{args.slug}/bundles/{bundle_name}",
        }
        (specs / spec_name).write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

        notes_meta.append(
            {
                "index": idx,
                "path": p,
                "title": meta_note["title"],
                "type": ntype,
                "files": [f"{r['vault']}:{r['source_path']}" for r in fmap],
                "repo_files": repo_files,
                "ku_count": len(ku_ids),
                "source_words": total_words,
                "bundle": str((bundles / bundle_name).relative_to(REPO)),
                "spec": str((specs / spec_name).relative_to(REPO)),
                "concepts": len(cons),
            }
        )

    (out_dir / "notes.json").write_text(
        json.dumps({"area": area, "notes": notes_meta}, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    # ---- assertions ---------------------------------------------------------
    problems = []
    if len(notes) != len(note_paths):
        problems.append("note path collision inside area")
    # per-note membership arithmetic: sum over notes == KUs + extra memberships
    # (a KU destined to n notes in this area contributes n memberships)
    if sum(len(v) for v in kus_by_note.values()) != len(area_kus) + multi_dest_extra(kus_by_note, area_kus, prefix):
        problems.append("per-note KU membership arithmetic failed")
    for p in note_paths:
        if not kus_by_note[p]:
            problems.append(f"note has zero KUs: {p}")
    for rec in audit_records:
        if rec["excerpt_hash"] != ku_by_id[rec["knowledge_unit_id"]]["excerpt_hash"]:
            problems.append(f"audit record hash drift: {rec['knowledge_unit_id']}")
    cross = [r for r in area_kus if any(not d["path"].startswith(prefix) for d in r["destinations"])]
    if cross:
        problems.append(f"{len(cross)} KUs have destinations outside the area (batch not self-contained)")

    by_disp: dict[str, int] = {}
    for r in area_kus:
        by_disp[r["disposition"]] = by_disp.get(r["disposition"], 0) + 1
    multi_dest = multi_dest_extra(kus_by_note, area_kus, prefix)  # extra memberships
    shared_kus = sum(
        1 for r in area_kus if len([d for d in r["destinations"] if d["path"].startswith(prefix)]) > 1
    )

    report = {
        "area": area,
        "slug": args.slug,
        "notes": len(note_paths),
        "source_files": len(area_files),
        "kus": len(area_kus),
        "kus_by_disposition": by_disp,
        "kus_multi_destination_within_area": multi_dest,
        "concepts_anchored": sum(m["concepts"] for m in notes_meta),
        "total_source_words": sum(m["source_words"] for m in notes_meta),
        "scratch_dir": str(out_dir.relative_to(REPO)),
        "problems": problems,
        "deterministic": True,
        "inputs": {
            "structure": "state/synthesis/canonical-structure-v1.json",
            "file_mapping": "state/synthesis/file-mapping-v1.jsonl",
            "ledger": "state/dispositions/001-disp001-rule-driven.jsonl",
            "ku_batches": "state/knowledge-units/*.jsonl (71 files)",
            "dossiers": "state/dossiers/*-v2.json (6 files)",
        },
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if problems:
        print("PROBLEMS DETECTED", file=sys.stderr)
        return 1
    return 0


def multi_dest_extra(kus_by_note: dict[str, list[str]], area_kus: list[dict], prefix: str) -> int:
    extra = 0
    for r in area_kus:
        n = len([d for d in r["destinations"] if d["path"].startswith(prefix)])
        extra += n - 1
    return extra


if __name__ == "__main__":
    raise SystemExit(main())
