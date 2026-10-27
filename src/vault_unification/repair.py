"""Evidence-based targeted repair loop for note defects (FRAME-002, CAP-020).

Turns artifact-lint defects into SMALL, bounded repair tasks instead of
whole-note rewrites, per the Phase 0 quality-tooling requirements. Every
step is recorded so a repair is auditable: what was broken, where, what
context was needed, what was attempted, what the diff was, whether the
same validator now passes.

LIFECYCLE:
- ``create_repair_tasks(lint_report)`` — one repair task per error/warning
  defect (info-level defects are convention notes, not repairs), each
  carrying the smallest sufficient context: file, line, check id, message,
  excerpt, and the EXPECTED FIX semantics for that check id.
- ``record_attempt(task, outcome, ...)`` — append-only attempt history
  (outcome: fixed / failed / skipped), with the unified diff of the change
  when provided; the ORIGINAL excerpt is preserved forever in the task.
- ``verify_repair(task, current_text, ...)`` — re-run the EXACT check that
  failed on the repaired file, then re-lint the whole file to catch
  collateral damage, and (when a diff is available) verify that unrelated
  regions were not touched (repair-scope discipline).
- Bounded retries: a task with ``max_attempts`` (default 3) failed
  attempts becomes ``escalated_review`` — the loop CANNOT run forever, and
  escalation is an explicit, recorded state, never a silent stall.

SAFETY RULES BAKED IN:
- The original file content excerpt is captured at task creation; a repair
  is NEVER accepted merely because the new output looks plausible — the
  originating check must pass on the new content.
- Tasks are content-addressed (deterministic ids from file+line+check+
  message): re-creating tasks from a fresh lint run is idempotent — an
  existing OPEN task for the same defect is reused, not duplicated.
- Records are JSONL, append-friendly, and schema-validated
  (schemas/repair-task.schema.json).
"""

from __future__ import annotations

import difflib
import hashlib
import json
import re
from pathlib import Path

from .artifactlint import lint_text

__all__ = [
    "RepairError",
    "DEFAULT_MAX_ATTEMPTS",
    "CHECK_FIX_GUIDANCE",
    "create_repair_tasks",
    "record_attempt",
    "verify_repair",
    "load_tasks",
    "save_tasks",
    "task_status",
]

DEFAULT_MAX_ATTEMPTS = 3


class RepairError(Exception):
    """Raised for invalid repair-loop inputs."""


# expected-fix semantics per check id: what "repaired" means, used both in
# the task record (so the repair prompt is precise) and by reviewers.
CHECK_FIX_GUIDANCE: dict[str, str] = {
    "FENCE_UNCLOSED": "close the code fence with a matching ``` line; preserve every body line unchanged",
    "CODE_LANG_MISSING": "add the correct language label to the opening fence; do not alter the body",
    "CODE_LANG_UNKNOWN": "correct the fence language label to a known one (or justify keeping it)",
    "CODE_PYTHON_SYNTAX": "repair the python syntax error while preserving the code's intent; if the source snippet is itself broken, reproduce it verbatim in a text fence and explain in prose",
    "CODE_JSON_INVALID": "repair the JSON so it parses; preserve the data",
    "MERMAID_PARSE": "repair the diagram line so it matches the declared diagram grammar (or fix the declaration); preserve node/edge semantics",
    "MATH_BLOCK_UNCLOSED": "close the display-math block with a matching $$; preserve the formula content",
    "MATH_INLINE_ODD": "pair or escape the stray '$' so inline math delimiters balance",
    "MATH_ENV_MISMATCH": "match every \\begin{env} with a \\end{env} in the correct order",
    "MATH_DELIM_STYLE_MIXED": "normalize display math to one delimiter convention",
    "TABLE_SEPARATOR_BAD": "repair the separator row so it has exactly as many cells as the header",
    "TABLE_CELL_MISMATCH": "make the row's cell count match the header (split/merge or fix the broken row)",
    "TABLE_SEPARATOR_MISSING": "add the missing separator row (or convert the block to prose/list if it is not a table)",
    "HEADING_SKIP": "fix the heading level so the hierarchy does not skip",
    "HEADING_EMPTY": "give the heading text or remove the empty heading",
    "LIST_INDENT_MIXED": "use one indentation style for list nesting",
    "LINK_BROKEN": "resolve the link: fix the target spelling, create the intended note, or convert to plain text with a rationale — never leave a silent dead link",
    "LINK_AMBIGUOUS": "disambiguate the link with a longer path",
    "LINK_MISSING_ANCHOR": "fix the anchor to an existing heading or create the heading intentionally",
    "LINK_MISSING_BLOCK": "fix or remove the block reference",
    "TRUNCATION_MID_SENTENCE": "complete the final sentence or section; check against the source knowledge units",
    "PLACEHOLDER_TEXT": "replace the placeholder with real content from the source evidence",
    "BRACKET_UNBALANCED": "balance the brackets outside code/math",
    "FRONTMATTER_INVALID": "repair the frontmatter YAML",
    "TRUNCATION_OPEN_CONSTRUCT": "close the construct left open at end of file",
    "EMPTY_SECTION": "fill or remove the empty section",
    "HEADING_MULTI_H1": "reduce to one H1 (info-level; fix only with layout reason)",
}

