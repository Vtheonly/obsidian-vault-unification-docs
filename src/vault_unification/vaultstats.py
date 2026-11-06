"""Content statistics for a vault root (BOOT-002 capability, CAP-015).

Aggregates per-file and per-vault lexical/structural statistics: words,
characters, lines, headings by level, code fences, math blocks, wikilinks,
embeds, markdown links, tags, and a documented token estimate.

All numbers are lexical measurements with explicitly documented methods.
They are never proof of semantic coverage or preservation (see
docs/TOOLING_FRAMEWORK.md principle 10: no metric laundering).

Counting methods (also emitted in every report):
- ``words_total``: whitespace-separated tokens over the full decoded file
  text, including frontmatter, headings, code, and math content.
- ``words_outside_fences``: whitespace tokens on lines that are not inside
  a code fence and not inside a display ``$$`` math block. Unclosed
  fences/math blocks extend to end-of-file (consistent with the extraction
  error semantics in mdextract: the content is treated as real content).
- ``tokens_estimate``: ``chars // 4`` — a rough BPE-style approximation of
  tokenizer output; actual token counts differ per tokenizer and language.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .mdextract import extract_structure
from .search import _TEXT_EXTENSIONS, _looks_binary

WORD_METHOD = (
    "whitespace-separated tokens over the full UTF-8 decoded file text "
    "(includes frontmatter, headings, code fences and math)"
)
PROSE_WORD_METHOD = (
    "whitespace tokens on lines outside code fences and outside display $$ "
    "math blocks; unclosed fences/math extend to end-of-file"
)
TOKEN_ESTIMATE_METHOD = (
    "chars // 4 (rough BPE-style approximation; not an exact tokenizer count)"
)

_MARKDOWN_EXTENSIONS = {".md", ".markdown"}


def _excluded_lines(structure: dict, total_lines: int) -> set[int]:
    """1-based line numbers inside code fences or display math blocks."""
    excluded: set[int] = set()
    for fence in structure["code_fences"]:
        start = fence["start_line"]
        end = fence["end_line"] if fence["end_line"] is not None else total_lines
        excluded.update(range(start, end + 1))
    for block in structure["math_blocks"]:
        start = block["start_line"]
        end = block["end_line"] if block["end_line"] is not None else total_lines
        excluded.update(range(start, end + 1))
    return excluded


def file_stats(path: str | os.PathLike) -> dict:
    """Per-file lexical/structural statistics.

    Errors (unreadable, binary, non-UTF-8) are reported in ``errors`` and
    never silently dropped. Non-markdown text files get lexical counts only,
    with an explicit note, because structure extraction is Markdown-specific.
    """
    path = Path(path)
    record: dict[str, Any] = {
        "path": str(path),
        "is_markdown": path.suffix.lower() in _MARKDOWN_EXTENSIONS,
        "size_bytes": None,
        "line_count": 0,
        "chars": 0,
        "words_total": 0,
        "words_outside_fences": 0,
        "tokens_estimate": 0,
        "headings_total": 0,
        "headings_by_level": {},
        "code_fences": 0,
        "code_fences_unclosed": 0,
        "math_blocks": 0,
        "math_blocks_unclosed": 0,
        "inline_math": 0,
        "wikilinks": 0,
        "embeds": 0,
        "md_links": 0,
        "tags": 0,
        "frontmatter_present": False,
        "is_empty": False,
        "errors": [],
        "warnings": [],
        "note": None,
    }
    try:
        raw = path.read_bytes()
    except OSError as exc:
        record["errors"].append(f"read failed: {type(exc).__name__}: {exc}")
        return record

    record["size_bytes"] = len(raw)
    record["is_empty"] = len(raw) == 0
    if record["is_empty"]:
        record["warnings"].append("file is empty (0 bytes)")
        return record
    if _looks_binary(raw):
        record["errors"].append("binary content detected in a text-extension file")
        return record
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        record["errors"].append(f"not valid UTF-8: {exc}")
        return record

    lines = text.splitlines()
    record["line_count"] = len(lines)
    record["chars"] = len(text)
    record["words_total"] = len(text.split())
    record["tokens_estimate"] = len(text) // 4

    if not record["is_markdown"]:
        record["note"] = (
            "non-markdown text file: lexical counts only; Markdown structure "
            "counts not extracted"
        )
        record["words_outside_fences"] = record["words_total"]
        return record

    structure = extract_structure(path)
    record["errors"].extend(structure["errors"])
    record["warnings"].extend(structure["warnings"])

    record["headings_total"] = len(structure["headings"])
    by_level: dict[str, int] = {}
    for heading in structure["headings"]:
        key = f"h{heading['level']}"
        by_level[key] = by_level.get(key, 0) + 1
    record["headings_by_level"] = by_level

    record["code_fences"] = len(structure["code_fences"])
    record["code_fences_unclosed"] = sum(
        1 for f in structure["code_fences"] if not f["closed"]
    )
    record["math_blocks"] = len(structure["math_blocks"])
    record["math_blocks_unclosed"] = sum(
        1 for b in structure["math_blocks"] if not b["closed"]
    )
    record["inline_math"] = structure["inline_math_count"]
    record["wikilinks"] = len(structure["wikilinks"])
    record["embeds"] = len(structure["embeds"])
    record["md_links"] = len(structure["md_links"])
    record["tags"] = len(structure["tags"])
    record["frontmatter_present"] = structure["frontmatter"] is not None

    excluded = _excluded_lines(structure, record["line_count"])
    record["words_outside_fences"] = sum(
        len(lines[i].split()) for i in range(len(lines)) if (i + 1) not in excluded
    )
    return record


def stats_root(root: str | os.PathLike, *, follow_symlinks: bool = False) -> dict:
    """Aggregate statistics over every file under *root*.

    Discovery mirrors ``inventory.scan_root`` (sorted walk, symlinks
    recorded). Every discovered file appears in exactly one of ``per_file``
    (text files), ``skipped_nontext`` (non-text extensions), or
    ``unreadable_files`` — nothing is silently skipped.
    """
    root_path = Path(root)
    if not root_path.is_dir():
        raise NotADirectoryError(f"stats root is not a directory: {root_path}")

    per_file: list[dict] = []
    skipped_nontext: list[dict] = []
    symlink_skipped: list[dict] = []

    for dirpath, dirnames, filenames in os.walk(root_path, followlinks=follow_symlinks):
        dirnames.sort()
        for name in sorted(filenames):
            abs_path = Path(dirpath) / name
            relpath = abs_path.relative_to(root_path).as_posix()
            if abs_path.suffix.lower() not in _TEXT_EXTENSIONS:
                skipped_nontext.append(
                    {"relpath": relpath, "extension": abs_path.suffix.lower()}
                )
                continue
            if abs_path.is_symlink() and not follow_symlinks:
                symlink_skipped.append(
                    {"relpath": relpath, "error": "symlink not followed"}
                )
                continue
            stats = file_stats(abs_path)
            stats["path"] = relpath
            per_file.append(stats)

    totals: dict[str, Any] = {
        "files_discovered": len(per_file) + len(skipped_nontext) + len(symlink_skipped),
        "text_files_analyzed": len([s for s in per_file if not s["errors"]]),
        "text_files_with_errors": len([s for s in per_file if s["errors"]]),
        "files_skipped_nontext": len(skipped_nontext),
        "files_unreadable_or_invalid": len(symlink_skipped)
        + len([s for s in per_file if s["errors"]]),
        "size_bytes": sum(s["size_bytes"] or 0 for s in per_file),
        "lines": sum(s["line_count"] for s in per_file),
        "chars": sum(s["chars"] for s in per_file),
        "words_total": sum(s["words_total"] for s in per_file),
        "words_outside_fences": sum(s["words_outside_fences"] for s in per_file),
        "tokens_estimate": sum(s["tokens_estimate"] for s in per_file),
        "headings_total": sum(s["headings_total"] for s in per_file),
        "headings_by_level": {},
        "code_fences": sum(s["code_fences"] for s in per_file),
        "code_fences_unclosed": sum(s["code_fences_unclosed"] for s in per_file),
        "math_blocks": sum(s["math_blocks"] for s in per_file),
        "math_blocks_unclosed": sum(s["math_blocks_unclosed"] for s in per_file),
        "inline_math": sum(s["inline_math"] for s in per_file),
        "wikilinks": sum(s["wikilinks"] for s in per_file),
        "embeds": sum(s["embeds"] for s in per_file),
        "md_links": sum(s["md_links"] for s in per_file),
        "tags": sum(s["tags"] for s in per_file),
        "files_with_frontmatter": sum(
            1 for s in per_file if s["frontmatter_present"]
        ),
        "empty_files": sum(1 for s in per_file if s["is_empty"]),
    }
    for stats in per_file:
        for level, count in stats["headings_by_level"].items():
            totals["headings_by_level"][level] = (
                totals["headings_by_level"].get(level, 0) + count
            )
    totals["headings_by_level"] = dict(
        sorted(totals["headings_by_level"].items())
    )

    # Unreadable summary combines symlink-skipped files (not in per_file) and
    # text files whose analysis failed (in per_file with errors recorded).
    unreadable_summary = symlink_skipped + [
        {"relpath": s["path"], "error": "; ".join(s["errors"])}
        for s in per_file
        if s["errors"]
    ]

    return {
        "root": str(root_path),
        "methods": {
            "words_total": WORD_METHOD,
            "words_outside_fences": PROSE_WORD_METHOD,
            "tokens_estimate": TOKEN_ESTIMATE_METHOD,
            "text_extensions": sorted(_TEXT_EXTENSIONS),
        },
        "totals": totals,
        "skipped_nontext": skipped_nontext,
        "unreadable_files": unreadable_summary,
        "files_with_warnings": [
            {"relpath": s["path"], "warnings": s["warnings"]}
            for s in per_file
            if s["warnings"]
        ],
        "per_file": per_file,
    }
