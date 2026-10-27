"""Deterministic knowledge-unit (KU) extraction from source notes (CAP-016).

Segments Markdown notes into structural blocks and mints schema-v1.1 KU
records with stable content-derived IDs, immutable locators and exact
excerpts. The extractor is deliberately STRUCTURAL:

- it assigns no semantic dispositions: every unit starts as ``Unaccounted``
  (permitted during work, blocks release) because overlap classification and
  disposition assignment are later, evidence-based work;
- it assigns no ``overlap_type``, ``concept_ids`` or ``destinations``;
- ``unit_type`` comes from a controlled STRUCTURAL vocabulary
  (prose/list/table/code_block/math_block/callout/quote/frontmatter/
  empty_section) derived from Markdown block syntax, never from meaning.

Completeness guarantee (line-accounting invariant): every line of every
processed file is accounted for in exactly one bucket — frontmatter, heading
context, unit content, excluded blank, excluded horizontal rule. A violation
is an internal-consistency failure that fails the run; content cannot
silently disappear between the lines the extractor reports.

Construct detection (frontmatter, ATX headings, code fences, ``$$`` math
blocks) delegates to CAP-003 ``mdextract`` — one shared authority — so
segmentation and structure extraction can never disagree.

Known limitations:
- excerpts are reconstructed with ``"\\n".join(splitlines())``; CR characters
  from CRLF files are normalized inside excerpts (source bytes are never
  modified; hashes are computed from raw bytes);
- inherits mdextract limitations: ATX headings only (setext ``===``/``---``
  underlines are not detected and may be classified as excluded horizontal
  rules), delimiter-based math detection without LaTeX validation, nested
  fences treated as fence content;
- a blank line splits a list into two units (no loose-list merging) — a
  granularity choice, never a content loss;
- an unclosed fence or math block absorbs all remaining lines into one unit
  (mdextract semantics); the content is preserved verbatim in the excerpt,
  a parse warning is recorded, and the affected unit is linkable to a finding
  (e.g. F-0002) via ``unclosed_finding``;
- ``empty_section`` units exist so that promised-but-empty sections are
  accounted for rather than silently dropped.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from . import __version__
from . import mdextract
from .inventory import classify_extension, load_manifest, scan_root
from .kuregistry import mint_ku_id
from .pathsafety import atomic_write_text
from .registry import validate_ku_file

UNIT_TYPES = (
    "prose",
    "list",
    "table",
    "code_block",
    "math_block",
    "callout",
    "quote",
    "frontmatter",
    "empty_section",
)

EXCLUDED_LINE_KINDS = ("blank", "horizontal_rule")

# a list item: "- x", "* x", "+ x", "1. x", "23) x" (marker + at least one space)
_LIST_ITEM_RE = re.compile(r"^(?:[-*+]|\d{1,9}[.)])\s+")
# horizontal rules: ---, ***, ___ (3+ identical marker characters only)
_HR_RE = re.compile(r"^(?:-{3,}|\*{3,}|_{3,})$")
# Obsidian callout marker inside a quote block: > [!note] Title
_CALLOUT_RE = re.compile(r"^>\s*\[!\w+\]")

_STABLE_VERIFICATION_STATUS = {
    "extraction": "machine-segmented",
    "accounting": "pending",
    "semantic": "pending",
    "technical": "pending",
    "editorial": "pending",
}


class ExtractionError(Exception):
    """Raised for actionable extraction configuration failures.

    (bad scope, unreadable manifest, destination problems). Per-file content
    problems are recorded as file outcomes instead; both make the overall run
    exit non-zero, but only ExtractionError aborts before enumeration.
    """


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _make_unit(
    unit_type: str,
    start: int,
    end: int,
    lines: list[str],
    heading_path_value: list[str],
) -> dict:
    excerpt = "\n".join(lines[start - 1 : end])
    return {
        "unit_type": unit_type,
        "line_start": start,
        "line_end": end,
        "excerpt": excerpt,
        "excerpt_hash": _sha256_text(excerpt),
        "heading_path": heading_path_value,
    }


def segment_note(text: str) -> dict:
    """Segment one note's text into structural blocks.

    Returns a dict with:
    - ``units``: block records (unit_type, line_start, line_end, excerpt,
      excerpt_hash, heading_path) sorted by position;
    - ``excluded``: counts of excluded lines by kind (blank, horizontal_rule)
      with the reason recorded in ``exclusion_reasons``;
    - ``headings``: heading context lines (from mdextract);
    - ``warnings``: parse warnings (unclosed constructs, YAML problems...);
    - ``unclosed_spans``: [(kind, start, end)] for constructs closed at EOF;
    - ``line_accounting``: per-bucket line counts plus the invariant check
      ``consistent`` (sum of buckets == total lines).

    The invariant is the extraction completeness guarantee: every line lands
    in exactly one bucket, so nothing can be silently dropped.
    """
    structure = mdextract.extract_structure_text(text)
    lines = text.splitlines()
    total = len(lines)
    headings = structure["headings"]
    heading_lines = {h["line"] for h in headings}

    # ---- occupied construct spans (single authority: mdextract) ----
    occupied: list[tuple[int, int, str]] = []
    unclosed_spans: list[tuple[str, int, int]] = []
    for fence in structure["code_fences"]:
        end = fence["end_line"] if fence["end_line"] is not None else total
        occupied.append((fence["start_line"], end, "code_block"))
        if not fence["closed"]:
            unclosed_spans.append(("code_block", fence["start_line"], end))
    for block in structure["math_blocks"]:
        end = block["end_line"] if block["end_line"] is not None else total
        occupied.append((block["start_line"], end, "math_block"))
        if not block["closed"]:
            unclosed_spans.append(("math_block", block["start_line"], end))
    occupied.sort()
    occupied_by_start = {start: (start, end, kind) for start, end, kind in occupied}
    occupied_lines: set[int] = set()
    for start, end, _kind in occupied:
        occupied_lines.update(range(start, end + 1))

    units: list[dict] = []
    excluded = {"blank": 0, "horizontal_rule": 0}

    # ---- frontmatter unit (metadata is knowledge: aliases, tags) ----
    fm_lines: set[int] = set()
    fm_span = structure["frontmatter_span"]
    if fm_span:
        fm_lines = set(range(fm_span[0], fm_span[1] + 1))
        units.append(_make_unit("frontmatter", fm_span[0], fm_span[1], lines, []))

    def heading_path_at(line: int) -> list[str]:
        return mdextract.heading_path(headings, line)

    # ---- main scan over unoccupied body lines ----
    i = 1
    while i <= total:
        line = lines[i - 1]
        stripped = line.strip()

        if i in fm_lines:  # frontmatter bucket
            i += 1
            continue
        if i in occupied_by_start:  # construct span -> its own unit
            start, end, kind = occupied_by_start[i]
            units.append(_make_unit(kind, start, end, lines, heading_path_at(start)))
            i = end + 1
            continue
        if i in heading_lines:  # heading context bucket
            i += 1
            continue
        if not stripped:  # excluded: blank separator
            excluded["blank"] += 1
            i += 1
            continue
        if _HR_RE.match(stripped):  # excluded: horizontal rule
            excluded["horizontal_rule"] += 1
            i += 1
            continue

        # ---- quote / callout block ----
        if stripped.startswith(">"):
            start = i
            is_callout = bool(_CALLOUT_RE.match(stripped))
            while i <= total:
                if i in fm_lines or i in occupied_lines or i in heading_lines:
                    break
                s = lines[i - 1].strip()
                if not s.startswith(">"):
                    break
                if _CALLOUT_RE.match(s):
                    is_callout = True
                i += 1
            units.append(
                _make_unit("callout" if is_callout else "quote", start, i - 1, lines, heading_path_at(start))
            )
            continue

        # ---- table block ----
        if stripped.startswith("|"):
            start = i
            while i <= total:
                if i in fm_lines or i in occupied_lines or i in heading_lines:
                    break
                if not lines[i - 1].strip().startswith("|"):
                    break
                i += 1
            units.append(_make_unit("table", start, i - 1, lines, heading_path_at(start)))
            continue

        # ---- list block (items + indented continuations) ----
        if _LIST_ITEM_RE.match(stripped):
            start = i
            while i <= total:
                if i in fm_lines or i in occupied_by_start or i in heading_lines:
                    break
                raw_line = lines[i - 1]
                s = raw_line.strip()
                if not s or _HR_RE.match(s):
                    break
                if s.startswith(">") or s.startswith("|"):
                    break
                if _LIST_ITEM_RE.match(s) or raw_line[:1] in (" ", "\t"):
                    i += 1
                    continue
                break  # non-indented non-item line: new block
            units.append(_make_unit("list", start, i - 1, lines, heading_path_at(start)))
            continue

        # ---- prose block (consecutive non-blank, non-construct lines) ----
        start = i
        while i <= total:
            if i in fm_lines or i in occupied_by_start or i in heading_lines:
                break
            s = lines[i - 1].strip()
            if not s or _HR_RE.match(s):
                break
            if s.startswith(">") or s.startswith("|") or _LIST_ITEM_RE.match(s):
                break
            i += 1
        units.append(_make_unit("prose", start, i - 1, lines, heading_path_at(start)))

    # ---- empty sections: headings whose subtree holds no content unit ----
    for index, heading in enumerate(headings):
        boundary = total + 1
        for later in headings[index + 1 :]:
            if later["level"] <= heading["level"]:
                boundary = later["line"]
                break
        lo, hi = heading["line"], boundary - 1
        has_content = any(lo < u["line_start"] <= hi for u in units)
        if not has_content:
            units.append(
                _make_unit(
                    "empty_section",
                    heading["line"],
                    heading["line"],
                    lines,
                    # parent path only: active hierarchy strictly before this
                    # heading, truncated to the heading's own level
                    heading_path_at(heading["line"] - 1)[: heading["level"] - 1],
                )
            )

    units.sort(key=lambda u: (u["line_start"], u["line_end"]))

    # ---- line-accounting invariant ----
    # Buckets partition every line: unit span lines (frontmatter unit
    # included), heading context lines, excluded blank, excluded horizontal
    # rule. Single-assignment by scan construction; the checks below prove
    # the partition and that unit spans never overlap.
    unit_lines: set[int] = set()
    for unit in units:
        unit_lines.update(range(unit["line_start"], unit["line_end"] + 1))
    span_total = sum(u["line_end"] - u["line_start"] + 1 for u in units)
    heading_only_lines = heading_lines - unit_lines
    accounted = (
        len(unit_lines)
        + len(heading_only_lines)
        + excluded["blank"]
        + excluded["horizontal_rule"]
    )
    consistent = (
        accounted == total
        and len(unit_lines) == span_total  # overlapping unit spans impossible
        and fm_lines <= unit_lines  # frontmatter lines live inside its unit
        and not (heading_only_lines & unit_lines)
    )

    warnings: list[str] = []
    warnings.extend(structure["errors"])
    warnings.extend(structure["warnings"])

    return {
        "lines_total": total,
        "units": units,
        "headings": headings,
        "excluded": excluded,
        "exclusion_reasons": {
            "blank": "blank separator lines carry no content",
            "horizontal_rule": "pure visual separators (---/***/___); structure only",
        },
        "warnings": warnings,
        "unclosed_spans": unclosed_spans,
        "line_accounting": {
            "unit_lines": len(unit_lines),
            "frontmatter_lines": len(fm_lines),
            "heading_context": len(heading_only_lines),
            "excluded_blank": excluded["blank"],
            "excluded_horizontal_rule": excluded["horizontal_rule"],
            "accounted": accounted,
            "lines_total": total,
            "consistent": consistent,
        },
    }


def _mint_records(
    *,
    vault_id: str,
    relpath: str,
    file_hash: str,
    segmentation: dict,
    unclosed_finding: str | None,
) -> list[dict]:
    """Mint schema-shaped KU records from a segmentation (no semantics)."""
    unclosed_unit_spans = {
        (kind, start, end) for kind, start, end in segmentation["unclosed_spans"]
    }
    records: list[dict] = []
    for unit in segmentation["units"]:
        record = {
            "knowledge_unit_id": "",  # minted below from stable identity basis
            "source_id": f"{vault_id}:{relpath}",
            "source_path": relpath,
            "source_file_hash": file_hash,
            "source_format": "markdown",
            "heading_path": list(unit["heading_path"]),
            "line_start": unit["line_start"],
            "line_end": unit["line_end"],
            "excerpt": unit["excerpt"],
            "excerpt_hash": unit["excerpt_hash"],
            "unit_type": unit["unit_type"],
            "disposition": "Unaccounted",
            # NOTE: this object's wording is part of the record's stable
            # fingerprint (idempotent re-loads); keep it version-free.
            "verification_status": dict(_STABLE_VERIFICATION_STATUS),
        }
        if unclosed_finding and (
            unit["unit_type"],
            unit["line_start"],
            unit["line_end"],
        ) in unclosed_unit_spans:
            record["finding_ids"] = [unclosed_finding]
        record["knowledge_unit_id"] = mint_ku_id(record)
        records.append(record)
    return records


def _is_under(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _scope_files(root: Path, scope: str) -> list[dict]:
    """Enumerate scope files as {relpath (root-relative), abs_path, class}."""
    scope_path = root / scope
    if scope_path.is_file():
        return [
            {
                "relpath": scope,
                "abs_path": scope_path,
                "class": classify_extension(scope_path.suffix),
            }
        ]
    scan = scan_root(scope_path)
    files = []
    for record in scan["files"]:
        files.append(
            {
                "relpath": f"{scope}/{record['relpath']}" if scope != "." else record["relpath"],
                "abs_path": scope_path / record["relpath"],
                "class": record["class"],
            }
        )
    # unreadable/unhashable entries surface as failures, not silent skips
    for record in scan["errors"]:
        files.append(
            {
                "relpath": f"{scope}/{record['relpath']}" if scope != "." else record["relpath"],
                "abs_path": scope_path / record["relpath"],
                "class": record["class"],
                "scan_error": record.get("error") or record.get("note") or "unreadable",
            }
        )
    return files


def extract_scope(
    root: str | Path,
    scope: str,
    vault_id: str,
    manifest_path: str | Path,
    out_path: str | Path,
    *,
    kus_schema: str | Path,
    unclosed_finding: str | None = None,
) -> dict:
    """Extract one bounded scope into a schema-valid KU batch.

    Enumerates every file under *root/scope* (the denominator), verifies each
    against the baseline manifest, segments markdown files deterministically,
    mints stable-ID records and writes them to *out_path*. The batch is then
    validated against the KU schema + cross-checks; any failure makes
    ``ok`` false (CLI exit 1).

    Read-only with respect to *root*: only *out_path* is written.
    """
    root_path = Path(root)
    if not root_path.is_dir():
        raise ExtractionError(f"source root is not a directory: {root_path}")
    if not vault_id or not vault_id.strip():
        raise ExtractionError("vault_id must be a non-empty stable identifier")
    if Path(scope).is_absolute() or ".." in Path(scope).parts:
        raise ExtractionError(f"scope must be a root-relative path without '..': {scope!r}")
    scope_path = root_path / scope
    if not scope_path.exists():
        raise ExtractionError(f"scope path does not exist under root: {scope}")
    resolved_root = root_path.resolve()
    resolved_scope = scope_path.resolve()
    if resolved_scope != resolved_root and not _is_under(resolved_scope, resolved_root):
        raise ExtractionError(f"scope escapes the source root: {scope}")

    try:
        manifest_records_list = load_manifest(manifest_path)
    except (OSError, ValueError) as exc:
        raise ExtractionError(f"cannot load baseline manifest: {exc}") from exc
    manifest_by_relpath = {rec["relpath"]: rec["sha256"] for rec in manifest_records_list}

    files = _scope_files(root_path, scope)
    if not files:
        raise ExtractionError(f"scope contains no files: {scope} (denominator 0 is an actionable scope mistake)")

    # manifest <-> disk reconciliation restricted to the scope
    scope_prefix = "" if scope == "." else scope + "/"
    manifest_scope_relpaths = {
        relpath
        for relpath in manifest_by_relpath
        if scope == "." or relpath.startswith(scope_prefix) or relpath == scope
    }

    file_outcomes: list[dict] = []
    records: list[dict] = []
    failures: list[dict] = []

    files_by_relpath = {f["relpath"]: f for f in files}

    # manifest entries under scope missing from disk
    for relpath in sorted(manifest_scope_relpaths - set(files_by_relpath)):
        outcome = {
            "relpath": relpath,
            "outcome": "failed_missing_on_disk",
            "reason": "file present in baseline manifest but not on disk under the scope",
        }
        file_outcomes.append(outcome)
        failures.append(outcome)

    for file in sorted(files, key=lambda f: f["relpath"]):
        relpath = file["relpath"]
        if file.get("scan_error"):
            outcome = {
                "relpath": relpath,
                "outcome": "failed_unreadable",
                "reason": file["scan_error"],
            }
            file_outcomes.append(outcome)
            failures.append(outcome)
            continue
        if relpath not in manifest_by_relpath:
            outcome = {
                "relpath": relpath,
                "outcome": "failed_not_in_manifest",
                "reason": "file on disk is absent from the baseline manifest (unaccounted new file)",
            }
            file_outcomes.append(outcome)
            failures.append(outcome)
            continue
        if file["class"] != "markdown":
            file_outcomes.append(
                {
                    "relpath": relpath,
                    "outcome": "excluded_non_markdown",
                    "reason": f"unsupported class {file['class']!r}; extraction handles markdown only",
                }
            )
            continue

        try:
            raw = file["abs_path"].read_bytes()
        except OSError as exc:
            outcome = {
                "relpath": relpath,
                "outcome": "failed_unreadable",
                "reason": f"{type(exc).__name__}: {exc}",
            }
            file_outcomes.append(outcome)
            failures.append(outcome)
            continue
        file_hash = hashlib.sha256(raw).hexdigest()
        if file_hash != manifest_by_relpath[relpath]:
            outcome = {
                "relpath": relpath,
                "outcome": "failed_hash_mismatch",
                "reason": "live sha256 differs from the baseline manifest; extraction must run against verified immutable sources",
            }
            file_outcomes.append(outcome)
            failures.append(outcome)
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            outcome = {
                "relpath": relpath,
                "outcome": "failed_encoding",
                "reason": f"UTF-8 decode error: {exc}",
            }
            file_outcomes.append(outcome)
            failures.append(outcome)
            continue

        segmentation = segment_note(text)
        if not segmentation["line_accounting"]["consistent"]:
            outcome = {
                "relpath": relpath,
                "outcome": "failed_internal_consistency",
                "reason": f"line accounting violated: {segmentation['line_accounting']}",
            }
            file_outcomes.append(outcome)
            failures.append(outcome)
            continue

        file_records = _mint_records(
            vault_id=vault_id,
            relpath=relpath,
            file_hash=file_hash,
            segmentation=segmentation,
            unclosed_finding=unclosed_finding,
        )
        records.extend(file_records)

        units_by_type: dict[str, int] = {}
        for unit in segmentation["units"]:
            units_by_type[unit["unit_type"]] = units_by_type.get(unit["unit_type"], 0) + 1
        file_outcomes.append(
            {
                "relpath": relpath,
                "outcome": "extracted",
                "sha256": file_hash,
                "manifest_match": True,
                "units": len(segmentation["units"]),
                "units_by_type": units_by_type,
                "warnings": segmentation["warnings"],
                "unclosed_spans": segmentation["unclosed_spans"],
                "line_accounting": segmentation["line_accounting"],
                "excluded_lines": segmentation["excluded"],
                "finding_ids": sorted(
                    {fid for r in file_records for fid in r.get("finding_ids", [])}
                ),
            }
        )

    # ---- write the batch (deterministic order; stable serialization; ATOMIC L-08) ----
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(
        json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n" for record in records
    )
    atomic_write_text(out, payload)

    batch_validation = validate_ku_file(out, kus_schema)
    if not batch_validation["valid"]:
        failures.append(
            {
                "relpath": None,
                "outcome": "failed_batch_validation",
                "reason": "generated batch failed schema/cross-check validation",
                "errors": batch_validation["errors"],
            }
        )

    denominator = len(file_outcomes)
    extracted = [o for o in file_outcomes if o["outcome"] == "extracted"]
    excluded = [o for o in file_outcomes if o["outcome"].startswith("excluded_")]
    units_by_type: dict[str, int] = {}
    for record in records:
        units_by_type[record["unit_type"]] = units_by_type.get(record["unit_type"], 0) + 1

    return {
        "ok": not failures,
        "command": "extract-kus",
        "framework_version": __version__,
        "vault_id": vault_id,
        "root": str(root_path),
        "scope": scope,
        "manifest": str(manifest_path),
        "batch_path": str(out),
        "records_written": len(records),
        "denominators": {
            "files_in_scope": denominator,
            "files_extracted": len(extracted),
            "files_excluded": len(excluded),
            "files_failed": len(failures),
            "scope_note": "denominator = every file enumerated under the scope (all classes); each has exactly one outcome",
        },
        "units_by_type": units_by_type,
        "file_outcomes": file_outcomes,
        "batch_validation": batch_validation,
        "determinism_note": (
            "records contain no timestamps and IDs are content-derived; "
            "re-extracting unchanged sources produces a byte-identical batch"
        ),
        "limitations": [
            "structural segmentation only: unit types describe Markdown block syntax, not meaning",
            "no dispositions are assigned: every unit is 'Unaccounted' until evidence-based classification",
            "excerpts normalize CR characters away (splitlines reconstruction); source bytes are untouched",
            "construct detection inherits mdextract limitations (ATX headings, delimiter-based math)",
            "extraction coverage is NOT semantic preservation; it is the accounting baseline for later audits",
        ],
    }