_REPAIRABLE_SEVERITIES = frozenset({"error", "warning"})


def _task_id(file: str, line: int, check: str, message: str) -> str:
    digest = hashlib.sha256(f"{file}|{line}|{check}|{message}".encode("utf-8")).hexdigest()[:12]
    return f"RT-{digest}"


def create_repair_tasks(
    lint_reports: list[dict],
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
) -> list[dict]:
    """Convert lint reports (per-file dicts or a tree report) to repair tasks.

    Idempotent by content-addressed id: callers merging new tasks with an
    existing task store should pass the existing tasks via :func:`merge`.
    """
    tasks: list[dict] = []
    seen: set[str] = set()
    for report in lint_reports:
        per_file = report.get("files", [report] if "defects" in report else [])
        for file_report in per_file:
            file_name = file_report.get("file") or file_report.get("path") or "<unknown>"
            for defect in file_report.get("defects", []):
                if defect["severity"] not in _REPAIRABLE_SEVERITIES:
                    continue
                tid = _task_id(file_name, defect.get("line", 0), defect["check"], defect["message"])
                if tid in seen:
                    continue
                seen.add(tid)
                tasks.append(
                    {
                        "repair_id": tid,
                        "status": "open",
                        "file": file_name,
                        "line": defect.get("line", 0),
                        "check": defect["check"],
                        "severity": defect["severity"],
                        "message": defect["message"],
                        "original_excerpt": defect.get("excerpt", ""),
                        "expected_fix": CHECK_FIX_GUIDANCE.get(
                            defect["check"], "repair the defect so the check passes; preserve unrelated content"
                        ),
                        "max_attempts": max_attempts,
                        "attempts": [],
                        "created_from": "artifactlint",
                    }
                )
    tasks.sort(key=lambda t: (t["file"], t["line"], t["check"]))
    return tasks


def merge_tasks(existing: list[dict], new: list[dict]) -> tuple[list[dict], list[str]]:
    """Merge new tasks into an existing store; returns (merged, added_ids).

    - A new task whose id matches an existing OPEN task updates location/
      message but keeps attempt history.
    - A new task matching a task already verified-fixed is re-OPENED (the
      defect came back — a regression signal worth recording).
    - Existing tasks not present in new (for their file) are left untouched
      (they may be verified or escalated; deletion is a review decision).
    """
    by_id = {t["repair_id"]: dict(t) for t in existing}
    added: list[str] = []
    for task in new:
        tid = task["repair_id"]
        if tid in by_id:
            current = by_id[tid]
            if current["status"] == "verified_fixed":
                reopened = dict(task)
                reopened["attempts"] = current["attempts"] + [
                    {
                        "outcome": "regression_detected",
                        "note": "defect reappeared after a verified fix",
                        "utc": None,
                    }
                ]
                reopened["status"] = "open"
                by_id[tid] = reopened
            else:
                current["line"] = task["line"]
                current["message"] = task["message"]
                current["original_excerpt"] = task["original_excerpt"]
        else:
            by_id[tid] = dict(task)
            added.append(tid)
    merged = sorted(by_id.values(), key=lambda t: (t["file"], t["line"], t["repair_id"]))
    return merged, added


def record_attempt(
    task: dict,
    outcome: str,
    *,
    diff: str | None = None,
    note: str | None = None,
    actor: str = "agent",
) -> dict:
    """Append an attempt to a task and update its status.

    outcome: 'fixed' (claims repair; verification still required),
    'failed', 'skipped', or 'regression_detected' (internal).
    """
    if outcome not in ("fixed", "failed", "skipped"):
        raise RepairError(f"invalid attempt outcome: {outcome!r}")
    task = dict(task)
    attempts = list(task.get("attempts", []))
    attempts.append(
        {
            "outcome": outcome,
            "actor": actor,
            "note": note,
            "diff": diff,
        }
    )
    task["attempts"] = attempts
    failed = sum(1 for a in attempts if a["outcome"] in ("failed", "regression_detected"))
    if outcome == "fixed":
        task["status"] = "awaiting_verification"
    elif failed >= task.get("max_attempts", DEFAULT_MAX_ATTEMPTS):
        task["status"] = "escalated_review"
    else:
        task["status"] = "open"
    return task


