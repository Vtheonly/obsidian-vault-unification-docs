"""Corpus-wide duplicate-phrase and duplicate-block scan (AUDIT-013; closes
the F-0037/F-0038 remaining risk).

Deterministic, read-only scan over a vault that detects two duplication
defect classes the lint and prose-quality checks cannot see:

1. **Intra-line phrase stutter** (the F-0037 shape): a phrase repeated
   back-to-back two or more times inside a single line, e.g. a sentence
   fragment pasted three times in a row.
2. **Tandem block repeat** (the F-0038 shape): a consecutive sequence of 1..20
   blocks (paragraph / list group / fence / callout, split on blank lines,
   fences atomic) repeated two or more times in a row anywhere in the note.

Evidence-calibrated exclusions (session-30 corpus survey: 14 raw intra-line
candidates of which 12 were legitimate notation — matrix rows, parameter
counts, pipeline arrows, architecture layer lists, learning-rate lists):

- lines inside code fences or blockquotes quoting fenced code are not scanned
  for stutters (code is verbatim source material; lint owns code checks);
- table rows (lines starting with ``|``) are not scanned (repeated rows are
  data, and source tables are preserved verbatim);
- frontmatter is not scanned;
- a repeated phrase is excluded when it contains an arrow (``→`` / ``->``;
  pipeline notation like "Linear → ReLU → Dropout →"), when its final token
  ends with ``,`` or ``;`` (enumeration continuation like "0.01, 0.01, 0.01,"
  or "Conv3-512, Conv3-512,"), or when fewer than 60% of its tokens are
  alphabetic words (math/numeric/symbolic content like "1 & 0 & -1 \\\\" or
  "\\rightarrow 4096");
- the two prose stutters found by the survey ("In norm notation, … family."
  and "We are provided with a labeled dataset … features.") pass all
  exclusions and are detected.

Verdict classes per finding: ``stutter`` (intra-line) and ``tandem_block``
(span-level). Severity: ``medium`` when the repeat count is >=3 or the
repeated unit is >=20 chars (the F-0037/F-0038 shapes), else ``low``.

Known limitations (documented, not silently ignored):
- matching is exact after whitespace collapsing (case-sensitive); drifted or
  edited duplicates are not detected;
- non-consecutive duplication (the same block twice in different sections) is
  out of scope: repetition across sections can be intentional structure;
- blockquote-quoted prose is scanned (it is content), only fenced code inside
  it is skipped like any other fence.
"""

from __future__ import annotations

import re
from pathlib import Path

_FRONTMATTER = re.compile(r"^---\n.*?\n---\n?", re.S)
_FENCE_OPEN = re.compile(r"^\s*(```|~~~)")
_MAX_SPAN_BLOCKS = 20
_MIN_PHRASE_CHARS = 12
_ALPHABETIC_TOKEN = re.compile(r"^[^\W\d_]+$", re.UNICODE)


def _split_blocks(body: str) -> list[str]:
    """Split a note body into blocks: blank-line separated, fences atomic."""
    blocks: list[str] = []
    current: list[str] = []
    in_fence = False
    for line in body.split("\n"):
        if _FENCE_OPEN.match(line):
            if in_fence:
                current.append(line)
                blocks.append("\n".join(current))
                current = []
                in_fence = False
            else:
                if current:
                    blocks.append("\n".join(current))
                    current = []
                current = [line]
                in_fence = True
            continue
        if not in_fence and not line.strip():
            if current:
                blocks.append("\n".join(current))
                current = []
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def _norm(block: str) -> str:
    return re.sub(r"\s+", " ", block).strip()


def _is_prose_phrase(phrase: str) -> bool:
    """Apply the evidence-calibrated exclusion rules to a repeated phrase."""
    if "→" in phrase or "->" in phrase:
        return False
    tokens = phrase.split()
    if not tokens:
        return False
    if tokens[-1].endswith((",", ";")):
        return False
    alpha = sum(1 for tok in tokens if len(tok) >= 2 and _ALPHABETIC_TOKEN.match(tok.strip(",.;:!?—–-\"'()[]")))
    return alpha / len(tokens) >= 0.6


def _find_line_stutter(line: str):
    """Return (phrase, repeat_count) for the longest phrase P
    (>= _MIN_PHRASE_CHARS) whose token sequence repeats back-to-back inside
    the line, or None. The repeat count is the maximal number of consecutive
    copies of the token tuple."""
    words = line.split()
    n = len(words)
    best = None
    for start in range(n):
        for end in range(start + 2, n):  # phrase needs >= 2 tokens
            length = end - start
            if end + length > n:
                break
            if words[start:end] == words[end : end + length]:
                phrase = " ".join(words[start:end])
                if len(phrase) >= _MIN_PHRASE_CHARS and _is_prose_phrase(phrase):
                    copies = 2
                    while (
                        end + copies * length <= n
                        and words[start:end]
                        == words[end + (copies - 1) * length : end + copies * length]
                    ):
                        copies += 1
                    if best is None or len(phrase) > len(best[0]):
                        best = (phrase, copies)
                break  # longest match at this start; move on
    return best


