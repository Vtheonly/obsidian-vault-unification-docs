"""Tests for the capability inventory and its verification logic.

The verification tests run pytest on bounded subsets (never the whole suite
and never this file) to avoid recursive test execution. The full-suite
verification is produced by ``vu capabilities --verify`` as CLI evidence.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import capabilities as caps  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestDeclaredInventory:
    def test_inventory_lists_core_capabilities(self):
        inv = caps.declared_inventory()
        ids = {c["id"] for c in inv["capabilities"]}
        for expected in [
            "CAP-000",
            "CAP-001",
            "CAP-002",
            "CAP-003",
            "CAP-004",
            "CAP-005",
            "CAP-006",
        ]:
            assert expected in ids

    def test_declared_is_marked_as_not_evidence(self):
        inv = caps.declared_inventory()
        assert "NOT evidence" in inv["note"]

    def test_planned_capabilities_have_no_tests(self):
        inv = caps.declared_inventory()
        for cap in inv["capabilities"]:
            if cap["status_declared"] == "planned":
                assert cap["tests"] == []
                assert cap["module"] is None

    def test_code_capabilities_reference_existing_test_files(self):
        inv = caps.declared_inventory()
        for cap in inv["capabilities"]:
            for test in cap.get("tests", []):
                assert (REPO_ROOT / test).is_file(), f"missing referenced test file: {test}"

    def test_no_capability_references_this_file(self):
        # referencing test_capabilities.py would recurse when --verify runs it
        inv = caps.declared_inventory()
        for cap in inv["capabilities"]:
            assert "test_capabilities.py" not in cap.get("tests", [])

    def test_every_capability_declares_limitations(self):
        inv = caps.declared_inventory()
        for cap in inv["capabilities"]:
            assert isinstance(cap["limitations"], list)
            assert cap["limitations"], f"capability {cap['id']} lacks limitations"


class TestVerifyLogic:
    """verify_capabilities logic, exercised on bounded pytest subsets."""

    def test_passing_subset_upgrades_matching_capability(self):
        result = caps.verify_capabilities(
            REPO_ROOT, test_files=["tests/test_selftest.py"]
        )
        assert result["verified"] is True
        assert result["pytest_returncode"] == 0
        by_id = {c["id"]: c for c in result["capabilities"]}
        # CAP-000 references tests/test_selftest.py -> verified
        assert by_id["CAP-000"]["status_verified"] == "implemented-and-tested"
        # CAP-002's tests were not part of the subset -> blocked, not claimed
        assert by_id["CAP-002"]["status_verified"] == "blocked"
        # planned capabilities keep their declared status
        # (CAP-011 became code-backed in BOOT-003; CAP-012 became code-backed
        # in BOOT-004 and now references real test files; CAP-013 is planned)
        assert by_id["CAP-013"]["status_verified"] == "planned"
        # code-backed capabilities whose tests were not in the subset are
        # blocked, not claimed (CAP-011 and CAP-012 now reference real files)
        assert by_id["CAP-011"]["status_verified"] == "blocked"
        assert by_id["CAP-012"]["status_verified"] == "blocked"

    def test_failing_test_prevents_upgrade(self, tmp_path, monkeypatch):
        # a failing test file that a fake capability references
        failing = tmp_path / "test_failing_fixture.py"
        failing.write_text(
            textwrap.dedent(
                """\
                def test_always_fails():
                    assert 1 == 2
                """
            ),
            encoding="utf-8",
        )
        conftest = tmp_path / "conftest.py"
        conftest.write_text("", encoding="utf-8")
        fake_cap = {
            "id": "CAP-999",
            "name": "fake capability for failure-path testing",
            "module": "vault_unification.nowhere",
            "command": "vu nothing",
            "status_declared": "implemented-and-tested",
            "tests": ["test_failing_fixture.py"],
            "limitations": [],
        }
        monkeypatch.setattr(caps, "CAPABILITIES", [fake_cap])
        result = caps.verify_capabilities(tmp_path, test_files=["test_failing_fixture.py"])
        assert result["verified"] is True  # the report itself parsed fine
        assert result["pytest_returncode"] == 1
        cap = result["capabilities"][0]
        assert cap["status_verified"] == "implemented"  # downgraded, not tested
        assert cap["verify_detail"]["failed"] == ["test_failing_fixture.py::test_always_fails"]

    def test_missing_test_files_do_not_claim_success(self, tmp_path):
        result = caps.verify_capabilities(tmp_path, test_files=["does/not/exist.py"])
        # either pytest produced no parseable report, or it failed and no
        # capability was upgraded; success must never be claimed
        if result["verified"]:
            assert result["pytest_returncode"] != 0
            for cap in result["capabilities"]:
                if cap.get("module"):
                    assert cap["status_verified"] != "implemented-and-tested"
        else:
            assert "error" in result

    def test_no_test_files_reports_error(self):
        result = caps.verify_capabilities(REPO_ROOT, test_files=[])
        assert result["verified"] is False
        assert "no test files" in result["error"]
