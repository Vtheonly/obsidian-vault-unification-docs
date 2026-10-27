"""Artifact integrity validation for generated notes (FRAME-002, CAP-018).

Deterministic structural validation of Markdown/Obsidian artifacts, per the
Phase 0 quality-tooling requirements. This module answers ONE question per
defect: "does this artifact parse / resolve / render as its syntax claims?"
It NEVER claims semantic correctness: a syntactically valid formula, table
or diagram may still be wrong, and every report carries the standing caveat
that syntax validation is not truth validation (see SEVERITY MODEL below).

CHECK FAMILIES (each check id is stable and machine-referenced by the repair
loop in :mod:`vault_unification.repair`):

- fences:      FENCE_UNCLOSED, CODE_LANG_MISSING, CODE_LANG_UNKNOWN,
               CODE_PYTHON_SYNTAX, CODE_JSON_INVALID
- math:        MATH_BLOCK_UNCLOSED, MATH_INLINE_ODD, MATH_ENV_MISMATCH,
               MATH_DELIM_STYLE_MIXED
- tables:      TABLE_SEPARATOR_BAD, TABLE_CELL_MISMATCH,
               TABLE_SEPARATOR_MISSING
- headings:    HEADING_SKIP, HEADING_EMPTY, HEADING_MULTI_H1
- lists:       LIST_INDENT_MIXED
- links:       LINK_BROKEN, LINK_AMBIGUOUS, LINK_MISSING_ANCHOR,
               LINK_MISSING_BLOCK (reuse of the CAP-004 resolver with
               folder-link awareness; folder links are evidence, not defects)
- mermaid:     MERMAID_PARSE (structural validation of the common diagram
               kinds: flowchart/graph, sequenceDiagram, stateDiagram-v2,
               classDiagram, pie, gantt — heuristic line-grammar checks,
               NOT a full mermaid AST)
- truncation:  TRUNCATION_OPEN_CONSTRUCT, TRUNCATION_MID_SENTENCE,
               PLACEHOLDER_TEXT, BRACKET_UNBALANCED, EMPTY_SECTION
- frontmatter: FRONTMATTER_INVALID

SEVERITY MODEL:
- ``error``   — the artifact cannot render as written (unclosed fence/math,
                broken internal link, invalid code/JSON, malformed table
                separator, file ends inside an open construct).
- ``warning`` — suspicious and needs review, but may be intentional (odd
                inline-math dollar count, cell-count drift, heading skips,
                mid-sentence file ending, placeholder markers).
- ``info``    — convention/best-practice notes (missing fence language,
                mixed math delimiter styles, multiple H1s, empty sections).

A clean lint pass is a NECESSARY condition for publishing a note, never a
sufficient one. Semantic review (factual accuracy, adequacy, coverage)
belongs to the quality workflow (:mod:`vault_unification.notequality`) and
the human/agent reviewer.

SAFETY: code validation NEVER executes note code. Python blocks are checked
with :func:`ast.parse` (compile-to-AST, no execution); JSON blocks with
:func:`json.loads`; everything else is label-level only.
"""

from __future__ import annotations

import ast
import json
import re
from collections import Counter
from pathlib import Path

from .mdextract import extract_structure_text

__all__ = [
    "ArtifactLintError",
    "lint_text",
    "lint_file",
    "lint_tree",
    "SEVERITY_ORDER",
]

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


class ArtifactLintError(Exception):
    """Raised for invalid lint inputs (unreadable file, bad arguments)."""


# ---------------------------------------------------------------------------
# shared line-level helpers

_PLACEHOLDER_RE = re.compile(
    r"(?:\bTODO\b|\bFIXME\b|\bTBD\b|\bXXX\b|\bWIP\b|\bTBA\b|"
    r"\blorem ipsum\b|\[placeholder\]|<insert [^>]*here>|"
    r"\bplaceholder text\b|\bcoming soon\b|\bto be continued\b)",
    re.IGNORECASE,
)