def _scan_note(text: str) -> list[dict]:
    findings: list[dict] = []
    m = _FRONTMATTER.match(text)
    body = text[m.end():] if m else text
    # frontmatter line offset for reporting absolute line numbers
    body_offset = text[: m.end()].count("\n") if m else 0

    # ---- intra-line stutters (skip fences and table rows) ----
    in_fence = False
    for line_no, line in enumerate(body.split("\n"), 1):
        if _FENCE_OPEN.match(line):
            in_fence = not in_fence
            continue
        if in_fence or line.strip().startswith("|"):
            continue
        hit = _find_line_stutter(line)
        if hit:
            phrase, repeats = hit
            findings.append(
                {
                    "class": "stutter",
                    "line": body_offset + line_no,
                    "body_line": line_no,
                    "repeat_count": repeats,
                    "phrase": phrase[:200],
                    "phrase_chars": len(phrase),
                    "severity": "medium" if (repeats >= 3 or len(phrase) >= 20) else "low",
                }
            )

    # ---- tandem block repeats ----
    blocks = [b for b in _split_blocks(body) if b.strip() and not b.strip().startswith("|")]
    normed = [_norm(b) for b in blocks]
    i = 0
    while i < len(normed):
        hit = None
        for span in range(min(_MAX_SPAN_BLOCKS, (len(normed) - i) // 2), 0, -1):
            if normed[i : i + span] == normed[i + span : i + 2 * span]:
                repeats = 2
                while (
                    i + (repeats + 1) * span <= len(normed)
                    and normed[i : i + span] == normed[i + repeats * span : i + (repeats + 1) * span]
                ):
                    repeats += 1
                hit = (span, repeats)
                break
        if hit:
            span, repeats = hit
            preview = normed[i][:200]
            findings.append(
                {
                    "class": "tandem_block",
                    "block_index": i,
                    "span_blocks": span,
                    "repeat_count": repeats,
                    "preview": preview,
                    "severity": "medium" if (repeats >= 3 or len(preview) >= 20) else "low",
                }
            )
            i += span * repeats
        else:
            i += 1
    return findings


def dup_scan(root: str | Path) -> dict:
    """Run the duplicate-phrase/block scan over a vault (read-only)."""
    root_path = Path(root)
    notes_scanned = 0
    lines_scanned = 0
    blocks_scanned = 0
    findings: list[dict] = []
    unreadable: list[str] = []
    for md in sorted(root_path.rglob("*.md")):
        rel = md.relative_to(root_path).as_posix()
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            unreadable.append(f"{rel}: {exc}")
            continue
        notes_scanned += 1
        note_findings = _scan_note(text)
        m = _FRONTMATTER.match(text)
        body = text[m.end():] if m else text
        in_fence = False
        for line in body.split("\n"):
            if _FENCE_OPEN.match(line):
                in_fence = not in_fence
                continue
            if not in_fence and not line.strip().startswith("|"):
                lines_scanned += 1
        blocks_scanned += len([b for b in _split_blocks(body) if b.strip()])
        for f in note_findings:
            f["note"] = rel
        findings.extend(note_findings)

    by_class: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    for f in findings:
        by_class[f["class"]] = by_class.get(f["class"], 0) + 1
        by_severity[f["severity"]] = by_severity.get(f["severity"], 0) + 1

    return {
        "command": "dup-scan",
        "root": str(root_path),
        "scope": {
            "notes_scanned": notes_scanned,
            "lines_scanned_excl_fences_tables": lines_scanned,
            "blocks_scanned": blocks_scanned,
            "unreadable": unreadable,
        },
        "exclusions": [
            "code fences (verbatim source material; lint owns code checks)",
            "table rows (repeated rows are data; source tables preserved verbatim)",
            "frontmatter",
            "phrases containing arrows (pipeline notation)",
            "phrases whose final token ends with ',' or ';' (enumeration continuation)",
            "phrases with <60% alphabetic tokens (math/numeric/symbolic content)",
        ],
        "limitations": [
            "exact matching after whitespace collapsing (case-sensitive); drifted duplicates not detected",
            "non-consecutive duplication is out of scope (can be intentional structure)",
        ],
        "results": {
            "findings_total": len(findings),
            "by_class": by_class,
            "by_severity": by_severity,
        },
        "findings": findings,
        "deterministic": True,
    }
