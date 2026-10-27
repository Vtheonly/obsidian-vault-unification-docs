"""Unit tests for the machine locator (L-13 migration of the EXT-010 X2 tool)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification.locators import locate_quote, locate_quote_in_file  # noqa: E402


LINES = [
    "# Backpropagation",        # 1
    "",                         # 2
    "The gradient flows",       # 3
    "through the network.",     # 4
    "",                         # 5
    "By the chain rule:",       # 6
    "    dL/dw = dL/da * da/dw",  # 7
    "",                         # 8
    "Again: the chain rule applies.",  # 9
]


class TestLocateQuote:
    def test_unique_quote_located_with_span(self):
        r = locate_quote(LINES, "gradient flows through the network", span=(3, 4))
        assert r["ok"]
        assert (r["line_start"], r["line_end"]) == (3, 4)

    def test_multiline_quote_with_indentation_and_case_differences(self):
        r = locate_quote(LINES, "BY THE CHAIN RULE:\n    dL/dw = dL/da * da/dw", span=(6, 7))
        assert r["ok"]
        assert (r["line_start"], r["line_end"]) == (6, 7)

    def test_span_defaults_to_whole_file(self):
        r = locate_quote(LINES, "gradient flows through the network")
        assert r["ok"]
        assert (r["line_start"], r["line_end"]) == (3, 4)

    def test_quote_across_blank_lines_in_span(self):
        r = locate_quote(LINES, "through the network. By the chain rule", span=(1, 9))
        assert r["ok"]
        assert (r["line_start"], r["line_end"]) == (4, 6)

    def test_non_unique_quote_fails_loudly(self):
        # 'the chain rule' appears at line 6 and line 9 -> X2 must refuse
        r = locate_quote(LINES, "the chain rule", span=(1, 9))
        assert not r["ok"]
        assert r["occurrences"] == 2
        assert "NOT unique" in r["message"]

    def test_narrowed_span_restores_uniqueness(self):
        r = locate_quote(LINES, "the chain rule", span=(6, 6))
        assert r["ok"]
        assert (r["line_start"], r["line_end"]) == (6, 6)

    def test_missing_quote_fails_with_zero_occurrences(self):
        r = locate_quote(LINES, "no such text anywhere", span=(1, 9))
        assert not r["ok"]
        assert r["occurrences"] == 0

    def test_empty_quote_rejected(self):
        r = locate_quote(LINES, "   ")
        assert not r["ok"]
        assert "empty" in r["message"]

    def test_invalid_span_rejected(self):
        r = locate_quote(LINES, "chain rule", span=(5, 2))
        assert not r["ok"]
        assert "invalid span" in r["message"]

    def test_span_beyond_file_rejected(self):
        r = locate_quote(LINES, "chain rule", span=(1, 99))
        assert not r["ok"]
        assert "invalid span" in r["message"]

    def test_blank_span_reports_no_text(self):
        r = locate_quote(["", "", ""], "anything", span=(1, 3))
        assert not r["ok"]
        assert "no non-blank text" in r["message"]

    def test_unicode_normalization_matches(self):
        lines = ["The café\u00a0rule applies"]  # NBSP inside
        r = locate_quote(lines, "the cafe rule applies")  # NFKC folds NBSP+é? no: é stays
        # NBSP collapses to space; 'café' vs 'cafe' differ by accent -> NOT found
        assert r["occurrences"] == 0

    def test_deterministic_repeat_calls(self):
        one = locate_quote(LINES, "chain rule:", span=(6, 6))
        two = locate_quote(LINES, "chain rule:", span=(6, 6))
        assert one == two


class TestLocateQuoteInFile:
    def test_file_wrapper_locates(self, tmp_path):
        f = tmp_path / "note.md"
        f.write_text("\n".join(LINES) + "\n", encoding="utf-8")
        r = locate_quote_in_file(f, "gradient flows through the network")
        assert r["ok"]
        assert (r["line_start"], r["line_end"]) == (3, 4)

    def test_file_wrapper_missing_file(self, tmp_path):
        r = locate_quote_in_file(tmp_path / "nope.md", "x")
        assert not r["ok"]
        assert "cannot read" in r["message"]
