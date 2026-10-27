"""CAP-019 tests: note quality assessment, drift detection, batch gates.

The centerpiece fixture reproduces the user-reported failure mode from the
large AI vault: the FIRST notes are polished (definitions, examples, math,
links, depth) and the LAST notes of the same type are thin (no definitions,
no examples, no links, shallow). detect_drift must flag exactly the
degraded dimensions with evidence, and batch_gate must fail the batch
listing every offending note individually (a high average can never hide
them).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification.notequality import (  # noqa: E402
    QualityError,
    STANDARDS_VERSION,
    assess_note,
    assess_tree,
    batch_gate,
    detect_drift,
    load_provenance,
)

GOOD_CONCEPT = """---
title: {title}
type: concept
sources: "[[AI Course 03.1]]"
---

{title} is a core concept in machine learning. It is defined as the
relationship between inputs and outputs learned from data. The concept
matters because it underpins both theory and practice.

## Definition

Formally, the model is a function $f: X \\to Y$ minimizing expected loss:

$$
L(f) = \\mathbb{E}[\\ell(f(x), y)]
$$

## Intuition

For example, when we fit a line to points, we minimize squared error.
Consider the simplest case: one feature, one parameter. In practice the
same principle scales to millions of parameters.

## See also

- [[Loss Functions]]
- [[Optimization]]
"""

THIN_CONCEPT = """---
title: {title}
type: concept
---

