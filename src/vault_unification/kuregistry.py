"""Persistent knowledge-unit registry (CAP-011).

Two layers (ADR-0007):

- Canonical store: JSONL batch files (e.g. under ``state/knowledge-units/``)
  are the committed source of truth for knowledge-unit (KU) records. They are
  validated against ``schemas/knowledge-unit.schema.json`` (v1.1) before use.
- Derived index: a SQLite database provides relational integrity and queries
  (many-to-many provenance, disposition accounting). It is always rebuildable
  from the canonical JSONL via ``kureg-init`` + ``kureg-load``; in v1 all
  writes flow through ``kureg-load`` (no direct-to-DB record creation), which
  keeps one write path fully validated and transactional.

Stable identifiers (docs/KNOWLEDGE_AND_PROVENANCE.md): KU IDs are minted from
source identity and content fingerprints — source id + file hash + heading
path + line range + excerpt hash — never from line numbers alone. A record
without any locator (no excerpt, no excerpt hash, no line range) cannot be
minted an ID; the caller must supply one explicitly.

Overlap classification and disposition are separate fields (schema v1.1,
ADR-0008): ``disposition`` records the outcome for a unit; ``overlap_type``
records the relationship between pieces of evidence. A ``Superseded``
disposition requires a non-empty ``superseded_rationale`` (enforced by
cross-checks at JSONL-validation and load time, not by the JSON Schema, so
error messages stay actionable).

Exit behavior: ``kureg-load``/``kureg-validate`` report problems and the CLI
turns ``valid: False`` into exit code 1; registry corruption, missing
databases and unsupported schema versions raise :class:`RegistryError` with
explicit messages instead of tracebacks.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .registry import check_ku_records, load_jsonl_records

try:  # optional dependency, availability checked by selftest
    import jsonschema  # type: ignore

    _HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover - exercised only without jsonschema
    _HAS_JSONSCHEMA = False

REGISTRY_SCHEMA_VERSION = 2
ID_NAMESPACE = "vault_unification-ku-v1"

DISPOSITIONS = (
    "Preserved",
    "Consolidated",
    "Contextualized",
    "Superseded",
    "Needs review",
    "Unaccounted",
)
OVERLAP_TYPES = (
    "Exact Duplicate",
    "Semantic Duplicate",
    "Partial Overlap",
    "Complementary Content",
    "Conflict or Historical Difference",
)

_DISPOSITION_LIST = ", ".join(f"'{d}'" for d in DISPOSITIONS)
_OVERLAP_LIST = ", ".join(f"'{o}'" for o in OVERLAP_TYPES)

_DDL = (
    """
    CREATE TABLE meta (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE knowledge_units (
        ku_id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        source_path TEXT NOT NULL,
        source_file_hash TEXT NOT NULL,
        source_format TEXT,
        heading_path TEXT NOT NULL,
        line_start INTEGER,
        line_end INTEGER,
        excerpt_hash TEXT,
        excerpt TEXT,
        unit_type TEXT NOT NULL,
        parent_unit_id TEXT REFERENCES knowledge_units(ku_id),
        source_context TEXT,
        disposition TEXT NOT NULL CHECK (disposition IN (%s)),
        overlap_type TEXT CHECK (overlap_type IS NULL OR overlap_type IN (%s)),
        superseded_rationale TEXT,
        verification_status TEXT NOT NULL,
        record_fingerprint TEXT NOT NULL,
        reviewer TEXT,
        review_method TEXT,
        review_date TEXT,
        created_utc TEXT NOT NULL,
        updated_utc TEXT NOT NULL
    )
    """
    % (_DISPOSITION_LIST, _OVERLAP_LIST),
    """
    CREATE TABLE concepts (
        concept_id TEXT PRIMARY KEY
    )
    """,
    """
    CREATE TABLE ku_concepts (
        ku_id TEXT NOT NULL REFERENCES knowledge_units(ku_id) ON DELETE CASCADE,
        concept_id TEXT NOT NULL REFERENCES concepts(concept_id) ON DELETE CASCADE,
        PRIMARY KEY (ku_id, concept_id)
    )
    """,
    """
    CREATE TABLE destinations (
        destination_id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL,
        heading TEXT,
        UNIQUE (path, heading)
    )
    """,
    """
    CREATE TABLE ku_destinations (
        ku_id TEXT NOT NULL REFERENCES knowledge_units(ku_id) ON DELETE CASCADE,
        destination_id INTEGER NOT NULL REFERENCES destinations(destination_id) ON DELETE CASCADE,
        PRIMARY KEY (ku_id, destination_id)
    )
    """,
    """
    CREATE TABLE ku_findings (
        ku_id TEXT NOT NULL REFERENCES knowledge_units(ku_id) ON DELETE CASCADE,
        finding_id TEXT NOT NULL,
        PRIMARY KEY (ku_id, finding_id)
    )
    """,
    """
    CREATE TABLE ku_supports (
        ku_id TEXT NOT NULL REFERENCES knowledge_units(ku_id) ON DELETE CASCADE,
        supports_ku_id TEXT NOT NULL REFERENCES knowledge_units(ku_id) ON DELETE CASCADE,
        PRIMARY KEY (ku_id, supports_ku_id)
    )
    """,
    """
    CREATE TABLE overlap_classifications (
        classification_id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL,
        topic TEXT NOT NULL,
        overlap_type TEXT NOT NULL CHECK (overlap_type IN (%s)),
        rationale TEXT NOT NULL CHECK (TRIM(rationale) != ''),
        candidate_ref TEXT,
        classified_by TEXT NOT NULL,
        method TEXT,
        date TEXT NOT NULL,
        supersedes_classification_id TEXT REFERENCES overlap_classifications(classification_id),
        review TEXT,
        record_fingerprint TEXT NOT NULL,
        applied_utc TEXT NOT NULL
    )
    """
    % (_OVERLAP_LIST,),
    """
    CREATE TABLE classification_kus (
        classification_id TEXT NOT NULL REFERENCES overlap_classifications(classification_id) ON DELETE CASCADE,
        ku_id TEXT NOT NULL REFERENCES knowledge_units(ku_id) ON DELETE CASCADE,
        PRIMARY KEY (classification_id, ku_id)
    )
    """,
    "CREATE INDEX idx_ku_disposition ON knowledge_units(disposition)",
    "CREATE INDEX idx_ku_source_path ON knowledge_units(source_path)",
    "CREATE INDEX idx_ku_source_id ON knowledge_units(source_id)",
    "CREATE INDEX idx_classification_ku ON classification_kus(ku_id)",
)


class RegistryError(Exception):
    """Raised for actionable registry failures (missing/corrupt database,
    unsupported schema version, invalid usage)."""


# ---------------------------------------------------------------------------
# canonical forms, fingerprints, stable IDs
# ---------------------------------------------------------------------------


def canonical_json(obj) -> str:
    """Deterministic JSON text: sorted keys, no whitespace padding."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def normalize_record(record: dict) -> dict:
    """Drop top-level keys whose value is None or an empty list.

    The schema treats an absent optional field, an explicit null and an
    empty list as equivalent, so all three forms must produce the same
    fingerprint (idempotent re-loads and round-trip comparisons rely on it).
    """
    return {
        key: value
        for key, value in record.items()
        if value is not None and value != []
    }


def record_fingerprint(record: dict) -> str:
    """SHA-256 over the canonical form of a full KU record."""
    return hashlib.sha256(
        canonical_json(normalize_record(record)).encode("utf-8")
    ).hexdigest()


def mint_ku_id(record: dict) -> str:
    """Mint a deterministic KU ID from source identity and content locators.

    Identity basis: source id, source file hash, heading path, line range and
    excerpt hash (excerpt text is hashed when no explicit excerpt hash was
    given). A record without any locator (no excerpt, no excerpt hash, no line
    range) cannot receive a collision-free ID and is rejected explicitly.
    """
    for field in ("source_id", "source_file_hash"):
        if not record.get(field):
            raise RegistryError(
                f"cannot mint knowledge_unit_id: required field '{field}' is missing"
            )
    has_locator = bool(
        record.get("excerpt_hash")
        or record.get("excerpt")
        or record.get("line_start") is not None
        or record.get("line_end") is not None
    )
    if not has_locator:
        raise RegistryError(
            "cannot mint knowledge_unit_id: record has no excerpt, excerpt_hash "
            "or line range; content-derived identity is impossible"
        )
    if record.get("excerpt_hash"):
        excerpt_hash = record["excerpt_hash"]
    elif record.get("excerpt"):
        excerpt_hash = hashlib.sha256(
            str(record["excerpt"]).encode("utf-8")
        ).hexdigest()
    else:
        excerpt_hash = ""
    basis = {
        "namespace": ID_NAMESPACE,
        "source_id": record["source_id"],
        "source_file_hash": record["source_file_hash"],
        "heading_path": list(record.get("heading_path") or []),
        "line_start": record.get("line_start"),
        "line_end": record.get("line_end"),
        "excerpt_hash": excerpt_hash,
    }
    digest = hashlib.sha256(canonical_json(basis).encode("utf-8")).hexdigest()[:16]
    return f"KU-{digest}"


# ---------------------------------------------------------------------------
# database plumbing
# ---------------------------------------------------------------------------


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    if not path.exists():
        raise RegistryError(
            f"registry database not found: {path} (run kureg-init first)"
        )
    try:
        conn = sqlite3.connect(str(path))
    except sqlite3.Error as exc:  # pragma: no cover - connect rarely fails
        raise RegistryError(f"cannot open registry database {path}: {exc}") from exc
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _check_registry(conn: sqlite3.Connection) -> None:
    """Verify the database is a registry with a supported schema version."""
    try:
        row = conn.execute(
            "SELECT value FROM meta WHERE key = 'registry_schema_version'"
        ).fetchone()
    except sqlite3.DatabaseError as exc:
        raise RegistryError(f"not a valid registry database: {exc}") from exc
    if row is None:
        raise RegistryError(
            "not a valid registry database: meta/registry_schema_version missing"
        )
    try:
        found = int(row["value"])
    except (TypeError, ValueError):
        raise RegistryError(
            f"corrupt registry schema version value: {row['value']!r}"
        ) from None
    if found != REGISTRY_SCHEMA_VERSION:
        raise RegistryError(
            f"unsupported registry schema version: {found} "
            f"(expected {REGISTRY_SCHEMA_VERSION}); a migration is required "
            "before this framework version can use the database"
        )


def init_registry(db_path: str | Path, *, force: bool = False) -> dict:
    """Create an empty registry database with the current schema.

    Refuses to overwrite an existing database unless ``force`` is set (the
    registry is a derived index: rebuilds delete + re-init + re-load, never
    in-place merges of unknown state).
    """
    path = Path(db_path)
    if path.exists():
        if not force:
            raise RegistryError(
                f"registry already exists: {path} (use --force to re-create)"
            )
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    created = _utcnow()
    conn = sqlite3.connect(str(path))
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        with conn:  # single transaction
            for stmt in _DDL:
                conn.execute(stmt)
            conn.executemany(
                "INSERT INTO meta (key, value) VALUES (?, ?)",
                [
                    ("registry_schema_version", str(REGISTRY_SCHEMA_VERSION)),
                    ("id_namespace", ID_NAMESPACE),
                    ("created_utc", created),
                ],
            )
    finally:
        conn.close()
    return {
        "db_path": str(path),
        "registry_schema_version": REGISTRY_SCHEMA_VERSION,
        "id_namespace": ID_NAMESPACE,
        "created_utc": created,
        "force_used": force,
    }


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------


def _schema_errors(records: list[dict], schema_path: str | Path) -> list[dict]:
    """Validate records against the KU JSON Schema; per-record error list."""
    if not _HAS_JSONSCHEMA:
        return [
            {
                "record_index": None,
                "knowledge_unit_id": None,
                "error": "jsonschema package is not installed; loading requires schema validation",
            }
        ]
    schema_file = Path(schema_path)
    if not schema_file.is_file():
        return [
            {
                "record_index": None,
                "knowledge_unit_id": None,
                "error": f"schema file not found: {schema_file}",
            }
        ]
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    validator = jsonschema.validators.validator_for(schema)(schema)
    errors: list[dict] = []
    for index, record in enumerate(records):
        for err in sorted(validator.iter_errors(record), key=lambda e: list(e.path)):
            location = ".".join(str(p) for p in err.absolute_path) or "<root>"
            errors.append(
                {
                    "record_index": index,
                    "knowledge_unit_id": record.get("knowledge_unit_id"),
                    "location": location,
                    "error": err.message,
                }
            )
    return errors


def _existing_ku_state(conn: sqlite3.Connection) -> dict[str, str]:
    rows = conn.execute(
        "SELECT ku_id, record_fingerprint FROM knowledge_units"
    ).fetchall()
    return {row["ku_id"]: row["record_fingerprint"] for row in rows}


def _insert_record(conn: sqlite3.Connection, record: dict) -> None:
    ku_id = record["knowledge_unit_id"]
    now = _utcnow()
    heading_path = canonical_json(list(record.get("heading_path") or []))
    conn.execute(
        """
        INSERT INTO knowledge_units (
            ku_id, source_id, source_path, source_file_hash, source_format,
            heading_path, line_start, line_end, excerpt_hash, excerpt,
            unit_type, parent_unit_id, source_context, disposition,
            overlap_type, superseded_rationale, verification_status,
            record_fingerprint, reviewer, review_method, review_date,
            created_utc, updated_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ku_id,
            record["source_id"],
            record["source_path"],
            record["source_file_hash"],
            record.get("source_format"),
            heading_path,
            record.get("line_start"),
            record.get("line_end"),
            record.get("excerpt_hash"),
            record.get("excerpt"),
            record["unit_type"],
            record.get("parent_unit_id"),
            record.get("source_context"),
            record["disposition"],
            record.get("overlap_type"),
            record.get("superseded_rationale"),
            canonical_json(record.get("verification_status") or {}),
            record_fingerprint(record),
            record.get("reviewer"),
            record.get("review_method"),
            record.get("review_date"),
            now,
            now,
        ),
    )
    for concept_id in sorted(set(record.get("concept_ids") or [])):
        conn.execute(
            "INSERT OR IGNORE INTO concepts (concept_id) VALUES (?)", (concept_id,)
        )
        conn.execute(
            "INSERT OR IGNORE INTO ku_concepts (ku_id, concept_id) VALUES (?, ?)",
            (ku_id, concept_id),
        )
    for destination in record.get("destinations") or []:
        conn.execute(
            "INSERT OR IGNORE INTO destinations (path, heading) VALUES (?, ?)",
            (destination["path"], destination.get("heading")),
        )
        row = conn.execute(
            "SELECT destination_id FROM destinations WHERE path = ? AND heading IS ?",
            (destination["path"], destination.get("heading")),
        ).fetchone()
        conn.execute(
            "INSERT OR IGNORE INTO ku_destinations (ku_id, destination_id) VALUES (?, ?)",
            (ku_id, row["destination_id"]),
        )
    for finding_id in sorted(set(record.get("finding_ids") or [])):
        conn.execute(
            "INSERT OR IGNORE INTO ku_findings (ku_id, finding_id) VALUES (?, ?)",
            (ku_id, finding_id),
        )
    for supports_id in sorted(set(record.get("supporting_unit_ids") or [])):
        conn.execute(
            "INSERT OR IGNORE INTO ku_supports (ku_id, supports_ku_id) VALUES (?, ?)",
            (ku_id, supports_id),
        )


def _counts_by_disposition(conn: sqlite3.Connection) -> dict:
    rows = conn.execute(
        "SELECT disposition, COUNT(*) AS n FROM knowledge_units GROUP BY disposition"
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) AS n FROM knowledge_units").fetchone()["n"]
    by_disposition = {row["disposition"]: row["n"] for row in rows}
    return {"total_kus": total, "by_disposition": by_disposition}


def load_records(
    db_path: str | Path,
    records: list[dict],
    *,
    schema_path: str | Path,
    mint_ids: bool = False,
) -> dict:
    """Validate and atomically load a batch of KU records into the registry.

    Semantics:
    - every record is schema-validated first; any invalid record aborts the
      whole batch (nothing is written);
    - cross-record rules run within the batch and, for parent/support
      references, against the union of batch + existing database IDs;
    - a record whose ID already exists with an identical fingerprint is
      skipped (idempotent re-load); the same ID with a different fingerprint
      is a conflict and aborts the batch;
    - inserts happen in one transaction with deferred foreign keys, so
      parent/support references to records later in the batch are legal.
    """
    report: dict = {
        "db_path": str(db_path),
        "records_in_batch": len(records),
        "inserted": 0,
        "skipped_identical": 0,
        "errors": [],
    }
    records = [dict(record) for record in records]  # never mutate caller data
    if mint_ids:
        for record in records:
            if not record.get("knowledge_unit_id"):
                record["knowledge_unit_id"] = mint_ku_id(record)

    conn = _connect(db_path)
    try:
        _check_registry(conn)

        for error in _schema_errors(records, schema_path):
            report["errors"].append({"stage": "schema", **error})
        if report["errors"]:
            report["valid"] = False
            return report

        existing = _existing_ku_state(conn)
        batch_ids = [record["knowledge_unit_id"] for record in records]
        known_ids = set(existing) | set(batch_ids)

        for error in check_ku_records(
            records, check_parent_refs=True, known_external_ids=set(existing)
        ):
            report["errors"].append(
                {
                    "stage": "cross_checks",
                    "record_index": error.get("record_index"),
                    "knowledge_unit_id": error.get("knowledge_unit_id"),
                    "rule": error["rule"],
                    "error": error["message"],
                }
            )

        to_insert: list[dict] = []
        seen_in_batch: set[str] = set()
        for record in records:
            ku_id = record["knowledge_unit_id"]
            if ku_id in seen_in_batch:
                continue  # duplicate_id already reported by cross-checks
            seen_in_batch.add(ku_id)
            if ku_id in existing:
                if existing[ku_id] == record_fingerprint(record):
                    report["skipped_identical"] += 1
                else:
                    report["errors"].append(
                        {
                            "stage": "conflict",
                            "knowledge_unit_id": ku_id,
                            "error": "knowledge_unit_id already exists with different content",
                        }
                    )
            else:
                to_insert.append(record)

        if report["errors"]:
            report["valid"] = False
            return report

        if to_insert:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("PRAGMA defer_foreign_keys = ON")
            try:
                for record in to_insert:
                    _insert_record(conn, record)
                conn.commit()
            except sqlite3.Error as exc:
                conn.rollback()
                raise RegistryError(
                    f"load failed and was rolled back entirely: {exc}"
                ) from exc
            report["inserted"] = len(to_insert)

        report["counts_after_load"] = _counts_by_disposition(conn)
        report["valid"] = True
        return report
    finally:
        conn.close()


def load_jsonl(
    db_path: str | Path,
    jsonl_path: str | Path,
    *,
    schema_path: str | Path,
    mint_ids: bool = False,
) -> dict:
    """Parse a JSONL batch file and load it (see :func:`load_records`)."""
    path = Path(jsonl_path)
    report: dict = {
        "db_path": str(db_path),
        "records_file": str(path),
        "records_in_batch": 0,
        "inserted": 0,
        "skipped_identical": 0,
        "errors": [],
    }
    if not path.is_file():
        report["valid"] = False
        report["errors"].append({"stage": "input", "error": f"records file not found: {path}"})
        return report
    entries, parse_errors = load_jsonl_records(path)
    for error in parse_errors:
        report["errors"].append({"stage": "parse", **error})
    records = [entry["record"] for entry in entries]
    result = load_records(db_path, records, schema_path=schema_path, mint_ids=mint_ids)
    # merge: keep parse errors alongside whatever load_records found
    merged_errors = report["errors"] + result.get("errors", [])
    result["errors"] = merged_errors
    result["records_file"] = str(path)
    if merged_errors:
        result["valid"] = False
    return result


# ---------------------------------------------------------------------------
# querying
# ---------------------------------------------------------------------------


def _row_to_record(
    row: sqlite3.Row,
    destinations: dict[str, list[dict]],
    concepts: dict[str, list[str]],
    findings: dict[str, list[str]],
    supports: dict[str, list[str]],
) -> dict:
    record: dict = {
        "knowledge_unit_id": row["ku_id"],
        "source_id": row["source_id"],
        "source_path": row["source_path"],
        "source_file_hash": row["source_file_hash"],
        "unit_type": row["unit_type"],
        "disposition": row["disposition"],
        "verification_status": json.loads(row["verification_status"]),
    }
    heading_path = json.loads(row["heading_path"])
    if heading_path:
        record["heading_path"] = heading_path
    optional_scalars = (
        "source_format",
        "line_start",
        "line_end",
        "excerpt_hash",
        "excerpt",
        "parent_unit_id",
        "source_context",
        "overlap_type",
        "superseded_rationale",
        "reviewer",
        "review_method",
        "review_date",
    )
    for field in optional_scalars:
        if row[field] is not None:
            record[field] = row[field]
    ku_id = row["ku_id"]
    if concepts.get(ku_id):
        record["concept_ids"] = concepts[ku_id]
    if destinations.get(ku_id):
        record["destinations"] = destinations[ku_id]
    if findings.get(ku_id):
        record["finding_ids"] = findings[ku_id]
    if supports.get(ku_id):
        record["supporting_unit_ids"] = supports[ku_id]
    return record


def _links_for(conn: sqlite3.Connection, ku_ids: list[str]) -> tuple:
    destinations: dict[str, list[dict]] = {}
    concepts: dict[str, list[str]] = {}
    findings: dict[str, list[str]] = {}
    supports: dict[str, list[str]] = {}

    def _chunks(items: list[str], size: int = 500):
        for start in range(0, len(items), size):
            yield items[start : start + size]

    for chunk in _chunks(ku_ids):
        marks = ",".join("?" for _ in chunk)
        for row in conn.execute(
            f"""
            SELECT kd.ku_id, d.path, d.heading
            FROM ku_destinations kd JOIN destinations d USING (destination_id)
            WHERE kd.ku_id IN ({marks}) ORDER BY d.path, d.heading
            """,
            chunk,
        ):
            destinations.setdefault(row["ku_id"], []).append(
                {"path": row["path"], "heading": row["heading"]}
            )
        for row in conn.execute(
            f"""
            SELECT ku_id, concept_id FROM ku_concepts
            WHERE ku_id IN ({marks}) ORDER BY concept_id
            """,
            chunk,
        ):
            concepts.setdefault(row["ku_id"], []).append(row["concept_id"])
        for row in conn.execute(
            f"""
            SELECT ku_id, finding_id FROM ku_findings
            WHERE ku_id IN ({marks}) ORDER BY finding_id
            """,
            chunk,
        ):
            findings.setdefault(row["ku_id"], []).append(row["finding_id"])
        for row in conn.execute(
            f"""
            SELECT ku_id, supports_ku_id FROM ku_supports
            WHERE ku_id IN ({marks}) ORDER BY supports_ku_id
            """,
            chunk,
        ):
            supports.setdefault(row["ku_id"], []).append(row["supports_ku_id"])
    return destinations, concepts, findings, supports


def query_registry(
    db_path: str | Path,
    *,
    ku_id: str | None = None,
    disposition: str | None = None,
    source_path: str | None = None,
    source_id: str | None = None,
    concept: str | None = None,
    finding: str | None = None,
    unit_type: str | None = None,
) -> dict:
    """Query the registry and reconstruct full schema-shaped KU records.

    Returns matching records (ordered by ku_id), the match count and the
    total KU count as the denominator. Filter values are validated (unknown
    dispositions are rejected as usage errors, not silent empty results).
    """
    if disposition is not None and disposition not in DISPOSITIONS:
        raise RegistryError(
            f"unknown disposition filter: {disposition!r}; valid values: {list(DISPOSITIONS)}"
        )
    conn = _connect(db_path)
    try:
        _check_registry(conn)
        where: list[str] = []
        params: list[str] = []
        if ku_id is not None:
            where.append("ku_id = ?")
            params.append(ku_id)
        if disposition is not None:
            where.append("disposition = ?")
            params.append(disposition)
        if source_path is not None:
            where.append("source_path = ?")
            params.append(source_path)
        if source_id is not None:
            where.append("source_id = ?")
            params.append(source_id)
        if unit_type is not None:
            where.append("unit_type = ?")
            params.append(unit_type)
        if concept is not None:
            where.append(
                "ku_id IN (SELECT ku_id FROM ku_concepts WHERE concept_id = ?)"
            )
            params.append(concept)
        if finding is not None:
            where.append(
                "ku_id IN (SELECT ku_id FROM ku_findings WHERE finding_id = ?)"
            )
            params.append(finding)
        clause = (" WHERE " + " AND ".join(where)) if where else ""
        total = conn.execute("SELECT COUNT(*) AS n FROM knowledge_units").fetchone()[
            "n"
        ]
        rows = conn.execute(
            f"SELECT * FROM knowledge_units{clause} ORDER BY ku_id", params
        ).fetchall()
        ku_ids = [row["ku_id"] for row in rows]
        destinations, concepts, findings_map, supports = _links_for(conn, ku_ids)
        records = [
            _row_to_record(row, destinations, concepts, findings_map, supports)
            for row in rows
        ]
        return {
            "db_path": str(db_path),
            "filters": {
                key: value
                for key, value in {
                    "ku_id": ku_id,
                    "disposition": disposition,
                    "source_path": source_path,
                    "source_id": source_id,
                    "concept": concept,
                    "finding": finding,
                    "unit_type": unit_type,
                }.items()
                if value is not None
            },
            "count": len(records),
            "total_kus": total,
            "records": records,
        }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------


def validate_registry_db(db_path: str | Path) -> dict:
    """Integrity and accounting-invariant report for a registry database.

    Errors (invalid=True): dangling references, enum violations, corrupt
    JSON, missing Superseded rationale, unsupported schema version.
    Warnings (do not invalidate): 'Needs review' units without linked
    findings, destinations not referenced by any unit.
    """
    conn = _connect(db_path)
    try:
        _check_registry(conn)
        errors: list[dict] = []
        warnings: list[dict] = []

        counts = _counts_by_disposition(conn)

        for row in conn.execute(
            "SELECT ku_id, disposition FROM knowledge_units "
            f"WHERE disposition NOT IN ({_DISPOSITION_LIST})"
        ):
            errors.append(
                {
                    "rule": "invalid_disposition",
                    "ku_id": row["ku_id"],
                    "error": f"disposition {row['disposition']!r} violates the enum",
                }
            )
        for row in conn.execute(
            "SELECT ku_id, overlap_type FROM knowledge_units "
            f"WHERE overlap_type IS NOT NULL AND overlap_type NOT IN ({_OVERLAP_LIST})"
        ):
            errors.append(
                {
                    "rule": "invalid_overlap_type",
                    "ku_id": row["ku_id"],
                    "error": f"overlap_type {row['overlap_type']!r} violates the enum",
                }
            )
        for row in conn.execute(
            "SELECT ku_id, parent_unit_id FROM knowledge_units "
            "WHERE parent_unit_id IS NOT NULL AND parent_unit_id NOT IN "
            "(SELECT ku_id FROM knowledge_units)"
        ):
            errors.append(
                {
                    "rule": "orphan_parent",
                    "ku_id": row["ku_id"],
                    "error": f"parent_unit_id {row['parent_unit_id']!r} does not exist",
                }
            )
        for row in conn.execute(
            "SELECT kd.ku_id AS ku_id, kd.destination_id AS destination_id "
            "FROM ku_destinations kd WHERE kd.ku_id NOT IN "
            "(SELECT ku_id FROM knowledge_units) OR kd.destination_id NOT IN "
            "(SELECT destination_id FROM destinations)"
        ):
            errors.append(
                {
                    "rule": "dangling_ku_destination",
                    "ku_id": row["ku_id"],
                    "error": f"destination link {row['destination_id']} dangles",
                }
            )
        for row in conn.execute(
            "SELECT ku_id, concept_id FROM ku_concepts WHERE concept_id NOT IN "
            "(SELECT concept_id FROM concepts)"
        ):
            errors.append(
                {
                    "rule": "dangling_ku_concept",
                    "ku_id": row["ku_id"],
                    "error": f"concept {row['concept_id']!r} does not exist",
                }
            )
        for row in conn.execute(
            "SELECT ku_id FROM ku_concepts WHERE ku_id NOT IN "
            "(SELECT ku_id FROM knowledge_units)"
        ):
            errors.append(
                {
                    "rule": "dangling_ku_concept",
                    "ku_id": row["ku_id"],
                    "error": "concept link references a non-existent unit",
                }
            )
        for row in conn.execute(
            "SELECT ku_id, finding_id FROM ku_findings WHERE ku_id NOT IN "
            "(SELECT ku_id FROM knowledge_units)"
        ):
            errors.append(
                {
                    "rule": "dangling_ku_finding",
                    "ku_id": row["ku_id"],
                    "error": "finding link references a non-existent unit",
                }
            )
        for row in conn.execute(
            "SELECT ku_id, supports_ku_id FROM ku_supports WHERE ku_id NOT IN "
            "(SELECT ku_id FROM knowledge_units) OR supports_ku_id NOT IN "
            "(SELECT ku_id FROM knowledge_units)"
        ):
            errors.append(
                {
                    "rule": "dangling_ku_support",
                    "ku_id": row["ku_id"],
                    "error": f"support link to {row['supports_ku_id']!r} dangles",
                }
            )
        for row in conn.execute(
            "SELECT ku_id FROM knowledge_units WHERE disposition = 'Superseded' "
            "AND (superseded_rationale IS NULL OR TRIM(superseded_rationale) = '')"
        ):
            errors.append(
                {
                    "rule": "superseded_rationale_missing",
                    "ku_id": row["ku_id"],
                    "error": "Superseded disposition requires a non-empty superseded_rationale",
                }
            )
        for row in conn.execute(
            "SELECT ku_id, verification_status FROM knowledge_units"
        ):
            try:
                json.loads(row["verification_status"])
            except (json.JSONDecodeError, TypeError):
                errors.append(
                    {
                        "rule": "corrupt_verification_status",
                        "ku_id": row["ku_id"],
                        "error": "verification_status is not valid JSON",
                    }
                )
        for row in conn.execute(
            "SELECT ku_id FROM knowledge_units WHERE disposition = 'Needs review' "
            "AND ku_id NOT IN (SELECT ku_id FROM ku_findings)"
        ):
            warnings.append(
                {
                    "rule": "needs_review_without_finding",
                    "ku_id": row["ku_id"],
                    "error": "'Needs review' unit has no linked finding; visibility relies on queries only",
                }
            )
        for row in conn.execute(
            "SELECT destination_id, path FROM destinations WHERE destination_id NOT IN "
            "(SELECT destination_id FROM ku_destinations)"
        ):
            warnings.append(
                {
                    "rule": "orphan_destination",
                    "destination_id": row["destination_id"],
                    "error": f"destination {row['path']!r} is not referenced by any unit",
                }
            )

        return {
            "db_path": str(db_path),
            "registry_schema_version": REGISTRY_SCHEMA_VERSION,
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "counts": counts,
            "overlap_classification_counts": _classification_counts(conn),
            "unaccounted_count": counts["by_disposition"].get("Unaccounted", 0),
            "needs_review_count": counts["by_disposition"].get("Needs review", 0),
            "note": "Unaccounted units block release (docs/KNOWLEDGE_AND_PROVENANCE.md invariant 2); "
            "counts are record accounting, never proof of semantic preservation",
        }
    finally:
        conn.close()


def _classification_counts(conn: sqlite3.Connection) -> dict:
    """Counting summary for overlap classification overlays."""
    total = conn.execute(
        "SELECT COUNT(*) AS n FROM overlap_classifications"
    ).fetchone()["n"]
    by_type: dict[str, int] = {}
    for row in conn.execute(
        "SELECT overlap_type, COUNT(*) AS n FROM overlap_classifications "
        "GROUP BY overlap_type ORDER BY overlap_type"
    ):
        by_type[row["overlap_type"]] = row["n"]
    classified_kus = conn.execute(
        "SELECT COUNT(DISTINCT ku_id) AS n FROM classification_kus"
    ).fetchone()["n"]
    return {
        "classifications_total": total,
        "by_overlap_type": by_type,
        "kus_participating": classified_kus,
        "note": "pair-level records (ADR-0009); per-KU overlap_type columns stay NULL "
        "because one unit can participate in multiple differently-typed pairs",
    }


# ---------------------------------------------------------------------------
# overlap classification application (CAP-013 / ADR-0009)
# ---------------------------------------------------------------------------


def _load_classification_records(
    jsonl_path: str | Path,
) -> list[dict]:
    """Read an overlap-classification JSONL file with per-line errors."""
    path = Path(jsonl_path)
    if not path.is_file():
        raise RegistryError(f"classification file not found: {path}")
    records: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RegistryError(f"cannot read classification file {path}: {exc}") from exc
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RegistryError(
                f"{path}:{lineno}: invalid JSON: {exc}"
            ) from exc
        if not isinstance(rec, dict):
            raise RegistryError(
                f"{path}:{lineno}: classification record must be a JSON object"
            )
        rec["_line"] = lineno
        records.append(rec)
    if not records:
        raise RegistryError(f"classification file {path} contains no records")
    return records


def _classification_schema_errors(
    records: list[dict],
    schema_path: str | Path,
) -> list[dict]:
    """Validate classification records against their JSON Schema."""
    if not _HAS_JSONSCHEMA:
        return [
            {
                "record_index": None,
                "classification_id": None,
                "error": "jsonschema package is not installed; applying requires schema validation",
            }
        ]
    schema_file = Path(schema_path)
    if not schema_file.is_file():
        return [
            {
                "record_index": None,
                "classification_id": None,
                "error": f"schema file not found: {schema_file}",
            }
        ]
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    validator = jsonschema.validators.validator_for(schema)(schema)
    errors: list[dict] = []
    for index, record in enumerate(records):
        candidate = {k: v for k, v in record.items() if not k.startswith("_")}
        for err in sorted(validator.iter_errors(candidate), key=lambda e: list(e.path)):
            location = ".".join(str(p) for p in err.absolute_path) or "<root>"
            errors.append(
                {
                    "record_index": index,
                    "classification_id": record.get("classification_id"),
                    "location": location,
                    "error": err.message,
                }
            )
    return errors


def _classification_cross_errors(
    records: list[dict],
    known_ku_ids: set[str],
    ku_vault: dict[str, str],
    known_classification_ids: set[str] | None = None,
) -> list[dict]:
    """Cross-checks beyond the schema: KU existence, cross-vault span."""
    errors: list[dict] = []
    known_classification_ids = known_classification_ids or set()
    for index, record in enumerate(records):
        cid = record.get("classification_id", "<missing>")
        ku_ids = record.get("ku_ids") or []
        for ku_id in ku_ids:
            if ku_id not in known_ku_ids:
                errors.append(
                    {
                        "record_index": index,
                        "classification_id": cid,
                        "error": f"ku_id {ku_id!r} is not present in the registry "
                        "(load the KU batches first)",
                    }
                )
        vaults = {ku_vault[ku_id] for ku_id in ku_ids if ku_id in ku_vault}
        if len(vaults) < 2:
            errors.append(
                {
                    "record_index": index,
                    "classification_id": cid,
                    "error": "classification must span at least two distinct vaults "
                    "(source_id prefixes); pair-level relationship (ADR-0009)",
                }
            )
        supersedes = record.get("supersedes_classification_id")
        if supersedes is not None:
            known = (
                {r.get("classification_id") for r in records}
                | known_classification_ids
            )
            if supersedes not in known:
                errors.append(
                    {
                        "record_index": index,
                        "classification_id": cid,
                        "error": f"supersedes_classification_id {supersedes!r} "
                        "does not exist (in this file or the database)",
                    }
                )
    return errors


def apply_overlap_classifications(
    db_path: str | Path,
    jsonl_path: str | Path,
    *,
    schema_path: str | Path,
) -> dict:
    """Apply append-only overlap classification records to the registry.

    Validates every record against the classification JSON Schema and
    cross-checks KU existence + cross-vault span before any write; the
    insert is a single transaction (atomic on failure). Re-applying the
    same classification_id with identical content is an idempotent no-op;
    a conflicting re-apply is an error (append-only discipline: corrections
    come as new records that supersede old ones, never edits).
    """
    records = _load_classification_records(jsonl_path)

    schema_errors = _classification_schema_errors(records, schema_path)
    if schema_errors:
        raise RegistryError(
            "classification schema violations: "
            + "; ".join(
                f"record {e['record_index']} ({e['classification_id']}) "
                f"{e['location']}: {e['error']}" if "location" in e
                else f"record {e['record_index']}: {e['error']}"
                for e in schema_errors[:3]
            )
            + (f" (+{len(schema_errors) - 3} more)" if len(schema_errors) > 3 else "")
        )

    conn = _connect(db_path)
    try:
        _check_registry(conn)
        known_rows = conn.execute(
            "SELECT ku_id, source_id FROM knowledge_units"
        ).fetchall()
        known_ku_ids = {row["ku_id"] for row in known_rows}
        ku_vault = {
            row["ku_id"]: row["source_id"].split(":", 1)[0] for row in known_rows
        }
        existing = {
            row["classification_id"]: row["record_fingerprint"]
            for row in conn.execute(
                "SELECT classification_id, record_fingerprint "
                "FROM overlap_classifications"
            )
        }
        cross_errors = _classification_cross_errors(
            records, known_ku_ids, ku_vault, set(existing)
        )
        if cross_errors:
            raise RegistryError(
                "classification cross-check failures: "
                + "; ".join(
                    f"record {e['record_index']} ({e['classification_id']}): {e['error']}"
                    for e in cross_errors[:3]
                )
                + (
                    f" (+{len(cross_errors) - 3} more)"
                    if len(cross_errors) > 3
                    else ""
                )
            )

        inserted = 0
        idempotent_skipped = 0
        with conn:  # single transaction
            # defer FK enforcement to commit so a record may supersede a
            # classification defined later in the same file
            conn.execute("PRAGMA defer_foreign_keys = ON")
            for record in records:
                cid = record["classification_id"]
                clean = {k: v for k, v in record.items() if not k.startswith("_")}
                fingerprint = canonical_json(clean)
                if cid in existing:
                    if existing[cid] == fingerprint:
                        idempotent_skipped += 1
                        continue
                    raise RegistryError(
                        f"classification {cid!r} already exists with different content; "
                        "append-only discipline: write a new record with "
                        "supersedes_classification_id instead of editing"
                    )
                conn.execute(
                    """
                    INSERT INTO overlap_classifications (
                        classification_id, task_id, topic, overlap_type, rationale,
                        candidate_ref, classified_by, method, date,
                        supersedes_classification_id, review, record_fingerprint,
                        applied_utc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cid,
                        clean.get("task_id"),
                        clean.get("topic"),
                        clean.get("overlap_type"),
                        clean.get("rationale"),
                        clean.get("candidate_ref"),
                        clean.get("classified_by"),
                        clean.get("method"),
                        clean.get("date"),
                        clean.get("supersedes_classification_id"),
                        (
                            json.dumps(clean["review"], sort_keys=True)
                            if clean.get("review") is not None
                            else None
                        ),
                        fingerprint,
                        _utcnow(),
                    ),
                )
                for ku_id in clean.get("ku_ids", []):
                    conn.execute(
                        "INSERT INTO classification_kus (classification_id, ku_id) "
                        "VALUES (?, ?)",
                        (cid, ku_id),
                    )
                inserted += 1
        return {
            "db_path": str(db_path),
            "classification_file": str(jsonl_path),
            "records_in_file": len(records),
            "inserted": inserted,
            "idempotent_skipped": idempotent_skipped,
            "rejected": 0,
        }
    finally:
        conn.close()