_KNOWN_CODE_LANGS = frozenset(
    """
    python python3 py bash sh shell zsh fish powershell ps1 cmd console
    javascript js typescript ts jsx tsx java c cpp c++ csharp cs go rust
    r ruby php swift kotlin scala sql graphql html css scss sass xml yaml
    yml toml ini json jsonc markdown md tex latex bibtex diff patch
    mermaid text plaintext txt plain csv dockerfile docker makefile
    matlab octave julia lua perl haskell erlang elixir clojure lisp
    scheme prolog fortran cobol ada asm nasm vhdl verilog systemverilog
    regex http proto protobuf tf terraform hcl nix graphviz dot
    """.split()
)

# sentence-terminal punctuation for the mid-sentence truncation heuristic
_SENTENCE_END = tuple(".!?。！？…\"'`:;)】」』")

# lines that are structural and exempt from the mid-sentence heuristic
_STRUCTURAL_LINE_RE = re.compile(
    r"^\s*(?:#{1,6}\s|[-*+]\s|\d+[.)]\s|>\s*\|?\s*$|\||```|~~~|!\[|<!--|$)"
)


def _excerpt(lines: list[str], line: int, context: int = 1) -> str:
    """Return a bounded excerpt around 1-based *line* (max 2*context+1 lines)."""
    lo = max(1, line - context)
    hi = min(len(lines), line + context)
    parts = [f"{i}: {lines[i - 1].rstrip()[:120]}" for i in range(lo, hi + 1)]
    return "\n".join(parts)


def _cell_count(row: str) -> int:
    """Count table cells in a pipe row (leading/trailing pipes optional)."""
    s = row.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    # escaped pipes do not split cells
    return len(re.split(r"(?<!\\)\|", s)) if s else 0


_SEPARATOR_CELL_RE = re.compile(r"^:?-{2,}:?$")


def _is_separator_line(line: str) -> bool:
    s = line.strip()
    if not s or "|" not in s and "-" not in s:
        return False
    stripped = s.strip("|")
    cells = [c.strip() for c in re.split(r"(?<!\\)\|", stripped)]
    if not cells or not all(_SEPARATOR_CELL_RE.match(c) for c in cells if c != ""):
        return False
    return any(c for c in cells)


# ---------------------------------------------------------------------------
# mermaid structural validation (heuristic line grammar, no execution)

_MERMAID_DIAGRAM_KINDS = (
    "flowchart",
    "graph",
    "sequencediagram",
    "statediagram",
    "statediagram-v2",
    "classdiagram",
    "erdiagram",
    "pie",
    "gantt",
    "journey",
    "mindmap",
    "timeline",
    "gitgraph",
    "quadrantchart",
    "sankey",
    "xychart",
    "block-beta",
    "requirementdiagram",
    "c4context",
)

# flowchart validation strategy: mermaid node labels may contain almost
# anything (colons, equals, quotes, parens, <br/>), so a line is judged by
# its OPERATORS, not by re-matching full node syntax:
#   1. header/direction/classDef/style/click/linkStyle/subgraph/end/comment
#   2. any recognized edge/link operator between node expressions
#   3. otherwise: a bare node declaration (id + optional shaped label)
_FLOWCHART_KEYWORD_LINE = re.compile(
    r"""^\s*(?:
        (?:flowchart|graph)\b.*            # diagram + direction header
      | (?:subgraph|end)\b.*
      | classDef\s+\S+.*
      | class\s+\S+.*
      | style\s+\S+.*
      | click\s+\S+.*
      | linkStyle\s+\S+.*
      | direction\s+(?:TB|TD|BT|RL|LR)\b.*
      | %%.*                               # comment
    )$""",
    re.VERBOSE,
)

# edge/link operators (arrow forms, plain links, labeled dotted links like
# A -. "text" .-> B, thick links, bidirectional)
_FLOWCHART_EDGE_OP = re.compile(
    r"<-->|<--|-\.?\.?->|-->|->|--x|-x|--o|-o|==>|=->|==o|==x|---|===|~~~"
)

_FLOWCHART_BARE_NODE = re.compile(
    r"""^\s*
        [A-Za-z0-9_\u4e00-\u9fff][\w\-]*    # node id
        (?:\s*"[^"]*"?                      # bare quoted label
          |\[\s*(?:"[^"]*"|[^\]]*)\s*\]     # [label] (quoted labels may contain ])
          |\(\s*(?:"[^"]*"|[^)]*)\s*\)      # (label) (quoted labels may contain ))
          |\{\s*(?:"[^"]*"|[^}]*)\s*\}      # {label}
          |\(\(.*\)\)                       # ((label)) incl. nested parens
          |>\s*[^>]*)?                      # > flag
        (?:\s*:::\w+)?                      # :::class shorthand
        \s*$""",
    re.VERBOSE,
)


