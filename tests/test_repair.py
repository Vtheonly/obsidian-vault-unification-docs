"""CAP-020 tests: evidence-based targeted repair loop.

Covers the full lifecycle: defect -> task -> attempt -> verification ->
bounded escalation; plus idempotent creation, regression re-opening, and
repair-scope discipline (a whole-note rewrite of unrelated content must be
REJECTED even when the defect itself is fixed).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification.artifactlint import lint_text  # noqa: E402
from vault_unification.repair import (  # noqa: E402
    RepairError,
    apply_verification,
    create_repair_tasks,
    merge_tasks,
    record_attempt,
    task_status,
    verify_repair,
)

BROKEN = """# Note

Some text with a bad python block:

```python
def f(:
```

Body line one with real content.
Body line two with more content.
Body line three keeps going.
Body line four for distance.
Body line five for distance.
Body line six for distance.
Body line seven for distance.
Body line eight for distance.

And a good tail paragraph that ends properly.
"""

FIXED = BROKEN.replace("def f(:", "def f():\n    pass")

# fix is correct BUT an unrelated line FAR from the defect was rewritten too
SCOPE_VIOLATION = FIXED.replace("And a good tail paragraph", "And a MALICIOUSLY rewritten paragraph")


def _first_task(text: str, name: str = "note.md") -> dict:
    report = lint_text(text, path=name)
    tasks = create_repair_tasks([report])
    assert tasks, "expected at least one repairable defect"
    return tasks[0]


# ---------------------------------------------------------------------------
# creation


def test_error_and_warning_defects_become_tasks_info_does_not():
    report = lint_text("```python\nbad(\n```\n\nTODO: x\n")
    tasks = create_repair_tasks([report])
    checks = {t["check"] for t in tasks}
    assert "CODE_PYTHON_SYNTAX" in checks
    assert "PLACEHOLDER_TEXT" in checks  # warning -> repairable
    assert all(t["status"] == "open" for t in tasks)
    assert all(t["expected_fix"] for t in tasks)


def test_creation_is_idempotent_and_merges():
    report = lint_text(BROKEN, path="note.md")
    t1 = create_repair_tasks([report])
    t2 = create_repair_tasks([report])
    merged, added = merge_tasks(t1, t2)
    assert added == []
    assert len(merged) == len(t1)
    assert all(t["repair_id"] == u["repair_id"] for t, u in zip(t1, merged))


def test_task_ids_are_content_addressed_and_stable():
    a = _first_task(BROKEN)
    b = _first_task(BROKEN)
    assert a["repair_id"] == b["repair_id"]
    assert a["repair_id"].startswith("RT-")


# ---------------------------------------------------------------------------
# attempts and bounded escalation


def test_fixed_moves_to_awaiting_verification():
    task = _first_task(BROKEN)
    updated = record_attempt(task, "fixed", note="closed the paren")
    assert updated["status"] == "awaiting_verification"
    assert len(updated["attempts"]) == 1


def test_bounded_retries_escalate_after_max_attempts():
    task = _first_task(BROKEN)
    for i in range(task["max_attempts"]):
        task = record_attempt(task, "failed", note=f"attempt {i + 1}")
    assert task["status"] == "escalated_review"
    assert len(task["attempts"]) == task["max_attempts"]


def test_invalid_outcome_rejected():
    task = _first_task(BROKEN)
    with pytest.raises(RepairError):
        record_attempt(task, "magically-perfect")


# ---------------------------------------------------------------------------
# verification


def test_successful_repair_verifies_and_closes():
    task = _first_task(BROKEN)
    verification = verify_repair(task, FIXED, original_text=BROKEN)
    assert verification["verified"], verification
    closed = apply_verification(task, verification)
    assert closed["status"] == "verified_fixed"


def test_unfixed_content_fails_verification():
    task = _first_task(BROKEN)
    verification = verify_repair(task, BROKEN, original_text=BROKEN)
    assert not verification["verified"]
    assert "still present" in verification["reason"]


def test_repair_introducing_new_defects_fails():
    task = _first_task(BROKEN)
    # fix the python but break a table elsewhere
    sabotaged = FIXED + "\n| a | b |\n| --- |\n"
    verification = verify_repair(task, sabotaged, original_text=BROKEN)
    assert not verification["verified"]
    assert "new defects" in verification["reason"]


def test_scope_violation_rejected_even_when_defect_fixed():
    """The core anti-rewrite-guard: fixing the defect while rewriting
    unrelated content must NOT verify."""
    task = _first_task(BROKEN)
    verification = verify_repair(task, SCOPE_VIOLATION, original_text=BROKEN)
    assert not verification["verified"]
    assert "far from the defect" in verification["reason"]


def test_verification_without_original_skips_scope_check():
    task = _first_task(BROKEN)
    verification = verify_repair(task, SCOPE_VIOLATION)
    assert verification["verified"]  # no original -> no scope evidence; origin passes


# ---------------------------------------------------------------------------
# regression handling


def test_verified_fix_reopens_when_defect_returns():
    task = _first_task(BROKEN)
    verification = verify_repair(task, FIXED, original_text=BROKEN)
    task = apply_verification(task, verification)
    assert task["status"] == "verified_fixed"

    # defect comes back in a fresh lint run -> merge re-opens with history
    fresh = create_repair_tasks([lint_text(BROKEN, path="note.md")])
    merged, added = merge_tasks([task], fresh)
    assert added == []
    reopened = next(t for t in merged if t["repair_id"] == task["repair_id"])
    assert reopened["status"] == "open"
    assert any(a["outcome"] == "regression_detected" for a in reopened["attempts"])


def test_task_status_aggregates():
    tasks = create_repair_tasks([lint_text(BROKEN, path="note.md")])
    status = task_status(tasks)
    assert status["total"] == len(tasks)
    assert status["by_status"].get("open") == len(tasks)
    assert status["escalated"] == []
