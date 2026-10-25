"""Markdown structure extraction.

Extracts headings, YAML frontmatter, code fences, math delimiters, wikilinks,
embeds, Markdown links and tags from a single note, reporting malformed
constructs explicitly instead of silently dropping them.

Known limitations (documented, by design, for v0.1):
- math detection is delimiter-based; inline ``$...$`` can produce false
  positives on currency amounts, and no LaTeX syntax validation is performed;
- nested code fences inside fenced blocks are treated as part of the fence;
- frontmatter parsing requires PyYAML; when unavailable the block is recorded
  with an explicit error instead of being silently skipped.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:  # optional dependency, availability checked by selftest
    import yaml  # type: ignore

    _HAS_YAML = True
except ImportError:  # pragma: no cover - exercised only without PyYAML
    _HAS_YAML = False

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_WIKILINK_RE = re.compile(r"(!?)\[\[([^\]|#^]*?)(?:#([^\]|^]*))?(?:\^([^\]]*?))?(?:\|([^\]]*?))?\]\]")
_MD_LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_TAG_RE = re.compile(r"(?:^|\s)#([A-Za-z0-9][\w/-]*)")
_EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "obsidian://")


def _is_blank(text: str) -> bool:
    return not text.strip()


def _new_result(path: str | None) -> dict[str, Any]:
    return {
        "path": path,
        "exists": path is not None,
        "errors": [],
        "warnings": [],
        "frontmatter": None,
        "frontmatter_span": None,
        "headings": [],
        "code_fences": [],
        "math_blocks": [],
        "inline_math_count": 0,
        "wikilinks": [],
        "embeds": [],
        "md_links": [],
        "tags": [],
        "line_count": 0,
        "is_empty": True,
        "ends_with_newline": None,
        "reading_error": None,
    }


def extract_structure(file_path: str | Path) -> dict:
    """Extract structural elements from one Markdown file.

    Returns a dict with ``errors`` and ``warnings`` lists so that malformed
    input is reported, never silently dropped.
    """
    path = Path(file_path)
    result = _new_result(str(path))
    if not path.exists():
        result["errors"].append("file does not exist")
        return result
    if not path.is_file():
        result["errors"].append("path is not a regular file")
        return result
    try:
        raw = path.read_bytes()
    except OSError as exc:
        result["reading_error"] = f"{type(exc).__name__}: {exc}"
        result["errors"].append(result["reading_error"])
        return result
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        result["reading_error"] = f"UTF-8 decode error: {exc}"
        result["errors"].append(result["reading_error"])
        return result
    return _scan_text(result, text)


def extract_structure_text(text: str) -> dict:
    """Same scan as :func:`extract_structure` over in-memory text.

    Added for CAP-016 (kuextract) so segmentation and file-level structure
    extraction share ONE construct-detection authority. Byte-level facts
    (``is_empty``, ``ends_with_newline``) are derived from the text itself:
    ``text`` is empty exactly when the decoded file bytes are empty, and a
    trailing "\n" in decoded text corresponds to a trailing newline byte.
    """
    return _scan_text(_new_result(None), text)


def _scan_text(result: dict[str, Any], text: str) -> dict:
    lines = text.splitlines()
    result["line_count"] = len(lines)
    result["is_empty"] = not text
    result["ends_with_newline"] = text.endswith("\n") if text else None

    # ---- frontmatter ----
    start = 0
    if lines and lines[0].strip() == "---":
        close = None
        for idx in range(1, len(lines)):
            if lines[idx].strip() in ("---", "..."):
                close = idx
                break
        if close is None:
            result["warnings"].append("frontmatter opening '---' has no closing delimiter")
        else:
            block = "\n".join(lines[1:close])
            result["frontmatter_span"] = [1, close + 1]  # 1-based inclusive
            if not _HAS_YAML:
                result["errors"].append(
                    "frontmatter present but PyYAML is not installed; block not parsed"
                )
            else:
                try:
                    parsed = yaml.safe_load(block)
                    if parsed is None:
                        result["warnings"].append("frontmatter block is empty")
                        parsed = None
                    elif not isinstance(parsed, dict):
                        result["errors"].append(
                            "frontmatter is not a mapping (YAML parses to "
                            f"{type(parsed).__name__})"
                        )
                    result["frontmatter"] = parsed
                except yaml.YAMLError as exc:
                    result["errors"].append(f"frontmatter YAML parse error: {exc}")
            start = close + 1

    # ---- line-by-line scan ----
    in_fence = False
    fence_info = ""
    fence_marker = "```"
    fence_start_line = None
    fence_buffer: list[str] = []

    def _flush_fence(end_line: int | None) -> None:
        nonlocal in_fence, fence_buffer
        body = "\n".join(fence_buffer)
        result["code_fences"].append(
            {
                "info": fence_info,
                "marker": fence_marker,
                "start_line": fence_start_line,
                "end_line": end_line,
                "body_lines": len(fence_buffer),
                "body_chars": len(body),
                "closed": end_line is not None,
            }
        )
        in_fence = False
        fence_buffer = []

    in_math_block = False
    math_start = None

    for idx in range(start, len(lines)):
        lineno = idx + 1  # 1-based
        line = lines[idx]
        stripped = line.strip()

        # code fences take precedence over everything inside them
        if in_fence:
            if stripped.startswith(fence_marker) and set(stripped) <= set(fence_marker):
                _flush_fence(lineno)
                continue
            fence_buffer.append(line)
            continue

        if stripped.startswith("```") or stripped.startswith("~~~"):
            if len(stripped) >= 3 and set(stripped[:3]) in ({"`"}, {"~"}):
                in_fence = True
                fence_marker = stripped[:3]
                fence_info = stripped[3:].strip()
                fence_start_line = lineno
                fence_buffer = []
                continue

        # display math blocks: $$ ... $$ (single-line or multi-line)
        if not in_math_block and stripped.startswith("$$"):
            if stripped.endswith("$$") and len(stripped) > 4:
                result["math_blocks"].append({"start_line": lineno, "end_line": lineno, "closed": True})
            elif stripped == "$$":
                in_math_block = True
                math_start = lineno
            else:
                # opening $$ with content that does not close on same line
                in_math_block = True
                math_start = lineno
            continue
        if in_math_block:
            if stripped.endswith("$$"):
                result["math_blocks"].append(
                    {"start_line": math_start, "end_line": lineno, "closed": True}
                )
                in_math_block = False
            continue

        # headings
        heading_match = _HEADING_RE.match(line)
        if heading_match:
            result["headings"].append(
                {
                    "level": len(heading_match.group(1)),
                    "text": heading_match.group(2).strip(),
                    "line": lineno,
                }
            )
            # still scan remainder of heading lines for links/tags below

        # wikilinks and embeds (also inside heading text)
        for match in _WIKILINK_RE.finditer(line):
            is_embed = match.group(1) == "!"
            record = {
                "target": match.group(2).strip(),
                "anchor": (match.group(3) or "").strip() or None,
                "block": (match.group(4) or "").strip() or None,
                "alias": (match.group(5) or "").strip() or None,
                "line": lineno,
                "embed": is_embed,
            }
            (result["embeds"] if is_embed else result["wikilinks"]).append(record)

        # markdown links (skip embeds/images ![...]())
        for match in _MD_LINK_RE.finditer(line):
            url = match.group(2)
            record = {
                "text": match.group(1),
                "url": url,
                "line": lineno,
                "kind": "external" if url.startswith(_EXTERNAL_PREFIXES) else "internal",
            }
            result["md_links"].append(record)

        # inline tags (#tag), outside code fences
        for match in _TAG_RE.finditer(line):
            result["tags"].append({"tag": match.group(1), "line": lineno})

    # unclosed constructs are errors, not silent drops
    if in_fence:
        result["errors"].append(
            f"unclosed code fence starting at line {fence_start_line}"
        )
        _flush_fence(None)
    if in_math_block:
        result["errors"].append(f"unclosed math block starting at line {math_start}")
        result["math_blocks"].append(
            {"start_line": math_start, "end_line": None, "closed": False}
        )

    # inline math $...$ (outside code fences): recompute on visible text
    visible_lines: list[str] = []
    skip = False
    for line in lines[start:]:
        stripped2 = line.strip()
        if not skip and (stripped2.startswith("```") or stripped2.startswith("~~~")):
            skip = True
            continue
        if skip:
            if stripped2.startswith("```") or stripped2.startswith("~~~"):
                skip = False
            continue
        visible_lines.append(line)
    visible_text = "\n".join(visible_lines)
    result["inline_math_count"] = len(
        re.findall(r"(?<!\$)\$(?!\$)[^$\n]+?(?<!\$)\$(?!\$)", visible_text)
    )

    # frontmatter tags
    if isinstance(result["frontmatter"], dict):
        fm_tags = result["frontmatter"].get("tags")
        if isinstance(fm_tags, list):
            for tag in fm_tags:
                result["tags"].append({"tag": str(tag), "line": None, "source": "frontmatter"})
        elif isinstance(fm_tags, str):
            result["tags"].append({"tag": fm_tags, "line": None, "source": "frontmatter"})

    if result["is_empty"]:
        result["warnings"].append("file is empty (0 bytes)")
    return result


def heading_path(headings: list[dict], line: int) -> list[str]:
    """Return the heading hierarchy active at *line* (1-based)."""
    path: list[str] = []
    for heading in headings:
        if heading["line"] <= line:
            if heading["level"] <= len(path):
                path = path[: heading["level"] - 1]
            path.append(heading["text"])
        else:
            break
    return path