def _flowchart_line_ok(stripped: str) -> bool:
    if _FLOWCHART_KEYWORD_LINE.match(stripped):
        return True
    if _FLOWCHART_EDGE_OP.search(stripped):
        return True
    return _FLOWCHART_BARE_NODE.match(stripped) is not None

_SEQUENCE_BLOCK_KEYWORDS = {
    "alt": "end",
    "opt": "end",
    "par": "end",
    "critical": "end",
    "loop": "end",
    "box": "end",
    "rect": "end",
    "autonumber": None,
    "deactivate": None,
    "activate": None,
}

_SEQUENCE_LINE_OK = re.compile(
    r"""^\s*(?:
        sequenceDiagram\b.*
      | (?:title|actor|participant|as)\s+\S.*
      | \S[^\s:]*\s*(?:-->|-->>|->>|->|-x|--x|-\)|--)\s*\S[^:]*:.*
      | note\s+(?:over|left\s+of|right\s+of)\s+[^:]+:.*
      | (?:activate|deactivate)\s+\S+.*
      | autonumber(?:\s+\d+)?\s*
      | (?:alt|else|opt|par|and|critical|option|loop|box|rect|end)\b.*
      | %%.*
    )$""",
    re.VERBOSE | re.IGNORECASE,
)

_STATE_LINE_OK = re.compile(
    r"""^\s*(?:
        stateDiagram(?:-v2)?\b.*
      | \[\*\]
      | [*A-Za-z0-9_\s\-]+?(?:-->|->)[*A-Za-z0-9_\s\-]+?(?::\s*.*)?$
      | state\s+[^:]+(?:\s*:\s*.*)?$
      | note\s+(?:left of|right of)\s+\S.*
      | note\s+[^:]*:.*
      | (?:fork|join|choice|end)\b(?:\s+state)?\s*\S*\s*$
      | %%.*
    )$""",
    re.VERBOSE,
)

_CLASS_LINE_OK = re.compile(
    r"""^\s*(?:
        classDiagram\b.*
      | class\s+\w+.*$
      | \w+\s*(?:<\|--|\.\.\||<\.\.\||\*--|o--|--|<\|\.|\^\.\.)\s*\w+.*$
      | \w+\s*:\s+\S.*$
      | <<\w+>>\s*$
      | namespace\s+\S+.*
      | direction\s+(?:TB|TD|BT|RL|LR)\b.*
      | %%.*
    )$""",
    re.VERBOSE,
)

_PIE_LINE_OK = re.compile(
    r"""^\s*(?:
        pie\s+(?:showData)?\s*(?:"[^"]*")?\s*$
      | title\s+\S.*
      | "[^"]*"\s*:\s*[\d.]+\s*$
      | %%.*
    )$""",
    re.VERBOSE,
)

_GANTT_LINE_OK = re.compile(
    r"""^\s*(?:
        gantt\b\s*$
      | title\s+\S.*
      | (?:dateFormat|axisFormat|tickInterval|excludes|includes|todayMarker|section)\s+\S.*
      | [^:|]*:\s*.*$                     # task row: name : tags, id, start, end
      | %%.*
    )$""",
    re.VERBOSE,
)


