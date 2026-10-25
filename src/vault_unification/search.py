"""Exact, case-insensitive and normalized search with term statistics.

All results carry explicit locations (file, 1-based line numbers) and the
report always states the scope, the number of scanned/skipped files, and the
matching mode so counts are reproducible.
"""

from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path

_TEXT_EXTENSIONS = {
    ".md", ".markdown", ".txt", ".rst", ".csv", ".json", ".yml", ".yaml",
    ".py", ".js", ".ts", ".sh", ".toml", ".cfg", ".ini", ".tex",
}


def _looks_binary(data: bytes) -> bool:
    if b"\x00" in data[:8192]:
        return True
    return False


def normalize_text(text: str) -> str:
    """NFKC normalization, whitespace collapsing and casefolding."""
    normalized = unicodedata.normalize("NFKC", text)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.casefold()


def _read_text(path: Path) -> tuple[str | None, str | None]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return None, f"read failed: {type(exc).__name__}: {exc}"
    if _looks_binary(raw):
        return None, "skipped: binary content detected"
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError as exc:
        return None, f"skipped: not valid UTF-8 ({exc})"


def _iter_text_files(root: str | os.PathLike, skip_dirs: tuple[str, ...] = (".git", ".obsidian")):
    root_path = Path(root)
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = sorted(d for d in dirnames if d not in skip_dirs)
        for name in sorted(filenames):
            abs_path = Path(dirpath) / name
            rel = abs_path.relative_to(root_path).as_posix()
            yield rel, abs_path


def search_term(
    root: str | os.PathLike,
    term: str,
    mode: str = "exact",
    *,
    skip_dirs: tuple[str, ...] = (".git", ".obsidian"),
) -> dict:
    """Search for *term* under *root*.

    Modes:
    - ``exact``: case-sensitive substring match;
    - ``case-insensitive``: casefolded substring match;
    - ``normalized``: NFKC + whitespace-collapsed + casefolded, applied
      per line (locations remain line-accurate).

    An empty term is rejected (ValueError) rather than matching everything;
    a missing or non-directory root raises NotADirectoryError.
    """
    if not term:
        raise ValueError("search term must be non-empty")
    if mode not in ("exact", "case-insensitive", "normalized"):
        raise ValueError(f"unknown search mode: {mode}")
    root_path = Path(root)
    if not root_path.is_dir():
        raise NotADirectoryError(f"search root is not a directory: {root_path}")

    matches: list[dict] = []
    scanned = 0
    skipped_binary = 0
    skipped_unreadable = 0
    skipped_nontext = 0

    for rel, abs_path in _iter_text_files(root, skip_dirs):
        if abs_path.suffix.lower() not in _TEXT_EXTENSIONS:
            skipped_nontext += 1
            continue
        text, error = _read_text(abs_path)
        if text is None:
            if error and error.startswith("skipped: binary"):
                skipped_binary += 1
            else:
                skipped_unreadable += 1
            continue
        scanned += 1
        for lineno, line in enumerate(text.splitlines(), start=1):
            haystack = line
            needle = term
            if mode == "case-insensitive":
                haystack = line.casefold()
                needle = term.casefold()
            elif mode == "normalized":
                haystack = normalize_text(line)
                needle = normalize_text(term)
            if needle in haystack:
                matches.append(
                    {
                        "file": rel,
                        "line": lineno,
                        "text": line.strip()[:300],
                    }
                )

    files_with_matches = sorted({m["file"] for m in matches})
    return {
        "root": str(root),
        "term": term,
        "mode": mode,
        "match_count": len(matches),
        "files_with_matches": files_with_matches,
        "files_with_matches_count": len(files_with_matches),
        "matches": matches,
        "scope": {
            "files_scanned": scanned,
            "files_skipped_nontext": skipped_nontext,
            "files_skipped_binary": skipped_binary,
            "files_skipped_unreadable": skipped_unreadable,
            "skip_dirs": list(skip_dirs),
            "text_extensions": sorted(_TEXT_EXTENSIONS),
        },
    }


def term_stats(
    root: str | os.PathLike,
    terms: list[str],
    *,
    aliases: dict[str, list[str]] | None = None,
    skip_dirs: tuple[str, ...] = (".git", ".obsidian"),
) -> dict:
    """Count occurrences of each term (plus aliases) per file.

    Terms file lines are ``term`` or ``term|alias1|alias2``. Counting is
    case-insensitive whole-word-ish substring counting (substring match on
    casefolded text); the method is stated in the report.
    """
    root_path = Path(root)
    if not root_path.is_dir():
        raise NotADirectoryError(f"term-stats root is not a directory: {root_path}")
    aliases = aliases or {}
    per_term: dict[str, dict] = {}
    scanned = 0
    skipped_binary = 0
    skipped_unreadable = 0
    skipped_nontext = 0

    file_terms: dict[str, dict[str, int]] = {}

    for rel, abs_path in _iter_text_files(root, skip_dirs):
        if abs_path.suffix.lower() not in _TEXT_EXTENSIONS:
            skipped_nontext += 1
            continue
        text, error = _read_text(abs_path)
        if text is None:
            if error and error.startswith("skipped: binary"):
                skipped_binary += 1
            else:
                skipped_unreadable += 1
            continue
        scanned += 1
        casefolded = text.casefold()
        file_terms[rel] = {}
        for term in terms:
            count = casefolded.count(term.casefold())
            for alias in aliases.get(term, []):
                count += casefolded.count(alias.casefold())
            if count:
                file_terms[rel][term] = count

    for term in terms:
        variant_counts = {
            rel: counts[term] for rel, counts in file_terms.items() if term in counts
        }
        per_term[term] = {
            "total_count": sum(variant_counts.values()),
            "files_with_term": len(variant_counts),
            "per_file": variant_counts,
            "aliases": aliases.get(term, []),
        }

    return {
        "root": str(root),
        "method": "case-insensitive substring counting of term plus declared aliases",
        "terms": list(terms),
        "denominator": {"files_scanned": scanned},
        "exclusions": {
            "files_skipped_nontext": skipped_nontext,
            "files_skipped_binary": skipped_binary,
            "files_skipped_unreadable": skipped_unreadable,
            "skip_dirs": list(skip_dirs),
        },
        "stats": per_term,
    }
