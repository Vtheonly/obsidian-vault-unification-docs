"""Tests for the content-statistics capability (vaultstats / CAP-015).

Covers: exact per-file counts on known content, word/fence exclusion
semantics (including unclosed fences), non-markdown text files, binary and
empty files, missing files, aggregate consistency, determinism, and negative
paths for the root argument.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from vault_unification import vaultstats as vs


class TestFileStats:
    def test_exact_counts_on_known_markdown(self, tmp_path: Path):
        note = tmp_path / "note.md"
        note.write_text(
            textwrap.dedent(
                """\
                ---
                title: T
                tags: [alpha]
                ---

                # Heading One

                alpha beta gamma

                ## Heading Two

                ```python
                x = 1
                y = 2
                ```

                $$
                E = mc^2
                $$

                Tail words here.
                """
            ),
            encoding="utf-8",
        )
        stats = vs.file_stats(note)
        assert stats["is_markdown"] is True
        assert stats["headings_total"] == 2
        assert stats["headings_by_level"] == {"h1": 1, "h2": 1}
        assert stats["code_fences"] == 1
        assert stats["code_fences_unclosed"] == 0
        assert stats["math_blocks"] == 1
        assert stats["math_blocks_unclosed"] == 0
        assert stats["frontmatter_present"] is True
        # frontmatter adds the words title/T/tags/alpha too (documented method)
        assert stats["words_total"] > stats["words_outside_fences"]
        # fence body (x = 1, y = 2) and math body excluded from prose words
        assert "x" not in str(stats["words_outside_fences"])
        assert stats["errors"] == []
        assert stats["tokens_estimate"] == stats["chars"] // 4
        assert stats["size_bytes"] == len(note.read_bytes())

    def test_words_outside_fences_excludes_fences_and_math(self, tmp_path: Path):
        note = tmp_path / "fences.md"
        note.write_text(
            "one two\n\n```python\nthree four\n```\n\nfive\n\n$$\nsix seven\n$$\n",
            encoding="utf-8",
        )
        stats = vs.file_stats(note)
        # total includes every whitespace token, including fence delimiters
        assert stats["words_total"] == 11
        # prose words: one two five (fence and math bodies excluded)
        assert stats["words_outside_fences"] == 3

    def test_unclosed_fence_extends_to_eof_and_reports_error(self, tmp_path: Path):
        note = tmp_path / "unclosed.md"
        note.write_text(
            "outside words\n\n```python\ncode words here\n",
            encoding="utf-8",
        )
        stats = vs.file_stats(note)
        assert stats["code_fences"] == 1
        assert stats["code_fences_unclosed"] == 1
        assert any("unclosed code fence" in e for e in stats["errors"])
        # unclosed fence extends to EOF: 'code words here' + delimiters excluded
        assert stats["words_total"] == 6  # outside words ```python code words here
        assert stats["words_outside_fences"] == 2

    def test_unclosed_math_block_treated_similarly(self, tmp_path: Path):
        note = tmp_path / "unclosed-math.md"
        note.write_text("a b\n\n$$\nE = x\n", encoding="utf-8")
        stats = vs.file_stats(note)
        assert stats["math_blocks_unclosed"] == 1
        assert any("unclosed math block" in e for e in stats["errors"])
        assert stats["words_total"] == 6  # a b $$ E = x
        assert stats["words_outside_fences"] == 2

    def test_non_markdown_text_gets_lexical_counts_only(self, tmp_path: Path):
        data = tmp_path / "data.txt"
        data.write_text("alpha beta\ngamma\n", encoding="utf-8")
        stats = vs.file_stats(data)
        assert stats["is_markdown"] is False
        assert stats["words_total"] == 3
        assert stats["headings_total"] == 0
        assert stats["code_fences"] == 0
        assert stats["note"] is not None
        assert "lexical counts only" in stats["note"]
        # no structure scan -> prose words equal total by definition
        assert stats["words_outside_fences"] == stats["words_total"]

    def test_binary_markdown_file_reports_error(self, tmp_path: Path):
        note = tmp_path / "binary.md"
        note.write_bytes(b"\x00\x01\x02fake")
        stats = vs.file_stats(note)
        assert stats["errors"], "binary .md must produce an explicit error"
        assert stats["words_total"] == 0

    def test_non_utf8_file_reports_error(self, tmp_path: Path):
        note = tmp_path / "latin.md"
        note.write_bytes(b"# caf\xe9 \xff\xfe broken")
        stats = vs.file_stats(note)
        assert any("UTF-8" in e for e in stats["errors"])

    def test_empty_file_reports_warning(self, tmp_path: Path):
        note = tmp_path / "empty.md"
        note.write_bytes(b"")
        stats = vs.file_stats(note)
        assert stats["is_empty"] is True
        assert any("empty" in w for w in stats["warnings"])
        assert stats["words_total"] == 0

    def test_missing_file_reports_error(self, tmp_path: Path):
        stats = vs.file_stats(tmp_path / "nope.md")
        assert stats["errors"]

    def test_links_and_tags_counted(self, fixture_vault):
        stats = vs.file_stats(fixture_vault["note_a"])
        assert stats["wikilinks"] >= 4
        assert stats["embeds"] == 1
        assert stats["md_links"] == 2
        assert stats["tags"] >= 3  # #inline + frontmatter tags (alpha, beta)
        assert stats["inline_math"] == 1


class TestStatsRoot:
    def test_aggregates_match_per_file_sum(self, fixture_vault):
        report = vs.stats_root(fixture_vault["root"])
        per = report["per_file"]
        assert report["totals"]["words_total"] == sum(s["words_total"] for s in per)
        assert report["totals"]["headings_total"] == sum(
            s["headings_total"] for s in per
        )
        assert report["totals"]["files_discovered"] == (
            len(per)
            + report["totals"]["files_skipped_nontext"]
            + len(report["unreadable_files"])
            - report["totals"]["text_files_with_errors"]
        )

    def test_binary_assets_are_explicit_not_silent(self, fixture_vault):
        report = vs.stats_root(fixture_vault["root"])
        skipped = report["skipped_nontext"]
        skipped_paths = {s["relpath"] for s in skipped}
        assert "image.png" in skipped_paths
        assert "doc.pdf" in skipped_paths
        assert report["totals"]["files_skipped_nontext"] == len(skipped)

    def test_unclosed_fixture_fence_is_flagged(self, fixture_vault):
        report = vs.stats_root(fixture_vault["root"])
        assert report["totals"]["code_fences_unclosed"] >= 1
        flagged = [s for s in report["per_file"] if s["errors"]]
        assert any("broken-fence.md" in s["path"] for s in flagged)
        # unreadable summary lists those files too
        assert any(
            "broken-fence.md" in u["relpath"] for u in report["unreadable_files"]
        )

    def test_empty_file_counted(self, fixture_vault):
        report = vs.stats_root(fixture_vault["root"])
        assert report["totals"]["empty_files"] == 1

    def test_methods_documented_in_report(self, fixture_vault):
        report = vs.stats_root(fixture_vault["root"])
        methods = report["methods"]
        assert "whitespace-separated tokens" in methods["words_total"]
        assert "chars // 4" in methods["tokens_estimate"]
        assert ".md" in methods["text_extensions"]

    def test_deterministic_output(self, fixture_vault):
        import copy
        import json

        first = vs.stats_root(fixture_vault["root"])
        second = vs.stats_root(fixture_vault["root"])
        assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
        # per-file order must be stable (sorted walk)
        paths_first = [s["path"] for s in first["per_file"]]
        paths_second = [s["path"] for s in second["per_file"]]
        assert paths_first == sorted(paths_first)
        assert copy.deepcopy(paths_first) == paths_second

    def test_empty_directory(self, tmp_path: Path):
        empty_root = tmp_path / "empty-root"
        empty_root.mkdir()
        report = vs.stats_root(empty_root)
        assert report["totals"]["files_discovered"] == 0
        assert report["per_file"] == []
        assert report["skipped_nontext"] == []
        assert report["unreadable_files"] == []

    def test_missing_root_raises(self, tmp_path: Path):
        with pytest.raises(NotADirectoryError):
            vs.stats_root(tmp_path / "missing-root")

    def test_symlink_not_followed_by_default(self, tmp_path: Path):
        real = tmp_path / "real.md"
        real.write_text("# Real\n", encoding="utf-8")
        root = tmp_path / "vault"
        root.mkdir()
        link = root / "link.md"
        link.symlink_to(real)
        report = vs.stats_root(root)
        assert report["unreadable_files"] == [
            {"relpath": "link.md", "error": "symlink not followed"}
        ]
        assert report["per_file"] == []