def _validate_mermaid(body: str, start_line: int) -> list[dict]:
    """Structurally validate a mermaid block body; return defect dicts.

    Heuristic line-grammar validation: the first non-comment line must
    declare a known diagram kind, every line must match that kind's
    statement grammar, and block constructs (subgraph/end, alt/end, ...)
    must balance. This catches the common failure modes (prose inside
    diagrams, unclosed subgraphs, arrows with prose on both sides) without
    pretending to be a full mermaid parser.
    """
    defects: list[dict] = []
    lines = body.split("\n")
    kind: str | None = None
    open_blocks: list[tuple[str, int]] = []
    declared = False

    for i, raw in enumerate(lines):
        line_no = start_line + i
        stripped = raw.strip()
        if not stripped or stripped.startswith("%%"):
            continue
        low = stripped.lower()
        if not declared:
            first_word = low.split(None, 1)[0] if low.split() else ""
            if first_word in _MERMAID_DIAGRAM_KINDS:
                kind = first_word
                declared = True
                continue
            defects.append(
                {
                    "check": "MERMAID_PARSE",
                    "severity": "error",
                    "line": line_no,
                    "message": "mermaid block does not start with a known diagram declaration",
                    "excerpt": _excerpt(lines, i + 1, 0).split(": ", 1)[-1],
                }
            )
            return defects

        # block-construct balance (shared across diagram kinds). A line only
        # OPENS a block when the keyword is not itself part of an edge
        # statement: a node legitimately named "Subgraph --> X" or
        # "Alt->>B: msg" must not open a block.
        opens_block = not _FLOWCHART_EDGE_OP.search(stripped)
        if kind in ("flowchart", "graph") and opens_block and re.match(r"^subgraph\b", low):
            open_blocks.append(("subgraph", line_no))
        elif (
            kind == "sequencediagram"
            and opens_block
            and low.split()
            and low.split()[0] in ("alt", "opt", "par", "critical", "loop", "box", "rect")
        ):
            open_blocks.append((low.split()[0], line_no))
        if low == "end" or low.startswith("end ") or low.startswith("end;"):
            if open_blocks:
                open_blocks.pop()
            elif kind in ("flowchart", "graph", "sequencediagram", "statediagram", "statediagram-v2"):
                defects.append(
                    {
                        "check": "MERMAID_PARSE",
                        "severity": "error",
                        "line": line_no,
                        "message": f"'end' without a matching open block ({kind})",
                        "excerpt": stripped[:120],
                    }
                )

        pattern = None
        if kind in ("flowchart", "graph"):
            if not _flowchart_line_ok(stripped):
                defects.append(
                    {
                        "check": "MERMAID_PARSE",
                        "severity": "error",
                        "line": line_no,
                        "message": f"line does not match the {kind} statement grammar",
                        "excerpt": stripped[:120],
                    }
                )
            continue
        pattern = {
            "sequencediagram": _SEQUENCE_LINE_OK,
            "statediagram": _STATE_LINE_OK,
            "statediagram-v2": _STATE_LINE_OK,
            "classdiagram": _CLASS_LINE_OK,
            "pie": _PIE_LINE_OK,
            "gantt": _GANTT_LINE_OK,
        }.get(kind or "")
        if pattern is None:
            # known kind without a specific grammar (journey, mindmap, ...):
            # only the block-balance checks apply
            continue
        if pattern.match(stripped) is None:
            defects.append(
                {
                    "check": "MERMAID_PARSE",
                    "severity": "error",
                    "line": line_no,
                    "message": f"line does not match the {kind} statement grammar",
                    "excerpt": stripped[:120],
                }
            )

    for block, line_no in open_blocks:
        defects.append(
            {
                "check": "MERMAID_PARSE",
                "severity": "error",
                "line": line_no,
                "message": f"unclosed '{block}' block (missing 'end')",
                "excerpt": _excerpt(lines, line_no - start_line + 1, 0).split(": ", 1)[-1],
            }
        )
    return defects


# ---------------------------------------------------------------------------
# core per-file lint


