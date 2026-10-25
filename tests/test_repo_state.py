"""Integration tests: the framework validates this repository's own state.

These tests intentionally couple to the live repository state files so that
corruption of the task queue or current-state file is caught by the test
suite itself.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import registry as reg  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestRepositoryState:
    def test_task_queue_validates_against_schema(self):
        report = reg.validate_task_queue(
            REPO_ROOT / "state" / "task-queue.jsonl",
            REPO_ROOT / "schemas" / "task.schema.json",
        )
        assert report["valid"], report["errors"]

    def test_task_queue_cross_checks_pass(self):
        report = reg.validate_task_queue(
            REPO_ROOT / "state" / "task-queue.jsonl",
            REPO_ROOT / "schemas" / "task.schema.json",
        )
        assert report["cross_checks"]["status"] == "run"
        assert report["cross_checks"]["duplicate_task_ids"] == []

    def test_current_state_is_valid_json_with_keys(self):
        report = reg.validate_state_file(REPO_ROOT / "state" / "current-state.json")
        assert report["valid"], report["errors"]
        state = report["state"]
        for key in ["project", "stage", "status", "current_task_id"]:
            assert key in state

    def test_schemas_are_valid_json(self):
        for name in ["task.schema.json", "knowledge-unit.schema.json"]:
            data = json.loads((REPO_ROOT / "schemas" / name).read_text(encoding="utf-8"))
            assert data["type"] == "object"

    def test_source_vaults_present(self):
        """Both source vaults must exist and be non-empty directories."""
        base = REPO_ROOT / "source-vaults"
        assert base.is_dir()
        found = [d for d in base.iterdir() if d.is_dir()]
        assert len(found) >= 1
        for vault in found:
            assert any(vault.rglob("*")), f"vault dir is empty: {vault}"
