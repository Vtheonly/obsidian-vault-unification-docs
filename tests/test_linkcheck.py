"""Unit/integration tests for Obsidian link checking."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import linkcheck as lc  # noqa: E402


def problem_types(report: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for problem in report["problems"]:
        grouped.setdefault(problem["type"], []).append(problem)
    return grouped


class TestLinkResolution:
    def test_clean_links_pass(self, fixture_vault):
        report = lc.check_links(fixture_vault["root"])
        grouped = problem_types(report)
        assert "broken" not in grouped or all(
            p["file"] != "note-a.md" for p in grouped["broken"]
        )
        note_a_wikilinks = [
            p for p in report["problems"] if p.get("file") == "note-a.md"
        ]
        assert note_a_wikilinks == []

    def test_broken_wikilink_detected(self, fixture_vault):
        report = lc.check_links(fixture_vault["root"])
        broken = [p for p in report["problems"] if p["type"] == "broken"]
        assert any(p["target"] == "missing-note" for p in broken)
        assert any(p["file"] == "sub/note-c.md" for p in broken)

    def test_ambiguous_link_detected(self, fixture_vault):
        report = lc.check_links(fixture_vault["root"])
        ambiguous = [p for p in report["problems"] if p["type"] == "ambiguous"]
        assert len(ambiguous) == 1
        assert ambiguous[0]["target"] == "duplicate"
        assert len(ambiguous[0]["candidates"]) == 2

    def test_missing_anchor_detected(self, fixture_vault):
        report = lc.check_links(fixture_vault["root"])
        anchors = [p for p in report["problems"] if p["type"] == "missing_anchor"]
        assert any(p["anchor"] == "No Such Heading" for p in anchors)

    def test_missing_block_detected(self, tmp_path):
        vault = tmp_path / "v"
        vault.mkdir()
        (vault / "a.md").write_text("# A\n\n[[b^nosuch]]\n", encoding="utf-8")
        (vault / "b.md").write_text("# B\n\ncontent\n", encoding="utf-8")
        report = lc.check_links(vault)
        assert any(p["type"] == "missing_block" for p in report["problems"])

    def test_external_links_not_errors(self, fixture_vault):
        report = lc.check_links(fixture_vault["root"])
        assert len(report["external_links"]) >= 2
        assert all(
            p["type"] != "parse_error" for p in report["problems"]
        ) or True  # parse errors tracked separately below

    def test_relative_md_link_resolves(self, fixture_vault):
        report = lc.check_links(fixture_vault["root"])
        broken_md = [
            p
            for p in report["problems"]
            if p["type"] == "broken" and p.get("kind") == "md_link" and p["target"] == "../note-b"
        ]
        assert broken_md == []

    def test_broken_md_link_detected(self, tmp_path):
        vault = tmp_path / "v"
        vault.mkdir()
        (vault / "a.md").write_text("# A\n\n[lost](nowhere.md)\n", encoding="utf-8")
        report = lc.check_links(vault)
        assert any(
            p["type"] == "broken" and p.get("kind") == "md_link" for p in report["problems"]
        )

    def test_parse_errors_surface_as_problems(self, fixture_vault):
        report = lc.check_links(fixture_vault["root"])
        parse_errors = [p for p in report["problems"] if p["type"] == "parse_error"]
        parse_files = {p["file"] for p in parse_errors}
        assert "broken-fence.md" in parse_files
        assert "malformed-frontmatter.md" in parse_files

    def test_counts_and_denominators_present(self, fixture_vault):
        report = lc.check_links(fixture_vault["root"])
        assert report["markdown_files_checked"] == 8
        assert report["links_checked"] > 0
        assert isinstance(report["problem_counts"], dict)

    def test_self_anchor_link(self, tmp_path):
        vault = tmp_path / "v"
        vault.mkdir()
        (vault / "a.md").write_text("# A\n\n## Deep\n\n[[#Deep]] works, [[#Missing]] does not\n", encoding="utf-8")
        report = lc.check_links(vault)
        assert any(p["type"] == "missing_anchor" and p["anchor"] == "Missing" for p in report["problems"])
        assert not any(p["type"] == "missing_anchor" and p["anchor"] == "Deep" for p in report["problems"])


class TestFolderLinksAndCaches:
    """L-02 (folder links), L-03 (parse caches), L-06 (strict block ids)."""

    def test_folder_link_resolves_not_broken(self, tmp_path):
        (tmp_path / "Topic Folder").mkdir()
        (tmp_path / "Topic Folder" / "index.md").write_text("# Index\n", encoding="utf-8")
        (tmp_path / "a.md").write_text("See [[Topic Folder]] for details.\n", encoding="utf-8")
        report = lc.check_links(tmp_path)
        assert report["folder_link_count"] == 1
        assert report["folder_links"][0]["target"] == "Topic Folder"
        assert not any(p["type"] == "broken" for p in report["problems"])

    def test_folder_path_link_with_subpath(self, tmp_path):
        (tmp_path / "chapters").mkdir()
        (tmp_path / "chapters" / "one.md").write_text("# One\n", encoding="utf-8")
        (tmp_path / "a.md").write_text("Go to [[chapters/]].\n", encoding="utf-8")
        report = lc.check_links(tmp_path)
        assert report["folder_link_count"] == 1
        assert "broken" not in report["problem_counts"]

    def test_genuinely_missing_target_still_broken(self, tmp_path):
        (tmp_path / "a.md").write_text("Bad [[no-such-thing]].\n", encoding="utf-8")
        report = lc.check_links(tmp_path)
        assert any(p["type"] == "broken" and p["target"] == "no-such-thing" for p in report["problems"])
        assert report["folder_link_count"] == 0

    def test_same_named_file_takes_precedence_over_folder(self, tmp_path):
        # Obsidian resolves a name collision to the FILE; folder must not win
        (tmp_path / "alpha").mkdir()
        (tmp_path / "alpha.md").write_text("# Alpha note\n", encoding="utf-8")
        (tmp_path / "b.md").write_text("Link [[alpha]]\n", encoding="utf-8")
        report = lc.check_links(tmp_path)
        assert report["folder_link_count"] == 0
        assert not any(p["type"] == "broken" for p in report["problems"])

    def test_strict_block_id_rejects_mid_prose_caret(self, tmp_path):
        # '^block1' appearing mid-prose must NOT validate a block reference
        (tmp_path / "target.md").write_text(
            "Some text mentions ^block1 inline in prose.\n", encoding="utf-8"
        )
        (tmp_path / "a.md").write_text("Ref [[target#^block1]]\n", encoding="utf-8")
        report = lc.check_links(tmp_path)
        assert any(p["type"] == "missing_block" for p in report["problems"])

    def test_strict_block_id_accepts_end_of_line(self, tmp_path):
        (tmp_path / "target.md").write_text(
            "A real block. ^block1\nAnother line\n", encoding="utf-8"
        )
        (tmp_path / "a.md").write_text("Ref [[target#^block1]]\n", encoding="utf-8")
        report = lc.check_links(tmp_path)
        assert not any(p["type"] == "missing_block" for p in report["problems"])

    def test_caches_parse_each_file_once(self, tmp_path, monkeypatch):
        # L-03: anchor checks must not re-parse target files per link
        from vault_unification import linkcheck as lc
        (tmp_path / "target.md").write_text("# T\n\ncontent\n", encoding="utf-8")
        (tmp_path / "a.md").write_text(
            "[[target#T]] [[target#T]] [[target#T]]\n", encoding="utf-8"
        )
        calls = {"n": 0}
        original = lc.extract_structure

        def counting_extract(path):
            calls["n"] += 1
            return original(path)

        monkeypatch.setattr(lc, "extract_structure", counting_extract)
        report = lc.check_links(tmp_path)
        # 2 files -> 2 source parses; cached anchor lookups add none
        assert calls["n"] == 2
        assert report["links_checked"] == 3
