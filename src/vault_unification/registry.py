"""Registry validation against JSON schemas.

Validates JSONL record files (task queue, knowledge units) against the JSON
Schemas stored in ``schemas/``, reporting per-record, per-line errors
explicitly. Cross-checks (e.g. task dependency references) run after per-record
schema validation.
"""

from __future__ import annotations

import json
from pathlib import Path

try:  # optional dependency, availability checked by selftest
    import jsonschema  # type: ignore

    _HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover - exercised only without jsonschema
    _HAS_JSONSCHEMA = False


def load_jsonl_records(path: str | Path) -> tuple[list[dict], list[dict]]:
    """Parse a JSONL file; return (records, errors).

    Errors carry the 1-based line number and message; a malformed line never
    aborts the whole parse.
    """
    records: list[dict] = []
    errors: list[dict] = []
    with open(path, encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as exc:
                errors.append({"line": lineno, "error": f"invalid JSON: {exc}"})
                continue
            if not isinstance(parsed, dict):
                errors.append({"line": lineno, "error": "record is not a JSON object"})
                continue
            records.append({"lineno": lineno, "record": parsed})
    return records, errors


def validate_records_against_schema(
    path: str | Path, schema_path: str | Path
) -> dict:
    """Validate every record in a JSONL file against a JSON Schema.

    Returns a report with per-record schema errors; returns an explicit
    dependency error when jsonschema is not installed.
    """
    path = Path(path)
    schema_path = Path(schema_path)
    report: dict = {
        "file": str(path),
        "schema": str(schema_path),
        "valid": False,
        "records_total": 0,
        "records_valid": 0,
        "errors": [],
    }
    if not _HAS_JSONSCHEMA:
        report["errors"].append(
            {
                "line": None,
                "error": "jsonschema package is not installed; validation could not run",
            }
        )
        return report
    if not path.exists():
        report["errors"].append({"line": None, "error": f"records file not found: {path}"})
        return report
    if not schema_path.exists():
        report["errors"].append({"line": None, "error": f"schema file not found: {schema_path}"})
        return report

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator_cls = jsonschema.validators.validator_for(schema)
    validator = validator_cls(schema)

    records, parse_errors = load_jsonl_records(path)
    for err in parse_errors:
        report["errors"].append(err)
    report["records_total"] = len(records) + len(parse_errors)
    for entry in records:
        errors = sorted(validator.iter_errors(entry["record"]), key=lambda e: list(e.path))
        if errors:
            for err in errors:
                location = ".".join(str(p) for p in err.absolute_path) or "<root>"
                report["errors"].append(
                    {
                        "line": entry["lineno"],
                        "task_id": entry["record"].get("task_id")
                        or entry["record"].get("knowledge_unit_id"),
                        "location": location,
                        "error": err.message,
                    }
                )
        else:
            report["records_valid"] += 1
    report["valid"] = not report["errors"]
    return report


def validate_task_queue(path: str | Path, schema_path: str | Path) -> dict:
    """Validate the task queue JSONL and cross-check dependency references.

    Cross-checks:
    - every dependency references an existing task_id in the same file;
    - task_ids are unique;
    - referenced statuses are among the schema enum (covered by schema).
    """
    report = validate_records_against_schema(path, schema_path)
    if report["errors"]:
        # per-record errors already block reliable cross-checks
        report["cross_checks"] = {"status": "not_run", "reason": "per-record errors present"}
        return report

    records, _ = load_jsonl_records(path)
    ids = [entry["record"]["task_id"] for entry in records]
    duplicates = sorted({tid for tid in ids if ids.count(tid) > 1})
    if duplicates:
        report["valid"] = False
        report["errors"].append(
            {"line": None, "error": f"duplicate task_ids: {duplicates}"}
        )
    id_set = set(ids)
    for entry in records:
        for dep in entry["record"].get("dependencies", []):
            if dep not in id_set:
                report["valid"] = False
                report["errors"].append(
                    {
                        "line": entry["lineno"],
                        "task_id": entry["record"]["task_id"],
                        "error": f"dependency references unknown task_id: {dep}",
                    }
                )
    report["cross_checks"] = {
        "status": "run",
        "tasks_total": len(records),
        "unique_task_ids": len(id_set),
        "duplicate_task_ids": duplicates,
    }
    return report


def validate_state_file(path: str | Path) -> dict:
    """Validate that the current-state JSON file parses and has expected keys."""
    path = Path(path)
    report = {"file": str(path), "valid": False, "errors": []}
    if not path.exists():
        report["errors"].append(f"state file not found: {path}")
        return report
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        report["errors"].append(f"invalid JSON: {exc}")
        return report
    if not isinstance(state, dict):
        report["errors"].append("state file is not a JSON object")
        return report
    required = ["project", "stage", "status", "current_task_id"]
    missing = [key for key in required if key not in state]
    if missing:
        report["errors"].append(f"missing required keys: {missing}")
        return report
    report["valid"] = True
    report["state"] = state
    return report
