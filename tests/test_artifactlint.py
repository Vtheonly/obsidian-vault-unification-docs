"""CAP-018 tests: artifact integrity validation (artifactlint).

Fixture policy mirrors tests/test_discovery.py: every check family gets a
minimal synthetic document that deliberately triggers it, plus clean
documents that must produce ZERO errors (false-positive guard — a linter
that cries wolf gets ignored, which is worse than no linter).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification.artifactlint import (  # noqa: E402
    ArtifactLintError,
    lint_file,
    lint_text,
    lint_tree,
)


def _checks(report: dict, *check_ids: str) -> list[dict]:
    return [d for d in report["defects"] if d["check"] in check_ids]


# ---------------------------------------------------------------------------
# false-positive guards FIRST: clean documents must stay clean


def test_clean_concept_note_has_zero_errors():
    text = """---
title: Gradient Descent
type: concept
---

Gradient descent is an iterative optimization algorithm. It is defined as
the repeated update of parameters against the gradient of the loss.

## Intuition

The method follows the slope downhill. Each step is scaled by a learning
rate $\\eta$, and the update rule is:

$$
\\theta_{t+1} = \\theta_t - \\eta \\nabla L(\\theta_t)
$$

## Algorithm

1. initialize $\\theta_0$
2. compute the gradient
3. update, repeat until convergence

| symbol | meaning |
| --- | --- |
| $\\theta$ | parameters |
| $\\eta$ | learning rate |

See [[Learning Rate]] for the companion note.
"""
    report = lint_text(text)
    assert report["error_count"] == 0, report["defects"]
    assert report["warning_count"] == 0, report["defects"]


def test_clean_mermaid_flowchart_and_sequence():
    text = """```mermaid
flowchart TD
    A[Start] --> B{Ready?}
    B -->|yes| C[Run]
    C --> D[End]
```

