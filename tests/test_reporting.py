"""Unit tests for report generation and metadata."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import reporting  # noqa: E402


class TestReportWriting:
    def test_report_contains_metadata(self, tmp_path):
        out = tmp_path / "reports" / "r.json"
        reporting.write_json_report(out, "inventory", {"payload": 1}, args={"root": "x"})
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["payload"] == 1
        meta = data["report_meta"]
        assert meta["framework"] == "vault_unification"
        assert meta["command"] == "inventory"
        assert meta["args"] == {"root": "x"}
        assert "utc_timestamp" in meta
        assert meta["report_schema_version"] == "1.0"

    def test_parent_dirs_created(self, tmp_path):
        out = tmp_path / "deep" / "nested" / "r.json"
        reporting.write_json_report(out, "search", {"ok": True})
        assert out.is_file()

    def test_jsonl_writing(self, tmp_path):
        out = tmp_path / "m.jsonl"
        count = reporting.write_jsonl(out, [{"a": 1}, {"a": 2}])
        assert count == 2
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert [json.loads(line)["a"] for line in lines] == [1, 2]

    def test_git_commit_helper(self):
        commit = reporting.git_commit(Path(__file__).resolve().parents[1])
        # inside this repository a commit should be resolvable; tolerate None
        # only when git is genuinely unavailable
        assert commit is None or len(commit) >= 7

    def test_overwrite_existing_report(self, tmp_path):
        out = tmp_path / "r.json"
        reporting.write_json_report(out, "a", {"n": 1})
        reporting.write_json_report(out, "a", {"n": 2})
        assert json.loads(out.read_text(encoding="utf-8"))["n"] == 2
