"""Unit/integration tests for the mechanical See-Also carry-over audit
(AUDIT-012; closes the F-0035 remaining risk)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import seealsoaudit as sa  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(tmp_path: Path) -> dict:
    """A miniature two-source-vault + unified-vault fixture.

    Source targets and expected verdicts:
    - "Self-Attention"            carried_over   (bare link in dest See Also)
    - "KV Cache Mechanics"        dropped        (F-0035 regression shape:
                                                 topic exists, dest lacks link)
    - "Planned Note"              target_absent_from_unified (phantom, no stem)
    - "Probability Essentials"    carried_over   (phantom in source, unified
                                                 stem match, path-form link)
    - "sub/Multi Target"          ambiguous_source_target (two source files
                                                 with same stem, divergent maps)
    - inline "*See also:* [[Backprop]]"  carried_over (course vault, alias link)
    """
    master = tmp_path / "master"
    course = tmp_path / "course"
    out = tmp_path / "unified"

    _write(
        master / "attn/Multi-Head Attention.md",
        "# MHA\n\nbody\n\n## See Also\n\n"
        "- [[Self-Attention]]\n"
        "- [[KV Cache Mechanics]]\n"
        "- [[Planned Note]]\n"
        "- [[Probability Essentials]]\n"
        "- [[Multi Target]]\n"
        "- no-link bullet (ignored)\n"
        "- [[Self-Attention]] and [[Transformer Block]] extra wikilinks\n",
    )
    _write(master / "attn/Self-Attention.md", "# Self-Attention\n\nbody\n")
    _write(master / "llm/KV Cache Mechanics.md", "# KV Cache\n\nbody\n")
    # phantom "Probability Essentials" does NOT exist in master or course
    _write(master / "sub/Multi Target.md", "# Multi Target A\n\nbody\n")
    _write(master / "other/Multi Target.md", "# Multi Target B\n\nbody\n")

    _write(
        course / "nn/LSTM Gates.md",
        "# LSTM\n\n*See also:* [[Backprop]] for the mechanics.\n",
    )
    _write(course / "nn/Backprop.md", "# Backprop source\n\nbody\n")

    _write(
        out / "08 - Attention/Multi-Head Attention.md",
        "---\ntitle: MHA\n---\n\n# Multi-Head Attention\n\nbody\n\n"
        "## See Also\n\n- [[Self-Attention]]\n"
        "- [[02 - Mathematics/Probability/Probability Essentials|Probability Essentials]]\n",
    )
    _write(out / "08 - Attention/Self-Attention.md", "# Self-Attention\n\nbody\n")
    _write(out / "10 - LLM/KV Cache Mechanics.md", "# KV Cache Mechanics\n\nbody\n")
    _write(out / "02 - Mathematics/Probability/Probability Essentials.md", "# PE\n\nbody\n")
    _write(out / "05 - NN/Backpropagation.md", "# Backpropagation\n\nbody\n")
    _write(out / "07 - Sequence/LSTM Gates.md", "# LSTM Gates\n\nbody\n\nSee [[05 - NN/Backpropagation|Backpropagation]].\n")
    _write(out / "08 - Attention/Multi Target A.md", "# MTA\n\nbody\n")
    _write(out / "19 - Reference/Multi Target B.md", "# MTB\n\nbody\n")

    mapping_rows = [
        {
            "vault": "master-ai",
            "source_path": "attn/Multi-Head Attention.md",
            "canonical_paths": ["08 - Attention/Multi-Head Attention.md"],
            "multi": False,
        },
        {
            "vault": "master-ai",
            "source_path": "attn/Self-Attention.md",
            "canonical_paths": ["08 - Attention/Self-Attention.md"],
            "multi": False,
        },
        {
            "vault": "master-ai",
            "source_path": "llm/KV Cache Mechanics.md",
            "canonical_paths": ["10 - LLM/KV Cache Mechanics.md"],
            "multi": False,
        },
        {
            "vault": "master-ai",
            "source_path": "sub/Multi Target.md",
            "canonical_paths": ["08 - Attention/Multi Target A.md"],
            "multi": False,
        },
        {
            "vault": "master-ai",
            "source_path": "other/Multi Target.md",
            "canonical_paths": ["19 - Reference/Multi Target B.md"],
            "multi": False,
        },
        {
            "vault": "ai-course",
            "source_path": "nn/LSTM Gates.md",
            "canonical_paths": ["07 - Sequence/LSTM Gates.md"],
            "multi": False,
        },
        {
            "vault": "ai-course",
            "source_path": "nn/Backprop.md",
            "canonical_paths": ["05 - NN/Backpropagation.md"],
            "multi": False,
        },
    ]
    mapping_path = tmp_path / "file-mapping.jsonl"
    mapping_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in mapping_rows) + "\n",
        encoding="utf-8",
    )

    return {
        "master": master,
        "course": course,
        "out": out,
        "mapping": mapping_path,
    }


def run_audit(fx: dict) -> dict:
    return sa.audit_see_also(
        master_root=fx["master"],
        course_root=fx["course"],
        file_mapping=fx["mapping"],
        output_root=fx["out"],
    )


def verdict_of(report: dict, source_note: str, target: str) -> dict:
    for row in report["pair_rows"]:
        if row["source_note"] == source_note and row["target"] == target:
            return row
    raise AssertionError(f"pair not found: {source_note} -> {target}")


class TestExtraction:
    def test_heading_block_items_extracted(self, tmp_path):
        fx = build_fixture(tmp_path)
        records = sa.extract_master_see_also(fx["master"])
        targets = [r["target"] for r in records if r["source_path"] == "attn/Multi-Head Attention.md"]
        assert "Self-Attention" in targets
        assert "KV Cache Mechanics" in targets
        assert "Planned Note" in targets
        # bullet without wikilink ignored
        assert all("no-link bullet" not in t for t in targets)
        # duplicate occurrence recorded, not dropped
        assert targets.count("Self-Attention") == 2
        # second wikilink inside one item kept as extra target
        rec = next(r for r in records if r["target"] == "Self-Attention" and r["extra_targets"])
        assert rec["extra_targets"] == ["Transformer Block"]

    def test_inline_references_extracted(self, tmp_path):
        fx = build_fixture(tmp_path)
        records = sa.extract_course_inline_see_also(fx["course"])
        assert len(records) == 1
        assert records[0]["target"] == "Backprop"
        assert records[0]["convention"] == "inline"
        assert records[0]["line"] == 3

    def test_block_ends_at_next_heading(self, tmp_path):
        master = tmp_path / "m"
        _write(
            master / "n.md",
            "# N\n\n## See Also\n\n- [[T]]\n\n## References\n\n- not a cross-link\n",
        )
        records = sa.extract_master_see_also(master)
        assert [r["target"] for r in records] == ["T"]

    def test_heading_match_is_case_insensitive(self, tmp_path):
        master = tmp_path / "m"
        _write(master / "n.md", "# N\n\n### see also\n\n- [[T]]\n")
        records = sa.extract_master_see_also(master)
        assert [r["target"] for r in records] == ["T"]

    def test_unreadable_source_raises(self, tmp_path):
        master = tmp_path / "m"
        _write(master / "n.md", "# N\n")
        (master / "n.md").chmod(0o000)
        try:
            import os

            if os.access(master / "n.md", os.R_OK):  # running as root: skip
                return
            try:
                sa.extract_master_see_also(master)
                raise AssertionError("expected ValueError")
            except ValueError as exc:
                assert "unreadable source note" in str(exc)
        finally:
            (master / "n.md").chmod(0o644)


class TestVerdicts:
    def test_carried_over_bare_link(self, tmp_path):
        report = run_audit(build_fixture(tmp_path))
        row = verdict_of(report, "attn/Multi-Head Attention.md", "Self-Attention")
        assert row["verdict"] == "carried_over"
        assert row["occurrences"] == 2
        assert "08 - Attention/Multi-Head Attention.md" in row["carried_by"]

    def test_dropped_f0035_regression_shape(self, tmp_path):
        report = run_audit(build_fixture(tmp_path))
        row = verdict_of(report, "attn/Multi-Head Attention.md", "KV Cache Mechanics")
        assert row["verdict"] == "dropped"
        assert row["target_canonical"] == ["10 - LLM/KV Cache Mechanics.md"]
        assert row in report["findings"]

    def test_target_absent_phantom(self, tmp_path):
        report = run_audit(build_fixture(tmp_path))
        row = verdict_of(report, "attn/Multi-Head Attention.md", "Planned Note")
        assert row["verdict"] == "target_absent_from_unified"

    def test_phantom_with_unified_stem_carries_over(self, tmp_path):
        report = run_audit(build_fixture(tmp_path))
        row = verdict_of(report, "attn/Multi-Head Attention.md", "Probability Essentials")
        assert row["verdict"] == "carried_over"
        assert row["target_canonical"] == [
            "02 - Mathematics/Probability/Probability Essentials.md"
        ]

    def test_ambiguous_source_target_needs_review(self, tmp_path):
        report = run_audit(build_fixture(tmp_path))
        row = verdict_of(report, "attn/Multi-Head Attention.md", "Multi Target")
        assert row["verdict"] == "ambiguous_source_target"
        assert row in report["findings"]

    def test_inline_course_link_carried_via_alias(self, tmp_path):
        report = run_audit(build_fixture(tmp_path))
        row = verdict_of(report, "nn/LSTM Gates.md", "Backprop")
        assert row["verdict"] == "carried_over"

    def test_denominators_consistent(self, tmp_path):
        report = run_audit(build_fixture(tmp_path))
        d = report["denominators"]
        assert d["unique_source_note_target_pairs"] == sum(report["results"].values())
        assert d["see_also_link_occurrences"] >= d["unique_source_note_target_pairs"]
        assert d["master_ai_files_with_heading_block"] == 1
        assert d["ai_course_files_with_inline_reference"] == 1


class TestFailurePaths:
    def test_unknown_vault_key_raises(self, tmp_path):
        fx = build_fixture(tmp_path)
        bad = tmp_path / "bad-mapping.jsonl"
        bad.write_text(
            json.dumps(
                {
                    "vault": "vault-x",
                    "source_path": "a.md",
                    "canonical_paths": ["b.md"],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            sa.load_file_mapping(bad)
            raise AssertionError("expected ValueError")
        except ValueError as exc:
            assert "unknown vault key" in str(exc)

    def test_unmapped_source_note_verdict(self, tmp_path):
        fx = build_fixture(tmp_path)
        _write(fx["master"] / "extra/Unmapped Note.md", "# U\n\n## See Also\n\n- [[Self-Attention]]\n")
        report = run_audit(fx)
        row = verdict_of(report, "extra/Unmapped Note.md", "Self-Attention")
        assert row["verdict"] == "source_note_unmapped"

    def test_missing_destination_verdict(self, tmp_path):
        fx = build_fixture(tmp_path)
        _write(fx["master"] / "attn/Ghost Dest.md", "# G\n\n## See Also\n\n- [[Self-Attention]]\n")
        with fx["mapping"].open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "vault": "master-ai",
                        "source_path": "attn/Ghost Dest.md",
                        "canonical_paths": ["08 - Attention/Does Not Exist.md"],
                        "multi": False,
                    }
                )
                + "\n"
            )
        report = run_audit(fx)
        row = verdict_of(report, "attn/Ghost Dest.md", "Self-Attention")
        assert row["verdict"] == "dest_missing"

    def test_multi_dest_any_cover_counts(self, tmp_path):
        fx = build_fixture(tmp_path)
        _write(fx["master"] / "attn/Multi Dest.md", "# M\n\n## See Also\n\n- [[KV Cache Mechanics]]\n")
        _write(fx["out"] / "07 - Sequence/Multi Dest A.md", "# MDA\n\nno link here\n")
        _write(fx["out"] / "07 - Sequence/Multi Dest B.md", "# MDB\n\nsee [[10 - LLM/KV Cache Mechanics]]\n")
        with fx["mapping"].open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "vault": "master-ai",
                        "source_path": "attn/Multi Dest.md",
                        "canonical_paths": [
                            "07 - Sequence/Multi Dest A.md",
                            "07 - Sequence/Multi Dest B.md",
                        ],
                        "multi": True,
                    }
                )
                + "\n"
            )
        report = run_audit(fx)
        row = verdict_of(report, "attn/Multi Dest.md", "KV Cache Mechanics")
        assert row["verdict"] == "carried_over"
        assert "07 - Sequence/Multi Dest B.md" in row["carried_by"]


class TestDeterminismAndCLI:
    def test_deterministic_re_run(self, tmp_path):
        fx = build_fixture(tmp_path)
        a = run_audit(fx)
        b = run_audit(fx)
        assert a == b

    def test_cli_exit_zero_when_clean(self, tmp_path):
        fx = build_fixture(tmp_path)
        # repair the dropped link so the audit is clean
        dest = fx["out"] / "08 - Attention/Multi-Head Attention.md"
        dest.write_text(
            dest.read_text(encoding="utf-8").replace(
                "- [[Self-Attention]]\n",
                "- [[Self-Attention]]\n- [[10 - LLM/KV Cache Mechanics|KV Cache Mechanics]]\n",
            ),
            encoding="utf-8",
        )
        # remove the ambiguous item from the source note so no pair needs review
        src = fx["master"] / "attn/Multi-Head Attention.md"
        src.write_text(
            src.read_text(encoding="utf-8").replace("- [[Multi Target]]\n", ""),
            encoding="utf-8",
        )
        report_path = tmp_path / "report.json"
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "vault_unification",
                "see-also-audit",
                "--master-root",
                str(fx["master"]),
                "--course-root",
                str(fx["course"]),
                "--file-mapping",
                str(fx["mapping"]),
                "--output-root",
                str(fx["out"]),
                "--report",
                str(report_path),
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[1]),
        )
        assert proc.returncode == 0, proc.stderr + proc.stdout
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        res = payload["result"]["results"]
        assert res["dropped"] == 0
        assert res["ambiguous_source_target"] == 0
        assert res["source_note_unmapped"] == 0
        assert res["dest_missing"] == 0

    def test_cli_exit_one_when_dropped(self, tmp_path):
        fx = build_fixture(tmp_path)
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "vault_unification",
                "see-also-audit",
                "--master-root",
                str(fx["master"]),
                "--course-root",
                str(fx["course"]),
                "--file-mapping",
                str(fx["mapping"]),
                "--output-root",
                str(fx["out"]),
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[1]),
        )
        assert proc.returncode == 1
        assert '"dropped": 1' in proc.stdout

    def test_source_roots_never_written(self, tmp_path):
        import hashlib

        fx = build_fixture(tmp_path)

        def digest(root: Path) -> dict[str, str]:
            return {
                str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(root.rglob("*"))
                if p.is_file()
            }

        before_m, before_c = digest(fx["master"]), digest(fx["course"])
        run_audit(fx)
        assert digest(fx["master"]) == before_m
        assert digest(fx["course"]) == before_c


class TestAliasAndDecisions:
    def _fixture_with_alias(self, tmp_path):
        fx = build_fixture(tmp_path)
        # give the Backpropagation unified note an alias for the phantom name
        p = fx["out"] / "05 - NN/Backpropagation.md"
        t = p.read_text(encoding="utf-8")
        p.write_text(
            t.replace(
                "# Backpropagation",
                "# Backpropagation\n\n<!-- no alias yet -->",
                1,
            ),
            encoding="utf-8",
        )
        # instead add alias to a NEW phantom-style target on the master note
        m = fx["master"] / "attn/Multi-Head Attention.md"
        m.write_text(
            m.read_text(encoding="utf-8").replace(
                "- [[Planned Note]]\n",
                "- [[Planned Note]]\n- [[BP Deep Dive]]\n",
            ),
            encoding="utf-8",
        )
        b = fx["out"] / "05 - NN/Backpropagation.md"
        b.write_text(
            "---\ntitle: Backpropagation\naliases: [BP Deep Dive, backprop]\n---\n\n"
            "# Backpropagation\n\nbody\n",
            encoding="utf-8",
        )
        return fx

    def test_phantom_resolved_via_alias(self, tmp_path):
        fx = self._fixture_with_alias(tmp_path)
        report = run_audit(fx)
        row = verdict_of(report, "attn/Multi-Head Attention.md", "BP Deep Dive")
        assert row["verdict"] in ("carried_over", "dropped")
        assert row["target_canonical"] == ["05 - NN/Backpropagation.md"]
        # the MHA destination note does not link Backpropagation, so the
        # correctly-resolved pair is honestly reported as dropped
        assert row["verdict"] == "dropped"

    def test_ambiguous_alias_needs_review(self, tmp_path):
        fx = build_fixture(tmp_path)
        # two unified notes claiming the same alias for the phantom
        m = fx["master"] / "attn/Multi-Head Attention.md"
        m.write_text(
            m.read_text(encoding="utf-8").replace(
                "- [[Planned Note]]\n", "- [[Planned Note]]\n- [[Twin Alias]]\n"
            ),
            encoding="utf-8",
        )
        for name in ("08 - Attention/Self-Attention.md", "10 - LLM/KV Cache Mechanics.md"):
            p = fx["out"] / name
            p.write_text(
                f"---\naliases: [Twin Alias]\n---\n\n# {p.stem}\n\nbody\n",
                encoding="utf-8",
            )
        report = run_audit(fx)
        row = verdict_of(report, "attn/Multi-Head Attention.md", "Twin Alias")
        assert row["verdict"] == "ambiguous_source_target"

    def test_decision_exclude_documented(self, tmp_path):
        fx = build_fixture(tmp_path)
        dec = tmp_path / "decisions.jsonl"
        dec.write_text(
            json.dumps(
                {
                    "vault": "master-ai",
                    "source_note": "attn/Multi-Head Attention.md",
                    "target": "KV Cache Mechanics",
                    "action": "exclude",
                    "rationale": "test exclusion rationale",
                    "decided_by": "unit test",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        report = sa.audit_see_also(
            master_root=fx["master"],
            course_root=fx["course"],
            file_mapping=fx["mapping"],
            output_root=fx["out"],
            decisions=dec,
        )
        row = verdict_of(report, "attn/Multi-Head Attention.md", "KV Cache Mechanics")
        assert row["verdict"] == "excluded_documented"
        assert row["decision"]["rationale"] == "test exclusion rationale"
        assert report["results"]["excluded_documented"] == 1
        assert report["results"]["dropped"] == 0
        assert report["decisions_applied"]["applied"] == 1

    def test_decision_resolve_overrides_ambiguity(self, tmp_path):
        fx = build_fixture(tmp_path)
        dec = tmp_path / "decisions.jsonl"
        dec.write_text(
            json.dumps(
                {
                    "vault": "master-ai",
                    "source_note": "attn/Multi-Head Attention.md",
                    "target": "Multi Target",
                    "action": "resolve",
                    "canonical_target": "08 - Attention/Multi Target A.md",
                    "rationale": "author meant the content note",
                    "decided_by": "unit test",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        report = sa.audit_see_also(
            master_root=fx["master"],
            course_root=fx["course"],
            file_mapping=fx["mapping"],
            output_root=fx["out"],
            decisions=dec,
        )
        row = verdict_of(report, "attn/Multi-Head Attention.md", "Multi Target")
        assert row["verdict"] in ("carried_over", "dropped")
        assert row["target_canonical"] == ["08 - Attention/Multi Target A.md"]

    def test_decision_resolve_missing_target_raises(self, tmp_path):
        fx = build_fixture(tmp_path)
        dec = tmp_path / "decisions.jsonl"
        dec.write_text(
            json.dumps(
                {
                    "vault": "master-ai",
                    "source_note": "attn/Multi-Head Attention.md",
                    "target": "Multi Target",
                    "action": "resolve",
                    "rationale": "missing canonical_target",
                    "decided_by": "unit test",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            sa.load_decisions(dec)
            raise AssertionError("expected ValueError")
        except ValueError as exc:
            assert "canonical_target" in str(exc)

    def test_decision_bad_action_raises(self, tmp_path):
        dec = tmp_path / "decisions.jsonl"
        dec.write_text(
            json.dumps(
                {
                    "vault": "master-ai",
                    "source_note": "a.md",
                    "target": "b",
                    "action": "delete",
                    "rationale": "x",
                    "decided_by": "t",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            sa.load_decisions(dec)
            raise AssertionError("expected ValueError")
        except ValueError as exc:
            assert "unknown action" in str(exc)

    def test_decision_without_rationale_raises(self, tmp_path):
        dec = tmp_path / "decisions.jsonl"
        dec.write_text(
            json.dumps(
                {
                    "vault": "master-ai",
                    "source_note": "a.md",
                    "target": "b",
                    "action": "exclude",
                    "decided_by": "t",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            sa.load_decisions(dec)
            raise AssertionError("expected ValueError")
        except ValueError as exc:
            assert "rationale" in str(exc)
