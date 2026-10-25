"""Unit tests for registry validation (schemas, malformed records, cross-checks)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import registry as reg  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_SCHEMA = REPO_ROOT / "schemas" / "task.schema.json"
KU_SCHEMA = REPO_ROOT / "schemas" / "knowledge-unit.schema.json"

VALID_TASK = {
    "task_id": "TST-001",
    "title": "Test task",
    "status": "queued",
    "inputs": ["x"],
    "outputs": ["y"],
    "acceptance_criteria": ["criterion one"],
}

VALID_KU = {
    "knowledge_unit_id": "KU-0001",
    "source_id": "SF-0001",
    "source_path": "vault/note.md",
    "source_file_hash": "0" * 64,
    "unit_type": "claim",
    "disposition": "Preserved",
    "verification_status": {},
}


def write_jsonl(path: Path, records: list[dict]) -> Path:
    with open(path, "w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec) + "\n")
    return path


class TestTaskQueueValidation:
    def test_valid_queue_passes(self, tmp_path):
        queue = write_jsonl(tmp_path / "q.jsonl", [VALID_TASK])
        report = reg.validate_task_queue(queue, TASK_SCHEMA)
        assert report["valid"], report["errors"]
        assert report["records_valid"] == 1

    def test_invalid_status_rejected(self, tmp_path):
        bad = dict(VALID_TASK, status="finished")
        queue = write_jsonl(tmp_path / "q.jsonl", [bad])
        report = reg.validate_task_queue(queue, TASK_SCHEMA)
        assert not report["valid"]
        assert any("finished" in e["error"] for e in report["errors"])

    def test_missing_required_field(self, tmp_path):
        bad = {k: v for k, v in VALID_TASK.items() if k != "acceptance_criteria"}
        queue = write_jsonl(tmp_path / "q.jsonl", [bad])
        report = reg.validate_task_queue(queue, TASK_SCHEMA)
        assert not report["valid"]
        assert any("acceptance_criteria" in e["error"] for e in report["errors"])

    def test_malformed_json_line_reports_line_number(self, tmp_path):
        queue = tmp_path / "q.jsonl"
        queue.write_text(
            json.dumps(VALID_TASK) + "\n{broken json\n" + json.dumps(VALID_TASK) + "\n",
            encoding="utf-8",
        )
        report = reg.validate_task_queue(queue, TASK_SCHEMA)
        assert not report["valid"]
        assert any(e["line"] == 2 for e in report["errors"])

    def test_unknown_dependency_detected(self, tmp_path):
        bad = dict(VALID_TASK, dependencies=["GHOST-999"])
        queue = write_jsonl(tmp_path / "q.jsonl", [bad])
        report = reg.validate_task_queue(queue, TASK_SCHEMA)
        assert not report["valid"]
        assert any("GHOST-999" in e["error"] for e in report["errors"])

    def test_duplicate_task_ids_detected(self, tmp_path):
        queue = write_jsonl(tmp_path / "q.jsonl", [VALID_TASK, VALID_TASK])
        report = reg.validate_task_queue(queue, TASK_SCHEMA)
        assert not report["valid"]
        assert any("duplicate" in e["error"] for e in report["errors"])

    def test_cross_checks_run_on_clean_records(self, tmp_path):
        other = dict(VALID_TASK, task_id="TST-002", dependencies=["TST-001"])
        queue = write_jsonl(tmp_path / "q.jsonl", [VALID_TASK, other])
        report = reg.validate_task_queue(queue, TASK_SCHEMA)
        assert report["valid"]
        assert report["cross_checks"]["status"] == "run"
        assert report["cross_checks"]["tasks_total"] == 2

    def test_missing_files_reported(self, tmp_path):
        report = reg.validate_task_queue(tmp_path / "ghost.jsonl", TASK_SCHEMA)
        assert not report["valid"]
        assert any("not found" in e["error"] for e in report["errors"])

    def test_repo_task_queue_is_valid(self):
        queue = REPO_ROOT / "state" / "task-queue.jsonl"
        report = reg.validate_task_queue(queue, TASK_SCHEMA)
        assert report["valid"], report["errors"]
        assert report["records_total"] >= 5


class TestKnowledgeUnitValidation:
    def test_valid_ku_passes(self, tmp_path):
        kus = write_jsonl(tmp_path / "ku.jsonl", [VALID_KU])
        report = reg.validate_records_against_schema(kus, KU_SCHEMA)
        assert report["valid"], report["errors"]

    def test_invalid_disposition_rejected(self, tmp_path):
        bad = dict(VALID_KU, disposition="Deleted")
        kus = write_jsonl(tmp_path / "ku.jsonl", [bad])
        report = reg.validate_records_against_schema(kus, KU_SCHEMA)
        assert not report["valid"]
        assert any("Deleted" in e["error"] for e in report["errors"])

    def test_missing_hash_rejected(self, tmp_path):
        bad = {k: v for k, v in VALID_KU.items() if k != "source_file_hash"}
        kus = write_jsonl(tmp_path / "ku.jsonl", [bad])
        report = reg.validate_records_against_schema(kus, KU_SCHEMA)
        assert not report["valid"]
        assert any("source_file_hash" in e["error"] for e in report["errors"])

    def test_unaccounted_disposition_is_schema_valid(self, tmp_path):
        bad = dict(VALID_KU, disposition="Unaccounted")
        kus = write_jsonl(tmp_path / "ku.jsonl", [bad])
        report = reg.validate_records_against_schema(kus, KU_SCHEMA)
        assert report["valid"]


class TestStateFile:
    def test_current_state_valid(self):
        report = reg.validate_state_file(REPO_ROOT / "state" / "current-state.json")
        assert report["valid"], report["errors"]

    def test_missing_state_reported(self, tmp_path):
        report = reg.validate_state_file(tmp_path / "ghost.json")
        assert not report["valid"]

    def test_invalid_json_reported(self, tmp_path):
        p = tmp_path / "state.json"
        p.write_text("{oops", encoding="utf-8")
        report = reg.validate_state_file(p)
        assert not report["valid"]
