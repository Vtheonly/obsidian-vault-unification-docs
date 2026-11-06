"""Unit tests for the environment self-test."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import selftest  # noqa: E402


class TestSelftest:
    def test_selftest_runs_and_passes_mandatory(self):
        result = selftest.run_selftest()
        assert result["ok"] is True
        assert result["mandatory_checks_passed"] is True
        assert isinstance(result["optional_missing"], list)

    def test_checks_have_required_flag(self):
        result = selftest.run_selftest()
        for check in result["checks"]:
            assert "name" in check and "required" in check and "ok" in check

    def test_platform_info_present(self):
        result = selftest.run_selftest()
        assert result["platform"]["python"]
        assert result["platform"]["executable"]

    def test_optional_dependencies_reported(self):
        result = selftest.run_selftest()
        names = {c["name"] for c in result["checks"]}
        assert "optional:jsonschema" in names
        assert "optional:yaml" in names
        assert "optional:pytest" in names