def lint_text(text: str, *, path: str = "<text>") -> dict:
    """Lint one Markdown document; return a defect report (never raises on
    note content — only on invalid arguments)."""
    if not isinstance(text, str):
        raise ArtifactLintError("text must be a string")
    structure = extract_structure_text(text)
    lines = text.split("\n")
    defects: list[dict] = []

    def add(check: str, severity: str, line: int, message: str, line_text: str = "") -> None:
        defects.append(
            {
                "check": check,
                "severity": severity,
                "line": line,
                "message": message,
                "excerpt": (line_text or (lines[line - 1] if 1 <= line <= len(lines) else ""))[:160],
            }
        )

    # -- frontmatter -----------------------------------------------------
    fm_lines = structure.get("frontmatter_span") or []
    if fm_lines:
        try:
            import yaml  # optional at runtime, available in the project env

            fm_text = "\n".join(text.split("\n")[fm_lines[0] : fm_lines[1] - 1])
            yaml.safe_load(fm_text)
        except Exception as exc:  # noqa: BLE001 - report, don't crash
            add("FRONTMATTER_INVALID", "error", int(fm_lines[0]), f"frontmatter YAML failed to parse: {exc}")

    # -- code fences ------------------------------------------------------
    fence_spans: list[tuple[int, int]] = []
    for fence in structure["code_fences"]:
        end = fence["end_line"] if fence.get("end_line") is not None else len(lines)
        fence_spans.append((fence["start_line"], end))
        if not fence.get("closed"):
            add(
                "FENCE_UNCLOSED",
                "error",
                fence["start_line"],
                f"code fence ({fence['info'] or 'no language'}) opened but never closed",
            )
            continue
        info = (fence.get("info") or "").strip()
        label = info.split()[0].lower() if info else ""
        if not label:
            add("CODE_LANG_MISSING", "info", fence["start_line"], "code fence has no language label")
        elif label not in _KNOWN_CODE_LANGS:
            add(
                "CODE_LANG_UNKNOWN",
                "warning",
                fence["start_line"],
                f"code fence language '{label}' is not in the known-language list",
            )
        body = _fence_body(lines, fence)
        if label in ("python", "python3", "py") and body is not None:
            try:
                ast.parse(body)
            except SyntaxError as exc:
                add(
                    "CODE_PYTHON_SYNTAX",
                    "error",
                    fence["start_line"] + max(0, (exc.lineno or 1) - 1),
                    f"python code block fails to parse: {exc.msg}",
                )
        elif label in ("json", "jsonc") and body is not None:
            try:
                json.loads(body)
            except json.JSONDecodeError as exc:
                add(
                    "CODE_JSON_INVALID",
                    "error",
                    fence["start_line"],
                    f"json code block fails to parse: {exc.msg}",
                )
        elif label == "mermaid" and body is not None:
            defects.extend(_validate_mermaid(body, fence["start_line"] + 1))

    def _in_fence(line: int) -> bool:
        return any(s <= line <= e for s, e in fence_spans)

    # -- math ---------------------------------------------------------------
    math_spans: list[tuple[int, int]] = []
    for block in structure["math_blocks"]:
        end = block["end_line"] if block.get("end_line") is not None else len(lines)
        math_spans.append((block["start_line"], end))
        if not block.get("closed"):
            add(
                "MATH_BLOCK_UNCLOSED",
                "error",
                block["start_line"],
                "block math ($$) opened but never closed",
            )

    def _in_math(line: int) -> bool:
        return any(s <= line <= e for s, e in math_spans)

    # \begin{env}/\end{env} pairing over the whole document (fences excluded)
    begin_stack: list[tuple[str, int]] = []
    env_re = re.compile(r"\\(begin|end)\{([^}]+)\}")
    for idx, line in enumerate(lines, start=1):
        if _in_fence(idx):
            continue
        for kind, env in env_re.findall(line):
            if kind == "begin":
                begin_stack.append((env, idx))
            elif begin_stack and begin_stack[-1][0] == env:
                begin_stack.pop()
            else:
                add(
                    "MATH_ENV_MISMATCH",
                    "error",
                    idx,
                    f"\\end{{{env}}} without matching \\begin{{{env}}}",
                    line,
                )
    for env, line_no in begin_stack:
        add("MATH_ENV_MISMATCH", "error", line_no, f"\\begin{{{env}}} never closed", lines[line_no - 1])

    # inline math dollar parity outside fences/math blocks (warning-level:
    # a single $ in prose, e.g. a price, triggers it deliberately — review
    # decides, the tool only flags)
    dollar_count = 0
    for idx, line in enumerate(lines, start=1):
        if _in_fence(idx) or _in_math(idx):
            continue
        dollar_count += len(re.findall(r"(?<!\\)\$", line))
    if dollar_count % 2 == 1:
        defects.append(
            {
                "check": "MATH_INLINE_ODD",
                "severity": "warning",
                "line": 0,
                "message": f"odd number of unescaped '$' characters outside code/math blocks ({dollar_count}); an inline formula is probably unclosed",
                "excerpt": "",
            }
        )

    # delimiter style consistency (info)
    has_dollar = bool(structure["math_blocks"])
    has_bracket = bool(re.search(r"^\s*\\\[", text, re.MULTILINE))
    if has_dollar and has_bracket:
        defects.append(
            {
                "check": "MATH_DELIM_STYLE_MIXED",
                "severity": "info",
                "line": 0,
                "message": "document mixes $$...$$ and \\[...\\] display-math delimiters; pick one convention",
                "excerpt": "",
            }
        )

    # -- tables ---------------------------------------------------------
    i = 0
    while i < len(lines):
        line_no = i + 1
        line = lines[i]
        if "|" not in line or _in_fence(line_no) or _in_math(line_no):
            i += 1
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if _is_separator_line(nxt) and not _is_separator_line(line):
            # table header at `line`, separator at `nxt`
            header_cells = _cell_count(line)
            sep_cells = _cell_count(nxt)
            if sep_cells != header_cells:
                add(
                    "TABLE_SEPARATOR_BAD",
                    "error",
                    line_no + 1,
                    f"table separator has {sep_cells} cells but the header has {header_cells}",
                    nxt,
                )
            j = i + 2
            while j < len(lines):
                row = lines[j]
                if "|" not in row or _is_separator_line(row):
                    break
                if _in_fence(j + 1) or _in_math(j + 1):
                    break
                cells = _cell_count(row)
                if cells != header_cells:
                    add(
                        "TABLE_CELL_MISMATCH",
                        "warning",
                        j + 1,
                        f"table row has {cells} cells but the header has {header_cells}",
                        row,
                    )
                j += 1
            i = j
            continue
        # pipe line NOT followed by a separator: a probable broken table
        if (
            not _is_separator_line(line)
            and line.count("|") >= 2
            and line.strip().startswith("|")
            and line.strip().endswith("|")
            and nxt.strip()
            and "|" not in nxt
            and not nxt.strip().startswith(("#", "-", "*", "```"))
        ):
            add(
                "TABLE_SEPARATOR_MISSING",
                "warning",
                line_no,
                "pipe row is not followed by a table separator row; if this is a table it will not render",
                line,
            )
        i += 1

    # -- headings ---------------------------------------------------------
    prev_level = 0
    h1_count = 0
    for head in structure["headings"]:
        level = head["level"]
        if not (head.get("text") or "").strip():
            add("HEADING_EMPTY", "warning", head["line"], "heading has empty text")
        if level == 1:
            h1_count += 1
        if prev_level and level > prev_level + 1:
            add(
                "HEADING_SKIP",
                "warning",
                head["line"],
                f"heading hierarchy jumps from H{prev_level} to H{level}",
                lines[head["line"] - 1] if head["line"] <= len(lines) else "",
            )
        prev_level = level
    if h1_count > 1:
        defects.append(
            {
                "check": "HEADING_MULTI_H1",
                "severity": "info",
                "line": 0,
                "message": f"document has {h1_count} H1 headings; Obsidian renders the filename as title, one H1 is the convention",
                "excerpt": "",
            }
        )

    # -- lists: mixed tab/space indentation -------------------------------
    list_item_re = re.compile(r"^(\s*)(?:[-*+]\s|\d+[.)]\s)")
    indent_styles: set[str] = set()
    for idx, line in enumerate(lines, start=1):
        m = list_item_re.match(line)
        if not m:
            continue
        indent = m.group(1)
        if "\t" in indent and " " in indent:
            add(
                "LIST_INDENT_MIXED",
                "warning",
                idx,
                "list indentation mixes tabs and spaces on one line",
                line,
            )
        elif indent:
            indent_styles.add("tab" if indent.startswith("\t") else "space")
    if len(indent_styles) > 1:
        defects.append(
            {
                "check": "LIST_INDENT_MIXED",
                "severity": "warning",
                "line": 0,
                "message": "list indentation mixes tab-indented and space-indented items across the document",
                "excerpt": "",
            }
        )

    # -- placeholder text ---------------------------------------------------
    for idx, line in enumerate(lines, start=1):
        if _in_fence(idx):
            # TODO comments in code are conventional — skip fenced bodies
            continue
        m = _PLACEHOLDER_RE.search(line)
        if m:
            add(
                "PLACEHOLDER_TEXT",
                "warning",
                idx,
                f"placeholder marker '{m.group(0)}' in prose",
                line,
            )

    # -- truncation & balance -------------------------------------------
    if fence_spans and fence_spans[-1][1] > len(lines) - 1 and not structure["code_fences"][-1].get("closed"):
        pass  # already reported as FENCE_UNCLOSED
    if math_spans and not structure["math_blocks"][-1].get("closed"):
        pass  # already reported as MATH_BLOCK_UNCLOSED

    nonempty = [idx for idx, line in enumerate(lines, start=1) if line.strip()]
    if nonempty:
        last = nonempty[-1]
        last_line = lines[last - 1]
        if not _STRUCTURAL_LINE_RE.match(last_line):
            if last_line.rstrip().endswith(",") or not last_line.rstrip().endswith(_SENTENCE_END):
                add(
                    "TRUNCATION_MID_SENTENCE",
                    "warning",
                    last,
                    "document ends on a non-terminal line (possible truncation)",
                    last_line,
                )
        # bracket balance over the whole document outside fences
        balance = {"(": 0, "[": 0, "{": 0}
        pairs = {")": "(", "]": "[", "}": "{"}
        for idx, line in enumerate(lines, start=1):
            if _in_fence(idx) or _in_math(idx):
                continue
            for ch in line:
                if ch in balance:
                    balance[ch] += 1
                elif ch in pairs:
                    balance[pairs[ch]] -= 1
        if any(v != 0 for v in balance.values()):
            defects.append(
                {
                    "check": "BRACKET_UNBALANCED",
                    "severity": "warning",
                    "line": 0,
                    "message": "unbalanced (), [] or {} outside code/math blocks (counts: "
                    + ", ".join(f"{k}:{v}" for k, v in balance.items() if v)
                    + ")",
                    "excerpt": "",
                }
            )

    # -- empty sections -------------------------------------------------
    heads = sorted(structure["headings"], key=lambda h: h["line"])
    for a, b in zip(heads, heads[1:]):
        between = lines[a["line"] : b["line"] - 1]
        if not any(x.strip() for x in between):
            add(
                "EMPTY_SECTION",
                "info",
                a["line"],
                f"section '{a['text']}' has no content before the next heading",
                lines[a["line"] - 1],
            )
    if heads and not any(x.strip() for x in lines[heads[-1]["line"] :]):
        add(
            "EMPTY_SECTION",
            "info",
            heads[-1]["line"],
            f"section '{heads[-1]['text']}' has no content",
            lines[heads[-1]["line"] - 1],
        )

    # deterministic order
    defects.sort(key=lambda d: (d.get("line", 0), SEVERITY_ORDER.get(d["severity"], 9), d["check"], d["message"]))
    counts = Counter(f"{d['severity']}:{d['check']}" for d in defects)
    return {
        "file": path,
        "defects": defects,
        "defect_count": len(defects),
        "error_count": sum(1 for d in defects if d["severity"] == "error"),
        "warning_count": sum(1 for d in defects if d["severity"] == "warning"),
        "info_count": sum(1 for d in defects if d["severity"] == "info"),
        "counts_by_check": dict(sorted(counts.items())),
    }


