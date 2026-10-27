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


class TestPhraseSearch:
    """L-01 fix: multi-line phrase search with span locators."""

    def test_phrase_spanning_lines_found(self, tmp_path):
        (tmp_path / "note.md").write_text(
            "# Title\n\nThe gradient\nflows through\nthe network.\n", encoding="utf-8"
        )
        result = se.search_phrase(tmp_path, "gradient flows through the network")
        assert result["mode"] == "phrase"
        assert result["match_count"] == 1
        m = result["matches"][0]
        assert m["file"] == "note.md"
        assert m["line_start"] == 3
        assert m["line_end"] == 5

    def test_phrase_across_blank_lines_and_indentation(self, tmp_path):
        (tmp_path / "note.md").write_text(
            "start of\n\n   the sentence\n\tcontinues here\n", encoding="utf-8"
        )
        result = se.search_phrase(tmp_path, "start of the sentence continues here")
        assert result["match_count"] == 1
        m = result["matches"][0]
        assert (m["line_start"], m["line_end"]) == (1, 4)

    def test_phrase_normalization_case_and_unicode(self, tmp_path):
        (tmp_path / "note.md").write_text(
            "The CHAIN\u00a0Rule applies\n", encoding="utf-8"  # NBSP collapses
        )
        result = se.search_phrase(tmp_path, "chain rule applies")
        assert result["match_count"] == 1

    def test_phrase_missing_returns_zero(self, tmp_path):
        (tmp_path / "note.md").write_text("nothing relevant\n", encoding="utf-8")
        result = se.search_phrase(tmp_path, "totally absent phrase")
        assert result["match_count"] == 0
        assert result["files_with_matches"] == []

    def test_phrase_empty_rejected(self, tmp_path):
        import pytest as _pytest
        with _pytest.raises(ValueError):
            se.search_phrase(tmp_path, "   ")

    def test_phrase_missing_root_raises(self, tmp_path):
        import pytest as _pytest
        with _pytest.raises(NotADirectoryError):
            se.search_phrase(tmp_path / "nope", "x y")

    def test_phrase_scope_denominators(self, tmp_path):
        (tmp_path / "a.md").write_text("alpha beta\n", encoding="utf-8")
        # a text-extension file with binary content is skipped as binary
        (tmp_path / "b.md").write_bytes(b"\x00\x01alpha beta\x00")
        result = se.search_phrase(tmp_path, "alpha beta")
        assert result["scope"]["files_scanned"] == 1
        assert result["scope"]["files_skipped_binary"] == 1
        assert result["match_count"] == 1


class TestWordBoundaryTermStats:
    """L-07 fix: word-boundary counting aligned with CAP-013 semantics."""

    def test_word_boundary_rejects_substring_false_positives(self, tmp_path):
        (tmp_path / "n.md").write_text(
            "bridge ridge\nridge: the ridge model\n", encoding="utf-8"
        )
        substring = se.term_stats(tmp_path, ["ridge"], match_mode="substring")
        wb = se.term_stats(tmp_path, ["ridge"], match_mode="word-boundary")
        # substring mode counts 'ridge' inside 'bridge' too: 4 total
        assert substring["stats"]["ridge"]["total_count"] == 4
        # word-boundary mode rejects the 'bridge' occurrence: 3 total
        assert wb["stats"]["ridge"]["total_count"] == 3

    def test_word_boundary_mode_stated_in_method(self, tmp_path):
        (tmp_path / "n.md").write_text("ridge\n", encoding="utf-8")
        wb = se.term_stats(tmp_path, ["ridge"], match_mode="word-boundary")
        assert wb["match_mode"] == "word-boundary"
        assert "word-boundary" in wb["method"]

    def test_word_boundary_matches_punctuation_adjacent(self, tmp_path):
        (tmp_path / "n.md").write_text("(ridge) ridge: ridge,\n", encoding="utf-8")
        wb = se.term_stats(tmp_path, ["ridge"], match_mode="word-boundary")
        assert wb["stats"]["ridge"]["total_count"] == 3

    def test_word_boundary_aliases_counted(self, tmp_path):
        (tmp_path / "n.md").write_text(
            "gradient descent and GD both appear\n", encoding="utf-8"
        )
        wb = se.term_stats(
            tmp_path, ["gradient descent"], aliases={"gradient descent": ["GD"]},
            match_mode="word-boundary",
        )
        assert wb["stats"]["gradient descent"]["total_count"] == 2

    def test_default_mode_backward_compatible(self, tmp_path):
        (tmp_path / "n.md").write_text("bridge ridge\n", encoding="utf-8")
        default = se.term_stats(tmp_path, ["ridge"])
        assert default["method"].startswith("case-insensitive substring")
        assert default["stats"]["ridge"]["total_count"] == 2

    def test_unknown_match_mode_rejected(self, tmp_path):
        import pytest as _pytest
        with _pytest.raises(ValueError):
            se.term_stats(tmp_path, ["x"], match_mode="regex")

    def test_boundary_pattern_shared_with_overlap(self):
        # L-07: one shared authority - overlap must delegate to search
        from vault_unification import overlap as overlap_mod
        assert overlap_mod._boundary_pattern("x").pattern == se.boundary_pattern("x").pattern
