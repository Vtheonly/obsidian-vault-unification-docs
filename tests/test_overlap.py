"""Tests for cross-vault overlap candidate discovery (CAP-013) and the
append-only overlap-classification overlay (ADR-0009).

F-0006 regression cases are first-class citizens here:
- 'bridge' must NOT match the term 'ridge' (word-boundary lookarounds);
- mermaid node labels like ``L1[Constant Change]`` / ``L2[Equation: y = ax
  + b]`` must be flagged ``mermaid_node_suspect`` and must never count as
  confirmed evidence for L1/L2 regularization terms.
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from vault_unification import kuregistry, overlap, registry  # noqa: E402
from vault_unification.kuregistry import RegistryError  # noqa: E402
from vault_unification.overlap import OverlapError  # noqa: E402

KUS_SCHEMA = REPO_ROOT / "schemas" / "knowledge-unit.schema.json"
CLS_SCHEMA = REPO_ROOT / "schemas" / "overlap-classification.schema.json"


def make_ku(
    ku_id: str,
    source_id: str,
    excerpt: str,
    *,
    unit_type: str = "prose",
    line_start: int = 1,
    excerpt_hash: str | None = None,
    heading_path: list | None = None,
) -> dict:
    return {
        "knowledge_unit_id": ku_id,
        "source_id": source_id,
        "source_path": source_id.split(":", 1)[1],
        "source_file_hash": "fh-" + source_id.split(":", 1)[0],
        "unit_type": unit_type,
        "disposition": "Unaccounted",
        "heading_path": heading_path or [],
        "line_start": line_start,
        "line_end": line_start + len(excerpt.splitlines()) - 1,
        "excerpt": excerpt,
        "excerpt_hash": excerpt_hash if excerpt_hash is not None else "h" + ku_id,
        "verification_status": {
            "accounting": "pending",
            "editorial": "pending",
            "semantic": "pending",
            "technical": "pending",
            "extraction": "machine-segmented",
        },
    }


def write_batch(path: Path, records: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")
    return path


# ---------------------------------------------------------------------------
# word-boundary pattern building


class TestBoundaryPatterns:
    def test_bridge_does_not_match_ridge(self):
        """F-0006: 'bridge' must not match the term 'ridge'."""
        pattern = overlap._boundary_pattern("ridge")
        assert pattern.search("the theoretical bridge between") is None
        assert pattern.search("use ridge regression") is not None
        assert pattern.search("Ridge (L2)") is not None  # case-insensitive

    def test_plain_ridge_matches(self):
        pattern = overlap._boundary_pattern("ridge")
        assert pattern.search("ridge") is not None
        assert pattern.search("(ridge)") is not None
        assert pattern.search("ridge:") is not None

    def test_plural_not_matched_without_alias(self):
        """No stemming: 'ridges' is not 'ridge' unless aliased."""
        pattern = overlap._boundary_pattern("ridge")
        assert pattern.search("ridges everywhere") is None

    def test_l1_followed_by_bracket_is_a_boundary_match_but_flagged(self):
        """L1[Constant Change] DOES hit a word boundary (the '[' is one) —
        which is exactly why the mermaid flag exists (F-0006)."""
        pattern = overlap._boundary_pattern("L1")
        m = pattern.search("    L1[Constant Change]")
        assert m is not None  # boundary-wise it matches ...
        # ... so discovery must flag it (see TestMermaidFlagging)

    def test_terms_with_special_characters(self):
        pattern = overlap._boundary_pattern("R^2")
        assert pattern.search("we compute R^2 for fit") is not None
        assert pattern.search("R^23 is different") is None


class TestBuildTermPatterns:
    def test_mapping_and_list_forms(self):
        from_map = overlap.build_term_patterns({"ridge": ["L2"]})
        assert [a for a, _ in from_map["ridge"]] == ["ridge", "L2"]
        from_list = overlap.build_term_patterns(["mse"])
        assert list(from_list) == ["mse"]

    def test_duplicate_alias_of_term_dropped(self):
        patterns = overlap.build_term_patterns({"ridge": ["ridge", "Ridge"]})
        assert len(patterns["ridge"]) == 1

    def test_empty_terms_rejected(self):
        with pytest.raises(OverlapError):
            overlap.build_term_patterns({})

    def test_empty_term_string_rejected(self):
        with pytest.raises(OverlapError):
            overlap.build_term_patterns({"": []})

    def test_bad_alias_type_rejected(self):
        with pytest.raises(OverlapError):
            overlap.build_term_patterns({"ridge": "L2"})


# ---------------------------------------------------------------------------
# term matching on KU records


class TestFindTermMatches:
    def test_mermaid_l1_l2_flagged_never_confirmed(self):
        """F-0006: mermaid L1[/L2[ node labels AND edge references
        (L1 --> L2 --> L3, the real KU-067bca8c3b42624f shape) are flagged
        and excluded from confirmed evidence."""
        rec = make_ku(
            "KU-mermaid",
            "ai-course:x.md",
            "```mermaid\ngraph TD\n    subgraph Linear\n    L1[Constant Change]\n"
            "    L2[Equation: y = ax + b]\n    L3[Shape: Straight Line]\n    end\n"
            "\n    L1 --> L2 --> L3\n    N1 --> N2 --> N3\n```",
            unit_type="code_block",
            line_start=140,
        )
        patterns = overlap.build_term_patterns({"L1 regularization": ["L1"], "L2 regularization": ["L2"]})
        matches = overlap.find_term_matches(rec, patterns)
        l1 = [m for m in matches if m.term == "L1 regularization"]
        l2 = [m for m in matches if m.term == "L2 regularization"]
        # node definitions (L1[...], L2[...]) AND edge references (L1 --> L2)
        assert len(l1) == 2  # noqa: PLR2004 - L1[Constant Change] + L1 --> L2
        assert len(l2) == 2  # noqa: PLR2004 - L2[Equation] + L1 --> L2
        # every match in a mermaid block is suspect, none confirmed
        assert all(m.mermaid_node_suspect for m in matches)
        assert l2[0].unit_is_code_block is True
        # confirmed evidence excludes them
        assert overlap._confirmed(matches) == []

    def test_mermaid_edge_only_reference_also_flagged(self):
        """Regression for the real-batch false positive: an edge line
        'L1 --> L2' has no '[' after L1, but it is still mermaid syntax."""
        rec = make_ku(
            "KU-mermaid-edge",
            "ai-course:x.md",
            "```mermaid\ngraph TD\n    A[Start]\n    L1 --> L2 --> L3\n```",
            unit_type="code_block",
        )
        patterns = overlap.build_term_patterns({"L1 regularization": ["L1"], "L2 regularization": ["L2"]})
        matches = overlap.find_term_matches(rec, patterns)
        assert len(matches) == 2  # L1 and L2 on the edge line
        assert all(m.mermaid_node_suspect for m in matches)
        assert overlap._confirmed(matches) == []

    def test_prose_l1_l2_not_flagged(self):
        rec = make_ku(
            "KU-prose-l1l2",
            "master-ai:y.md",
            "L1 regularization zeroes weights; L2 shrinks them.",
        )
        patterns = overlap.build_term_patterns({"L1 regularization": ["L1"], "L2 regularization": ["L2"]})
        matches = overlap.find_term_matches(rec, patterns)
        # 3 matches: canonical 'L1 regularization' + alias 'L1' + alias 'L2'
        # (canonical and alias both matching the same text is by design:
        # each is recorded as independent evidence)
        assert len(matches) == 3
        assert all(m.mermaid_node_suspect is False for m in matches)
        assert len(overlap._confirmed(matches)) == 3

    def test_bridge_excerpt_yields_no_ridge_evidence(self):
        """The exact AI Course 'bridge' sentence must not produce ridge
        evidence (F-0006 verbatim case)."""
        rec = make_ku(
            "KU-bridge",
            "ai-course:04. Logistic Regression.md",
            "Understanding the mathematical foundation of logistic regression requires understanding the concepts of odds and log-odds, which provide the theoretical bridge between linear regression and logistic regression.",
            line_start=94,
        )
        patterns = overlap.build_term_patterns(
            {"ridge regression": ["ridge", "L2 regularization"], "lasso": []}
        )
        matches = overlap.find_term_matches(rec, patterns)
        assert matches == []

    def test_source_line_mapping(self):
        rec = make_ku(
            "KU-lines",
            "master-ai:y.md",
            "first line\nridge on second",
            line_start=37,
        )
        patterns = overlap.build_term_patterns({"ridge": []})
        matches = overlap.find_term_matches(rec, patterns)
        assert len(matches) == 1
        assert matches[0].source_line == 38

    def test_no_excerpt_no_matches(self):
        rec = make_ku("KU-noex", "a:x.md", "text", excerpt_hash="h")
        rec["excerpt"] = None
        patterns = overlap.build_term_patterns({"ridge": []})
        assert overlap.find_term_matches(rec, patterns) == []

    def test_alias_and_case_insensitive(self):
        rec = make_ku("KU-alias", "a:x.md", " RIDGE regression and L2 terms ")
        patterns = overlap.build_term_patterns({"ridge regression": ["ridge", "L2"]})
        matches = overlap.find_term_matches(rec, patterns)
        # canonical 'ridge regression' + aliases 'ridge' and 'L2' all match
        aliases = {m.alias for m in matches}
        assert aliases == {"ridge regression", "ridge", "L2"}


# ---------------------------------------------------------------------------
# candidate discovery


def regression_fixture_batches(tmp_path: Path):
    """Two small batches reproducing the EXT-001/EXT-002 shape, including
    the F-0006 traps (bridge sentence + mermaid L1/L2 labels) and one
    exact-hash duplicate pair."""
    ai_course = [
        make_ku(
            "KU-course-bridge",
            "ai-course:04. Logistic Regression.md",
            "which provide the theoretical bridge between linear regression and logistic regression.",
            line_start=94,
        ),
        make_ku(
            "KU-course-mermaid",
            "ai-course:05. Regression Fundamentals (In Depth).md",
            "```mermaid\ngraph TD\n    subgraph Linear\n    L1[Constant Change]\n"
            "    L2[Equation: y = ax + b]\n    L3[Shape: Straight Line]\n    end\n"
            "\n    L1 --> L2 --> L3\n    N1 --> N2 --> N3\n```",
            unit_type="code_block",
            line_start=140,
        ),
        make_ku(
            "KU-course-mse",
            "ai-course:02. Linear Regression.md",
            "We use the **Mean Squared Error (MSE)** as our loss.",
            line_start=21,
        ),
        make_ku(
            "KU-course-shared",
            "ai-course:02. Linear Regression.md",
            "Exact same line in both vaults.",
            excerpt_hash="sharedhash01",
            line_start=10,
        ),
    ]
    master_ai = [
        make_ku(
            "KU-master-mse",
            "master-ai:02 - Linear and Logistic Regression.md",
            "$$\nL(\\mathbf{w}, b) = \\frac{1}{N}\\sum (y_i - \\hat{y}_i)^2\n$$\nMSE is the loss.",
            unit_type="math_block",
            line_start=17,
        ),
        make_ku(
            "KU-master-ridge",
            "master-ai:02 - Linear and Logistic Regression.md",
            "Ridge regression adds an L2 penalty; lasso uses L1.",
            line_start=39,
        ),
        make_ku(
            "KU-master-shared",
            "master-ai:02 - Linear and Logistic Regression.md",
            "Exact same line in both vaults.",
            excerpt_hash="sharedhash01",
            line_start=50,
        ),
    ]
    p1 = write_batch(tmp_path / "batch-course.jsonl", ai_course)
    p2 = write_batch(tmp_path / "batch-master.jsonl", master_ai)
    return p1, p2


class TestDiscoverCandidates:
    TERMS = {
        "MSE": ["mean squared error"],
        "ridge regression": ["ridge", "L2 regularization", "L2"],
        "lasso": ["L1 regularization", "L1"],
    }

    def _run(self, tmp_path):
        p1, p2 = regression_fixture_batches(tmp_path)
        records = overlap.load_ku_batches([p1, p2], KUS_SCHEMA)
        patterns = overlap.build_term_patterns(self.TERMS)
        return overlap.discover_candidates(records, patterns)

    def test_cross_vault_topic_found_with_evidence(self, tmp_path):
        result = self._run(tmp_path)
        topics = result["topics"]
        assert "MSE" in topics
        assert set(topics["MSE"]) == {"ai-course", "master-ai"}
        pairs = [p for p in result["pairs"] if p["topic"] == "MSE"]
        assert len(pairs) == 1
        pair = pairs[0]
        assert pair["ku_a"]["ku_id"] == "KU-course-mse"
        assert pair["ku_b"]["ku_id"] == "KU-master-mse"
        assert pair["confirmed"] is True
        # evidence: matched term + position + context on both sides
        assert pair["matches_a"][0]["term"] == "MSE"
        assert pair["matches_a"][0]["source_line"] == 21
        assert "⟦" in pair["matches_a"][0]["context"]  # marked context
        assert pair["matches_b"], "master side must carry evidence too"

    def test_bridge_and_mermaid_produce_no_confirmed_ridge_candidates(self, tmp_path):
        """F-0006 end-to-end: the course side has zero genuine ridge
        evidence, so no confirmed ridge pair may exist."""
        result = self._run(tmp_path)
        ridge_pairs = [p for p in result["pairs"] if p["topic"] == "ridge regression"]
        # course side has only the bridge sentence + mermaid labels:
        # the mermaid KU produces only flagged matches
        course_ridge_kus = {
            ku_id
            for ku_id, ms in result["topics"]["ridge regression"]["ai-course"]["per_ku_matches"].items()
            if any(m["alias"] == "L2" for m in ms)
        }
        assert course_ridge_kus == {"KU-course-mermaid"}
        for pair in ridge_pairs:
            assert pair["confirmed"] is False
            assert pair["unconfirmed_only"] is True
            assert "mermaid" in pair["unconfirmed_reason"]

    def test_exact_hash_duplicates_found(self, tmp_path):
        result = self._run(tmp_path)
        assert len(result["exact_hash_pairs"]) == 1
        pair = result["exact_hash_pairs"][0]
        assert {pair["ku_a"]["ku_id"], pair["ku_b"]["ku_id"]} == {
            "KU-course-shared",
            "KU-master-shared",
        }
        assert pair["kind"] == "exact_hash"
        assert pair["confirmed"] is True

    def test_single_vault_topic_not_paired(self, tmp_path):
        """'lasso' has genuine evidence only on the master side. The course
        mermaid label L1[...] creates a cross-vault lasso pair, but it is
        unconfirmed_only (mermaid flag) — never confirmed evidence (F-0006)."""
        result = self._run(tmp_path)
        lasso_pairs = [p for p in result["pairs"] if p["topic"] == "lasso"]
        assert lasso_pairs != []
        for pair in lasso_pairs:
            assert pair["ku_a"]["ku_id"] == "KU-course-mermaid"
            assert pair["confirmed"] is False
            assert pair["unconfirmed_only"] is True
            assert "mermaid" in pair["unconfirmed_reason"]
        # no CONFIRMED lasso pair exists (course side has zero genuine lasso)
        assert not [p for p in lasso_pairs if p["confirmed"]]

    def test_determinism(self, tmp_path):
        r1 = self._run(tmp_path / "a")
        r2 = self._run(tmp_path / "b")
        assert r1["pairs"] == r2["pairs"]
        assert r1["counts"] == r2["counts"]

    def test_pair_cap_flags_truncation(self, tmp_path):
        """A topic whose pair cross-product exceeds the cap is truncated,
        flagged, and its per-KU evidence stays complete."""
        p1, p2 = regression_fixture_batches(tmp_path)
        records = overlap.load_ku_batches([p1, p2], KUS_SCHEMA)
        # add 3 course + 2 extra master MSE KUs -> 4 x 3 = 12 pairs for MSE
        for i in range(3):
            records.append(
                make_ku(
                    f"KU-course-mse-{i}",
                    "ai-course:02. Linear Regression.md",
                    "MSE appears here too",
                    excerpt_hash=f"c-mse-{i}",
                )
            )
        for i in range(2):
            records.append(
                make_ku(
                    f"KU-master-mse-{i}",
                    "master-ai:02 - Linear and Logistic Regression.md",
                    "MSE again",
                    excerpt_hash=f"m-mse-{i}",
                )
            )
        patterns = overlap.build_term_patterns({"MSE": ["mean squared error"]})
        result = overlap.discover_candidates(records, patterns, max_pairs_per_topic=4)
        assert result["counts"]["term_pairs"] == 4
        assert len(result["truncated_topics"]) == 1
        assert result["truncated_topics"][0]["topic"] == "MSE"
        assert result["truncated_topics"][0]["pair_count"] == 12
        assert result["truncated_topics"][0]["emitted"] == 4
        # per-KU evidence stays complete despite the cap
        topic = result["topics"]["MSE"]
        assert len(topic["ai-course"]["ku_ids"]) == 4
        assert len(topic["master-ai"]["ku_ids"]) == 3

    def test_records_without_excerpt_excluded_explicitly(self, tmp_path):
        p1, p2 = regression_fixture_batches(tmp_path)
        records = overlap.load_ku_batches([p1, p2], KUS_SCHEMA)
        records.append(make_ku("KU-noex", "a:x.md", "irrelevant", excerpt_hash="z"))
        records[-1]["excerpt"] = None
        patterns = overlap.build_term_patterns(self.TERMS)
        result = overlap.discover_candidates(records, patterns)
        assert "KU-noex" in result["excluded_no_excerpt"]

    def test_invalid_cap_rejected(self, tmp_path):
        p1, p2 = regression_fixture_batches(tmp_path)
        records = overlap.load_ku_batches([p1, p2], KUS_SCHEMA)
        patterns = overlap.build_term_patterns(self.TERMS)
        with pytest.raises(OverlapError):
            overlap.discover_candidates(records, patterns, max_pairs_per_topic=0)


# ---------------------------------------------------------------------------
# batch loading


class TestLoadBatches:
    def test_rejects_missing_file(self):
        with pytest.raises(OverlapError):
            overlap.load_ku_batches(["nope.jsonl"], KUS_SCHEMA)

    def test_rejects_invalid_json_line(self, tmp_path):
        bad = tmp_path / "bad.jsonl"
        bad.write_text("{not json}\n", encoding="utf-8")
        with pytest.raises(OverlapError):
            overlap.load_ku_batches([bad], KUS_SCHEMA)

    def test_rejects_schema_violation(self, tmp_path):
        rec = make_ku("KU-x", "a:x.md", "text")
        del rec["disposition"]
        p = write_batch(tmp_path / "bad.jsonl", [rec])
        with pytest.raises(OverlapError):
            overlap.load_ku_batches([p], KUS_SCHEMA)

    def test_rejects_source_id_without_vault(self, tmp_path):
        rec = make_ku("KU-x", "a:x.md", "text")
        rec["source_id"] = "no-vault-prefix"
        p = write_batch(tmp_path / "bad.jsonl", [rec])
        with pytest.raises(OverlapError):
            overlap.load_ku_batches([p], KUS_SCHEMA)

    def test_rejects_duplicate_ku_ids_across_batches(self, tmp_path):
        rec = make_ku("KU-dup", "a:x.md", "text")
        p1 = write_batch(tmp_path / "b1.jsonl", [rec])
        p2 = write_batch(tmp_path / "b2.jsonl", [rec])
        with pytest.raises(OverlapError):
            overlap.load_ku_batches([p1, p2], KUS_SCHEMA)

    def test_rejects_empty_batch(self, tmp_path):
        p = tmp_path / "empty.jsonl"
        p.write_text("\n\n", encoding="utf-8")
        with pytest.raises(OverlapError):
            overlap.load_ku_batches([p], KUS_SCHEMA)


class TestLoadTermsFile:
    def test_object_form(self, tmp_path):
        f = tmp_path / "terms.json"
        f.write_text(json.dumps({"ridge": ["L2"]}), encoding="utf-8")
        assert overlap.load_terms_file(f) == {"ridge": ["L2"]}

    def test_list_form(self, tmp_path):
        f = tmp_path / "terms.json"
        f.write_text(json.dumps(["mse", "ridge"]), encoding="utf-8")
        assert overlap.load_terms_file(f) == {"mse": [], "ridge": []}

    def test_missing_file(self, tmp_path):
        with pytest.raises(OverlapError):
            overlap.load_terms_file(tmp_path / "nope.json")

    def test_empty_rejected(self, tmp_path):
        f = tmp_path / "terms.json"
        f.write_text("[]", encoding="utf-8")
        with pytest.raises(OverlapError):
            overlap.load_terms_file(f)

    def test_wrong_shape_rejected(self, tmp_path):
        f = tmp_path / "terms.json"
        f.write_text("42", encoding="utf-8")
        with pytest.raises(OverlapError):
            overlap.load_terms_file(f)


class TestRunDiscovery:
    def test_end_to_end_writes_jsonl(self, tmp_path):
        p1, p2 = regression_fixture_batches(tmp_path)
        terms = tmp_path / "terms.json"
        terms.write_text(
            json.dumps({"MSE": ["mean squared error"], "ridge regression": ["ridge", "L2"]}),
            encoding="utf-8",
        )
        out = tmp_path / "pairs.jsonl"
        result = overlap.run_discovery(
            [p1, p2], terms, out, kus_schema=KUS_SCHEMA
        )
        assert result["counts"]["records_total"] == 7
        assert out.exists()
        lines = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
        expected = (
            result["counts"]["term_pairs"]
            + result["counts"]["exact_hash_pairs"]
            + result["counts"]["normalized_hash_pairs"]
        )
        assert len(lines) == expected
        ids = [l["candidate_id"] for l in lines]
        assert len(ids) == len(set(ids))

    def test_single_vault_batches_rejected(self, tmp_path):
        p1, _ = regression_fixture_batches(tmp_path)
        terms = tmp_path / "terms.json"
        terms.write_text(json.dumps({"ridge": []}), encoding="utf-8")
        with pytest.raises(OverlapError):
            overlap.run_discovery([p1], terms, tmp_path / "o.jsonl", kus_schema=KUS_SCHEMA)


# ---------------------------------------------------------------------------
# classification file validation (registry layer)


def make_classification(
    cid: str = "OC-test-0001",
    ku_ids: list | None = None,
    overlap_type: str = "Semantic Duplicate",
    rationale: str = "Same formula, same claim.",
    evidence_ku: str | None = None,
) -> dict:
    ku_ids = ku_ids or ["KU-course-mse", "KU-master-mse"]
    return {
        "classification_id": cid,
        "task_id": "EXT-003",
        "topic": "MSE",
        "overlap_type": overlap_type,
        "ku_ids": ku_ids,
        "rationale": rationale,
        "evidence": [
            {
                "ku_id": evidence_ku or ku_ids[0],
                "quote": "Mean Squared Error",
                "source_path": "a.md",
                "lines": [21],
            }
        ],
        "candidate_ref": "reports/extraction/ext003-overlap-candidates.json",
        "classified_by": "EXT-003 test",
        "method": "CAP-013 candidates + excerpt review",
        "date": "2026-10-26",
    }


class TestValidateClassificationFile:
    def test_valid_file(self, tmp_path):
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(make_classification()) + "\n", encoding="utf-8")
        report = registry.validate_classification_file(f, CLS_SCHEMA)
        assert report["valid"] is True, report["errors"]
        assert report["cross_checks"]["classifications_total"] == 1

    def test_evidence_ku_not_in_ku_ids(self, tmp_path):
        rec = make_classification(evidence_ku="KU-not-in-ku-ids")
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        report = registry.validate_classification_file(f, CLS_SCHEMA)
        assert report["valid"] is False
        assert report["errors"][0]["rule"] == "evidence_ku_not_in_ku_ids"

    def test_duplicate_classification_id(self, tmp_path):
        rec = make_classification()
        f = tmp_path / "cls.jsonl"
        f.write_text(
            json.dumps(rec) + "\n" + json.dumps(make_classification(cid="OC-test-0001", ku_ids=["a", "b"])) + "\n",
            encoding="utf-8",
        )
        report = registry.validate_classification_file(f, CLS_SCHEMA)
        assert report["valid"] is False
        assert report["errors"][0]["rule"] == "duplicate_classification_id"

    def test_self_supersede_rejected(self, tmp_path):
        rec = make_classification()
        rec["supersedes_classification_id"] = "OC-test-0001"
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        report = registry.validate_classification_file(f, CLS_SCHEMA)
        assert report["valid"] is False
        assert report["errors"][0]["rule"] == "self_supersede"

    def test_external_supersede_deferred_not_error(self, tmp_path):
        rec = make_classification()
        rec["supersedes_classification_id"] = "OC-earlier-file-0001"
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        report = registry.validate_classification_file(f, CLS_SCHEMA)
        assert report["valid"] is True
        assert report["external_supersedes_references"] == [
            {
                "classification_id": "OC-test-0001",
                "supersedes": "OC-earlier-file-0001",
            }
        ]

    def test_schema_rejects_bad_overlap_type(self, tmp_path):
        rec = make_classification(overlap_type="Sorta Same")
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        report = registry.validate_classification_file(f, CLS_SCHEMA)
        assert report["valid"] is False

    def test_schema_rejects_missing_rationale(self, tmp_path):
        rec = make_classification()
        del rec["rationale"]
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        report = registry.validate_classification_file(f, CLS_SCHEMA)
        assert report["valid"] is False

    def test_schema_requires_two_kus(self, tmp_path):
        rec = make_classification(ku_ids=["only-one"])
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        report = registry.validate_classification_file(f, CLS_SCHEMA)
        assert report["valid"] is False


# ---------------------------------------------------------------------------
# registry application (kuregistry layer)


@pytest.fixture()
def loaded_db(tmp_path):
    """A v2 registry database with the fixture KUs loaded."""
    db = tmp_path / "kuregistry.db"
    kuregistry.init_registry(db)
    p1, p2 = regression_fixture_batches(tmp_path)
    for p in (p1, p2):
        report = kuregistry.load_jsonl(
            db, p, schema_path=REPO_ROOT / "schemas" / "knowledge-unit.schema.json"
        )
        assert not report["errors"], report["errors"]
    return db, p1, p2


class TestApplyOverlapClassifications:
    def test_apply_inserts_and_counts(self, loaded_db, tmp_path):
        db, _, _ = loaded_db
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(make_classification()) + "\n", encoding="utf-8")
        result = kuregistry.apply_overlap_classifications(db, f, schema_path=CLS_SCHEMA)
        assert result["inserted"] == 1
        report = kuregistry.validate_registry_db(db)
        assert report["valid"] is True
        assert report["overlap_classification_counts"]["classifications_total"] == 1
        assert report["overlap_classification_counts"]["by_overlap_type"] == {
            "Semantic Duplicate": 1
        }
        assert report["overlap_classification_counts"]["kus_participating"] == 2

    def test_idempotent_reapply(self, loaded_db, tmp_path):
        db, _, _ = loaded_db
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(make_classification()) + "\n", encoding="utf-8")
        kuregistry.apply_overlap_classifications(db, f, schema_path=CLS_SCHEMA)
        result = kuregistry.apply_overlap_classifications(db, f, schema_path=CLS_SCHEMA)
        assert result["inserted"] == 0
        assert result["idempotent_skipped"] == 1

    def test_conflicting_reapply_rejected(self, loaded_db, tmp_path):
        db, _, _ = loaded_db
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(make_classification()) + "\n", encoding="utf-8")
        kuregistry.apply_overlap_classifications(db, f, schema_path=CLS_SCHEMA)
        other = make_classification(rationale="changed my mind")
        f2 = tmp_path / "cls2.jsonl"
        f2.write_text(json.dumps(other) + "\n", encoding="utf-8")
        with pytest.raises(RegistryError, match="append-only"):
            kuregistry.apply_overlap_classifications(db, f2, schema_path=CLS_SCHEMA)

    def test_unknown_ku_rejected(self, loaded_db, tmp_path):
        db, _, _ = loaded_db
        rec = make_classification(ku_ids=["KU-course-mse", "KU-unknown"])
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        with pytest.raises(RegistryError, match="not present in the registry"):
            kuregistry.apply_overlap_classifications(db, f, schema_path=CLS_SCHEMA)

    def test_single_vault_classification_rejected(self, loaded_db, tmp_path):
        db, _, _ = loaded_db
        rec = make_classification(
            ku_ids=["KU-course-mse", "KU-course-bridge"]
        )
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        with pytest.raises(RegistryError, match="two distinct vaults"):
            kuregistry.apply_overlap_classifications(db, f, schema_path=CLS_SCHEMA)

    def test_schema_violation_rejected(self, loaded_db, tmp_path):
        db, _, _ = loaded_db
        rec = make_classification(overlap_type="Bogus")
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        with pytest.raises(RegistryError, match="schema"):
            kuregistry.apply_overlap_classifications(db, f, schema_path=CLS_SCHEMA)

    def test_supersede_via_external_reference(self, loaded_db, tmp_path):
        """Correct an earlier classification by superseding it (append-only)."""
        db, _, _ = loaded_db
        f1 = tmp_path / "cls1.jsonl"
        f1.write_text(json.dumps(make_classification(cid="OC-1")) + "\n", encoding="utf-8")
        kuregistry.apply_overlap_classifications(db, f1, schema_path=CLS_SCHEMA)
        corrected = make_classification(
            cid="OC-2",
            overlap_type="Partial Overlap",
            rationale="On review, the formulas differ in granularity.",
        )
        corrected["supersedes_classification_id"] = "OC-1"
        f2 = tmp_path / "cls2.jsonl"
        f2.write_text(json.dumps(corrected) + "\n", encoding="utf-8")
        result = kuregistry.apply_overlap_classifications(db, f2, schema_path=CLS_SCHEMA)
        assert result["inserted"] == 1
        counts = kuregistry.validate_registry_db(db)["overlap_classification_counts"]
        assert counts["classifications_total"] == 2

    def test_supersede_unknown_reference_rejected(self, loaded_db, tmp_path):
        db, _, _ = loaded_db
        rec = make_classification()
        rec["supersedes_classification_id"] = "OC-never-existed"
        f = tmp_path / "cls.jsonl"
        f.write_text(json.dumps(rec) + "\n", encoding="utf-8")
        with pytest.raises(RegistryError, match="supersedes"):
            kuregistry.apply_overlap_classifications(db, f, schema_path=CLS_SCHEMA)

    def test_missing_classification_file(self, loaded_db, tmp_path):
        db, _, _ = loaded_db
        with pytest.raises(RegistryError, match="not found"):
            kuregistry.apply_overlap_classifications(
                db, tmp_path / "nope.jsonl", schema_path=CLS_SCHEMA
            )


class TestRegistrySchemaV2:
    def test_fresh_db_is_version_2_with_overlay_tables(self, tmp_path):
        db = tmp_path / "db.sqlite"
        kuregistry.init_registry(db)
        assert kuregistry.REGISTRY_SCHEMA_VERSION == 2
        import sqlite3

        conn = sqlite3.connect(str(db))
        tables = {
            r[0]
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        conn.close()
        assert {"overlap_classifications", "classification_kus"} <= tables

    def test_old_v1_db_rejected_with_clear_error(self, tmp_path):
        """A v1 database (pre-EXT-003) must be rejected, telling the user
        to rebuild (the DB is a derived index; ADR-0007)."""
        db = tmp_path / "v1db.sqlite"
        kuregistry.init_registry(db)
        # downgrade the version like a v1 database would have it
        import sqlite3

        conn = sqlite3.connect(str(db))
        conn.execute("UPDATE meta SET value = '1' WHERE key = 'registry_schema_version'")
        conn.commit()
        conn.close()
        with pytest.raises(RegistryError, match="unsupported registry schema version"):
            kuregistry.validate_registry_db(db)


class TestTermsFileCommentKeys:
    def test_underscore_keys_ignored(self, tmp_path):
        f = tmp_path / "terms.json"
        f.write_text(
            json.dumps({"_comment": "docs", "ridge": ["L2"]}), encoding="utf-8"
        )
        assert overlap.load_terms_file(f) == {"ridge": ["L2"]}

    def test_only_underscore_keys_rejected(self, tmp_path):
        f = tmp_path / "terms.json"
        f.write_text(json.dumps({"_comment": "docs only"}), encoding="utf-8")
        with pytest.raises(OverlapError):
            overlap.load_terms_file(f)
