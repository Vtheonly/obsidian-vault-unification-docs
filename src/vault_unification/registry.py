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


KU_CROSS_CHECK_RULES = (
    "duplicate_id",
    "self_parent",
    "superseded_rationale_missing",
    "self_support",
    "unknown_parent",
    "unknown_support",
)


def check_ku_records(
    records: list[dict],
    *,
    check_parent_refs: bool = False,
    known_external_ids: set[str] | None = None,
) -> list[dict]:
    """Cross-record checks over a list of KU records (plain dicts).

    Shared authority for KU cross-check rules; used by ``validate_ku_file``
    (file-level) and ``kuregistry.load_records`` (database-level) so the two
    validation layers cannot drift apart.

    Rules:
    - ``duplicate_id``: the same knowledge_unit_id appears twice in the list;
    - ``self_parent``: parent_unit_id equals the record's own id;
    - ``superseded_rationale_missing``: disposition 'Superseded' without a
      non-empty ``superseded_rationale`` (schema v1.1, ADR-0008);
    - ``self_support``: supporting_unit_ids contains the record's own id;
    - ``unknown_parent`` / ``unknown_support``: only when ``check_parent_refs``
      is True (database loads know the full ID universe); a file-level batch
      may legitimately reference units stored in an earlier batch.

    Returns error dicts: record_index, knowledge_unit_id, rule, message.
    """
    errors: list[dict] = []
    known = known_external_ids or set()
    ids = [record.get("knowledge_unit_id") for record in records]
    id_set = set(ids)

    for index, record in enumerate(records):
        ku_id = record.get("knowledge_unit_id")

        if ids.count(ku_id) > 1 and ku_id is not None:
            errors.append(
                {
                    "record_index": index,
                    "knowledge_unit_id": ku_id,
                    "rule": "duplicate_id",
                    "message": f"knowledge_unit_id {ku_id!r} appears more than once",
                }
            )

        parent = record.get("parent_unit_id")
        if parent is not None:
            if parent == ku_id:
                errors.append(
                    {
                        "record_index": index,
                        "knowledge_unit_id": ku_id,
                        "rule": "self_parent",
                        "message": "parent_unit_id references the unit itself",
                    }
                )
            elif check_parent_refs and parent not in id_set and parent not in known:
                errors.append(
                    {
                        "record_index": index,
                        "knowledge_unit_id": ku_id,
                        "rule": "unknown_parent",
                        "message": f"parent_unit_id {parent!r} not found in batch or registry",
                    }
                )

        if record.get("disposition") == "Superseded":
            rationale = record.get("superseded_rationale")
            if not isinstance(rationale, str) or not rationale.strip():
                errors.append(
                    {
                        "record_index": index,
                        "knowledge_unit_id": ku_id,
                        "rule": "superseded_rationale_missing",
                        "message": "disposition 'Superseded' requires a non-empty "
                        "superseded_rationale (unique information preserved elsewhere "
                        "must be recorded, docs/KNOWLEDGE_AND_PROVENANCE.md invariant 3)",
                    }
                )

        supports = record.get("supporting_unit_ids") or []
        for supported in supports:
            if supported == ku_id:
                errors.append(
                    {
                        "record_index": index,
                        "knowledge_unit_id": ku_id,
                        "rule": "self_support",
                        "message": "supporting_unit_ids contains the unit itself",
                    }
                )
            elif (
                check_parent_refs
                and supported not in id_set
                and supported not in known
            ):
                errors.append(
                    {
                        "record_index": index,
                        "knowledge_unit_id": ku_id,
                        "rule": "unknown_support",
                        "message": f"supporting_unit_id {supported!r} not found in batch or registry",
                    }
                )
    return errors


def validate_ku_file(path: str | Path, schema_path: str | Path) -> dict:
    """Validate a KU JSONL batch file: schema + cross-record checks.

    File-level cross-checks cover duplicate IDs, self-parents, self-supports
    and the Superseded rationale rule. Parent/support references to units in
    *other* batch files are not file-level errors (append-only batches may be
    split across files); the authoritative check runs at registry load time
    against the union of batch + database IDs.
    """
    report = validate_records_against_schema(path, schema_path)
    if report["errors"]:
        report["cross_checks"] = {"status": "not_run", "reason": "per-record errors present"}
        return report

    entries, _ = load_jsonl_records(path)
    records = [entry["record"] for entry in entries]
    for error in check_ku_records(records, check_parent_refs=False):
        report["errors"].append(
            {
                "line": None,
                "knowledge_unit_id": error.get("knowledge_unit_id"),
                "rule": error["rule"],
                "error": error["message"],
            }
        )
    report["valid"] = not report["errors"]
    report["cross_checks"] = {
        "status": "run",
        "kus_total": len(records),
        "rules": ["duplicate_id", "self_parent", "superseded_rationale_missing", "self_support"],
        "note": "cross-batch parent/support references are checked at registry load time",
    }
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


def validate_classification_file(path: str | Path, schema_path: str | Path) -> dict:
    """Validate an overlap-classification JSONL file: schema + cross-checks.

    File-level cross-checks (complementary to the registry's apply-time
    checks against loaded KUs):
    - classification_ids are unique within the file;
    - every evidence ku_id also appears in the record's ku_ids;
    - every evidence quote is attributable (has ku_id, quote, source_path,
      lines);
    - supersedes_classification_id references exist within the file (the
      registry additionally resolves references to earlier files).

    KU existence in a registry database is NOT checked here (this file-level
    validation has no database context); the authoritative check runs at
    ``kureg-apply-overlap`` time.
    """
    report = validate_records_against_schema(path, schema_path)
    if report["errors"]:
        report["cross_checks"] = {"status": "not_run", "reason": "per-record errors present"}
        return report

    entries, _ = load_jsonl_records(path)
    records = [entry["record"] for entry in entries]

    seen_ids: set[str] = set()
    for record in records:
        cid = record.get("classification_id")
        if cid in seen_ids:
            report["errors"].append(
                {
                    "line": None,
                    "classification_id": cid,
                    "rule": "duplicate_classification_id",
                    "error": f"classification_id {cid!r} appears more than once",
                }
            )
        seen_ids.add(cid)
        ku_ids = set(record.get("ku_ids") or [])
        for ev in record.get("evidence") or []:
            ev_ku = ev.get("ku_id")
            if ev_ku not in ku_ids:
                report["errors"].append(
                    {
                        "line": None,
                        "classification_id": cid,
                        "rule": "evidence_ku_not_in_ku_ids",
                        "error": f"evidence references ku_id {ev_ku!r} "
                        "which is not in the record's ku_ids",
                    }
                )
        supersedes = record.get("supersedes_classification_id")
        if supersedes is not None:
            file_ids = {r.get("classification_id") for r in records}
            if supersedes == cid:
                report["errors"].append(
                    {
                        "line": None,
                        "classification_id": cid,
                        "rule": "self_supersede",
                        "error": "classification cannot supersede itself",
                    }
                )
            elif supersedes not in file_ids:
                # external reference: resolved at registry apply time
                report.setdefault("external_supersedes_references", []).append(
                    {"classification_id": cid, "supersedes": supersedes}
                )

    report["valid"] = not report["errors"]
    report["cross_checks"] = {
        "status": "run",
        "classifications_total": len(records),
        "rules": [
            "duplicate_classification_id",
            "evidence_ku_not_in_ku_ids",
            "self_supersede",
        ],
        "note": "KU existence, cross-vault span and external supersedes "
        "references are checked at registry apply time",
    }
    return report