def _fence_body(lines: list[str], fence: dict) -> str | None:
    """Return the body text of a closed fence (None if unclosed)."""
    if not fence.get("closed"):
        return None
    start = fence["start_line"]
    end = fence["end_line"]
    if start >= end or end - 1 > len(lines):
        return ""
    return "\n".join(lines[start:end - 1])


def lint_file(path: str | Path, *, vault_root: str | Path | None = None, link_context: dict | None = None) -> dict:
    """Lint one file; optionally resolve its internal links against *vault_root*.

    *link_context* is an opaque per-run context built by :func:`build_link_context`
    (index + caches) so tree-wide linting does not re-index per file.
    """
    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ArtifactLintError(f"cannot read {file_path}: {exc}") from exc
    report = lint_text(text, path=str(file_path))
    if vault_root is not None or link_context is not None:
        link_defects = _lint_links(file_path, text, vault_root, link_context)
        report["defects"].extend(link_defects)
        report["defects"].sort(
            key=lambda d: (d.get("line", 0), SEVERITY_ORDER.get(d["severity"], 9), d["check"], d["message"])
        )
        report["defect_count"] = len(report["defects"])
        report["error_count"] = sum(1 for d in report["defects"] if d["severity"] == "error")
        report["warning_count"] = sum(1 for d in report["defects"] if d["severity"] == "warning")
        report["info_count"] = sum(1 for d in report["defects"] if d["severity"] == "info")
        counts = Counter(f"{d['severity']}:{d['check']}" for d in report["defects"])
        report["counts_by_check"] = dict(sorted(counts.items()))
    return report