{title} short note.
"""


def _write_series(root: Path, count: int, thin_from: int) -> None:
    """Write `count` concept notes; notes numbered >= thin_from are thin."""
    root.mkdir(parents=True, exist_ok=True)
    for companion in ("Loss Functions.md", "Optimization.md", "AI Course 03.1.md"):
        (root / companion).write_text(f"# {companion[:-3]}\n\nCompanion note.\n", encoding="utf-8")
    for i in range(1, count + 1):
        template = THIN_CONCEPT if i >= thin_from else GOOD_CONCEPT
        (root / f"{i:03d}-concept.md").write_text(
            template.replace("{title}", f"Concept {i}"), encoding="utf-8"
        )


# ---------------------------------------------------------------------------
# assessment basics


def test_assess_note_concept_dimensions_and_bands(tmp_path: Path):
    note = tmp_path / "c.md"
    note.write_text(GOOD_CONCEPT.replace("{title}", "Supervised Learning"), encoding="utf-8")
    report = assess_note(note)
    assert report["type"] == "concept"
    assert report["standards_version"] == STANDARDS_VERSION
    dims = report["dimensions"]
    assert dims["definitions"]["score"] == 1.0
    # without a vault_root the lint is structural-only: links present, no resolution
    assert dims["links"]["evidence"][0] == "2 internal links"
    # with a vault_root the unresolved links are defects -> score drops
    report_linked = assess_note(note, vault_root=tmp_path)
    assert report_linked["dimensions"]["links"]["score"] == 0.0
    assert report_linked["lint_error_count"] >= 1
    assert dims["source_coverage"]["score"] is None  # no provenance -> unmeasured
    assert dims["source_coverage"]["band"] == "unmeasured"
    assert dims["examples"]["score"] >= 0.6
    assert report["overall"] is not None and 0.0 <= report["overall"] <= 1.0


def test_note_type_from_frontmatter_drives_standard(tmp_path: Path):
    note = tmp_path / "d.md"
    note.write_text(
        "---\ntype: derivation\n---\n\nWe derive the gradient. Therefore it follows\n$$\ng = \\nabla L\n$$\n",
        encoding="utf-8",
    )
    report = assess_note(note)
    assert report["type"] == "derivation"
    assert report["dimensions"]["math_rigor"]["weight"] > report["dimensions"]["examples"]["weight"]


def test_missing_note_raises(tmp_path: Path):
    with pytest.raises(QualityError):
        assess_note(tmp_path / "ghost.md")


# ---------------------------------------------------------------------------
# source coverage with provenance mapping


def test_source_coverage_measured_with_provenance(tmp_path: Path):
    note = tmp_path / "n.md"
    note.write_text(
        "---\ntype: concept\n---\n\nBackpropagation is an algorithm. It is defined as the chain rule applied "
        "to networks. Gradients flow backwards through layers during training of neural networks.\n",
        encoding="utf-8",
    )
    batch = tmp_path / "batch.jsonl"
    batch.write_text(
        json.dumps({"ku_id": "KU-1", "topic": "backpropagation chain rule gradients"})
        + "\n"
        + json.dumps({"ku_id": "KU-2", "topic": "learning rate schedule decay"})
        + "\n",
        encoding="utf-8",
    )
    prov = tmp_path / "prov.jsonl"
    prov.write_text(json.dumps({"note": "n.md", "ku_ids": ["KU-1", "KU-2"]}) + "\n", encoding="utf-8")
    provenance = load_provenance(prov)
    report = assess_note(note, note_key="n.md", provenance=provenance, ku_batches=[batch])
    cov = report["dimensions"]["source_coverage"]
    assert cov["score"] == 0.5  # KU-1 covered, KU-2 not
    uncovered_ids = [u["ku_id"] for u in cov["uncovered"]]
    assert uncovered_ids == ["KU-2"]


def test_word_boundary_coverage_no_substring_false_positive(tmp_path: Path):
    note = tmp_path / "n.md"
    note.write_text("---\ntype: concept\n---\n\nWe cross the bridge to understand bridging.\n", encoding="utf-8")
    batch = tmp_path / "batch.jsonl"
    batch.write_text(json.dumps({"ku_id": "KU-1", "topic": "ridge regression regularization"}) + "\n", encoding="utf-8")
    prov = tmp_path / "prov.jsonl"
    prov.write_text(json.dumps({"note": "n.md", "ku_ids": ["KU-1"]}) + "\n", encoding="utf-8")
    report = assess_note(note, note_key="n.md", provenance=load_provenance(prov), ku_batches=[batch])
    cov = report["dimensions"]["source_coverage"]
    assert cov["score"] == 0.0  # 'ridge' must NOT match inside 'bridge'/'bridging'
    assert "ridge" in " ".join(cov["uncovered"][0].get("terms", []))


# ---------------------------------------------------------------------------
# THE drift scenario


def test_detect_drift_flags_degraded_late_notes(tmp_path: Path):
    vault = tmp_path / "vault"
    _write_series(vault, count=9, thin_from=7)  # notes 7,8,9 thin
    result = assess_tree(vault)
    drift = detect_drift(result["notes"])
    assert drift["verdict"] == "drift_detected"
    entry = next(e for e in drift["drifted_types"] if e["type"] == "concept")
    dims = {d["dimension"] for d in entry["drifted_dimensions"]}
    assert "definitions" in dims
    assert "examples" in dims
    for d in entry["drifted_dimensions"]:
        assert d["delta"] < 0
        assert d["first_third_mean"] > d["last_third_mean"]
        assert d["last_notes"]


def test_detect_drift_clean_when_consistent(tmp_path: Path):
    vault = tmp_path / "vault"
    _write_series(vault, count=9, thin_from=99)  # all good
    result = assess_tree(vault)
    drift = detect_drift(result["notes"])
    assert drift["verdict"] == "no_systematic_drift"


def test_detect_drift_too_few_notes(tmp_path: Path):
    vault = tmp_path / "vault"
    _write_series(vault, count=2, thin_from=2)
    result = assess_tree(vault)
    drift = detect_drift(result["notes"])
    entry = next(e for e in drift["clean_types"] if e["type"] == "concept")
    assert entry["verdict"] == "too_few_notes_to_compare"


# ---------------------------------------------------------------------------
# batch gate


def test_batch_gate_fails_listing_every_thin_note(tmp_path: Path):
    vault = tmp_path / "vault"
    _write_series(vault, count=9, thin_from=7)
    result = assess_tree(vault)
    drift = detect_drift(result["notes"])
    gate = batch_gate(result["notes"], expected_notes=[n["note"] for n in result["notes"]], drift_report=drift)
    assert gate["verdict"] == "fail"
    failed_notes = {f["note"] for f in gate["failures"]}
    assert any("007" in n for n in failed_notes)
    assert any("008" in n for n in failed_notes)
    assert any("009" in n for n in failed_notes)
    assert any(f["criterion"] == "no_unexplained_quality_drift" for f in gate["failures"])


def test_batch_gate_passes_on_consistent_vault(tmp_path: Path):
    vault = tmp_path / "vault"
    _write_series(vault, count=9, thin_from=99)
    result = assess_tree(vault)
    drift = detect_drift(result["notes"])
    batch = [n["note"] for n in result["notes"] if "concept" in n["note"]]
    gate = batch_gate(result["notes"], expected_notes=batch, drift_report=drift)
    assert gate["verdict"] == "pass", gate["failures"]


def test_batch_gate_missing_expected_note_fails(tmp_path: Path):
    vault = tmp_path / "vault"
    _write_series(vault, count=3, thin_from=99)
    result = assess_tree(vault)
    gate = batch_gate(result["notes"], expected_notes=[n["note"] for n in result["notes"]] + ["ghost.md"])
    assert gate["verdict"] == "fail"
    assert any(f["criterion"] == "expected_note_present" and f["note"] == "ghost.md" for f in gate["failures"])


def test_batch_gate_waiver_must_carry_reason(tmp_path: Path):
    vault = tmp_path / "vault"
    _write_series(vault, count=9, thin_from=7)
    result = assess_tree(vault)
    thin = [n for n in result["notes"] if n["dimensions"]["definitions"]["score"] == 0.0]
    target = thin[0]
    key = f"{target['note']}::definitions"
    gate = batch_gate(result["notes"], waivers={key: "intentionally minimal stub, approved in review"})
    assert not any(
        f.get("note") == target["note"] and f.get("dimension") == "definitions" for f in gate["failures"]
    )
    # waivers are recorded, not silent
    assert gate["waivers_applied"] == [(key, "intentionally minimal stub, approved in review")]


def test_high_average_cannot_hide_failing_note(tmp_path: Path):
    vault = tmp_path / "vault"
    _write_series(vault, count=9, thin_from=99)
    # one catastrophic note among eight good ones
    (vault / "010-broken.md").write_text(THIN_CONCEPT.replace("{title}", "Broken"), encoding="utf-8")
    result = assess_tree(vault)
    gate = batch_gate(result["notes"])
    assert gate["verdict"] == "fail"
    assert any("010-broken.md" in f["note"] for f in gate["failures"])


def test_assess_tree_deterministic(tmp_path: Path):
    vault = tmp_path / "vault"
    _write_series(vault, count=6, thin_from=4)
    r1 = assess_tree(vault)
    r2 = assess_tree(vault)
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)
