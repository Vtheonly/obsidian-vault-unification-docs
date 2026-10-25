"""Unit tests for Markdown structure extraction, including malformed input."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification.mdextract import extract_structure, heading_path  # noqa: E402


class TestHeadings:
    def test_heading_extraction(self, fixture_vault):
        result = extract_structure(fixture_vault["note_a"])
        headings = [(h["level"], h["text"]) for h in result["headings"]]
        assert (1, "Note A Title") in headings
        assert (2, "Section One") in headings
        assert (3, "Subsection") in headings

    def test_heading_lines_are_one_based(self, fixture_vault):
        result = extract_structure(fixture_vault["note_b"])
        assert result["headings"][0] == {"level": 1, "text": "Note B", "line": 1}

    def test_heading_path_helper(self, fixture_vault):
        result = extract_structure(fixture_vault["note_a"])
        deep = heading_path(result["headings"], 40)
        assert deep[:2] == ["Note A Title", "Section One"]


class TestFrontmatter:
    def test_valid_frontmatter(self, fixture_vault):
        result = extract_structure(fixture_vault["note_a"])
        assert result["frontmatter"] == {"title": "Note A", "tags": ["alpha", "beta"]}
        assert result["frontmatter_span"] == [1, 6]  # includes closing delimiter
        assert not result["errors"]

    def test_malformed_frontmatter_reports_error(self, fixture_vault):
        result = extract_structure(fixture_vault["malformed_frontmatter"])
        assert any("frontmatter YAML parse error" in e for e in result["errors"])
        assert result["frontmatter"] is None

    def test_frontmatter_without_close_is_warning(self, tmp_path):
        p = tmp_path / "no-close.md"
        p.write_text("---\ntitle: X\n", encoding="utf-8")
        result = extract_structure(p)
        assert any("no closing delimiter" in w for w in result["warnings"])

    def test_frontmatter_tags_collected(self, fixture_vault):
        result = extract_structure(fixture_vault["note_a"])
        fm_tags = [t["tag"] for t in result["tags"] if t.get("source") == "frontmatter"]
        assert fm_tags == ["alpha", "beta"]


class TestCodeFences:
    def test_closed_fence(self, fixture_vault):
        result = extract_structure(fixture_vault["note_a"])
        fences = result["code_fences"]
        assert len(fences) == 1
        assert fences[0]["info"] == "python"
        assert fences[0]["closed"] is True
        assert fences[0]["body_lines"] == 2

    def test_unclosed_fence_is_error(self, fixture_vault):
        result = extract_structure(fixture_vault["broken_fence"])
        assert any("unclosed code fence" in e for e in result["errors"])
        assert result["code_fences"][0]["closed"] is False

    def test_tilde_fence(self, tmp_path):
        p = tmp_path / "tilde.md"
        p.write_text("# T\n\n~~~bash\necho hi\n~~~\n", encoding="utf-8")
        result = extract_structure(p)
        assert len(result["code_fences"]) == 1
        assert result["code_fences"][0]["info"] == "bash"
        assert result["code_fences"][0]["closed"] is True

    def test_no_links_inside_fences(self, tmp_path):
        p = tmp_path / "fence-links.md"
        p.write_text(
            "# T\n\n```text\n[[not-a-link]]\n#not-a-tag\n```\n",
            encoding="utf-8",
        )
        result = extract_structure(p)
        assert result["wikilinks"] == []
        assert result["tags"] == []


class TestMath:
    def test_display_math_block(self, fixture_vault):
        result = extract_structure(fixture_vault["note_a"])
        blocks = result["math_blocks"]
        assert len(blocks) == 1
        assert blocks[0]["closed"] is True

    def test_inline_math_counted(self, fixture_vault):
        result = extract_structure(fixture_vault["note_a"])
        assert result["inline_math_count"] >= 1

    def test_unclosed_math_is_error(self, tmp_path):
        p = tmp_path / "unclosed-math.md"
        p.write_text("# T\n\n$$\n\\frac{1}{2}\n", encoding="utf-8")
        result = extract_structure(p)
        assert any("unclosed math block" in e for e in result["errors"])


class TestLinks:
    def test_wikilinks_extracted(self, fixture_vault):
        result = extract_structure(fixture_vault["note_a"])
        targets = [w["target"] for w in result["wikilinks"]]
        # plain + aliased + anchor + block variants all target note-b
        assert targets.count("note-b") == 4

    def test_alias_and_anchor_and_block(self, fixture_vault):
        result = extract_structure(fixture_vault["note_a"])
        by_target = {}
        for w in result["wikilinks"]:
            by_target.setdefault(w["target"], []).append(w)
        aliased = [w for w in by_target["note-b"] if w["alias"]]
        assert any(w["alias"] == "display name" for w in aliased)
        assert any(w["anchor"] == "Deep Heading" for w in by_target["note-b"])
        assert any(w["block"] == "blockref" for w in by_target["note-b"])

    def test_embeds_separated_from_wikilinks(self, fixture_vault):
        result = extract_structure(fixture_vault["note_a"])
        assert len(result["embeds"]) == 1
        assert result["embeds"][0]["target"] == "image.png"

    def test_md_links_classified(self, fixture_vault):
        result = extract_structure(fixture_vault["note_c"])
        kinds = {link["kind"] for link in result["md_links"]}
        assert kinds == {"external", "internal"}  # ../note-b is internal


class TestEdgeCases:
    def test_empty_file_reported(self, fixture_vault):
        result = extract_structure(fixture_vault["empty"])
        assert result["is_empty"] is True
        assert any("file is empty" in w for w in result["warnings"])

    def test_missing_file_is_error(self, tmp_path):
        result = extract_structure(tmp_path / "ghost.md")
        assert result["errors"] == ["file does not exist"]

    def test_directory_rejected(self, tmp_path):
        result = extract_structure(tmp_path)
        assert any("not a regular file" in e for e in result["errors"])

    def test_invalid_utf8_reported(self, tmp_path):
        p = tmp_path / "latin.md"
        p.write_bytes(b"# Caf\xe9\n")
        result = extract_structure(p)
        assert any("UTF-8 decode error" in e for e in result["errors"])

    def test_inline_tags_extracted(self, fixture_vault):
        result = extract_structure(fixture_vault["note_a"])
        inline = [t["tag"] for t in result["tags"] if t.get("source") != "frontmatter"]
        assert "inline" in inline
