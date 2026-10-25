"""Tests for CAP-016: deterministic KU extraction (kuextract).

Covers ordinary, boundary and malformed segmentation inputs — including the
F-0002 unclosed-fence source defect class — plus the line-accounting
completeness invariant, record minting rules (no semantic claims), manifest
verification, failure paths, determinism and registry integration.
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import kuextract, mdextract  # noqa: E402
from vault_unification.kuregistry import init_registry, load_jsonl, validate_registry_db  # noqa: E402
from vault_unification.registry import validate_ku_file  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
KU_SCHEMA = REPO_ROOT / "schemas" / "knowledge-unit.schema.json"


def note(text: str) -> str:
    return textwrap.dedent(text).lstrip("\n")


def unit_types(segmentation: dict) -> list[str]:
    return [u["unit_type"] for u in segmentation["units"]]


def spans(segmentation: dict) -> list[tuple[int, int]]:
    return [(u["line_start"], u["line_end"]) for u in segmentation["units"]]


class TestSegmentOrdinary:
    def test_prose_paragraphs(self):
        text = note(
            """\
            First paragraph line one.
            First paragraph line two.

            Second paragraph.
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["prose", "prose"]
        assert spans(seg) == [(1, 2), (4, 4)]
        assert seg["units"][0]["excerpt"] == "First paragraph line one.\nFirst paragraph line two."
        assert seg["line_accounting"]["consistent"] is True
        assert seg["line_accounting"]["excluded_blank"] == 1

    def test_list_block_including_nested_items(self):
        text = note(
            """\
            # Title

            *   top item
                *   nested item
                *   another nested
            *   second top
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["list"]
        assert spans(seg) == [(3, 6)]
        assert "nested item" in seg["units"][0]["excerpt"]
        assert seg["units"][0]["heading_path"] == ["Title"]
        assert seg["line_accounting"]["consistent"] is True

    def test_numbered_list_with_indented_continuation(self):
        text = note(
            """\
            1.  First step
                continuation of first
            2.  Second step
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["list"]
        assert spans(seg) == [(1, 3)]

    def test_table_block(self):
        text = note(
            """\
            | A | B |
            | :---: | :---: |
            | 1 | 2 |

            After the table.
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["table", "prose"]
        assert spans(seg) == [(1, 3), (5, 5)]
        assert seg["units"][0]["excerpt"].startswith("| A | B |")

    def test_code_fence_closed(self):
        text = note(
            """\
            ```python
            def f(x):
                return x + 1
            ```
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["code_block"]
        assert spans(seg) == [(1, 4)]
        assert seg["units"][0]["excerpt"].startswith("```python")
        assert seg["units"][0]["excerpt"].endswith("```")
        assert seg["line_accounting"]["consistent"] is True

    def test_math_block_multiline_and_single_line(self):
        text = note(
            """\
            $$
            E = mc^2
            $$

            Then a paragraph.

            $$y = ax + b$$
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["math_block", "prose", "math_block"]
        assert spans(seg) == [(1, 3), (5, 5), (7, 7)]

    def test_callout_versus_plain_quote(self):
        text = note(
            """\
            > [!NOTE] Mathematical Background
            > *   arithmetic sequence note
            > *   geometric sequence note

            > a plain quoted line
            > another quoted line
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["callout", "quote"]
        assert spans(seg) == [(1, 3), (5, 6)]

    def test_frontmatter_unit_and_heading_paths(self):
        text = note(
            """\
            ---
            title: Note
            tags:
              - alpha
            ---

            # Top

            ## Section

            Content under section.
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["frontmatter", "prose"]
        assert spans(seg) == [(1, 5), (11, 11)]
        content = seg["units"][1]
        assert content["heading_path"] == ["Top", "Section"]
        assert seg["units"][0]["heading_path"] == []

    def test_excerpt_is_byte_exact_slice_of_source_lines(self):
        text = note(
            """\
            # H

            - alpha
            - beta with $x^2$ math and [[wikilink|alias]]

            Tail paragraph.
            """
        )
        lines = text.splitlines()
        seg = kuextract.segment_note(text)
        for unit in seg["units"]:
            assert unit["excerpt"] == "\n".join(lines[unit["line_start"] - 1 : unit["line_end"]])
            assert unit["excerpt_hash"] == kuextract._sha256_text(unit["excerpt"])


class TestSegmentBoundary:
    def test_empty_file(self):
        seg = kuextract.segment_note("")
        assert seg["units"] == []
        assert seg["line_accounting"]["consistent"] is True
        assert seg["line_accounting"]["lines_total"] == 0
        assert seg["warnings"]  # mdextract reports the empty file

    def test_file_with_only_headings_yields_empty_section_units(self):
        text = note(
            """\
            # Top

            ## Empty A

            ## Empty B

            # Also Empty
            """
        )
        seg = kuextract.segment_note(text)
        # Top has no content unit in its subtree; A and B empty; Also Empty empty
        assert unit_types(seg) == ["empty_section", "empty_section", "empty_section", "empty_section"]
        top = next(u for u in seg["units"] if u["excerpt"] == "# Top")
        assert top["heading_path"] == []  # parents only, the heading IS the unit
        empty_b = next(u for u in seg["units"] if u["excerpt"] == "## Empty B")
        assert empty_b["heading_path"] == ["Top"]
        assert seg["line_accounting"]["consistent"] is True

    def test_heading_with_only_deeper_content_is_not_empty(self):
        text = note(
            """\
            # Top

            ## Wrapper

            ### Deep

            actual content
            """
        )
        seg = kuextract.segment_note(text)
        assert "empty_section" not in unit_types(seg)
        assert unit_types(seg) == ["prose"]
        assert seg["units"][0]["heading_path"] == ["Top", "Wrapper", "Deep"]

    def test_heading_at_eof_without_content_is_empty_section(self):
        seg = kuextract.segment_note("# Lone Heading\n")
        assert unit_types(seg) == ["empty_section"]
        assert seg["line_accounting"]["consistent"] is True

    def test_horizontal_rules_and_blank_lines_excluded_with_reasons(self):
        text = note(
            """\
            First.

            ---

            ***
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["prose"]
        assert seg["excluded"] == {"blank": 2, "horizontal_rule": 2}
        assert "structure only" in seg["exclusion_reasons"]["horizontal_rule"]
        assert seg["line_accounting"]["consistent"] is True

    def test_blank_line_splits_list_into_two_units(self):
        text = note(
            """\
            - one

            - two
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["list", "list"]

    def test_indented_math_inside_list_splits_the_list(self):
        # mirrors the real 03.1 Regression source shape (file 01)
        text = note(
            """\
            *   **Equation:** The classic line equation.
                $$y = ax + b$$
            *   $a$: Slope (gradient)
            """
        )
        seg = kuextract.segment_note(text)
        # mdextract detects the $$...$$ line as a math block -> list splits around it
        assert unit_types(seg) == ["list", "math_block", "list"]
        assert spans(seg) == [(1, 1), (2, 2), (3, 3)]
        assert seg["units"][1]["excerpt"] == "    $$y = ax + b$$"  # exact raw slice incl. indentation
        assert seg["line_accounting"]["consistent"] is True

    def test_crlf_text_accounting_consistent(self):
        text = "Para one.\r\n\r\n- item\r\n".replace("\r\n", "\n")  # sanity baseline
        seg_a = kuextract.segment_note(text)
        assert seg_a["line_accounting"]["consistent"] is True
        crlf = "Para one.\r\n\r\n- item\r\n"
        seg_b = kuextract.segment_note(crlf)
        assert seg_b["line_accounting"]["consistent"] is True
        # CR normalization inside excerpts is a documented limitation
        assert seg_b["units"][0]["excerpt"] == "Para one."

    def test_prose_stops_at_table_and_list_starts(self):
        text = note(
            """\
            Intro line
            | T |
            |---|
            - item after table
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["prose", "table", "list"]
        assert spans(seg) == [(1, 1), (2, 3), (4, 4)]


class TestSegmentMalformed:
    def test_unclosed_fence_content_preserved_with_warning(self):
        """The F-0002 defect class: never silently drop unclosed fence content."""
        text = note(
            """\
            # Doc

            Intro paragraph.

            ```mermaid
            graph LR
                A --> B
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["prose", "code_block"]
        fence = seg["units"][1]
        assert (fence["line_start"], fence["line_end"]) == (5, 7)  # to EOF
        assert "graph LR" in fence["excerpt"]
        assert any("unclosed code fence" in w for w in seg["warnings"])
        assert ("code_block", 5, 7) in [tuple(s) for s in seg["unclosed_spans"]]
        assert seg["line_accounting"]["consistent"] is True

    def test_unclosed_math_block_preserved_with_warning(self):
        text = note(
            """\
            $$
            E = mc^2
            """
        )
        seg = kuextract.segment_note(text)
        assert unit_types(seg) == ["math_block"]
        assert spans(seg) == [(1, 2)]
        assert any("unclosed math block" in w for w in seg["warnings"])

    def test_unclosed_frontmatter_reports_warning_and_keeps_body(self):
        text = note(
            """\
            ---
            title: broken

            Body paragraph.
            """
        )
        seg = kuextract.segment_note(text)
        # frontmatter without a closing delimiter is a warning, not a drop
        assert any("frontmatter" in w for w in seg["warnings"])
        assert seg["units"], "body content must still be extracted"
        assert seg["line_accounting"]["consistent"] is True

    def test_text_before_any_newline(self):
        seg = kuextract.segment_note("single line")
        assert unit_types(seg) == ["prose"]
        assert seg["line_accounting"]["consistent"] is True

    def test_no_double_counting_between_buckets(self):
        # a heading line inside a table-looking construct still lands once
        text = note(
            """\
            | a | b |
            # Not a table row
            """
        )
        seg = kuextract.segment_note(text)
        assert seg["line_accounting"]["consistent"] is True


class TestMintedRecords:
    def _records(self, text: str) -> list[dict]:
        seg = kuextract.segment_note(text)
        return kuextract._mint_records(
            vault_id="test-vault",
            relpath="dir/note.md",
            file_hash="a" * 64,
            segmentation=seg,
            unclosed_finding=None,
        )

    def test_no_semantic_claims_in_extractor_records(self):
        records = self._records(note("# H\n\nContent here.\n"))
        # the heading has content -> no empty_section unit; one prose record
        assert len(records) == 1
        rec = records[0]
        assert rec["disposition"] == "Unaccounted"
        assert "overlap_type" not in rec
        assert "concept_ids" not in rec
        assert "destinations" not in rec
        assert rec["verification_status"]["extraction"] == "machine-segmented"
        assert rec["verification_status"]["semantic"] == "pending"

    def test_source_identity_fields(self):
        rec = self._records(note("Text.\n"))[0]
        assert rec["source_id"] == "test-vault:dir/note.md"
        assert rec["source_path"] == "dir/note.md"
        assert rec["source_file_hash"] == "a" * 64
        assert rec["source_format"] == "markdown"

    def test_stable_ids_across_identical_segmentations(self):
        a = self._records(note("# H\n\nOne.\n\n- x\n"))
        b = self._records(note("# H\n\nOne.\n\n- x\n"))
        assert [r["knowledge_unit_id"] for r in a] == [r["knowledge_unit_id"] for r in b]

    def test_unclosed_finding_links_only_affected_unit(self):
        text = note("Intro.\n\n```python\nx = 1\n")  # unclosed fence
        seg = kuextract.segment_note(text)
        records = kuextract._mint_records(
            vault_id="v",
            relpath="n.md",
            file_hash="b" * 64,
            segmentation=seg,
            unclosed_finding="F-0002",
        )
        with_finding = [r for r in records if r.get("finding_ids")]
        assert len(with_finding) == 1
        assert with_finding[0]["unit_type"] == "code_block"
        assert with_finding[0]["finding_ids"] == ["F-0002"]

    def test_records_validate_against_schema(self, tmp_path: Path):
        text = note(
            """\
            ---
            title: T
            ---

            # H

            Paragraph.

            - list
            - items

            | a | b |
            |---|---|

            ```python
            x = 1
            ```

            $$
            E = x
            $$

            > [!TIP]
            > callout body

            > plain quote

            ## Empty
            """
        )
        records = self._records(text)
        batch = tmp_path / "batch.jsonl"
        batch.write_text(
            "".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8"
        )
        report = validate_ku_file(batch, KU_SCHEMA)
        assert report["valid"], report["errors"]
        by_type = {r["unit_type"] for r in records}
        assert by_type == {
            "frontmatter",
            "prose",
            "list",
            "table",
            "code_block",
            "math_block",
            "callout",
            "quote",
            "empty_section",
        }


# ---------------------------------------------------------------------------
# extract_scope (integration with manifest, hashing, failures, registry)
# ---------------------------------------------------------------------------


def build_vault(tmp_path: Path) -> tuple[Path, Path, Path]:
    """A small synthetic source vault + baseline manifest; returns (root, manifest, kus_out)."""
    root = tmp_path / "src-vault"
    (root / "notes").mkdir(parents=True)
    (root / "notes" / "a.md").write_text(
        note(
            """\
            # A

            Content of A with $math$ and [[wikilink]].

            - item one
            - item two
            """
        ),
        encoding="utf-8",
    )
    (root / "notes" / "b.md").write_text(
        note(
            """\
            ---
            aliases: [bee]
            ---

            # B

            Intro.

            ```python
            x = 42
            """
        ),
        encoding="utf-8",  # unclosed fence on purpose (F-0002 class)
    )
    import hashlib as _hashlib

    manifest_lines = []
    for rel in ["notes/a.md", "notes/b.md"]:
        digest = _hashlib.sha256((root / rel).read_bytes()).hexdigest()
        manifest_lines.append(json.dumps({"relpath": rel, "sha256": digest, "size": len((root / rel).read_bytes())}))
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    return root, manifest, tmp_path / "batch.jsonl"


class TestExtractScope:
    def test_happy_path_counts_and_outcomes(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        result = kuextract.extract_scope(
            root, "notes", "vault-x", manifest, out, kus_schema=KU_SCHEMA
        )
        assert result["ok"] is True
        assert result["denominators"]["files_in_scope"] == 2
        assert result["denominators"]["files_extracted"] == 2
        assert result["denominators"]["files_failed"] == 0
        outcomes = {o["relpath"]: o["outcome"] for o in result["file_outcomes"]}
        assert outcomes == {"notes/a.md": "extracted", "notes/b.md": "extracted"}
        b_outcome = next(o for o in result["file_outcomes"] if o["relpath"] == "notes/b.md")
        assert any("unclosed code fence" in w for w in b_outcome["warnings"])
        assert b_outcome["line_accounting"]["consistent"] is True
        assert result["batch_validation"]["valid"] is True

    def test_every_unit_unaccounted_and_locator_complete(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        kuextract.extract_scope(root, "notes", "vault-x", manifest, out, kus_schema=KU_SCHEMA)
        records = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
        assert records
        for rec in records:
            assert rec["disposition"] == "Unaccounted"
            assert rec["line_start"] >= 1 and rec["line_end"] >= rec["line_start"]
            assert rec["excerpt"] and rec["excerpt_hash"]
            assert rec["knowledge_unit_id"].startswith("KU-")
            assert "overlap_type" not in rec and "destinations" not in rec

    def test_deterministic_byte_identical_rerun(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        kuextract.extract_scope(root, "notes", "vault-x", manifest, out, kus_schema=KU_SCHEMA)
        first = out.read_bytes()
        out2 = tmp_path / "batch2.jsonl"
        kuextract.extract_scope(root, "notes", "vault-x", manifest, out2, kus_schema=KU_SCHEMA)
        assert out2.read_bytes() == first

    def test_unclosed_finding_propagates_to_batch(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        kuextract.extract_scope(
            root, "notes", "vault-x", manifest, out,
            kus_schema=KU_SCHEMA, unclosed_finding="F-0002",
        )
        records = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
        linked = [r for r in records if r.get("finding_ids") == ["F-0002"]]
        assert len(linked) == 1 and linked[0]["unit_type"] == "code_block"

    def test_hash_mismatch_fails(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        (root / "notes" / "a.md").write_text("# A tampered\n", encoding="utf-8")
        result = kuextract.extract_scope(root, "notes", "vault-x", manifest, out, kus_schema=KU_SCHEMA)
        assert result["ok"] is False
        bad = next(o for o in result["file_outcomes"] if o["relpath"] == "notes/a.md")
        assert bad["outcome"] == "failed_hash_mismatch"

    def test_disk_file_missing_from_manifest_fails(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        (root / "notes" / "new.md").write_text("# New\n", encoding="utf-8")
        result = kuextract.extract_scope(root, "notes", "vault-x", manifest, out, kus_schema=KU_SCHEMA)
        assert result["ok"] is False
        assert any(
            o["outcome"] == "failed_not_in_manifest" and o["relpath"] == "notes/new.md"
            for o in result["file_outcomes"]
        )

    def test_manifest_file_missing_on_disk_fails(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        (root / "notes" / "b.md").unlink()
        result = kuextract.extract_scope(root, "notes", "vault-x", manifest, out, kus_schema=KU_SCHEMA)
        assert result["ok"] is False
        assert any(
            o["outcome"] == "failed_missing_on_disk" and o["relpath"] == "notes/b.md"
            for o in result["file_outcomes"]
        )

    def test_non_markdown_file_excluded_explicitly(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        png = root / "notes" / "pic.png"
        png.write_bytes(b"\x89PNG\r\n\x1a\n")
        import hashlib as _hashlib

        manifest_records = [
            json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()
        ]
        manifest_records.append(
            {
                "relpath": "notes/pic.png",
                "sha256": _hashlib.sha256(png.read_bytes()).hexdigest(),
                "size": len(png.read_bytes()),
            }
        )
        manifest.write_text(
            "".join(json.dumps(r) + "\n" for r in manifest_records), encoding="utf-8"
        )
        result = kuextract.extract_scope(root, "notes", "vault-x", manifest, out, kus_schema=KU_SCHEMA)
        assert result["ok"] is True  # explicit exclusion is a valid outcome, not a failure
        pic = next(o for o in result["file_outcomes"] if o["relpath"] == "notes/pic.png")
        assert pic["outcome"] == "excluded_non_markdown"
        assert result["denominators"]["files_in_scope"] == 3
        assert result["denominators"]["files_excluded"] == 1

    def test_non_utf8_file_fails_explicitly(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        bad = root / "notes" / "latin.md"
        bad.write_bytes(b"# \xff\xfe broken\n")
        import hashlib as _hashlib

        manifest_records = [
            json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()
        ]
        manifest_records.append(
            {
                "relpath": "notes/latin.md",
                "sha256": _hashlib.sha256(bad.read_bytes()).hexdigest(),
                "size": len(bad.read_bytes()),
            }
        )
        manifest.write_text(
            "".join(json.dumps(r) + "\n" for r in manifest_records), encoding="utf-8"
        )
        result = kuextract.extract_scope(root, "notes", "vault-x", manifest, out, kus_schema=KU_SCHEMA)
        assert result["ok"] is False
        latin = next(o for o in result["file_outcomes"] if o["relpath"] == "notes/latin.md")
        assert latin["outcome"] == "failed_encoding"

    def test_single_file_scope(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        result = kuextract.extract_scope(
            root, "notes/a.md", "vault-x", manifest, out, kus_schema=KU_SCHEMA
        )
        assert result["ok"] is True
        assert result["denominators"]["files_in_scope"] == 1
        assert result["records_written"] > 0

    def test_whole_vault_scope_dot(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        # manifest only covers notes/*; the manifest itself is not under root
        result = kuextract.extract_scope(root, ".", "vault-x", manifest, out, kus_schema=KU_SCHEMA)
        assert result["ok"] is True
        assert result["denominators"]["files_in_scope"] == 2

    def test_empty_scope_dir_is_actionable_error(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        (root / "empty-dir").mkdir()
        with pytest.raises(kuextract.ExtractionError, match="no files"):
            kuextract.extract_scope(root, "empty-dir", "vault-x", manifest, out, kus_schema=KU_SCHEMA)

    def test_missing_scope_raises(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        with pytest.raises(kuextract.ExtractionError, match="does not exist"):
            kuextract.extract_scope(root, "nope", "vault-x", manifest, out, kus_schema=KU_SCHEMA)

    def test_scope_with_dotdot_raises(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        with pytest.raises(kuextract.ExtractionError):
            kuextract.extract_scope(root, "../outside", "vault-x", manifest, out, kus_schema=KU_SCHEMA)

    def test_absolute_scope_raises(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        with pytest.raises(kuextract.ExtractionError):
            kuextract.extract_scope(root, str(tmp_path), "vault-x", manifest, out, kus_schema=KU_SCHEMA)

    def test_bad_manifest_raises(self, tmp_path: Path):
        root, _manifest, out = build_vault(tmp_path)
        broken = tmp_path / "broken.jsonl"
        broken.write_text("not json\n", encoding="utf-8")
        with pytest.raises(kuextract.ExtractionError, match="manifest"):
            kuextract.extract_scope(root, "notes", "vault-x", broken, out, kus_schema=KU_SCHEMA)

    def test_batch_loads_into_registry_and_validates(self, tmp_path: Path):
        root, manifest, out = build_vault(tmp_path)
        kuextract.extract_scope(root, "notes", "vault-x", manifest, out, kus_schema=KU_SCHEMA)
        db = tmp_path / "kureg.db"
        init_registry(db)
        load_report = load_jsonl(db, out, schema_path=KU_SCHEMA)
        assert load_report["valid"] is True, load_report["errors"]
        assert load_report["inserted"] == load_report["records_in_batch"]
        # idempotent re-load
        reload_report = load_jsonl(db, out, schema_path=KU_SCHEMA)
        assert reload_report["valid"] is True
        assert reload_report["inserted"] == 0
        assert reload_report["skipped_identical"] == load_report["inserted"]
        validation = validate_registry_db(db)
        assert validation["valid"] is True
        assert validation["counts"]["total_kus"] == load_report["inserted"]
        assert validation["counts"]["by_disposition"].get("Unaccounted") == load_report["inserted"]


class TestMdextractAuthority:
    def test_segmentation_agrees_with_mdextract_construct_spans(self, tmp_path: Path):
        text = note(
            """\
            # T

            ```js
            const x = 1;
            ```

            $$
            z = y
            $$
            """
        )
        path = tmp_path / "n.md"
        path.write_text(text, encoding="utf-8")
        structure = mdextract.extract_structure(path)
        seg = kuextract.segment_note(text)
        fence_units = [u for u in seg["units"] if u["unit_type"] == "code_block"]
        math_units = [u for u in seg["units"] if u["unit_type"] == "math_block"]
        assert (fence_units[0]["line_start"], fence_units[0]["line_end"]) == (
            structure["code_fences"][0]["start_line"],
            structure["code_fences"][0]["end_line"],
        )
        assert (math_units[0]["line_start"], math_units[0]["line_end"]) == (
            structure["math_blocks"][0]["start_line"],
            structure["math_blocks"][0]["end_line"],
        )
