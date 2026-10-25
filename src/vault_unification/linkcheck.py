"""Obsidian link, embed and anchor integrity checking.

Builds a vault-wide file index and resolves every wikilink, embed, internal
Markdown link, heading anchor and block reference. Problems are classified
explicitly:

- ``broken``: no file matches the target;
- ``ambiguous``: multiple files match (Obsidian would prompt);
- ``missing_anchor``: target file exists but the referenced heading does not;
- ``missing_block``: target file exists but the block id does not;
- ``external``: an outside link, reported separately (not an error).

Known limitations (v0.1):
- heading matching is case-sensitive text equality after whitespace
  normalisation; numbered/emoji variant anchors may not match exactly;
- Markdown links with URL fragments/percent-encoding are matched literally;
- links inside code fences are excluded by design (Obsidian also ignores
  them in some contexts; residual risk is recorded as a limitation).
"""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path

from .mdextract import extract_structure


def build_vault_index(root: str | os.PathLike, extensions: tuple[str, ...] = (".md",)) -> dict:
    """Index vault files by relative path and basename for link resolution."""
    root_path = Path(root)
    by_relpath: dict[str, Path] = {}
    by_basename: dict[str, list[Path]] = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames.sort()
        for name in sorted(filenames):
            abs_path = Path(dirpath) / name
            rel = abs_path.relative_to(root_path).as_posix()
            by_relpath[rel] = abs_path
            by_basename[name].append(abs_path)
    return {"root": root_path, "by_relpath": by_relpath, "by_basename": dict(by_basename)}


def _resolve_target(index: dict, target: str, extensions: tuple[str, ...]) -> tuple[str, Path | None, list[Path]]:
    """Resolve a wikilink target string.

    Returns (resolution, path, candidates) where resolution is one of
    'resolved', 'ambiguous', 'broken'. Bare stems (no '/') resolve by
    basename the way Obsidian does, so multiple same-named files produce
    'ambiguous'; path-like targets resolve by vault-relative path first.
    """
    if not target:
        return "resolved", None, []  # pure anchor/self links are handled by caller

    if "/" in target or target.endswith(tuple(extensions)):
        # 1. exact relative-path match (with or without extension)
        normalized = target if target.endswith(tuple(extensions)) else f"{target}.md"
        if normalized in index["by_relpath"]:
            return "resolved", index["by_relpath"][normalized], []
        if target in index["by_relpath"]:
            return "resolved", index["by_relpath"][target], []

    # 2. basename match (Obsidian default for bare stems)
    stem = target.rsplit("/", 1)[-1]
    base_candidates: list[Path] = []
    for ext in ("",) + tuple(extensions):
        key = f"{stem}{ext}" if ext else stem
        if key in index["by_basename"]:
            base_candidates.extend(index["by_basename"][key])
    # also match files whose full name is the target (e.g. image.png)
    if target in index["by_basename"]:
        base_candidates.extend(index["by_basename"][target])
    # dedupe while preserving order: targets that already carry an extension
    # can match the same file through both keys
    base_candidates = list(dict.fromkeys(base_candidates))

    if len(base_candidates) == 1:
        return "resolved", base_candidates[0], []
    if len(base_candidates) > 1:
        # filter by path suffix match when target contains '/'
        if "/" in target:
            suffix = f"/{target}"
            narrowed = [c for c in base_candidates if c.as_posix().endswith(suffix)]
            if len(narrowed) == 1:
                return "resolved", narrowed[0], []
        return "ambiguous", None, base_candidates
    return "broken", None, []


def _heading_exists(target_path: Path, anchor: str) -> bool:
    structure = extract_structure(target_path)
    wanted = " ".join(anchor.strip().split()).lower()
    for heading in structure["headings"]:
        if " ".join(heading["text"].split()).lower() == wanted:
            return True
    return False


def _block_exists(target_path: Path, block: str) -> bool:
    try:
        text = target_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return f"^{block}" in text


def check_links(root: str | os.PathLike, *, skip_dirs: tuple[str, ...] = (".git",)) -> dict:
    """Validate all links/embeds in every Markdown file under *root*.

    Returns a report with explicit per-problem records and summary counts.
    """
    index = build_vault_index(root)
    problems: list[dict] = []
    externals: list[dict] = []
    checked_files = 0
    checked_links = 0

    for rel, abs_path in sorted(index["by_relpath"].items()):
        if abs_path.suffix.lower() != ".md":
            continue
        if any(part in skip_dirs for part in Path(rel).parts):
            continue
        structure = extract_structure(abs_path)
        for error in structure["errors"]:
            problems.append(
                {
                    "type": "parse_error",
                    "file": rel,
                    "detail": error,
                }
            )
        checked_files += 1

        link_records = [
            (record, False) for record in structure["wikilinks"]
        ] + [(record, True) for record in structure["embeds"]]
        for record, is_embed in link_records:
            checked_links += 1
            target = record["target"]
            anchor = record.get("anchor")
            block = record.get("block")
            resolution, target_path, candidates = _resolve_target(index, target, (".md",))

            if target and resolution == "broken":
                problems.append(
                    {
                        "type": "broken",
                        "kind": "embed" if is_embed else "wikilink",
                        "file": rel,
                        "line": record["line"],
                        "target": target,
                    }
                )
                continue
            if target and resolution == "ambiguous":
                problems.append(
                    {
                        "type": "ambiguous",
                        "kind": "embed" if is_embed else "wikilink",
                        "file": rel,
                        "line": record["line"],
                        "target": target,
                        "candidates": [str(c) for c in candidates],
                    }
                )
                continue
            if target_path is None:
                target_path = abs_path  # self-reference like [[#Heading]]
            if anchor is not None and not _heading_exists(target_path, anchor):
                problems.append(
                    {
                        "type": "missing_anchor",
                        "kind": "embed" if is_embed else "wikilink",
                        "file": rel,
                        "line": record["line"],
                        "target": target or "(self)",
                        "anchor": anchor,
                    }
                )
            if block is not None and not _block_exists(target_path, block):
                problems.append(
                    {
                        "type": "missing_block",
                        "kind": "embed" if is_embed else "wikilink",
                        "file": rel,
                        "line": record["line"],
                        "target": target or "(self)",
                        "block": block,
                    }
                )

        for record in structure["md_links"]:
            checked_links += 1
            if record["kind"] == "external":
                externals.append(
                    {"file": rel, "line": record["line"], "url": record["url"]}
                )
                continue
            url = record["url"]
            base = url.split("#", 1)[0]
            if not base:
                continue
            source_dir = abs_path.parent
            candidate = (source_dir / base).resolve()
            if candidate.exists():
                continue
            with_ext = (
                (source_dir / f"{base}.md").resolve()
                if not base.endswith(".md")
                else candidate
            )
            if with_ext.exists():
                continue
            # Obsidian-style bare note reference
            resolution, target_path, _ = _resolve_target(index, base.strip("./"), (".md",))
            if resolution == "resolved":
                continue
            problems.append(
                {
                    "type": "broken",
                    "kind": "md_link",
                    "file": rel,
                    "line": record["line"],
                    "target": url,
                }
            )

    by_type: dict[str, int] = defaultdict(int)
    for problem in problems:
        by_type[problem["type"]] += 1
    return {
        "root": str(root),
        "markdown_files_checked": checked_files,
        "links_checked": checked_links,
        "problems": problems,
        "external_links": externals,
        "problem_counts": dict(by_type),
    }
