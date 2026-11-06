"""Mechanical See-Also cross-link audit (AUDIT-012; closes the F-0035
remaining risk).

Deterministic, read-only audit that enumerates every source-vault
cross-reference link of the See-Also family and mechanically checks whether
the unified vault's destination note still links the same target topic.

Two source conventions exist in the corpus (survey evidence, session 30):

- **Vault B (Master AI)**: heading-based ``See Also`` blocks — 314 files,
  bullet items whose first wikilink is the cross-reference. A ``References``
  heading (1 file: ``28 - Glossary/03 - Notation Conventions.md``) is a
  bibliography, NOT a See-Also block, and is out of scope by definition.
- **Vault A (AI Course)**: inline ``*See also:* [[target]]`` references —
  8 files, 9 occurrences (no heading-based blocks anywhere in the vault).

Per unique (source note, target) pair the audit assigns exactly one verdict:

- ``carried_over`` — at least one destination note (per the committed
  file-mapping) contains a wikilink resolving to the target's canonical
  unified path (basename, path-form, or alias; ambiguous candidates count
  when the canonical path is among them).
- ``dropped`` — the target topic exists in the unified vault and the
  destination notes exist, but none of them links it (the F-0035 defect
  shape). Defect candidates; each becomes a findings-ledger entry after
  orchestrator confirmation.
- ``target_absent_from_unified`` — the source target does not resolve in
  its own vault (phantom / planned note) and no unified note carries its
  stem; no carry-over obligation exists (nothing to link to).
- ``ambiguous_source_target`` — the target resolves ambiguously inside the
  source vault to files mapping to divergent canonical paths, or a phantom
  stem matches multiple unified notes; needs review, not an auto-defect.
- ``source_note_unmapped`` — the file-mapping has no canonical path for the
  source note (expected 0; the mapping covers all 609 source files).
- ``dest_missing`` — a mapped canonical destination path does not exist on
  disk (expected 0; audit-output would have flagged it).

Method notes:
- Source-target resolution uses Obsidian semantics via the same machinery
  as ``check-links`` (``linkcheck._resolve_target``): path-like targets
  resolve by vault-relative path first, bare stems by basename.
- Phantom targets (unresolved in their source vault) are matched against
  the unified vault by note stem, case-insensitive, exactly-one required.
- Destination coverage scans every wikilink of the destination note (whole
  note, not only a See Also section), excluding code fences, matching the
  F-0035 repair convention ("topic survives as unlinked prose" was the
  defect; a link anywhere in the note is a carry-over).
- Multi-mapped source notes (``multi: true``) check every canonical
  destination; any covering destination counts as carried over.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .linkcheck import _resolve_target, build_vault_index
from .mdextract import extract_structure

SEE_ALSO_HEADING = re.compile(r"^#{1,6}[ \t]+see also[ \t]*$", re.I | re.M)
_WIKILINK = re.compile(r"\[\[([^\]\|#]+)(#[^\]\|]*)?(\|[^\]]*)?\]\]")
INLINE_SEE_ALSO = re.compile(
    r"(?i)see[ \t]*also[ \t]*:?[ \t]*\*{0,2}[ \t]*(\[\[[^\]]*\]\])"
)
_BULLET = re.compile(r"^\s*[-*•][ \t]+")
_NEXT_HEADING = re.compile(r"^#{1,6}[ \t]+", re.M)

VAULT_KEYS = {"master-ai": "master-ai", "ai-course": "ai-course"}


def load_file_mapping(path: str | Path) -> dict[tuple[str, str], list[str]]:
    """Load the committed file-mapping JSONL.

    Returns a dict keyed by ``(vault, source_relpath_posix)`` whose values
    are the (possibly multiple) canonical unified paths. Empty lists are
    preserved (they map to the ``source_note_unmapped`` verdict class).
    """
    mapping: dict[tuple[str, str], list[str]] = {}
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            vault = VAULT_KEYS.get(row.get("vault"))
            if vault is None:
                raise ValueError(f"unknown vault key in file mapping: {row.get('vault')!r}")
            mapping[(vault, Path(row["source_path"]).as_posix())] = list(
                row.get("canonical_paths") or []
            )
    return mapping


def extract_master_see_also(root: str | Path) -> list[dict]:
    """Extract heading-based See-Also links from the Master AI vault.

    Each record: {source_path, target, item, line}. One record per bullet
    item carrying at least one wikilink (the first wikilink is the target;
    subsequent wikilinks inside one item are recorded as extra_targets so
    nothing is silently ignored).
    """
    root_path = Path(root)
    records: list[dict] = []
    for md in sorted(root_path.rglob("*.md")):
        rel = md.relative_to(root_path).as_posix()
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ValueError(f"unreadable source note {rel}: {exc}") from exc
        for hm in SEE_ALSO_HEADING.finditer(text):
            rest = text[hm.end():]
            nxt = _NEXT_HEADING.search(rest)
            block = rest[: nxt.start()] if nxt else rest
            block_start_line = text[: hm.end()].count("\n") + 1
            for offset, line in enumerate(block.splitlines()):
                if not _BULLET.match(line):
                    continue
                links = _WIKILINK.findall(line)
                if not links:
                    continue
                target = links[0][0].strip()
                extras = [t[0].strip() for t in links[1:]]
                records.append(
                    {
                        "source_path": rel,
                        "target": target,
                        "extra_targets": extras,
                        "item": line.strip(),
                        "line": block_start_line + offset,
                        "convention": "heading-block",
                    }
                )
    return records


def extract_course_inline_see_also(root: str | Path) -> list[dict]:
    """Extract inline ``*See also:* [[target]]`` references from the AI
    Course vault. Each record: {source_path, target, item, line}."""
    root_path = Path(root)
    records: list[dict] = []
    for md in sorted(root_path.rglob("*.md")):
        rel = md.relative_to(root_path).as_posix()
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise ValueError(f"unreadable source note {rel}: {exc}") from exc
        for im in INLINE_SEE_ALSO.finditer(text):
            link_text = im.group(1)
            lm = _WIKILINK.search(link_text)
            if not lm:
                continue
            line_no = text[: im.start()].count("\n") + 1
            line = text.splitlines()[line_no - 1] if line_no <= len(text.splitlines()) else ""
            records.append(
                {
                    "source_path": rel,
                    "target": lm.group(1).strip(),
                    "extra_targets": [],
                    "item": line.strip(),
                    "line": line_no,
                    "convention": "inline",
                }
            )
    return records


def _index_stems(index: dict) -> dict[str, list[str]]:
    """Map lowercase note stem -> list of vault-relative posix paths."""
    stems: dict[str, list[str]] = {}
    for rel in index["by_relpath"]:
        stem = Path(rel).stem.lower()
        stems.setdefault(stem, []).append(rel)
    return stems


_ALIASES_RE = re.compile(r"^aliases:\s*\[(.*?)\]\s*$", re.M)


def _index_aliases(index: dict) -> dict[str, list[str]]:
    """Map lowercase frontmatter alias -> note relpaths (deterministic).

    Only the inline list form ``aliases: [a, b]`` is parsed; other YAML
    shapes are ignored and reported as unmatched (conservative).
    """
    aliases: dict[str, list[str]] = {}
    for rel, path in index["by_relpath"].items():
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        m = re.match(r"^---\n(.*?)\n---", text, re.S)
        if not m:
            continue
        am = _ALIASES_RE.search(m.group(1))
        if not am:
            continue
        for alias in am.group(1).split(","):
            alias = alias.strip().strip("\"'")
            if alias:
                aliases.setdefault(alias.lower(), []).append(rel)
    return aliases


def _resolve_source_target(index: dict, target: str) -> tuple[str, str | None, list[str]]:
    """Resolve a wikilink target inside a SOURCE vault.

    Returns (resolution_class, relpath_or_None, candidate_relpaths) where
    resolution_class is 'resolved' | 'ambiguous' | 'unresolved'.
    """
    resolution, path, candidates = _resolve_target(index, target, (".md",))
    root: Path = index["root"]
    if resolution == "resolved" and path is not None:
        return "resolved", path.relative_to(root).as_posix(), []
    if resolution == "ambiguous" and candidates:
        rels = sorted(c.relative_to(root).as_posix() for c in candidates)
        return "ambiguous", None, rels
    return "unresolved", None, []


def _covering_links(index: dict, note_rel: str, canonical: set[str]) -> list[dict]:
    """Return the destination note's wikilinks that resolve to any of the
    canonical target paths (whole-note scan, code fences excluded)."""
    note_path: Path = index["root"] / note_rel
    structure = extract_structure(note_path)
    covering: list[dict] = []
    for link in structure["wikilinks"]:
        resolution, path, candidates = _resolve_target(index, link["target"], (".md",))
        hit_paths: set[str] = set()
        if resolution == "resolved" and path is not None:
            hit_paths = {path.relative_to(index["root"]).as_posix()}
        elif resolution == "ambiguous" and candidates:
            hit_paths = {c.relative_to(index["root"]).as_posix() for c in candidates}
        inter = hit_paths & canonical
        if inter:
            covering.append(
                {
                    "link_target": link["target"],
                    "line": link.get("line"),
                    "resolved_to": sorted(inter),
                }
            )
    return covering


def load_decisions(path: str | Path) -> dict[tuple[str, str, str], dict]:
    """Load orchestrator decision records for specific (vault, source note,
    target) pairs.

    Each JSONL row: {"vault", "source_note", "target", "action":
    "resolve"|"exclude", "canonical_target"? (resolve), "rationale",
    "decided_by", "evidence"?}. Rows with unknown action or a resolve row
    missing canonical_target raise ValueError (fail loudly rather than
    silently skipping a recorded decision).
    """
    decisions: dict[tuple[str, str, str], dict] = {}
    with Path(path).open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            key = (row.get("vault"), row.get("source_note"), row.get("target"))
            if key[0] not in VAULT_KEYS or not all(key):
                raise ValueError(f"decision row {lineno}: bad key {key!r}")
            action = row.get("action")
            if action not in ("resolve", "exclude"):
                raise ValueError(f"decision row {lineno}: unknown action {action!r}")
            if action == "resolve" and not row.get("canonical_target"):
                raise ValueError(f"decision row {lineno}: resolve without canonical_target")
            if not row.get("rationale") or not row.get("decided_by"):
                raise ValueError(
                    f"decision row {lineno}: rationale and decided_by are required"
                )
            decisions[key] = row
    return decisions


def audit_see_also(
    *,
    master_root: str | Path,
    course_root: str | Path,
    file_mapping: str | Path,
    output_root: str | Path,
    decisions: str | Path | None = None,
) -> dict:
    """Run the full mechanical See-Also carry-over audit (read-only)."""
    master_root, course_root = Path(master_root), Path(course_root)
    output_root = Path(output_root)
    mapping = load_file_mapping(file_mapping)
    decision_rows = load_decisions(decisions) if decisions else {}

    master_index = build_vault_index(master_root)
    course_index = build_vault_index(course_root)
    out_index = build_vault_index(output_root)
    out_stems = _index_stems(out_index)
    out_aliases = _index_aliases(out_index)

    records = [
        ("master-ai", r) for r in extract_master_see_also(master_root)
    ] + [
        ("ai-course", r) for r in extract_course_inline_see_also(course_root)
    ]

    # de-duplicate to unique (vault, source_path, target) pairs, keeping all
    # occurrences as evidence (duplicate items are recorded, not dropped)
    pairs: dict[tuple[str, str, str], list[dict]] = {}
    for vault, rec in records:
        pairs.setdefault((vault, rec["source_path"], rec["target"]), []).append(rec)

    verdicts: dict[str, int] = {
        "carried_over": 0,
        "dropped": 0,
        "target_absent_from_unified": 0,
        "ambiguous_source_target": 0,
        "source_note_unmapped": 0,
        "dest_missing": 0,
        "excluded_documented": 0,
    }
    findings: list[dict] = []
    pair_rows: list[dict] = []

    for (vault, src, target), occurrences in sorted(pairs.items()):
        src_key = (vault, src)
        dests = mapping.get(src_key, [])
        src_index = master_index if vault == "master-ai" else course_index

        row = {
            "vault": vault,
            "source_note": src,
            "target": target,
            "occurrences": len(occurrences),
            "occurrence_lines": [o["line"] for o in occurrences],
            "convention": occurrences[0]["convention"],
        }

        if not dests:
            row["verdict"] = "source_note_unmapped"
            row["detail"] = "file-mapping has no canonical path for the source note"
            verdicts["source_note_unmapped"] += 1
            findings.append(row)
            pair_rows.append(row)
            continue

        decision = decision_rows.get((vault, src, target))
        if decision is not None and decision["action"] == "exclude":
            row["verdict"] = "excluded_documented"
            row["decision"] = {
                "action": "exclude",
                "rationale": decision["rationale"],
                "decided_by": decision["decided_by"],
                "evidence": decision.get("evidence"),
            }
            verdicts["excluded_documented"] += 1
            findings.append(row)
            pair_rows.append(row)
            continue

        missing_dests = [d for d in dests if d not in out_index["by_relpath"]]
        if missing_dests:
            row["verdict"] = "dest_missing"
            row["detail"] = {"missing_destinations": missing_dests}
            verdicts["dest_missing"] += 1
            findings.append(row)
            pair_rows.append(row)
            continue

        # resolve the target inside its own source vault
        res_class, src_target_rel, cands = _resolve_source_target(src_index, target)
        target_canonical: set[str] = set()
        ambiguity: list[str] = []

        if decision is not None and decision["action"] == "resolve":
            target_canonical = {decision["canonical_target"]}
            row["decision"] = {
                "action": "resolve",
                "canonical_target": decision["canonical_target"],
                "rationale": decision["rationale"],
                "decided_by": decision["decided_by"],
                "evidence": decision.get("evidence"),
            }
        elif res_class == "resolved" and src_target_rel is not None:
            mapped = mapping.get((vault, src_target_rel))
            if mapped is not None:
                target_canonical = set(mapped)
            else:  # pragma: no cover - mapping covers all files
                row["verdict"] = "source_note_unmapped"
                row["detail"] = f"target source note {src_target_rel} unmapped"
                verdicts["source_note_unmapped"] += 1
                findings.append(row)
                pair_rows.append(row)
                continue
        elif res_class == "ambiguous":
            mapped_sets = [tuple(sorted(mapping.get((vault, c), []))) for c in cands]
            unique_sets = {s for s in mapped_sets if s}
            if len(unique_sets) == 1 and unique_sets != {()}:
                target_canonical = set(next(iter(unique_sets)))
            else:
                ambiguity = cands
        else:  # unresolved in its own vault -> phantom / planned target
            stem = Path(target).stem.lower()
            matches = out_stems.get(stem, [])
            if len(matches) == 1:
                target_canonical = {matches[0]}
            elif len(matches) > 1:
                ambiguity = matches
            else:
                alias_matches = out_aliases.get(stem, [])
                if len(alias_matches) == 1:
                    target_canonical = {alias_matches[0]}
                elif len(alias_matches) > 1:
                    ambiguity = alias_matches

        if ambiguity:
            row["verdict"] = "ambiguous_source_target"
            row["detail"] = {
                "source_resolution": res_class,
                "candidates": ambiguity,
                "note": "ambiguous target; needs review, not an auto-defect",
            }
            verdicts["ambiguous_source_target"] += 1
            findings.append(row)
            pair_rows.append(row)
            continue

        if not target_canonical:
            row["verdict"] = "target_absent_from_unified"
            row["detail"] = (
                "target unresolved in its source vault and no unified note "
                "carries its stem; no carry-over obligation"
            )
            verdicts["target_absent_from_unified"] += 1
            findings.append(row)
            pair_rows.append(row)
            continue

        covering: dict[str, list[dict]] = {}
        for dest in sorted(dests):
            hits = _covering_links(out_index, dest, target_canonical)
            if hits:
                covering[dest] = hits
        row["target_canonical"] = sorted(target_canonical)
        row["destination_notes"] = sorted(dests)
        if covering:
            row["verdict"] = "carried_over"
            row["carried_by"] = {d: covering[d] for d in sorted(covering)}
            verdicts["carried_over"] += 1
            pair_rows.append(row)
        else:
            row["verdict"] = "dropped"
            row["detail"] = (
                "target topic exists in the unified vault but no destination "
                "note links it (whole-note scan, fences excluded)"
            )
            verdicts["dropped"] += 1
            findings.append(row)
            pair_rows.append(row)

    total_pairs = len(pairs)
    checked = sum(verdicts.values())
    return {
        "command": "see-also-audit",
        "scope": {
            "master_root": str(master_root),
            "course_root": str(course_root),
            "output_root": str(output_root),
            "file_mapping": str(file_mapping),
            "conventions": [
                "Master AI heading-based 'See Also' blocks (case-insensitive)",
                "AI Course inline '*See also:* [[target]]' references",
            ],
            "exclusions": [
                "'References' heading in 28 - Glossary/03 - Notation Conventions.md "
                "(bibliography of external citations, not a See-Also block)",
            ],
        },
        "method": {
            "target_resolution": "Obsidian semantics via linkcheck._resolve_target "
            "(path-form by vault-relative path first, bare stems by basename)",
            "phantom_targets": "unresolved in source vault -> matched against unified "
            "vault by note stem (case-insensitive, exactly-one required)",
            "carry_over": "any wikilink of any mapped destination note resolving to the "
            "target's canonical unified path (whole note, code fences excluded)",
            "phantom_alias_matching": "phantom targets additionally match unified "
            "frontmatter aliases (inline list form, case-insensitive, exactly-one)",
            "decisions_file": (
                "orchestrator decision rows (resolve/exclude with rationale and "
                "decided_by) applied deterministically before verdict assignment"
                if decisions
                else None
            ),
            "multi_mapped_sources": "all canonical destinations checked; any covering "
            "destination counts as carried over",
            "dedupe": "unique (vault, source note, target) pairs; duplicate occurrences "
            "recorded as evidence",
        },
        "denominators": {
            "see_also_link_occurrences": len(records),
            "unique_source_note_target_pairs": total_pairs,
            "pairs_with_verdict": checked,
            "master_ai_files_with_heading_block": len(
                {r["source_path"] for v, r in records if v == "master-ai"}
            ),
            "ai_course_files_with_inline_reference": len(
                {r["source_path"] for v, r in records if v == "ai-course"}
            ),
        },
        "results": verdicts,
        "decisions_applied": {
            "file": str(decisions) if decisions else None,
            "rows": len(decision_rows),
            "applied": sum(
                1 for r in pair_rows if r.get("decision") is not None
            ),
        },
        "findings": findings,
        "pair_rows": pair_rows,
        "deterministic": True,
    }
