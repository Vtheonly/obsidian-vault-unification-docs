"""CAP-021 tests: generation-prompt specification and validation.

Covers: testable acceptance criteria (lint/quality/manual references),
vague-language rejection, ku_id resolvability against real batches,
boundedness (requirements cap, context budget), standing constraints, and
repair-prompt construction from a repair task.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification.promptspec import (  # noqa: E402
    PromptSpecError,
    build_repair_prompt,
    check_prompt,
    load_prompt_spec,
)

GOOD_SPEC = {
    "objective": "Write the unified note for the chain-rule concept",
    "target_note": {"path": "unified/concepts/Chain Rule.md", "type": "concept"},
    "source_evidence": {
        "ku_ids": ["KU-1", "KU-2"],
        "files": [],
        "excerpts": ["the chain rule states that d/dx f(g(x)) = f'(g(x)) g'(x)"],
    },
    "requirements": [
        "define the chain rule with the standard formula",
        "give one worked example with numbers",
        "link to [[Backpropagation]] and [[Gradient]]",
    ],
    "constraints": [
        "do not invent content; every claim must trace to the provided KU evidence",
        "preserve provenance: cite source ku_ids in frontmatter",
    ],
    "acceptance_criteria": [
        {"criterion": "no unclosed math blocks", "check": "lint:MATH_BLOCK_UNCLOSED"},
        {"criterion": "definitions dimension within band", "check": "quality:definitions"},
        {"criterion": "formula correctness", "check": "manual_review"},
    ],
    "output_contract": {"path": "unified/concepts/Chain Rule.md", "format": "markdown"},
}


@pytest.fixture()
def batch(tmp_path: Path) -> Path:
    p = tmp_path / "batch.jsonl"
    p.write_text(
        json.dumps({"ku_id": "KU-1", "topic": "chain rule differentiation"})
        + "\n"
        + json.dumps({"ku_id": "KU-2", "topic": "composite functions gradient"})
        + "\n",
        encoding="utf-8",
    )
    return p


# ---------------------------------------------------------------------------
# good spec


def test_good_spec_passes(batch: Path):
    result = check_prompt(GOOD_SPEC, ku_batches=[batch])
    assert result["ok"], [c for c in result["checks"] if not c["ok"]]
    assert result["estimated_context_words"] > 0


def test_spec_roundtrip_via_file(tmp_path: Path):
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(GOOD_SPEC), encoding="utf-8")
    loaded = load_prompt_spec(spec_path)
    assert loaded["objective"] == GOOD_SPEC["objective"]
    with pytest.raises(PromptSpecError):
        load_prompt_spec(tmp_path / "missing.json")


# ---------------------------------------------------------------------------
# individual check families


def test_missing_target_note_fails():
    spec = {**GOOD_SPEC, "target_note": {}}
    result = check_prompt(spec)
    assert not result["ok"]
    assert any(c["check"] == "target_note_present" and not c["ok"] for c in result["checks"])


def test_unresolvable_ku_ids_fail(batch: Path):
    spec = {**GOOD_SPEC, "source_evidence": {**GOOD_SPEC["source_evidence"], "ku_ids": ["KU-GHOST"]}}
    result = check_prompt(spec, ku_batches=[batch])
    assert not result["ok"]
    resolvable = next(c for c in result["checks"] if c["check"] == "source_evidence_resolvable")
    assert "KU-GHOST" in resolvable["detail"]


def test_untestable_criterion_fails():
    spec = {**GOOD_SPEC, "acceptance_criteria": [{"criterion": "should be well written", "check": "vibes"}]}
    result = check_prompt(spec)
    assert not result["ok"]
    testable = next(c for c in result["checks"] if c["check"] == "acceptance_criteria_testable")
    assert not testable["ok"]


def test_vague_language_flagged():
    spec = {**GOOD_SPEC, "acceptance_criteria": [{"criterion": "note must be polished and nice", "check": "manual_review"}]}
    result = check_prompt(spec)
    vague = next(c for c in result["checks"] if c["check"] == "no_unoperationalized_language")
    assert not vague["ok"]


def test_all_manual_criteria_fail_machine_check_requirement():
    spec = {**GOOD_SPEC, "acceptance_criteria": [{"criterion": "x", "check": "manual_review"}]}
    result = check_prompt(spec)
    assert any(c["check"] == "at_least_one_machine_check" and not c["ok"] for c in result["checks"])


def test_missing_standing_constraints_fail():
    spec = {**GOOD_SPEC, "constraints": ["be terse"]}
    result = check_prompt(spec)
    assert not result["ok"]
    assert any(c["check"].startswith("constraint:") and not c["ok"] for c in result["checks"])


def test_requirements_cap_enforced():
    spec = {**GOOD_SPEC, "requirements": [f"requirement number {i}" for i in range(30)]}
    result = check_prompt(spec, max_requirements=25)
    bounded = next(c for c in result["checks"] if c["check"] == "requirements_bounded")
    assert not bounded["ok"] and "split the task" in bounded["detail"]


def test_context_budget_exceeded():
    big = ["word " * 50 for _ in range(40)]  # ~2000 words of excerpts
    spec = {**GOOD_SPEC, "source_evidence": {**GOOD_SPEC["source_evidence"], "excerpts": big}}
    result = check_prompt(spec, context_budget_words=500)
    budget = next(c for c in result["checks"] if c["check"] == "context_budget_respected")
    assert not budget["ok"] and "EXCEEDS" in budget["detail"]


def test_missing_output_contract_fails():
    spec = {**GOOD_SPEC, "output_contract": {}}
    result = check_prompt(spec)
    assert any(c["check"] == "output_contract_present" and not c["ok"] for c in result["checks"])


# ---------------------------------------------------------------------------
# repair prompts


def test_build_repair_prompt_is_targeted():
    task = {
        "repair_id": "RT-abc123def456",
        "file": "notes/broken.md",
        "line": 12,
        "check": "MERMAID_PARSE",
        "severity": "error",
        "message": "unclosed 'subgraph' block (missing 'end')",
        "original_excerpt": "subgraph s",
        "expected_fix": "repair the diagram line so it matches the declared diagram grammar",
        "max_attempts": 3,
        "attempts": [],
    }
    spec = build_repair_prompt(task, note_path="notes/broken.md")
    assert spec["target_note"]["path"] == "notes/broken.md"
    assert "MERMAID_PARSE" in spec["objective"]
    # the acceptance criteria are machine-checkable against the originating check
    checks = [c["check"] for c in spec["acceptance_criteria"]]
    assert "lint:MERMAID_PARSE" in checks
    # anti-rewrite constraint is baked in
    assert any("do not rewrite" in c for c in spec["constraints"])
    # and the repair prompt itself passes check_prompt against its own rules
    # (objective, evidence, criteria, constraints, contract all present)
    result = check_prompt(spec)
    assert result["ok"], [c for c in result["checks"] if not c["ok"]]