```mermaid
sequenceDiagram
    participant U as User
    participant S as Server
    U->>S: request
    activate S
    S-->>U: response
    deactivate S
```
"""
    report = lint_text(text)
    assert report["error_count"] == 0, report["defects"]


def test_clean_subgraph_balanced():
    text = """```mermaid
flowchart LR
    subgraph prep
        A --> B
    end
    B --> C
```
"""
    report = lint_text(text)
    assert report["error_count"] == 0, report["defects"]


def test_pipe_in_prose_is_not_a_table():
    text = "In logic we write a|b to mean disjunction. This is prose, not a table.\n"
    report = lint_text(text)
    assert not _checks(report, "TABLE_SEPARATOR_MISSING", "TABLE_SEPARATOR_BAD")


# ---------------------------------------------------------------------------
# per-family defect fixtures


def test_unclosed_fence_detected():
    report = lint_text("# T\n\n```python\nx = 1\n")
    hits = _checks(report, "FENCE_UNCLOSED")
    assert len(hits) == 1 and hits[0]["severity"] == "error"
    assert hits[0]["line"] == 3


def test_unclosed_math_block_detected():
    report = lint_text("Text\n\n$$\nx = 1\n")
    hits = _checks(report, "MATH_BLOCK_UNCLOSED")
    assert len(hits) == 1 and hits[0]["severity"] == "error"


def test_odd_inline_dollars_flagged_as_warning():
    report = lint_text("This costs 5$ at the store, or so the prose claims.\n")
    hits = _checks(report, "MATH_INLINE_ODD")
    assert len(hits) == 1 and hits[0]["severity"] == "warning"


def test_math_env_mismatch_detected():
    report = lint_text("$$\n\\begin{aligned}\nx &= 1\n\\end{cases}\n$$\n")
    hits = _checks(report, "MATH_ENV_MISMATCH")
    assert hits, report["defects"]
    assert all(h["severity"] == "error" for h in hits)


def test_table_separator_cell_count_mismatch():
    report = lint_text("| a | b |\n| --- |\n| 1 | 2 |\n")
    assert len(_checks(report, "TABLE_SEPARATOR_BAD")) == 1
    assert len(_checks(report, "TABLE_CELL_MISMATCH")) == 0  # row matches header


def test_table_row_cell_count_mismatch():
    report = lint_text("| a | b |\n| --- | --- |\n| 1 |\n")
    assert len(_checks(report, "TABLE_CELL_MISMATCH")) == 1
    assert len(_checks(report, "TABLE_SEPARATOR_BAD")) == 0


def test_heading_hierarchy_skip_detected():
    report = lint_text("# Title\n\n### Skipped to three\n")
    assert len(_checks(report, "HEADING_SKIP")) == 1


def test_python_syntax_error_in_code_block():
    report = lint_text("```python\ndef f(:\n```\n")
    hits = _checks(report, "CODE_PYTHON_SYNTAX")
    assert len(hits) == 1 and hits[0]["severity"] == "error"


def test_invalid_json_block_detected():
    report = lint_text("```json\n{\"a\": }\n```\n")
    assert len(_checks(report, "CODE_JSON_INVALID")) == 1


def test_missing_language_is_info_not_error():
    report = lint_text("```\nplain text\n```\n")
    hits = _checks(report, "CODE_LANG_MISSING")
    assert len(hits) == 1 and hits[0]["severity"] == "info"


def test_mermaid_prose_line_rejected():
    text = "```mermaid\nflowchart TD\nA --> B\nthis line is just prose, not a diagram statement\n```\n"
    report = lint_text(text)
    hits = _checks(report, "MERMAID_PARSE")
    assert len(hits) == 1 and hits[0]["line"] == 4


def test_mermaid_missing_end_detected():
    text = "```mermaid\nsequenceDiagram\nA->>B: hi\nalt cond\nB-->>A: bye\n```\n"
    report = lint_text(text)
    hits = _checks(report, "MERMAID_PARSE")
    assert any("unclosed" in h["message"] for h in hits)


def test_mermaid_unknown_declaration_detected():
    text = "```mermaid\nnotadiagram\nA --> B\n```\n"
    report = lint_text(text)
    assert len(_checks(report, "MERMAID_PARSE")) == 1


def test_placeholder_markers_flagged():
    report = lint_text("Intro.\n\nTODO: write this.\n\nFIXME later.\n")
    hits = _checks(report, "PLACEHOLDER_TEXT")
    assert len(hits) == 2


def test_todo_inside_code_fence_not_flagged():
    report = lint_text("```python\n# TODO: implement\nx = 1\n```\n")
    assert not _checks(report, "PLACEHOLDER_TEXT")


def test_mid_sentence_ending_flagged():
    report = lint_text("Intro.\n\nThe derivation ends abruptly without\n")
    hits = _checks(report, "TRUNCATION_MID_SENTENCE")
    assert len(hits) == 1


def test_structural_ending_not_flagged():
    report = lint_text("Intro.\n\n- item one\n- item two\n")
    assert not _checks(report, "TRUNCATION_MID_SENTENCE")


def test_empty_section_flagged_info():
    report = lint_text("# Title\n\nintro text here.\n\n## Empty\n\n## Full\n\ncontent here.\n")
    hits = _checks(report, "EMPTY_SECTION")
    assert len(hits) == 1 and hits[0]["severity"] == "info"
    assert "Empty" in hits[0]["message"]


def test_mixed_math_delimiters_info():
    report = lint_text("$$\na = b\n$$\n\n\\[\nc = d\n\\]\n")
    assert len(_checks(report, "MATH_DELIM_STYLE_MIXED")) == 1


def test_invalid_frontmatter_detected():
    report = lint_text("---\ntitle: [unclosed\n---\n\nbody\n")
    assert len(_checks(report, "FRONTMATTER_INVALID")) == 1


# ---------------------------------------------------------------------------
# frontmatter field-shape (FRONTMATTER_FIELD_TYPE, F-0030)


def test_frontmatter_stray_bracket_tag_flagged():
    report = lint_text("---\ntitle: X\ntags: oc, machine-learning]\n---\n\nbody text.\n")
    hits = _checks(report, "FRONTMATTER_FIELD_TYPE")
    assert len(hits) == 1 and hits[0]["severity"] == "error"
    assert "tags" in hits[0]["message"]


def test_frontmatter_missing_open_bracket_alias_flagged():
    report = lint_text("---\ntitle: X\naliases: [a, b]\nsources: S1]\n---\n\nbody text.\n")
    hits = _checks(report, "FRONTMATTER_FIELD_TYPE")
    assert len(hits) == 1 and "sources" in hits[0]["message"]


def test_frontmatter_flow_list_ok():
    report = lint_text("---\ntitle: X\ntags: [oc, machine-learning]\n---\n\nbody text.\n")
    assert not _checks(report, "FRONTMATTER_FIELD_TYPE")


def test_frontmatter_block_list_ok():
    report = lint_text("---\ntitle: X\ntags:\n  - oc\n  - machine-learning\n---\n\nbody text.\n")
    assert not _checks(report, "FRONTMATTER_FIELD_TYPE")


def test_frontmatter_bracket_free_scalar_ok():
    # a scalar without brackets is not a proven defect (Obsidian accepts it)
    report = lint_text("---\ntitle: X\naliases: single alias\n---\n\nbody text.\n")
    assert not _checks(report, "FRONTMATTER_FIELD_TYPE")


def test_frontmatter_quoted_wikilink_scalar_ok():
    # quoted scalars are deliberate string values (e.g. a single wikilink
    # source), not hand-typed list typos
    report = lint_text('---\ntitle: X\nsources: "[[AI Course 03.1]]"\n---\n\nbody text.\n')
    assert not _checks(report, "FRONTMATTER_FIELD_TYPE")


def test_frontmatter_non_scalar_member_flagged():
    report = lint_text("---\ntitle: X\ntags:\n  - [nested, list]\n---\n\nbody text.\n")
    hits = _checks(report, "FRONTMATTER_FIELD_TYPE")
    assert len(hits) == 1 and "non-scalar member" in hits[0]["message"]


def test_frontmatter_non_mapping_flagged():
    report = lint_text("---\n- just\n- a list\n---\n\nbody text.\n")
    hits = _checks(report, "FRONTMATTER_FIELD_TYPE")
    assert len(hits) == 1 and "mapping" in hits[0]["message"]


def test_frontmatter_empty_ok():
    report = lint_text("Just body text with no frontmatter at all.\n")
    assert not _checks(report, "FRONTMATTER_FIELD_TYPE")


# ---------------------------------------------------------------------------
# link integration + file/tree level


def test_broken_internal_link_detected(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "real.md").write_text("# Real\n", encoding="utf-8")
    (vault / "note.md").write_text(
        "Link to [[real]] works, but [[ghost]] does not.\n", encoding="utf-8"
    )
    report = lint_tree(vault)
    broken = [d for f in report["files"] for d in f["defects"] if d["check"] == "LINK_BROKEN"]
    assert len(broken) == 1
    assert broken[0]["excerpt"].startswith("ghost")
    assert report["summary"]["files"] == 2


def test_folder_link_is_not_a_defect(tmp_path: Path):
    vault = tmp_path / "vault"
    (vault / "folder").mkdir(parents=True)
    (vault / "note.md").write_text("Index: [[folder]]\n", encoding="utf-8")
    report = lint_tree(vault)
    link_defects = [d for f in report["files"] for d in f["defects"] if d["check"].startswith("LINK_")]
    assert link_defects == []


def test_lint_file_requires_existing_file(tmp_path: Path):
    with pytest.raises(ArtifactLintError):
        lint_file(tmp_path / "missing.md")


def test_lint_tree_requires_directory(tmp_path: Path):
    with pytest.raises(ArtifactLintError):
        lint_tree(tmp_path / "nope")


def test_deterministic_order_and_counts(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "a.md").write_text("```python\nbad(\n```\n", encoding="utf-8")
    r1 = lint_tree(vault)
    r2 = lint_tree(vault)
    assert r1 == r2  # fully deterministic, byte-identical reports


def test_caveat_present_in_tree_report(tmp_path: Path):
    vault = tmp_path
    (vault / "x.md").write_text("ok\n", encoding="utf-8")
    report = lint_tree(vault)
    assert "never sufficient" in report["caveat"]


# ---------------------------------------------------------------------------
# regression guards: REAL mermaid forms found in the source corpus during the
# FRAME-002 baseline lint (every form below once produced a false positive;
# these tests pin the permissive grammar)


@pytest.mark.parametrize(
    "line",
    [
        'K5["K=5<br/> Recommended"] --- K10["K=10<br/>More thorough"]',
        'A[Input Data: Drug Dosage] --> B[Forward Pass: Neural Network]',
        'A[Function Equation: y = f of x] --> B(Plot the Curve)',
        'A -. "Chain Rule: Multiply the rates" .-> C',
        'A["Original Equation: f(g(x))"] --> B["Identify Inside Function: g(x)"]',
        "X ~~~ A",
        "L1 <-- L2 <-- L3 <-- LN",
        "L((Loss)):::output",
        'DeltaP(("δ_p (Output Error)")):::output',
        "W2((Weight w2_1)):::hidden",
        'V["[ C1_row1, C1_row2, ..., C2_row1 ]"]',
        "Subgraph --> ContextFuse[Context Fusion]",
    ],
)
def test_real_corpus_mermaid_forms_are_valid(line):
    text = f"```mermaid\nflowchart TD\nA[Start]\n{line}\n```\n"
    report = lint_text(text)
    assert not _checks(report, "MERMAID_PARSE"), (line, report["defects"])


def test_gantt_task_rows_are_valid():
    text = (
        "```mermaid\ngantt\ntitle Batch\nsection S\n"
        "Short req 1 :done, a1, 0, 5\n"
        "Long req :active, a4, 0, 30\n"
        "```\n"
    )
    report = lint_text(text)
    assert not _checks(report, "MERMAID_PARSE"), report["defects"]


# F-0025 regression: open dotted links (no arrowhead) with text are valid
# mermaid (A-. text .-B). The construct appears live in the unified-vault
# synthesis output (KNN / evaluation notes copy it from ai-course sources,
# where it was hidden inside a ```markdown fence and thus never calibrated).


@pytest.mark.parametrize(
    "line",
    [
        "New -. distance .- C",
        "A-. text .-B",
        "A -.- B",
        "A-.-> B",
    ],
)
def test_open_dotted_links_are_valid(line):
    text = f"```mermaid\nflowchart TD\nA[Start]\n{line}\n```\n"
    report = lint_text(text)
    assert not _checks(report, "MERMAID_PARSE"), (line, report["defects"])


def test_mermaid_prose_still_rejected_after_dotted_link_fix():
    text = "```mermaid\nflowchart TD\nA --> B\nthis line is just prose, not a diagram statement\n```\n"
    report = lint_text(text)
    assert _checks(report, "MERMAID_PARSE")


# F-0026 regression: half-open interval notation inside inline math
# ($\gamma \in [0, 1)$ etc.) must not trigger BRACKET_UNBALANCED.


def test_half_open_intervals_in_inline_math_do_not_unbalance():
    text = (
        "The discount factor $\\gamma \\in [0, 1)$ weighs future rewards, "
        "and the shrinkage $\\nu \\in (0, 1]$ scales each tree.\n"
    )
    report = lint_text(text)
    assert not _checks(report, "BRACKET_UNBALANCED"), report["defects"]


def test_genuinely_unbalanced_brackets_still_detected():
    text = "An unclosed paren ( like this stays a finding.\n"
    report = lint_text(text)
    assert _checks(report, "BRACKET_UNBALANCED")