def build_link_context(vault_root: str | Path) -> dict:
    """Build a reusable link-resolution context (index + parse caches)."""
    from .linkcheck import _make_run_caches, build_vault_index

    return {"index": build_vault_index(vault_root), "caches": _make_run_caches()}


def _lint_links(
    file_path: Path, text: str, vault_root: str | Path | None, link_context: dict | None
) -> list[dict]:
    """Resolve this file's wikilinks/embeds and emit link defects."""
    from .linkcheck import _block_exists, _heading_exists, _resolve_target

    if link_context is None:
        if vault_root is None:
            return []
        link_context = build_link_context(vault_root)
    index = link_context["index"]
    caches = link_context["caches"]
    structure = extract_structure_text(text)
    defects: list[dict] = []

    def link_defect(check: str, line: int, message: str, target: str) -> None:
        defects.append(
            {
                "check": check,
                "severity": "error",
                "line": line,
                "message": message,
                "excerpt": target[:160],
            }
        )

    records = [(r, r.get("embed", False)) for r in structure["wikilinks"]] + [
        (r, True) for r in structure["embeds"]
    ]
    for record, _is_embed in records:
        target = record.get("target")
        if not target:
            # self-anchors like [[#Heading]]: target is this file
            target_path = file_path
            resolution = "resolved"
        else:
            resolution, target_path, _candidates = _resolve_target(index, target, (".md",))
            if resolution == "broken":
                link_defect("LINK_BROKEN", record["line"], f"unresolved internal link '{target}'", target)
                continue
            if resolution == "ambiguous":
                link_defect("LINK_AMBIGUOUS", record["line"], f"ambiguous basename '{target}'", target)
                continue
        if record.get("anchor") is not None and not _heading_exists(target_path, record["anchor"], caches):
            link_defect(
                "LINK_MISSING_ANCHOR",
                record["line"],
                f"target has no heading '{record['anchor']}'",
                f"{target or '(self)'}#{record['anchor']}",
            )
        if record.get("block") is not None and not _block_exists(target_path, record["block"], caches):
            link_defect(
                "LINK_MISSING_BLOCK",
                record["line"],
                f"target has no block ^{record['block']}",
                f"{target or '(self)'}#^{record['block']}",
            )
    return defects