def verify_repair(
    task: dict,
    current_text: str,
    *,
    original_text: str | None = None,
    path: str | None = None,
) -> dict:
    """Verify a claimed repair: the originating check must pass on the new
    content, the whole-file lint must not gain NEW defects, and (when the
    original text is provided) the change must stay local to the defect
    region — unrelated content may not be silently rewritten.

    Returns a verification record; the caller applies the status change
    (verified_fixed / repair_failed) via :func:`apply_verification`.
    """
    path = path or task["file"]
    new_lint = lint_text(current_text, path=path)

    # 1. the originating defect must be gone (same check, same line region)
    originating = [
        d
        for d in new_lint["defects"]
        if d["check"] == task["check"]
        and abs((d.get("line") or 0) - (task["line"] or 0)) <= 2
        and d["message"] == task["message"]
    ]
    if originating:
        return {
            "repair_id": task["repair_id"],
            "verified": False,
            "reason": "originating defect still present after repair",
            "remaining": originating,
        }

    # 2. no NEW defects of any kind (regression guard)
    if original_text is not None:
        old_lint = lint_text(original_text, path=path)
        old_keys = {(d["check"], d.get("line"), d["message"]) for d in old_lint["defects"]}
        new_keys = {(d["check"], d.get("line"), d["message"]) for d in new_lint["defects"]}
        gained = [k for k in new_keys - old_keys if k[0] != task["check"]]
        if gained:
            return {
                "repair_id": task["repair_id"],
                "verified": False,
                "reason": "repair introduced new defects elsewhere in the note",
                "gained": [f"{c}@{ln}: {m[:80]}" for c, ln, m in gained],
            }
        # 3. repair-scope discipline: the diff must stay near the defect line
        diff_lines = [
            dl
            for dl in difflib.unified_diff(
                original_text.split("\n"), current_text.split("\n"), lineterm="", n=0
            )
            if dl.startswith(("+", "-")) and not dl.startswith(("+++", "---"))
        ]
        if diff_lines:
            old_lineno = task["line"]
            changed_regions = _diff_regions(original_text, current_text)
            far = [r for r in changed_regions if abs(r - old_lineno) > 8]
            if far:
                return {
                    "repair_id": task["repair_id"],
                    "verified": False,
                    "reason": "repair touched regions far from the defect; use a targeted fix",
                    "changed_line_regions": changed_regions,
                    "defect_line": old_lineno,
                }

    return {
        "repair_id": task["repair_id"],
        "verified": True,
        "reason": "originating check passes; no new defects; scope local" if original_text is not None else "originating check passes",
        "new_lint_summary": {
            "errors": new_lint["error_count"],
            "warnings": new_lint["warning_count"],
            "infos": new_lint["info_count"],
        },
    }


def _diff_regions(old: str, new: str) -> list[int]:
    """Approximate 1-based line numbers where old and new differ."""
    sm = difflib.SequenceMatcher(None, old.split("\n"), new.split("\n"), autojunk=False)
    regions = []
    for tag, i1, _i2, _j1, _j2 in sm.get_opcodes():
        if tag != "equal":
            regions.append(i1 + 1)
    return regions


def apply_verification(task: dict, verification: dict) -> dict:
    """Apply a verification record to a task (status transition)."""
    task = dict(task)
    if verification["verified"]:
        task["status"] = "verified_fixed"
    else:
        attempts = list(task.get("attempts", []))
        attempts.append(
            {
                "outcome": "failed",
                "actor": "verify_repair",
                "note": verification["reason"],
                "diff": None,
            }
        )
        task["attempts"] = attempts
        failed = sum(1 for a in attempts if a["outcome"] in ("failed", "regression_detected"))
        task["status"] = "escalated_review" if failed >= task.get("max_attempts", DEFAULT_MAX_ATTEMPTS) else "open"
    return task


def load_tasks(path: str | Path) -> list[dict]:
    """Load a repair-task JSONL store."""
    p = Path(path)
    if not p.is_file():
        return []
    tasks = []
    with p.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                tasks.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise RepairError(f"{p}:{lineno} is not valid JSON: {exc}") from exc
    return tasks


def save_tasks(path: str | Path, tasks: list[dict]) -> None:
    """Write a repair-task JSONL store (sorted, stable formatting)."""
    from .reporting import write_jsonl

    write_jsonl(Path(path), tasks)


def task_status(tasks: list[dict]) -> dict:
    """Aggregate status counts for reporting."""
    counts: dict[str, int] = {}
    for t in tasks:
        counts[t["status"]] = counts.get(t["status"], 0) + 1
    escalated = [
        {"repair_id": t["repair_id"], "file": t["file"], "check": t["check"], "message": t["message"]}
        for t in tasks
        if t["status"] == "escalated_review"
    ]
    return {"total": len(tasks), "by_status": dict(sorted(counts.items())), "escalated": escalated}
