"""Exact, case-insensitive, normalized and multi-line phrase search with term statistics.

All results carry explicit locations (file, 1-based line numbers) and the
report always states the scope, the number of scanned/skipped files, and the
matching mode so counts are reproducible.

L-01 fix: the ``phrase`` mode matches a normalized phrase against the whole
file text, so phrases that span line breaks are found; matches carry a
(line_start, line_end) span locator derived from a per-line offset map.

L-07 fix: :func:`term_stats` accepts ``match_mode='word-boundary'`` using the
SAME word-boundary pattern authority as CAP-013 overlap discovery
(:func:`boundary_pattern`), closing the F-0006 false-positive class for
term statistics ('ridge' no longer counts inside 'bridge' when the
word-boundary mode is selected; substring mode remains the default for
backward compatibility).
"""

from __future__ import annotations

import os
import re
import unicodedata
from functools import lru_cache
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


def boundary_pattern(term: str) -> re.Pattern:
    """Case-insensitive word-boundary pattern for *term* (shared authority).

    Boundaries: no ``[a-zA-Z0-9_]`` (word character) immediately before or
    after the match. This is what rejects 'ridge' inside 'bridge' while still
    matching 'ridge' at 'ridge:' or '(ridge)'. CAP-013 overlap discovery and
    word-boundary term statistics use this ONE implementation so their
    semantics can never drift apart (L-07).

    Performance (F-0017): callers iterate term-by-term (all occurrences of
    one term before the next), so a small memo of compiled patterns removes
    re-compilation per occurrence. Compiled patterns are immutable, so
    sharing them cannot change behavior.
    """
    return _boundary_pattern_cached(term)


@lru_cache(maxsize=512)
def _boundary_pattern_cached(term: str) -> re.Pattern:
    escaped = re.escape(term.casefold())
    return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)


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


def search_phrase(
    root: str | os.PathLike,
    phrase: str,
    *,
    skip_dirs: tuple[str, ...] = (".git", ".obsidian"),
) -> dict:
    """Search for a normalized *phrase* that may span line breaks (L-01).

    The phrase and each file's text are normalized with :func:`normalize_text`
    (NFKC + whitespace collapse + casefold); matching runs over the whole-file
    normalized text so a phrase broken across lines, with arbitrary
    indentation and blank lines between its words, is found. Every match
    carries a precise ``(line_start, line_end)`` span derived from a per-line
    offset map built during normalization, so evidence locators stay
    line-accurate even though matching is whole-text.

    An empty or whitespace-only phrase is rejected (ValueError); a phrase
    that normalizes to nothing (e.g. only combining marks stripped by NFKC)
    is likewise rejected.
    """
    if not phrase or not phrase.strip():
        raise ValueError("search phrase must be non-empty")
    needle = normalize_text(phrase).strip()
    if not needle:
        raise ValueError("search phrase normalizes to an empty string")
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

        # Build the whole-file normalized text with a per-segment offset map.
        # Blank lines normalize away entirely (whitespace collapses into the
        # single separator space), exactly like normalize_text(whole_text).
        segments: list[tuple[int, int, str]] = []  # (start_offset, line_no, norm)
        joined_parts: list[str] = []
        offset = 0
        for lineno, line in enumerate(text.splitlines(), start=1):
            norm = normalize_text(line).strip()
            if not norm:
                continue
            if joined_parts:
                joined_parts.append(" ")
                offset += 1
            segments.append((offset, lineno, norm))
            joined_parts.append(norm)
            offset += len(norm)
        haystack = "".join(joined_parts)

        start_at = 0
        while True:
            idx = haystack.find(needle, start_at)
            if idx == -1:
                break
            end_idx = idx + len(needle)
            # map char offsets back to line numbers via the segment table
            line_start = None
            line_end = None
            for seg_off, seg_line, seg_norm in segments:
                seg_end = seg_off + len(seg_norm)
                if line_start is None and seg_end > idx:
                    line_start = seg_line
                if seg_off < end_idx:
                    line_end = seg_line
            if line_start is None:  # cannot happen when idx is within haystack
                line_start = segments[0][1] if segments else 1
            matches.append(
                {
                    "file": rel,
                    "line_start": line_start,
                    "line_end": line_end,
                    "text": needle[:300],
                }
            )
            start_at = idx + 1  # overlapping matches allowed (deterministic)

    files_with_matches = sorted({m["file"] for m in matches})
    return {
        "root": str(root),
        "term": phrase,
        "mode": "phrase",
        "match_count": len(matches),
        "files_with_matches": files_with_matches,
        "files_with_matches_count": len(files_with_matches),
        "matches": matches,
        "method": (
            "whole-file normalized (NFKC + whitespace-collapse + casefold) "
            "substring search; matches carry (line_start, line_end) span locators"
        ),
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
    match_mode: str = "substring",
    skip_dirs: tuple[str, ...] = (".git", ".obsidian"),
) -> dict:
    """Count occurrences of each term (plus aliases) per file.

    Terms file lines are ``term`` or ``term|alias1|alias2``. Counting is
    case-insensitive on casefolded text with the method stated in the report.

    ``match_mode`` (L-07 fix):
    - ``substring`` (default, backward compatible): casefolded substring
      counting; 'ridge' counts inside 'bridge'.
    - ``word-boundary``: same word-boundary semantics as CAP-013 overlap
      discovery (:func:`boundary_pattern`); substring false positives are
      rejected. Use this mode when counts feed overlap/classification work.
    """
    if match_mode not in ("substring", "word-boundary"):
        raise ValueError(f"unknown match mode: {match_mode}")
    root_path = Path(root)
    if not root_path.is_dir():
        raise NotADirectoryError(f"term-stats root is not a directory: {root_path}")
    aliases = aliases or {}
    scanned = 0
    skipped_binary = 0
    skipped_unreadable = 0
    skipped_nontext = 0

    # precompile patterns per variant once (performance on large vaults)
    variant_patterns: dict[str, list[tuple[str, re.Pattern]]] = {}
    for term in terms:
        patterns = [(term, None)]  # substring mode marker: None pattern
        if match_mode == "word-boundary":
            patterns = [(term, boundary_pattern(term))]
            for alias in aliases.get(term, []):
                patterns.append((alias, boundary_pattern(alias)))
        variant_patterns[term] = patterns

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
            if match_mode == "substring":
                count = casefolded.count(term.casefold())
                for alias in aliases.get(term, []):
                    count += casefolded.count(alias.casefold())
            else:
                count = 0
                for _variant, pattern in variant_patterns[term]:
                    count += len(pattern.findall(text))
            if count:
                file_terms[rel][term] = count

    per_term: dict[str, dict] = {}
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

    method = (
        "case-insensitive substring counting of term plus declared aliases"
        if match_mode == "substring"
        else "word-boundary (CAP-013 semantics) counting of term plus declared aliases"
    )
    return {
        "root": str(root),
        "method": method,
        "match_mode": match_mode,
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
