"""Machine locators for evidence quotes (L-13 migration of the EXT-010 X2 tool).

The EXT-005..009 classification generators relied on hand-typed line numbers,
which produced off-by-one and misattribution defects (EXT-009 review finding
R2). EXT-010 replaced them with a runtime machine locator that requires a
UNIQUE in-span occurrence of every evidence quote; the first run caught five
defects that hand-typing had introduced.

This module migrates that X2 locator from the one-shot task script
``scripts/ext010_classifications.py`` into the reusable framework so every
future evidence workflow (classifications, discovery candidates, audits)
locates quotes the same way: pass a quote and a span, get machine-verified
line numbers or a loud failure — never a silent guess.

Matching semantics (deterministic, identical to CAP-005 phrase search):
NFKC normalization + whitespace collapse + casefold on both the quote and
the span text, so indentation and line-wrapping differences cannot break a
locator while byte-level content remains authoritative at the source.
"""

from __future__ import annotations

import unicodedata
import re


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.casefold().strip()


def _span_segments(lines: list[str], start: int, end: int) -> tuple[str, list[tuple[int, int, int]]]:
    """Build normalized joined text for a 1-based inclusive line span.

    Returns (joined_text, segments) where each segment is
    (start_offset, line_number, segment_length); blank lines are skipped
    exactly like ``search.search_phrase`` builds its haystack.
    """
    segments: list[tuple[int, int, int]] = []
    parts: list[str] = []
    offset = 0
    for lineno in range(start, end + 1):
        if lineno < 1 or lineno > len(lines):
            continue
        norm = _normalize(lines[lineno - 1])
        if not norm:
            continue
        if parts:
            parts.append(" ")
            offset += 1
        segments.append((offset, lineno, len(norm)))
        parts.append(norm)
        offset += len(norm)
    return "".join(parts), segments


def _line_span_for_range(
    segments: list[tuple[int, int, int]], idx: int, end_idx: int
) -> tuple[int | None, int | None]:
    line_start = None
    line_end = None
    for seg_off, seg_line, seg_len in segments:
        seg_end = seg_off + seg_len
        if line_start is None and seg_end > idx:
            line_start = seg_line
        if seg_off < end_idx:
            line_end = seg_line
    return line_start, line_end


def locate_quote(
    lines: list[str],
    quote: str,
    *,
    span: tuple[int, int] | None = None,
) -> dict:
    """Locate *quote* inside a line span with a UNIQUE-occurrence guarantee.

    Args:
        lines: the file's lines (1-based indexing implied; ``lines[0]`` is
            line 1).
        quote: the evidence quote; may span multiple lines and differ in
            whitespace/indentation/case from the source.
        span: optional ``(start_line, end_line)`` 1-based inclusive search
            window (e.g. a KU's locator). ``None`` = whole file.

    Returns a dict (never raises on location failures):

    - ``ok``: True only when the quote occurs EXACTLY ONCE in the span;
    - ``line_start`` / ``line_end``: machine-verified 1-based span of the
      occurrence (None when not ok);
    - ``occurrences``: how many normalized occurrences were found;
    - ``message``: human-readable status for reports and defect triage.

    A quote that appears twice in the span FAILS (occurrences=2) — the caller
    must narrow the span rather than let the locator guess. This is the X2
    rule: machine-verified, unique, or loudly wrong.
    """
    if not quote or not quote.strip():
        return {
            "ok": False,
            "line_start": None,
            "line_end": None,
            "occurrences": 0,
            "message": "quote is empty",
        }
    needle = _normalize(quote)
    if not needle:
        return {
            "ok": False,
            "line_start": None,
            "line_end": None,
            "occurrences": 0,
            "message": "quote normalizes to an empty string",
        }
    if span is None:
        start, end = 1, len(lines)
    else:
        start, end = span
        if start < 1 or end < start or end > len(lines):
            return {
                "ok": False,
                "line_start": None,
                "line_end": None,
                "occurrences": 0,
                "message": (
                    f"invalid span ({start}, {end}) for a {len(lines)}-line file"
                ),
            }

    haystack, segments = _span_segments(lines, start, end)
    if not haystack:
        return {
            "ok": False,
            "line_start": None,
            "line_end": None,
            "occurrences": 0,
            "message": f"span ({start}, {end}) contains no non-blank text",
        }

    occurrences = 0
    found_span: tuple[int, int] | None = None
    at = 0
    while True:
        idx = haystack.find(needle, at)
        if idx == -1:
            break
        occurrences += 1
        if found_span is None:
            found_span = _line_span_for_range(segments, idx, idx + len(needle))
        at = idx + 1

    if occurrences == 0:
        return {
            "ok": False,
            "line_start": None,
            "line_end": None,
            "occurrences": 0,
            "message": "quote not found in span (normalized matching)",
        }
    if occurrences > 1:
        return {
            "ok": False,
            "line_start": None,
            "line_end": None,
            "occurrences": occurrences,
            "message": (
                f"quote is NOT unique in span ({start}, {end}): "
                f"{occurrences} occurrences; narrow the span or lengthen the quote"
            ),
        }
    return {
        "ok": True,
        "line_start": found_span[0],
        "line_end": found_span[1],
        "occurrences": 1,
        "message": "located: unique occurrence in span",
    }


def locate_quote_in_file(path, quote: str, *, span: tuple[int, int] | None = None) -> dict:
    """File-path convenience wrapper around :func:`locate_quote`.

    Read errors become explicit ``ok: False`` results (never silent skips).
    """
    from pathlib import Path

    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return {
            "ok": False,
            "line_start": None,
            "line_end": None,
            "occurrences": 0,
            "message": f"cannot read {file_path}: {type(exc).__name__}: {exc}",
        }
    return locate_quote(text.splitlines(), quote, span=span)