def lint_tree(
    root: str | Path,
    *,
    skip_dirs: tuple[str, ...] = (".git", ".obsidian"),
    check_links: bool = True,
    link_context: dict | None = None,
) -> dict:
    """Lint every Markdown file under *root*; aggregate per-file reports.

    The link context is built once per run (O(files) parses) and shared
    across files, mirroring the CAP-004 per-run cache discipline.
    """
    root_path = Path(root)
    if not root_path.is_dir():
        raise ArtifactLintError(f"lint root is not a directory: {root_path}")
    ctx = link_context
    if ctx is None and check_links:
        ctx = build_link_context(root_path)
    files: list[dict] = []
    for path in sorted(root_path.rglob("*.md")):
        if any(part in skip_dirs for part in path.relative_to(root_path).parts):
            continue
        report = lint_file(path, link_context=ctx if check_links else None)
        report["file"] = path.relative_to(root_path).as_posix()
        files.append(report)
    total = {
        "files": len(files),
        "defects": sum(f["defect_count"] for f in files),
        "errors": sum(f["error_count"] for f in files),
        "warnings": sum(f["warning_count"] for f in files),
        "infos": sum(f["info_count"] for f in files),
        "files_with_errors": sum(1 for f in files if f["error_count"]),
    }
    by_check: Counter[str] = Counter()
    for f in files:
        by_check.update(f["counts_by_check"])
    return {
        "root": str(root_path),
        "summary": total,
        "counts_by_check": dict(sorted(by_check.items())),
        "files": files,
        "caveat": (
            "syntax/reference validation only: a passing lint is necessary, "
            "never sufficient — semantic correctness requires review"
        ),
    }
