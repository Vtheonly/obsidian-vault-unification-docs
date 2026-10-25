"""Unit tests for search modes and term statistics."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import search as se  # noqa: E402


class TestSearchModes:
    def test_exact_case_sensitive(self, fixture_vault):
        result = se.search_term(fixture_vault["root"], "Note B", "exact")
        # only the heading in note-b.md; wikilinks use lowercase note-b
        assert result["match_count"] == 1

    def test_exact_misses_other_case(self, fixture_vault):
        result = se.search_term(fixture_vault["root"], "note b", "exact")
        assert result["match_count"] == 0

    def test_case_insensitive_matches(self, fixture_vault):
        result = se.search_term(fixture_vault["root"], "note b", "case-insensitive")
        # "Note B" heading matches case-insensitively
        assert result["match_count"] >= 1
        assert result["files_with_matches"] == ["note-b.md"]

    def test_normalized_matches_whitespace_and_case(self, tmp_path):
        p = tmp_path / "n.md"
        p.write_text("The  Convolution   layer\nworks well\n", encoding="utf-8")
        result = se.search_term(tmp_path, "the convolution layer", "normalized")
        assert result["match_count"] == 1

    def test_locations_are_line_accurate(self, fixture_vault):
        result = se.search_term(fixture_vault["root"], "missing-note", "exact")
        assert all(m["file"] == "sub/note-c.md" for m in result["matches"])
        assert all(isinstance(m["line"], int) for m in result["matches"])

    def test_binary_files_skipped_explicitly(self, fixture_vault, binary_file, tmp_path):
        (fixture_vault["root"] / "blob.bin").write_bytes(binary_file.read_bytes())
        result = se.search_term(fixture_vault["root"], "Note", "case-insensitive")
        assert "blob.bin" not in [m["file"] for m in result["matches"]]
        # .bin is not a text extension -> skipped as nontext
        assert result["scope"]["files_skipped_nontext"] >= 1

    def test_scope_and_denominators_reported(self, fixture_vault):
        result = se.search_term(fixture_vault["root"], "the", "case-insensitive")
        assert result["scope"]["files_scanned"] == 8
        assert result["scope"]["files_skipped_nontext"] == 2
        assert result["scope"]["text_extensions"]

    def test_empty_term_rejected(self, fixture_vault):
        with pytest.raises(ValueError):
            se.search_term(fixture_vault["root"], "", "exact")

    def test_unknown_mode_rejected(self, fixture_vault):
        with pytest.raises(ValueError):
            se.search_term(fixture_vault["root"], "x", "fuzzy")

    def test_missing_root_raises(self, tmp_path):
        with pytest.raises(NotADirectoryError):
            se.search_term(tmp_path / "nope", "x", "exact")


class TestTermStats:
    def test_counts_with_aliases(self, tmp_path):
        p = tmp_path / "t.md"
        p.write_text(
            "CNN and convnet and convolutional network and CNN again\n",
            encoding="utf-8",
        )
        result = se.term_stats(
            tmp_path,
            ["CNN"],
            aliases={"CNN": ["convnet", "convolutional network"]},
        )
        assert result["stats"]["CNN"]["total_count"] == 4
        assert result["stats"]["CNN"]["files_with_term"] == 1

    def test_per_file_distribution(self, tmp_path):
        (tmp_path / "a.md").write_text("alpha beta alpha\n", encoding="utf-8")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "b.md").write_text("alpha only\n", encoding="utf-8")
        result = se.term_stats(tmp_path, ["alpha", "gamma"])
        assert result["stats"]["alpha"]["per_file"] == {"a.md": 2, "sub/b.md": 1}
        assert result["stats"]["gamma"]["total_count"] == 0
        assert result["denominator"]["files_scanned"] == 2

    def test_method_is_stated(self, tmp_path):
        result = se.term_stats(tmp_path, ["x"])
        assert "case-insensitive" in result["method"]
